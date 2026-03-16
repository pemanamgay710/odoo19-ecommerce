from datetime import datetime, timedelta, timezone

import requests

from odoo import fields, models
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = "res.users"

    tiktok_access_token = fields.Char(string="TikTok Access Token", copy=False)
    tiktok_refresh_token = fields.Char(string="TikTok Refresh Token", copy=False)
    tiktok_open_id = fields.Char(string="TikTok Open ID", copy=False)
    tiktok_scope = fields.Char(string="TikTok Scope", copy=False)
    tiktok_token_expires_at = fields.Datetime(string="TikTok Token Expiry", copy=False)

    def _tiktok_get_config(self):
        icp = self.env["ir.config_parameter"].sudo()
        client_key = icp.get_param("tiktok_content_posting.client_key")
        client_secret = icp.get_param("tiktok_content_posting.client_secret")
        redirect_uri = icp.get_param("tiktok_content_posting.redirect_uri")

        if not client_key or not client_secret or not redirect_uri:
            raise UserError("Please configure TikTok Client Key, Client Secret, and Redirect URI in Settings.")

        return client_key, client_secret, redirect_uri

    def _tiktok_refresh_access_token(self):
        self.ensure_one()

        client_key, client_secret, _redirect_uri = self._tiktok_get_config()

        if not self.tiktok_refresh_token:
            raise UserError("No TikTok refresh token found. Please connect your TikTok account first.")

        response = requests.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_key": client_key,
                "client_secret": client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.tiktok_refresh_token,
            },
            timeout=60,
        )

        data = response.json()

        if response.status_code != 200 or "access_token" not in data:
            raise UserError(f"TikTok token refresh failed: {data}")

        expires_in = int(data.get("expires_in", 86400))
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 300)

        self.write({
            "tiktok_access_token": data.get("access_token"),
            "tiktok_refresh_token": data.get("refresh_token", self.tiktok_refresh_token),
            "tiktok_open_id": data.get("open_id", self.tiktok_open_id),
            "tiktok_scope": data.get("scope", self.tiktok_scope),
            "tiktok_token_expires_at": expires_at.replace(tzinfo=None),
        })

    def _tiktok_get_valid_access_token(self):
        self.ensure_one()

        if not self.tiktok_access_token:
            raise UserError("No TikTok access token found. Please connect your TikTok account first.")

        if not self.tiktok_token_expires_at:
            self._tiktok_refresh_access_token()
            return self.tiktok_access_token

        now_utc_naive = datetime.utcnow()
        if self.tiktok_token_expires_at <= now_utc_naive:
            self._tiktok_refresh_access_token()

        return self.tiktok_access_token