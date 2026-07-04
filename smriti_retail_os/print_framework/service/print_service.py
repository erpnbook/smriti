# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/service/print_service.py
# @desc:    Core orchestration service.
# @author:  Jawahar R. Mallah
#

from smriti_retail_os.print_framework.queue.print_queue import PrintQueue
from smriti_retail_os.print_framework.dispatcher.print_dispatcher import PrintDispatcher
import hashlib

class PrintService:
    """
    Core service orchestrating SMRITI printing queues and dispatching.
    Follows Reference Studio layered rules.
    """

    @classmethod
    def print_label(cls, module_name, printer_id, payload_str) -> str:
        """
        Enqueues and dispatches a print job.
        Returns the created print job name (Job ID).
        """
        payload_bytes = payload_str.encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()

        # Mock payload file URL saving (stubbed out for scaffolding)
        payload_file_url = f"/private/files/jobs/{payload_hash}.txt"

        # 1. Enqueue job
        job_id = PrintQueue.enqueue(module_name, printer_id, payload_hash, payload_file_url)

        # 2. Dispatch job
        try:
            success = PrintDispatcher.dispatch(printer_id, payload_bytes)
            if success:
                PrintQueue.mark_completed(job_id)
            else:
                PrintQueue.mark_failed(job_id, "Dispatcher reported send failure.")
        except Exception as e:
            PrintQueue.mark_failed(job_id, str(e))

        return job_id
