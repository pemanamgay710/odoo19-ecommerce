import base64

from odoo import http
from odoo.http import request


class OfflinePaymentUpload(http.Controller):

    @http.route(
        "/shop/offline_payment_submit",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def offline_payment_submit(self, **post):
        # 1) Get order
        order_id = post.get("order_id")
        if not order_id:
            return request.redirect("/shop")

        order = request.env["sale.order"].sudo().browse(int(order_id))
        if not order.exists():
            return request.redirect("/shop")

        # 2) Security
        # - public user must provide access_token
        # - logged-in user must own the order (partner match)
        if request.website.is_public_user():
            token = post.get("access_token")
            if not token or token != order.access_token:
                return request.redirect("/shop")
        else:
            if order.partner_id != request.env.user.partner_id:
                return request.redirect("/shop")

        # 3) Save transaction reference
        order.transaction_reference = post.get("transaction_reference")

        # 4) Save screenshot + create attachment (for admin + email attachment)
        attachment = False
        upload = request.httprequest.files.get("payment_screenshot")
        if upload:
            data = upload.read()
            b64 = base64.b64encode(data)

            # store on the order (your custom fields)
            order.payment_screenshot = b64
            order.payment_screenshot_filename = upload.filename

            # also store as attachment linked to the sale order
            attachment = request.env["ir.attachment"].sudo().create({
                "name": upload.filename,
                "type": "binary",
                "datas": b64,
                "res_model": "sale.order",
                "res_id": order.id,
                "mimetype": upload.mimetype,
            })

        # 5) Notify admins (attach screenshot if available)
        self._notify_admins(order, attachment=attachment)

        # 6) Back to confirmation page
        return request.redirect(f"/shop/confirmation?order_id={order.id}")

    def _notify_admins(self, order, attachment=False):
        base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url") or ""
        order_url = f"{base_url}/web#id={order.id}&model=sale.order&view_type=form"

        group_rec = request.env.ref("base.group_system").sudo()

        # Odoo versions differ: some have `users`, others `user_ids`
        admin_users = getattr(group_rec, "users", False) or getattr(group_rec, "user_ids", False)
        if not admin_users:
            return

        admin_emails = [u.email for u in admin_users if u.email]
        if not admin_emails:
            return

        subject = f"[Offline Payment] Proof submitted for {order.name}"
        body = f"""
            <p>A customer has submitted offline payment proof.</p>
            <ul>
                <li><strong>Order:</strong> {order.name}</li>
                <li><strong>Customer:</strong> {order.partner_id.name}</li>
                <li><strong>Transaction Ref:</strong> {order.transaction_reference or ""}</li>
            </ul>
            <p>Open order in Odoo: <a href="{order_url}">{order_url}</a></p>
        """

        mail_vals = {
            "subject": subject,
            "body_html": body,
            "email_to": ",".join(admin_emails),
        }
        if attachment:
            # link existing attachment to the outgoing email
            mail_vals["attachment_ids"] = [(4, attachment.id)]

        request.env["mail.mail"].sudo().create(mail_vals).send()