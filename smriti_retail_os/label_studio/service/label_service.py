# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/label_studio/service/label_service.py
# @desc:    Label Studio orchestration service.
# @author:  Jawahar R. Mallah
#

from smriti_retail_os.label_studio.service.preview_engine import PreviewEngine
from smriti_retail_os.label_studio.service.render_engine import RenderEngine
from smriti_retail_os.print_framework.service.print_service import PrintService

class LabelService:
    """
    Orchestrates label preview compilation and print jobs dispatch.
    """

    @staticmethod
    def get_preview(label_data) -> dict:
        """Returns browser canvas rendering coordinates."""
        return PreviewEngine.render_canvas_json(label_data)

    @staticmethod
    def dispatch_print(label_data, printer_id, format_type="ZPL") -> str:
        """Translates and dispatches label elements to Print Framework."""
        payload_stream = RenderEngine.render_stream(label_data, format_type)
        job_id = PrintService.print_label("Label Studio", printer_id, payload_stream)
        return job_id
