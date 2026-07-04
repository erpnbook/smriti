# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/label_studio/service/render_engine.py
# @desc:    Translates neutral elements to printer-specific ZPL/TSPL streams.
# @author:  Jawahar R. Mallah
#

class BaseRenderer:
    """Strategy Base Class for printer-specific translations."""
    def render(self, elements, width, height) -> str:
        raise NotImplementedError("Render strategies must implement render().")

class ZPLRenderer(BaseRenderer):
    """Strategy rendering elements into Zebra Programming Language stream."""
    def render(self, elements, width, height):
        stream = ["^XA", f"^PW{int(width * 8)}", f"^LL{int(height * 8)}"]  # mm to dots at 203 DPI
        for el in elements:
            x_dots = int(float(el.get("x", 0)) * 8)
            y_dots = int(float(el.get("y", 0)) * 8)
            content = el.get("content", "")
            if el.get("type") == "Barcode":
                stream.append(f"^FO{x_dots},{y_dots}^BCN,60,Y,N,N^FD{content}^FS")
            else:
                stream.append(f"^FO{x_dots},{y_dots}^A0N,28,28^FD{content}^FS")
        stream.append("^XZ")
        return "\n".join(stream)

class TSPLRenderer(BaseRenderer):
    """Strategy rendering elements into TSPL stream."""
    def render(self, elements, width, height):
        stream = [f"SIZE {width} mm, {height} mm", "CLS"]
        for el in elements:
            x_dots = int(float(el.get("x", 0)) * 8)
            y_dots = int(float(el.get("y", 0)) * 8)
            content = el.get("content", "")
            if el.get("type") == "Barcode":
                stream.append(f'BARCODE {x_dots},{y_dots},"128",60,1,0,2,2,"{content}"')
            else:
                stream.append(f'TEXT {x_dots},{y_dots},"3",0,1,1,"{content}"')
        stream.append("PRINT 1,1")
        return "\n".join(stream)

class RenderEngine:
    """
    Translates neutral Label elements to raw print streams based on target capability.
    Follows Strategy Pattern.
    """
    _strategies = {
        "ZPL": ZPLRenderer(),
        "TSPL": TSPLRenderer()
    }

    @classmethod
    def render_stream(cls, label_data, format_type="ZPL") -> str:
        """
        Translates neutral label elements into target printer stream format.
        
        Parameters
        ----------
        label_data : dict
            Structure representing the printer-neutral Label model elements.
        format_type : str
            Desired target stream format (e.g. ZPL, TSPL).
        """
        renderer = cls._strategies.get(format_type)
        if not renderer:
            raise ValueError(f"No render strategy registered for format '{format_type}'.")
            
        elements = label_data.get("elements", [])
        width = float(label_data.get("width_mm", 100))
        height = float(label_data.get("height_mm", 50))
        
        return renderer.render(elements, width, height)
