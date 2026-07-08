# -*- coding: utf-8 -*-
# SMRITI Purchase Studio — Purchase Workflow Service
import frappe
from frappe.utils import now_datetime
from smriti_retail_os.purchase_studio.repository import PurchaseRepository
from smriti_retail_os.purchase_studio.service.purchase_validation_service import PurchaseValidationService
from smriti_retail_os.purchase_studio.service.purchase_calculation_service import PurchaseCalculationService

class PurchaseWorkflowService:
    @staticmethod
    def transition_to(po_name, target_status, remarks=None, user_id=None):
        po = PurchaseRepository.get_po(po_name)
        PurchaseValidationService.validate_state_change(po.status, target_status)
        po.status = target_status
        if remarks:
            po.remarks = (po.remarks or "") + f"\n[{now_datetime()}] status changed to {target_status}: {remarks}"
        PurchaseRepository.save_po(po)
        return po

    @staticmethod
    def submit(po_name):
        po = PurchaseRepository.get_po(po_name)
        PurchaseValidationService.validate_state_change(po.status, "Submitted")

        # Issue #5: Use check_approval_required with both totals so that
        # approval_threshold_inclusive_of_tax setting is respected.
        # net_total = pre-GST line-item subtotal; grand_total = GST-inclusive total.
        from smriti_retail_os.purchase_studio.service import purchase_settings_service as settings_svc
        net_total = getattr(po, "net_total", None) or po.grand_total
        requires_approval = settings_svc.check_approval_required(
            grand_total=po.grand_total,
            net_total=net_total
        )

        if requires_approval:
            po.status = "Submitted"
        else:
            po.status = "Approved"
            po.approved_by = "System"
            po.approved_on = now_datetime()

        PurchaseRepository.save_po(po)
        return po

    @staticmethod
    def approve(po_name, approved_by):
        po = PurchaseRepository.get_po(po_name)
        PurchaseValidationService.validate_state_change(po.status, "Approved")
        po.status = "Approved"
        po.approved_by = approved_by
        po.approved_on = now_datetime()
        PurchaseRepository.save_po(po)
        return po

    @staticmethod
    def reject(po_name, reason):
        po = PurchaseRepository.get_po(po_name)
        # Rejection cancels the PO and records the rejection reason
        PurchaseValidationService.validate_state_change(po.status, "Cancelled")
        po.status = "Cancelled"
        po.rejection_reason = reason
        PurchaseRepository.save_po(po)
        return po

    @staticmethod
    def order(po_name):
        return PurchaseWorkflowService.transition_to(po_name, "Ordered")

    @staticmethod
    def receive(po_name, received_items):
        """
        Updates received quantities on the PO items and recalculates overall PO status.
        received_items: dict of {item_code: qty} or {po_item_name: qty}
        """
        po = PurchaseRepository.get_po(po_name)
        
        # We must be in Approved, Ordered, or Partially Received state to start receiving
        if po.status not in ("Approved", "Ordered", "Partially Received"):
            frappe.throw(f"Cannot receive items on a Purchase Order with status '{po.status}'")

        # Update received_qty on each row
        for item in po.items:
            # Match by item_code or row name
            recv_qty = received_items.get(item.name) or received_items.get(item.item_code) or 0
            if recv_qty > 0:
                item.received_qty = float(item.received_qty or 0) + float(recv_qty)

        # Recalculate calculations
        PurchaseCalculationService.calculate_per_received(po)

        # Update status based on received percentage
        if po.per_received >= 100:
            po.status = "Completed"
        elif po.per_received > 0:
            po.status = "Partially Received"
        else:
            po.status = "Ordered"

        PurchaseRepository.save_po(po)
        return po

    @staticmethod
    def close(po_name):
        return PurchaseWorkflowService.transition_to(po_name, "Closed")

    @staticmethod
    def cancel(po_name):
        return PurchaseWorkflowService.transition_to(po_name, "Cancelled")
