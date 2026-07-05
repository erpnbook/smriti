# -*- coding: utf-8 -*-
# SMRITI Purchase Matrix Adapter

class PurchaseMatrixAdapter:
    @staticmethod
    def cells_to_po_items(cells, warehouse=None):
        """
        Converts flattened MatrixCellDTO dict list into flat SMRITI Purchase Order Item dicts.
        """
        items = []
        for cell in cells:
            qty = float(cell.get("qty") or 0)
            if qty <= 0:
                continue
                
            variant = cell.get("variant") or {}
            item_code = variant.get("item_code")
            if not item_code:
                continue
                
            items.append({
                "item_code": item_code,
                "item_name": variant.get("item_name"),
                "qty": qty,
                "rate": float(variant.get("rate") or 0),
                "uom": variant.get("uom") or "Nos",
                "warehouse": warehouse,
                "article": cell.get("article"),
                "attribute_summary": f"{cell.get('y_val')} / {cell.get('x_val')}",
                "barcode": variant.get("barcode")
            })
        return items
