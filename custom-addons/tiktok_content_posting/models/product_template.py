from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tiktok_video = fields.Binary(string="TikTok Video")
    tiktok_video_filename = fields.Char(string="TikTok Video Filename")
    tiktok_product_url = fields.Char(string="TikTok Product URL")

    tiktok_publish_id = fields.Char(string="TikTok Publish ID", copy=False)
    tiktok_last_status = fields.Char(string="TikTok Last Status", copy=False)
    tiktok_last_message = fields.Text(string="TikTok Message", copy=False)

    def action_tiktok_upload_draft(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/tiktok/post/product/{self.id}",
            "target": "self",
        }

    def action_tiktok_check_status(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/tiktok/status/product/{self.id}",
            "target": "self",
        }