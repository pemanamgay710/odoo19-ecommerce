# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_tracking_stage = fields.Selection(
        selection=[
            ("placed", "Order Placed"),
            ("confirmed", "Confirmed"),
            ("picked", "Picked"),
            ("packed", "Packed"),
            ("delivered", "Delivered"),
        ],
        compute="_compute_tracking",
        store=False,
    )

    x_pick_done = fields.Boolean(compute="_compute_tracking", store=False)
    x_pack_done = fields.Boolean(compute="_compute_tracking", store=False)
    x_delivery_done = fields.Boolean(compute="_compute_tracking", store=False)

    def _get_pick_pack_out_pickings(self):
        self.ensure_one()
        Picking = self.env["stock.picking"]
        pick = Picking
        pack = Picking
        out = Picking

        pickings = self.picking_ids

        # OUT (customer delivery)
        out_candidates = pickings.filtered(lambda p: p.picking_type_id.code == "outgoing")
        if out_candidates:
            out = out_candidates[:1]

        # Internal transfers (pick + pack)
        internal = pickings.filtered(lambda p: p.picking_type_id.code == "internal")

        def _dest_name(p):
            return (p.location_dest_id.display_name or "").lower()

        # PICK → destination contains "packing"
        pick_candidates = internal.filtered(lambda p: "packing" in _dest_name(p))
        if pick_candidates:
            pick = pick_candidates[:1]

        # PACK → destination contains "output"
        pack_candidates = internal.filtered(lambda p: "output" in _dest_name(p))
        if pack_candidates:
            pack = pack_candidates[:1]

        # Fallback: pick earliest two internal transfers
        if (not pick or not pack) and internal:
            internal_sorted = internal.sorted(lambda p: p.scheduled_date or p.create_date)
            if not pick and len(internal_sorted) >= 1:
                pick = internal_sorted[0]
            if not pack and len(internal_sorted) >= 2:
                pack = internal_sorted[1]

        return {"pick": pick, "pack": pack, "out": out}

    @api.depends("state", "date_order", "picking_ids.state", "picking_ids.location_dest_id", "picking_ids.picking_type_id")
    def _compute_tracking(self):
        for order in self:
            pmap = order._get_pick_pack_out_pickings()
            pick = pmap["pick"]
            pack = pmap["pack"]
            out = pmap["out"]

            pick_done = bool(pick) and pick.state == "done"
            pack_done = bool(pack) and pack.state == "done"
            delivery_done = bool(out) and out.state == "done"

            order.x_pick_done = pick_done
            order.x_pack_done = pack_done
            order.x_delivery_done = delivery_done

            stage = "placed"

            # Confirmed when SO is confirmed
            if order.state in ("sale", "done"):
                stage = "confirmed"

            if pick_done:
                stage = "picked"
            if pack_done:
                stage = "packed"
            if delivery_done:
                stage = "delivered"

            order.x_tracking_stage = stage

    def x_step_dates(self):
        """Safe dates dictionary for portal display."""
        self.ensure_one()
        pmap = self._get_pick_pack_out_pickings()
        pick = pmap["pick"]
        pack = pmap["pack"]
        out = pmap["out"]

        # "confirmed" date fallback:
        # If you don't have confirmation_date, we can show date_order for placed,
        # and show the first picking create_date as a proxy for "confirmed".
        confirmed_proxy = False
        if self.state in ("sale", "done"):
            # best lightweight proxy: earliest picking create_date
            if self.picking_ids:
                confirmed_proxy = min(self.picking_ids.mapped("create_date"))
            else:
                confirmed_proxy = self.date_order

        return {
            "placed": self.date_order,
            "confirmed": confirmed_proxy,
            "picked": pick.date_done if pick and pick.state == "done" else False,
            "packed": pack.date_done if pack and pack.state == "done" else False,
            "delivered": out.date_done if out and out.state == "done" else False,
        }