# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/label_studio/service/preview_engine.py
# @desc:    Generates browser canvas preview coordinate JSON structure.
# @author:  Jawahar R. Mallah
#

class PreviewEngine:
    """
    Renders printer-neutral preview coordinates for web canvas elements.
    Does not produce ZPL or TSPL syntax.
    """

    @staticmethod
    def render_canvas_json(label_data) -> dict:
        """
        Translates raw label metadata elements into canvas coordinates coordinates.
        
        Parameters
        ----------
        label_data : dict
            Structure representing the printer-neutral Label model elements.
        """
        elements = label_data.get("elements", [])
        width = float(label_data.get("width_mm", 100))
        height = float(label_data.get("height_mm", 50))
        
        canvas_elements = []
        for el in elements:
            el_type = el.get("type", "Text")
            x = float(el.get("x", 0))
            y = float(el.get("y", 0))
            
            canvas_elements.append({
                "id": el.get("id"),
                "type": el_type,
                "x_px": x * 3.78,  # Millimeter to pixel scale factor (approx 96 DPI)
                "y_px": y * 3.78,
                "content": el.get("content", ""),
                "width_px": float(el.get("width", 20)) * 3.78,
                "height_px": float(el.get("height", 10)) * 3.78
            })
            
        return {
            "width_px": width * 3.78,
            "height_px": height * 3.78,
            "elements": canvas_elements
        }
