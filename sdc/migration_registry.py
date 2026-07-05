# -*- coding: utf-8 -*-
#
# @file: sdc/migration_registry.py
# @description: IR Schema Migration Registry for SMRITI SDC v1.x
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.1.2-GA
#

class IRMigratorRegistry(object):
    @classmethod
    def migrate(cls, data, target_version="1.2"):
        current_version = data.get("ir_version") or data.get("schema_version") or "1.0"
        if current_version == target_version:
            return data

        # Simple pipeline of migrators
        if current_version == "1.0":
            data = cls.migrate_10_to_11(data)
            current_version = "1.1"

        if current_version == "1.1":
            data = cls.migrate_11_to_12(data)
            current_version = "1.2"

        return data

    @classmethod
    def migrate_10_to_11(cls, data):
        # Upgrade metadata structure from 1.0 to 1.1
        data["ir_version"] = "1.1"
        data["schema_version"] = "1.1"
        return data

    @classmethod
    def migrate_11_to_12(cls, data):
        # Upgrade metadata structure from 1.1 to 1.2
        data["ir_version"] = "1.2"
        data["schema_version"] = "1.2"
        
        # Ensure all entities have status defaults if missing
        # SMRITI supports: files, doctypes, fields, apis, business_dictionary, screens
        for key in ["data", "doctypes", "fields", "apis", "business_dictionary", "screens"]:
            if key in data:
                # In some inventory files, data is stored as a list
                items = data[key]
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            if "validation_status" not in item:
                                item["validation_status"] = "Verified"
                            if "operational_status" not in item:
                                item["operational_status"] = "Active"
                            if "coverage_rules" not in item:
                                item["coverage_rules"] = {}
                            if "coverage_score" not in item:
                                item["coverage_score"] = 100.0
        return data
