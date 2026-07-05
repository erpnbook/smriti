# -*- coding: utf-8 -*-
# SMRITI Matrix Platform Service
import frappe
import json
from frappe import _
from smriti_retail_os.matrix_engine.dto.matrix_dtos import (
    MatrixDefinitionDTO, MatrixVariantDTO, MatrixCellDTO, MatrixSessionDTO
)

class MatrixService:
    @staticmethod
    def get_active_definition(matrix_name=None):
        """
        Retrieves the active Matrix Definition.
        Falls back to a default Color/Size matrix if none matches.
        """
        if not matrix_name:
            matrix_name = frappe.db.get_value("SMRITI Matrix Definition", {}, "name")
            
        if matrix_name and frappe.db.exists("SMRITI Matrix Definition", matrix_name):
            doc = frappe.get_doc("SMRITI Matrix Definition", matrix_name)
            # Map axes
            axis_x = "Size"
            axis_y = "Color"
            for ax in doc.axes:
                if ax.display_role == "Column":
                    axis_x = ax.attribute
                elif ax.display_role == "Row":
                    axis_y = ax.attribute
            return MatrixDefinitionDTO(
                name=doc.name,
                axis_x=axis_x,
                axis_y=axis_y,
                allow_auto_variant=bool(doc.allow_auto_variant),
                allow_excel_import=bool(doc.allow_excel_import),
                allow_barcode_scan=bool(doc.allow_barcode_scan),
                cell_validation=doc.cell_validation or "None",
                default_view=doc.default_view or "Expanded"
            )
        else:
            # Fallback Default Definition
            return MatrixDefinitionDTO(
                name="Default Grid",
                axis_x="Size",
                axis_y="Color",
                allow_auto_variant=True,
                allow_excel_import=True,
                allow_barcode_scan=True,
                cell_validation="None",
                default_view="Expanded"
            )

    @staticmethod
    def build_session(article, matrix_name=None):
        """
        Builds a complete MatrixSessionDTO for an Article template.
        Uses Redis cache for performance optimization.
        """
        cache_key = f"smriti_matrix_session:{article}:{matrix_name or 'default'}"
        cached = frappe.cache().get_value(cache_key)
        if cached:
            try:
                data = json.loads(cached)
                # Reconstruct DTO
                definition = MatrixDefinitionDTO(**data["definition"]) if data.get("definition") else None
                variants_list = [MatrixVariantDTO(**v) for v in data["variants_list"]]
                cells = [MatrixCellDTO(c["x_val"], c["y_val"], c["qty"], MatrixVariantDTO(**c["variant"]) if c.get("variant") else None) for c in data["cells"]]
                return MatrixSessionDTO(
                    article=data["article"],
                    definition=definition,
                    colors=data["colors"],
                    sizes=data["sizes"],
                    cells=cells,
                    variants_list=variants_list,
                    item_name=data.get("item_name"),
                    mrp=float(data.get("mrp") or 0.0)
                )
            except Exception:
                frappe.cache().delete_key(cache_key)

        # 1. Fetch Definition
        definition = MatrixService.get_active_definition(matrix_name)

        # 2. Query Variants
        variants = frappe.db.get_all(
            "Item",
            filters={"variant_of": article, "disabled": 0},
            fields=["name", "item_name", "standard_rate", "stock_uom"]
        )

        variants_list = []
        all_colors = set()
        all_sizes = set()

        for v in variants:
            # Fetch attributes
            v_attrs = frappe.db.get_all(
                "Item Variant Attribute",
                filters={"parent": v.name},
                fields=["attribute", "attribute_value"]
            )
            attr_dict = {d.attribute: d.attribute_value for d in v_attrs}
            
            # Map Axis values
            x_val = attr_dict.get(definition.axis_x) or "Default"
            y_val = attr_dict.get(definition.axis_y) or "Default"
            
            all_sizes.add(x_val)
            all_colors.add(y_val)

            # Barcode
            barcode = frappe.db.get_value(
                "Item Barcode",
                {"parent": v.name, "custom_is_primary": 1},
                "barcode"
            ) or v.name

            variants_list.append(MatrixVariantDTO(
                item_code=v.name,
                item_name=v.item_name,
                color=y_val,
                size=x_val,
                rate=v.standard_rate or 0.0,
                barcode=barcode,
                uom=v.stock_uom or "Nos"
            ))

        # Sort sizes numerically if possible, otherwise by standard size sequences
        is_all_numeric = all(x.replace('.', '', 1).isdigit() for x in all_sizes if x != "Default")
        if is_all_numeric:
            sizes_sorted = sorted(list(all_sizes), key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else 0.0)
        else:
            std_order = ["3XS", "2XS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL"]
            std_order_map = {size: idx for idx, size in enumerate(std_order)}
            
            def get_sort_key(sz):
                val = sz.upper()
                if val in std_order_map:
                    return (0, std_order_map[val])
                else:
                    return (1, val)
            sizes_sorted = sorted(list(all_sizes), key=get_sort_key)

        colors_sorted = sorted(list(all_colors))

        # Build initial empty cells for all permutations
        cells = []
        variant_map = {(v.size, v.color): v for v in variants_list}
        
        for y in colors_sorted or ["Default"]:
            for x in sizes_sorted or ["Default"]:
                var_dto = variant_map.get((x, y))
                cells.append(MatrixCellDTO(x_val=x, y_val=y, qty=0, variant=var_dto))

        # Fetch template Item name and rate
        tpl_name, tpl_rate = frappe.db.get_value("Item", article, ["item_name", "standard_rate"]) or (article, 0.0)

        session = MatrixSessionDTO(
            article=article,
            definition=definition,
            colors=colors_sorted or ["Default"],
            sizes=sizes_sorted or ["Default"],
            cells=cells,
            variants_list=variants_list,
            item_name=tpl_name,
            mrp=float(tpl_rate or 0.0)
        )

        # Cache session representation
        session_dict = session.to_dict()
        frappe.cache().set_value(cache_key, json.dumps(session_dict), expires_in_sec=300)

        return session

    @staticmethod
    def parse_excel_grid(tsv_content):
        """
        Parses Excel clipboard tab-separated values (TSV) into Matrix cells.
        Supports comma-separated fallback.
        """
        if not tsv_content:
            return []

        # Detect separator
        sep = "\t"
        if "\t" not in tsv_content and "," in tsv_content:
            sep = ","

        lines = [l.strip().split(sep) for l in tsv_content.strip().split("\n") if l.strip()]
        if not lines:
            return []

        # Columns header (Axis X values)
        headers = [h.strip() for h in lines[0][1:] if h.strip()]
        cells = []
        for line in lines[1:]:
            if not line:
                continue
            row_header = line[0].strip() # Axis Y value
            for idx, val in enumerate(line[1:]):
                if idx < len(headers):
                    qty = 0
                    try:
                        qty = float(val)
                    except ValueError:
                        pass
                    if qty > 0:
                        cells.append({
                            "x_val": headers[idx],
                            "y_val": row_header,
                            "qty": qty
                        })
        return cells

    @staticmethod
    def clear_cache(article):
        """
        Invalidates redis matrix session cache for an article.
        """
        # Delete keys matching different definition name combinations
        frappe.cache().delete_key(f"smriti_matrix_session:{article}:default")
        definitions = frappe.db.get_all("SMRITI Matrix Definition", pluck="name")
        for d in definitions:
            frappe.cache().delete_key(f"smriti_matrix_session:{article}:{d}")
