from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tiktok_client_key = fields.Char(
        string="TikTok Client Key",
        config_parameter="tiktok_content_posting.client_key",
    )

    tiktok_client_secret = fields.Char(
        string="TikTok Client Secret",
        config_parameter="tiktok_content_posting.client_secret",
    )

    tiktok_redirect_uri = fields.Char(
        string="TikTok Redirect URI",
        config_parameter="tiktok_content_posting.redirect_uri",
        help="Example: https://your-ngrok-domain/tiktok/callback",
    )