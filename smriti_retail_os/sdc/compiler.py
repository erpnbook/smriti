# -*- coding: utf-8 -*-
#
# @file: sdc/compiler.py
# @description: Core compiler runtime framework for SMRITI Documentation Compiler (SDC) v1.1.2 GA
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
#

import os
import json
import hashlib
import sys
import datetime
import io

# Standard SDC Exit Codes
EXIT_CODES = {
    "SDC000": 0,    # Success
    "SDC101": 101,  # Repository not found
    "SDC102": 102,  # IR validation failed (Schema mismatch)
    "SDC103": 103,  # Policy validation failed (Schema/Content error)
    "SDC104": 104,  # Snapshot corruption / load failure
    "SDC105": 105,  # Unsupported schema/policy version
    "SDC201": 201,  # Structural regression (Missing files / broken links)
    "SDC202": 202,  # Semantic regression warning
    "SDC301": 301,  # Dependency graph inconsistent (cycle or orphans)
    "SDC401": 401,  # Quality gate failed (coverage < threshold or broken references > 0)
    "SDC402": 402,  # Formula drift detected
    "SDC403": 403   # Banned terminology drift detected
}


class SDCLogger:
    @staticmethod
    def log(level, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    @staticmethod
    def info(message):
        SDCLogger.log("INFO", message)

    @staticmethod
    def warn(message):
        SDCLogger.log("WARN", message)

    @staticmethod
    def error(message):
        SDCLogger.log("ERROR", message)


class SDCException(Exception):
    def __init__(self, code, message):
        super(SDCException, self).__init__(message)
        self.code = code


def sdc_exit(code_str, message):
    """Gracefully log and exit SDC compilation with corresponding code."""
    code = EXIT_CODES.get(code_str, 1)
    if code == 0:
        SDCLogger.info(f"SUCCESS: {message}")
    else:
        SDCLogger.error(f"FAILURE [{code_str}]: {message}")
    sys.exit(code)


class CompilerConfig(object):
    def __init__(self, config_path=None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compiler_config.json")
        self.config_path = config_path
        self.data = {}
        self.load()

    def load(self):
        if not os.path.exists(self.config_path):
            raise SDCException("SDC101", f"Compiler configuration not found at {self.config_path}")
        try:
            with io.open(self.config_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            SDCLogger.info("Compiler configuration loaded successfully.")
        except Exception as e:
            raise SDCException("SDC102", f"Failed to parse compiler configuration: {str(e)}")

    def get(self, key, default=None):
        return self.data.get(key, default)


class ArtifactRegistry(object):
    def __init__(self, registry_path=None):
        if not registry_path:
            registry_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifact_registry.json")
        self.registry_path = registry_path
        self.data = {"lease_count": 0, "artifacts": {}}
        self.load()

    def load(self):
        if os.path.exists(self.registry_path):
            try:
                with io.open(self.registry_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                SDCLogger.warn(f"Failed to parse registry: {str(e)}. Initializing clean registry.")

    def save(self):
        try:
            with io.open(self.registry_path, "w", encoding="utf-8") as f:
                # In Python 2, json.dumps might produce unicode. Write as unicode text.
                content = json.dumps(self.data, indent=2, ensure_ascii=False)
                f.write(content if isinstance(content, type(u"")) else content.decode("utf-8"))
        except Exception as e:
            SDCLogger.error(f"Failed to save registry: {str(e)}")

    def lease_id(self, artifact_type, identifier_name):
        """
        Leases a permanent, stable Artifact ID for a given code/schema element name.
        Guarantees that moving or reorganizing components preserves their ID.
        """
        artifacts = self.data.setdefault("artifacts", {})
        key = f"{artifact_type}:{identifier_name}"
        
        if key in artifacts:
            # Return leased ID
            record = artifacts[key]
            if record.get("status") == "RETIRED":
                # Re-activate if found again
                record["status"] = "ACTIVE"
                self.save()
            return record["id"]

        # Lease a new ID
        self.data["lease_count"] += 1
        new_id = f"ART-{artifact_type.upper()}-{self.data['lease_count']:05d}"
        artifacts[key] = {
            "id": new_id,
            "name": identifier_name,
            "type": artifact_type,
            "status": "ACTIVE",
            "leased_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save()
        SDCLogger.info(f"Leased new Stable Identity: {new_id} -> {key}")
        return new_id


class SDCValidator(object):
    @staticmethod
    def validate_schema(data, schema_name):
        """
        Lightweight, dependency-free schema validator for SDC JSON drafts.
        Ensures strict type-checking and field presence.
        """
        schema_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "schemas", f"{schema_name}.schema.json"
        )
        if not os.path.exists(schema_path):
            raise SDCException("SDC102", f"Schema file not found: {schema_path}")

        try:
            with io.open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
        except Exception as e:
            raise SDCException("SDC102", f"Failed to parse schema file {schema_name}: {str(e)}")

        # Validate core fields
        required = schema.get("required", [])
        for req in required:
            if req not in data:
                raise SDCException("SDC102", f"Validation error in schema '{schema_name}': Missing required property '{req}'")

        # Validate types
        properties = schema.get("properties", {})
        for prop_name, prop_def in properties.items():
            if prop_name in data:
                val = data[prop_name]
                expected_type = prop_def.get("type", "").upper()
                
                if expected_type == "STRING" and not isinstance(val, (str, type(u""))):
                    raise SDCException("SDC102", f"Schema type mismatch: property '{prop_name}' must be STRING.")
                elif expected_type == "INTEGER" and not isinstance(val, (int, long) if sys.version_info[0] < 3 else int):
                    raise SDCException("SDC102", f"Schema type mismatch: property '{prop_name}' must be INTEGER.")
                elif expected_type == "OBJECT" and not isinstance(val, dict):
                    raise SDCException("SDC102", f"Schema type mismatch: property '{prop_name}' must be OBJECT.")
                elif expected_type == "ARRAY" and not isinstance(val, list):
                    raise SDCException("SDC102", f"Schema type mismatch: property '{prop_name}' must be ARRAY.")

        SDCLogger.info(f"Schema validation passed: {schema_name}")
        return True


def get_git_commit(repo_path):
    """Helper to extract git head hash from repository files without execution."""
    git_dir = os.path.join(repo_path, ".git")
    if not os.path.exists(git_dir):
        return "UNKNOWN_COMMIT"
    
    try:
        # Read HEAD reference pointer
        head_path = os.path.join(git_dir, "HEAD")
        with io.open(head_path, "r", encoding="utf-8") as f:
            ref = f.read().strip()
        
        if ref.startswith("ref:"):
            ref_path = os.path.join(git_dir, ref.split(" ")[1].replace("/", os.sep))
            if os.path.exists(ref_path):
                with io.open(ref_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
        else:
            return ref
    except Exception:
        pass
    return "UNKNOWN_COMMIT"
