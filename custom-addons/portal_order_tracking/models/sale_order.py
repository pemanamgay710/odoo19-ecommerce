from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_shipping_status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        ],
        string="Shipping Status",
        compute="_compute_x_shipping_status",
        store=True,
        readonly=True,
        copy=False,
    )

    x_shipping_status_label = fields.Char(
        string="Shipping Status Label",
        compute="_compute_x_shipping_status",
        store=True,
        readonly=True,
        copy=False,
    )

    x_shipping_status_css = fields.Char(
        string="Shipping Status CSS",
        compute="_compute_x_shipping_status",
        store=True,
        readonly=True,
        copy=False,
    )

    @api.depends("picking_ids.state", "picking_ids.picking_type_id", "state")
    def _compute_x_shipping_status(self):
        """
        Logic:
        - If SO is cancelled -> Cancelled
        - Consider outgoing pickings only (delivery orders)
        - If any outgoing picking is done -> Delivered
        - Else if any outgoing picking is assigned/confirmed/waiting -> In Progress
        - Else -> Pending
        """
        for order in self:
            # Default
            status = "pending"

            if order.state == "cancel":
                status = "cancelled"
            else:
                outgoing_pickings = order.picking_ids.filtered(
                    lambda p: p.picking_type_id.code == "outgoing" and p.state != "cancel"
                )

                if outgoing_pickings:
                    if any(p.state == "done" for p in outgoing_pickings):
                        status = "delivered"
                    elif any(p.state in ("assigned", "confirmed", "waiting", "partially_available") for p in outgoing_pickings):
                        status = "in_progress"
                    else:
                        status = "pending"
                else:
                    # No delivery created yet
                    status = "pending"

            order.x_shipping_status = status

            label_map = {
                "pending": "Pending",
                "in_progress": "In Progress",
                "delivered": "Delivered",
                "cancelled": "Cancelled",
            }
            css_map = {
                # Bootstrap-ish badge classes used by portal templates
                "pending": "badge rounded-pill text-bg-secondary",
                "in_progress": "badge rounded-pill text-bg-warning",
                "delivered": "badge rounded-pill text-bg-success",
                "cancelled": "badge rounded-pill text-bg-danger",
            }

            order.x_shipping_status_label = label_map.get(status, "Pending")
            order.x_shipping_status_css = css_map.get(status, "badge rounded-pill text-bg-secondary")