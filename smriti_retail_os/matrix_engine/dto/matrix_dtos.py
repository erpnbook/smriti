# -*- coding: utf-8 -*-
# SMRITI Matrix DTO Definitions

class MatrixVariantDTO:
    def __init__(self, item_code, item_name, color, size, rate, barcode, uom):
        self.item_code = item_code
        self.item_name = item_name
        self.color = color
        self.size = size
        self.rate = rate
        self.barcode = barcode
        self.uom = uom

    def to_dict(self):
        return {
            "item_code": self.item_code,
            "item_name": self.item_name,
            "color": self.color,
            "size": self.size,
            "rate": self.rate,
            "barcode": self.barcode,
            "uom": self.uom
        }

class MatrixDefinitionDTO:
    def __init__(self, name, axis_x, axis_y, allow_auto_variant=True, allow_excel_import=True, allow_barcode_scan=True, cell_validation="None", default_view="Expanded"):
        self.name = name
        self.axis_x = axis_x
        self.axis_y = axis_y
        self.allow_auto_variant = allow_auto_variant
        self.allow_excel_import = allow_excel_import
        self.allow_barcode_scan = allow_barcode_scan
        self.cell_validation = cell_validation
        self.default_view = default_view

    def to_dict(self):
        return {
            "name": self.name,
            "axis_x": self.axis_x,
            "axis_y": self.axis_y,
            "allow_auto_variant": self.allow_auto_variant,
            "allow_excel_import": self.allow_excel_import,
            "allow_barcode_scan": self.allow_barcode_scan,
            "cell_validation": self.cell_validation,
            "default_view": self.default_view
        }

class MatrixCellDTO:
    def __init__(self, x_val, y_val, qty=0, variant=None):
        self.x_val = x_val
        self.y_val = y_val
        self.qty = qty
        self.variant = variant

    def to_dict(self):
        return {
            "x_val": self.x_val,
            "y_val": self.y_val,
            "qty": self.qty,
            "variant": self.variant.to_dict() if self.variant else None
        }

class MatrixSessionDTO:
    def __init__(self, article, definition, colors, sizes, cells, variants_list, item_name=None, mrp=0.0):
        self.article = article
        self.definition = definition
        self.colors = colors
        self.sizes = sizes
        self.cells = cells
        self.variants_list = variants_list
        self.item_name = item_name
        self.mrp = mrp

    def to_dict(self):
        return {
            "article": self.article,
            "definition": self.definition.to_dict() if self.definition else None,
            "colors": self.colors,
            "sizes": self.sizes,
            "cells": [c.to_dict() for c in self.cells],
            "variants_list": [v.to_dict() for v in self.variants_list],
            "item_name": self.item_name,
            "mrp": self.mrp
        }
