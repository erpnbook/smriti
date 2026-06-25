# SMRITI Documentation Compiler (SDC) — Technical Specification (v1.1.2 GA)

---

## 1. Intermediate Representation (IR) Contracts

Every JSON artifact generated during Phase 0 must conform to the following schema wrappers and structures.

### A. Run Manifest Schema (`discovery_manifest.json`)
```json
{
  "ir_version": "1.0",
  "compiler_version": "1.1",
  "artifact_type": "discovery_manifest",
  "generated_at": "ISO_TIMESTAMP",
  "repository_commit": "SHA1_HASH",
  "provenance": {
    "artifact_id": "ART-MANIFEST-00001",
    "produced_by": "Phase0_Discovery",
    "consumes": [],
    "used_by": ["compiler_core"]
  },
  "data": {
    "scan_scope": ["apps/smriti_retail_os"],
    "excluded": ["node_modules", ".git", "__pycache__", "env", "venv"],
    "generated_artifacts": [
      "docs/discovery/file_inventory.json",
      "docs/discovery/doctype_inventory.json",
      "docs/discovery/field_inventory.json",
      "docs/discovery/api_inventory.json",
      "docs/discovery/dependency_graph.json"
    ]
  }
}
```

### B. File Inventory Schema (`file_inventory.json`)
```json
{
  "ir_version": "1.0",
  "compiler_version": "1.1",
  "artifact_type": "file_inventory",
  "generated_at": "ISO_TIMESTAMP",
  "repository_commit": "SHA1_HASH",
  "provenance": {
    "artifact_id": "ART-FILE-INV-00001",
    "produced_by": "Phase0_Discovery",
    "consumes": ["apps/smriti_retail_os"],
    "used_by": ["dependency_graph"]
  },
  "data": [
    {
      "file_path": "apps/smriti_retail_os/smriti_retail_os/barcode_api.py",
      "sha256": "SHA256_HASH",
      "size_bytes": 100877,
      "modified_date": "ISO_TIMESTAMP"
    }
  ]
}
```

### C. DocType Inventory Schema (`doctype_inventory.json`)
```json
{
  "ir_version": "1.0",
  "compiler_version": "1.1",
  "artifact_type": "doctype_inventory",
  "generated_at": "ISO_TIMESTAMP",
  "repository_commit": "SHA1_HASH",
  "provenance": {
    "artifact_id": "ART-DOCTYPE-INV-00001",
    "produced_by": "Phase0_Discovery",
    "consumes": ["apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/"],
    "used_by": ["dependency_graph", "docs_renderers"]
  },
  "data": [
    {
      "artifact_id": "ART-DOCTYPE-00014",
      "doctype_name": "SMRITI Print Template",
      "evidence_type": "JSON",
      "schema_path": "apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_print_template/smriti_print_template.json",
      "checksum": "SHA256_HASH",
      "fields": [
        {
          "fieldname": "template_title",
          "label": "Template Title",
          "fieldtype": "Data",
          "mandatory": 1
        }
      ]
    }
  ]
}
```

### D. Field Inventory Schema (`field_inventory.json`)
```json
{
  "ir_version": "1.0",
  "compiler_version": "1.1",
  "artifact_type": "field_inventory",
  "generated_at": "ISO_TIMESTAMP",
  "repository_commit": "SHA1_HASH",
  "provenance": {
    "artifact_id": "ART-FIELD-INV-00001",
    "produced_by": "Phase0_Discovery",
    "consumes": ["apps/smriti_retail_os/setup.py"],
    "used_by": ["dependency_graph", "docs_renderers"]
  },
  "data": [
    {
      "artifact_id": "ART-FIELD-00082",
      "target_doctype": "Item Barcode",
      "fieldname": "custom_is_primary",
      "label": "Is Primary",
      "fieldtype": "Check",
      "evidence_type": "AST",
      "source_file": "apps/smriti_retail_os/setup.py",
      "source_line": 26,
      "checksum": "SHA256_HASH"
    }
  ]
}
```

### E. API Inventory Schema (`api_inventory.json`)
```json
{
  "ir_version": "1.0",
  "compiler_version": "1.1",
  "artifact_type": "api_inventory",
  "generated_at": "ISO_TIMESTAMP",
  "repository_commit": "SHA1_HASH",
  "provenance": {
    "artifact_id": "ART-API-INV-00001",
    "produced_by": "Phase0_Discovery",
    "consumes": ["apps/smriti_retail_os/smriti_retail_os/barcode_api.py"],
    "used_by": ["dependency_graph", "docs_renderers"]
  },
  "data": [
    {
      "artifact_id": "ART-API-00012",
      "method": "smriti_retail_os.barcode_api.generate_prn",
      "evidence_type": "AST",
      "source_file": "apps/smriti_retail_os/smriti_retail_os/barcode_api.py",
      "arguments": ["items", "template_name"],
      "checksum": "SHA256_HASH"
    }
  ]
}
```

### F. Dependency Graph Schema (`dependency_graph.json`)
```json
{
  "ir_version": "1.0",
  "compiler_version": "1.1",
  "artifact_type": "dependency_graph",
  "generated_at": "ISO_TIMESTAMP",
  "repository_commit": "SHA1_HASH",
  "provenance": {
    "artifact_id": "ART-GRAPH-00001",
    "produced_by": "Phase2_5_DependencyGraph",
    "consumes": [
      "docs/discovery/doctype_inventory.json",
      "docs/discovery/field_inventory.json",
      "docs/discovery/api_inventory.json"
    ],
    "used_by": ["docs_renderers", "quality_gates"]
  },
  "data": {
    "nodes": [
      { "id": "ART-DOCTYPE-00014", "type": "DOCTYPE", "label": "SMRITI Print Template" },
      { "id": "ART-FIELD-00082", "type": "FIELD", "label": "custom_is_primary" }
    ],
    "edges": [
      {
        "source": "ART-FIELD-00082",
        "target": "ART-DOCTYPE-00014",
        "relation": "EXTENDS"
      }
    ]
  }
}
```

---

## 2. Dependency Graph Edge Semantics

Edges inside `dependency_graph.json` are strictly limited to the following direction-aware taxonomy:

| Edge Type | Semantic Meaning | Example Usage |
| :--- | :--- | :--- |
| **`USES`** | Relies on properties/values of target | `Item` $\rightarrow$ `Barcode` |
| **`DEPENDS_ON`** | Core schema/logical dependency | `Variant` $\rightarrow$ `Template` |
| **`GENERATES`** | Method writes or outputs target | `API` $\rightarrow$ `PRN` |
| **`EXTENDS`** | Subclassing or field injection | `custom_is_primary` $\rightarrow$ `Item Barcode` |
| **`IMPLEMENTS`** | Direct code interface implementation | `BarcodeStudioPlugin` $\rightarrow$ `SDCPlugin` |
| **`REFERENCES`** | Cross-linking or documentation pointers | `POS User Manual` $\rightarrow$ `Outlet Health Score` |
| **`RENDERS`** | Formatting visual layout outputs | `Layout JSON` $\rightarrow$ `Label Studio Preview` |
| **`VALIDATES`** | Quality gate checking target integrity | `Syntax Validator` $\rightarrow$ `PRN Template` |

---

## 3. Evidence Type Taxonomy

Every record compiled by Phase 0 must carry one of the following objective classifications:

| Evidence Type | Meaning |
| :--- | :--- |
| `FILE` | Directly extracted from a repository file. |
| `AST` | Parsed from source code syntax (Abstract Syntax Tree). |
| `JSON` | Parsed from JSON schema. |
| `CONFIG` | Parsed from configuration files. |
| `GIT` | Derived from Git metadata. |
| `GENERATED` | Produced mathematically from verified evidence. |
| `MISSING` | Referenced in code/config but not found. |
| `LEGACY` | Present in codebase but marked deprecated. |

---

## 4. Artifact Namespace & Permanent Registry

Artifact IDs are globally unique namespaces formatted as `ART-[TYPE]-[Num]`. To prevent numbering drift, IDs are leased and locked inside the central database file `sdc/artifact_registry.json`. Once assigned, an ID remains stable for the lifetime of that artifact, even if the file path is refactored. Retired IDs are marked as `RETIRED` and never reused.

---

## 5. Plugin Architecture Specifications

Plugins (located under `sdc/plugins/`) must extend compiler core operations by implementing the following Python class interface:

```python
class SDCPlugin:
    def get_discovery_rules(self) -> dict:
        """Returns file/pattern search patterns for Phase 0."""
        pass

    def get_ir_extensions(self, raw_ir: dict) -> dict:
        """Appends custom metadata fields to the parsed IR."""
        pass

    def get_validators(self) -> list:
        """Returns custom quality gate check functions."""
        pass

    def get_renderers(self) -> dict:
        """Returns Markdown rendering template mappings."""
        pass

    def get_migration_handlers(self) -> dict:
        """Maps old IR schema versions to current v1.0 specifications."""
        pass
```

---

## 6. Compiler Exit Codes

The SDC executable uses these standard exit codes:

| Code | Meaning | Action |
| :--- | :--- | :--- |
| `SDC000` | Success | Normal build termination |
| `SDC101` | Repository not found | Build aborted |
| `SDC102` | IR validation failed | Build aborted (Schema mismatch) |
| `SDC201` | Structural regression | Build aborted (Missing files / broken links) |
| `SDC202` | Semantic regression | Build warning (Altered API/field names) |
| `SDC301` | Dependency graph inconsistent | Build aborted (Circular loop or orphan edges) |
| `SDC401` | Quality gate failed | Build aborted (Markdown lint error) |

---

## 7. Quality Gate Execution Pipeline

The validation gate (Phase 7) enforces compilation checks:
1. **JSON Schema Check**: Asserts all JSONs under `docs/discovery/` validate against `sdc/schemas/`.
2. **Link Integrity Check**: All cross-references between rendered files resolve successfully.
3. **Artifact Uniqueness**: Validates that no two components share the same Artifact ID.
4. **Provenance Validation**: Asserts that every Markdown file has its provenance array defined.
5. **Graph Cycle Check**: Analyzes `dependency_graph.json` to verify that no circular reference loops exist.

---

## Revision History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 1.1.2-GA | 2026-06-25 | Jawahar R. Mallah | Initial frozen release of SDC GA Technical Specification. |

---

## Author Profile

* **Author:** Jawahar R. Mallah
* **Designation:** Founder & Chief Architect
* **Organization:** AITDL – AI Technology & Development Lab
* **Professional Experience:** 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> 
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
