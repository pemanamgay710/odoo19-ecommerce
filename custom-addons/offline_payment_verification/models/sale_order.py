from odoo import models, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    transaction_reference = fields.Char(string="Transaction Reference")
    payment_screenshot = fields.Binary(string="Payment Screenshot")
    payment_screenshot_filename = fields.Char(string="Screenshot Filename")
    payment_verified = fields.Boolean(string="Payment Verified", default=False)

    def _is_wire_transfer_order(self):
        """Detect Wire Transfer based on the last portal transaction."""
        self.ensure_one()
        tx = self.get_portal_last_transaction()
        return bool(tx and tx.provider_id and tx.provider_id.name == "Wire Transfer")

    def action_create_invoice(self):
        """Block invoice creation for Wire Transfer orders until verified."""
        for order in self:
            if order._is_wire_transfer_order() and not order.payment_verified:
                raise UserError(_(
                    "You cannot create an invoice for this order until offline payment is verified."
                ))
        return super().action_create_invoice()