import base64
import logging
import mimetypes
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests
from werkzeug.wrappers import Response

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TikTokContentPostingController(http.Controller):

    @http.route(
        "/tiktokIhysI0H3wmCctxGl3HSyTTjLNfQSSpoA.txt",
        type="http",
        auth="public",
        website=False,
        csrf=False,
        sitemap=False,
    )
    def tiktok_site_verification(self, **kwargs):
        content = "tiktok-developers-site-verification=IhysI0H3wmCctxGl3HSyTTjLNfQSSpoA"
        return request.make_response(
            content,
            headers=[("Content-Type", "text/plain; charset=utf-8")]
        )

    def _render_card_page(
        self,
        title,
        subtitle,
        status_type="info",
        primary_link=None,
        primary_text=None,
        secondary_link="/web",
        secondary_text="Back to Odoo",
        details_html="",
    ):
        theme_map = {
            "success": {
                "accent": "#1f5a92",
                "soft_bg": "#eef5fb",
                "soft_border": "#cfe0f1",
                "icon_bg": "#e8f1fa",
                "icon_color": "#1f5a92",
                "icon_html": "✓",
            },
            "warning": {
                "accent": "#9a6700",
                "soft_bg": "#fff8e6",
                "soft_border": "#f3d38a",
                "icon_bg": "#fff3cd",
                "icon_color": "#9a6700",
                "icon_html": "!",
            },
            "error": {
                "accent": "#b42318",
                "soft_bg": "#fff1f2",
                "soft_border": "#fecdd3",
                "icon_bg": "#ffe4e6",
                "icon_color": "#b42318",
                "icon_html": "×",
            },
            "info": {
                "accent": "#1f5a92",
                "soft_bg": "#eef5fb",
                "soft_border": "#cfe0f1",
                "icon_bg": "#e8f1fa",
                "icon_color": "#1f5a92",
                "icon_html": "i",
            },
        }
        theme = theme_map.get(status_type, theme_map["info"])

        primary_button = ""
        if primary_link and primary_text:
            primary_button = f"""
                <a href="{primary_link}" style="
                    display:inline-block;
                    padding:12px 22px;
                    border-radius:10px;
                    background:#1f5a92;
                    color:#ffffff;
                    text-decoration:none;
                    font-weight:600;
                    border:1px solid #1f5a92;
                    margin-right:10px;
                ">{primary_text}</a>
            """

        secondary_button = f"""
            <a href="{secondary_link}" style="
                display:inline-block;
                padding:12px 22px;
                border-radius:10px;
                background:#f3f4f6;
                color:#111827;
                text-decoration:none;
                font-weight:600;
                border:1px solid #e5e7eb;
            ">{secondary_text}</a>
        """

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1"/>
        </head>
        <body style="
            margin:0;
            font-family:Arial, sans-serif;
            background:#f6f8fb;
            color:#111827;
        ">
            <div style="
                max-width:920px;
                margin:48px auto;
                padding:0 20px;
            ">
                <div style="
                    background:#ffffff;
                    border:1px solid #e5e7eb;
                    border-radius:22px;
                    box-shadow:0 12px 30px rgba(17, 24, 39, 0.08);
                    overflow:hidden;
                ">
                    <div style="
                        padding:30px 34px 26px 34px;
                        border-bottom:1px solid #eef2f7;
                        display:flex;
                        align-items:center;
                        gap:18px;
                    ">
                        <div style="
                            width:62px;
                            height:62px;
                            min-width:62px;
                            border-radius:50%;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            font-size:34px;
                            font-weight:700;
                            background:{theme['icon_bg']};
                            color:{theme['icon_color']};
                            border:1px solid {theme['soft_border']};
                            line-height:1;
                        ">
                            {theme['icon_html']}
                        </div>

                        <div style="flex:1;">
                            <div style="
                                font-size:30px;
                                font-weight:700;
                                color:#0f172a;
                                margin-bottom:6px;
                            ">
                                {title}
                            </div>
                            <div style="
                                font-size:17px;
                                color:#475569;
                                line-height:1.5;
                            ">
                                {subtitle}
                            </div>
                        </div>
                    </div>

                    <div style="padding:28px 34px 30px 34px;">
                        <div style="
                            background:{theme['soft_bg']};
                            border:1px solid {theme['soft_border']};
                            border-radius:16px;
                            padding:22px 20px;
                            font-size:16px;
                            line-height:1.8;
                            color:#1f2937;
                        ">
                            {details_html}
                        </div>

                        <div style="
                            margin-top:24px;
                            display:flex;
                            gap:12px;
                            flex-wrap:wrap;
                        ">
                            {primary_button}
                            {secondary_button}
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return request.make_response(html, headers=[("Content-Type", "text/html")])

    def _external_redirect(self, url):
        return Response("", status=302, headers={"Location": url})

    def _get_config(self):
        icp = request.env["ir.config_parameter"].sudo()
        client_key = icp.get_param("tiktok_content_posting.client_key")
        client_secret = icp.get_param("tiktok_content_posting.client_secret")
        redirect_uri = icp.get_param("tiktok_content_posting.redirect_uri")
        return client_key, client_secret, redirect_uri

    @http.route("/tiktok/login", type="http", auth="user", website=False)
    def tiktok_login(self, next_url="/web", **kwargs):
        client_key, _client_secret, redirect_uri = self._get_config()

        if not client_key or not redirect_uri:
            return self._render_card_page(
                "TikTok setup missing",
                "Please complete the TikTok configuration before continuing.",
                status_type="error",
                details_html="""
                    TikTok Client Key, TikTok Client Secret, and TikTok Redirect URI
                    must all be configured in Odoo Settings before you can upload product videos.
                """,
            )

        state = secrets.token_urlsafe(24)
        request.session["tiktok_oauth_state"] = state
        request.session["tiktok_next_url"] = next_url
        request.session["tiktok_oauth_uid"] = request.env.user.id

        params = {
            "client_key": client_key,
            "response_type": "code",
            "scope": "user.info.basic,video.upload",
            "redirect_uri": redirect_uri,
            "state": state,
            "disable_auto_auth": 1,
        }

        auth_url = "https://www.tiktok.com/v2/auth/authorize/?" + urlencode(params)
        _logger.info("TikTok auth URL = %s", auth_url)
        return self._external_redirect(auth_url)

    @http.route(
        "/tiktok/callback",
        type="http",
        auth="public",
        website=False,
        csrf=False,
        methods=["GET", "POST"],
    )
    def tiktok_callback(self, **kwargs):
        code = kwargs.get("code")
        state = kwargs.get("state")
        error = kwargs.get("error")
        error_description = kwargs.get("error_description")

        expected_state = request.session.get("tiktok_oauth_state")
        next_url = request.session.get("tiktok_next_url", "/web")
        oauth_uid = request.session.get("tiktok_oauth_uid")

        _logger.info("TikTok callback kwargs = %s", kwargs)

        if error:
            return self._render_card_page(
                "TikTok authorization failed",
                "Odoo could not complete the connection to your TikTok account.",
                status_type="error",
                details_html=f"""
                    <strong>Reason:</strong> {error}<br/>
                    <strong>Description:</strong> {error_description or 'Unknown error'}
                """,
            )

        if not code:
            return self._render_card_page(
                "Authorization code missing",
                "TikTok did not return an authorization code.",
                status_type="error",
                details_html="Please go back and try the TikTok connection again.",
            )

        if not state or state != expected_state:
            return self._render_card_page(
                "Security check failed",
                "The TikTok response could not be verified.",
                status_type="error",
                details_html="Please start the upload again from the product page.",
            )

        if not oauth_uid:
            return self._render_card_page(
                "Session expired",
                "The TikTok response could not be matched to your Odoo session.",
                status_type="error",
                details_html="Please return to Odoo and try again.",
            )

        client_key, client_secret, redirect_uri = self._get_config()

        try:
            response = requests.post(
                "https://open.tiktokapis.com/v2/oauth/token/",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_key": client_key,
                    "client_secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
                timeout=60,
            )
            data = response.json()
        except Exception as exc:
            _logger.exception("TikTok token exchange error")
            return self._render_card_page(
                "TikTok connection failed",
                "Odoo could not exchange the authorization code for an access token.",
                status_type="error",
                details_html=str(exc),
            )

        if response.status_code != 200 or "access_token" not in data:
            return self._render_card_page(
                "TikTok connection failed",
                "TikTok did not return a valid access token.",
                status_type="error",
                details_html=str(data),
            )

        expires_in = int(data.get("expires_in", 86400))
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 300)

        user = request.env["res.users"].sudo().browse(oauth_uid)
        user.write({
            "tiktok_access_token": data.get("access_token"),
            "tiktok_refresh_token": data.get("refresh_token"),
            "tiktok_open_id": data.get("open_id"),
            "tiktok_scope": data.get("scope"),
            "tiktok_token_expires_at": expires_at.replace(tzinfo=None),
        })

        request.session.pop("tiktok_oauth_state", None)
        request.session.pop("tiktok_next_url", None)
        request.session.pop("tiktok_oauth_uid", None)

        return request.redirect(next_url)

    @http.route("/tiktok/post/product/<int:product_id>", type="http", auth="user", website=False)
    def tiktok_post_product(self, product_id, **kwargs):
        product = request.env["product.template"].sudo().browse(product_id)
        if not product.exists():
            return self._render_card_page(
                "Product not found",
                "The selected product could not be found.",
                status_type="error",
                details_html="Please return to Odoo and try another product.",
            )

        if not product.tiktok_video:
            return self._render_card_page(
                "No TikTok video found",
                "This product does not have a TikTok video yet.",
                status_type="warning",
                details_html="Please upload a TikTok video in the product form before sending it to TikTok.",
            )

        user = request.env.user.sudo()

        if not user.tiktok_access_token:
            return request.redirect(f"/tiktok/login?next_url=/tiktok/post/product/{product.id}")

        try:
            access_token = user._tiktok_get_valid_access_token()
        except Exception as exc:
            return self._render_card_page(
                "TikTok account not connected",
                "Your TikTok account is not ready for upload.",
                status_type="error",
                details_html=str(exc),
            )

        video_bytes = base64.b64decode(product.tiktok_video)
        video_size = len(video_bytes)
        filename = product.tiktok_video_filename or "product_video.mp4"
        content_type = mimetypes.guess_type(filename)[0] or "video/mp4"

        try:
            init_response = requests.post(
                "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "source_info": {
                        "source": "FILE_UPLOAD",
                        "video_size": video_size,
                        "chunk_size": video_size,
                        "total_chunk_count": 1,
                    }
                },
                timeout=60,
            )
            init_data = init_response.json()
        except Exception as exc:
            _logger.exception("TikTok init upload error")
            return self._render_card_page(
                "Upload failed",
                "Odoo could not start the upload to TikTok.",
                status_type="error",
                details_html=str(exc),
            )

        if init_response.status_code != 200 or init_data.get("error", {}).get("code") != "ok":
            product.write({
                "tiktok_last_status": "INIT_FAILED",
                "tiktok_last_message": str(init_data),
            })
            return self._render_card_page(
                "Upload failed",
                "TikTok did not accept the upload request.",
                status_type="error",
                details_html=str(init_data),
            )

        publish_id = init_data["data"]["publish_id"]
        upload_url = init_data["data"].get("upload_url")

        if not upload_url:
            product.write({
                "tiktok_publish_id": publish_id,
                "tiktok_last_status": "NO_UPLOAD_URL",
                "tiktok_last_message": str(init_data),
            })
            return self._render_card_page(
                "Upload failed",
                "TikTok did not provide an upload link for this video.",
                status_type="error",
                details_html=f"<strong>Reference ID:</strong> {publish_id}",
            )

        try:
            put_response = requests.put(
                upload_url,
                headers={
                    "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
                    "Content-Type": content_type,
                },
                data=video_bytes,
                timeout=300,
            )
        except Exception as exc:
            _logger.exception("TikTok binary upload failed")
            product.write({
                "tiktok_publish_id": publish_id,
                "tiktok_last_status": "UPLOAD_FAILED",
                "tiktok_last_message": str(exc),
            })
            return self._render_card_page(
                "Upload failed",
                "The video could not be uploaded to TikTok.",
                status_type="error",
                details_html=str(exc),
            )

        if put_response.status_code not in (200, 201, 204):
            product.write({
                "tiktok_publish_id": publish_id,
                "tiktok_last_status": "UPLOAD_FAILED",
                "tiktok_last_message": put_response.text,
            })
            return self._render_card_page(
                "Upload failed",
                "TikTok rejected the video upload.",
                status_type="error",
                details_html=f"HTTP {put_response.status_code}",
            )

        product.write({
            "tiktok_publish_id": publish_id,
            "tiktok_last_status": "UPLOADED",
            "tiktok_last_message": "Video uploaded to TikTok draft flow successfully.",
        })

        return self._render_card_page(
            "Video uploaded successfully",
            "Your product video has been sent to TikTok.",
            status_type="success",
            primary_link=f"/tiktok/status/product/{product.id}",
            primary_text="Check TikTok Status",
            details_html=f"""
                TikTok has received your video successfully.<br/><br/>
                <strong>Reference ID:</strong> {publish_id}<br/>
                Next, TikTok will process the upload and move it to the TikTok inbox.
            """,
        )

    @http.route("/tiktok/status/product/<int:product_id>", type="http", auth="user", website=False)
    def tiktok_status_product(self, product_id, **kwargs):
        product = request.env["product.template"].sudo().browse(product_id)
        if not product.exists():
            return self._render_card_page(
                "Product not found",
                "The selected product could not be found.",
                status_type="error",
                details_html="Please return to Odoo and try another product.",
            )

        if not product.tiktok_publish_id:
            return self._render_card_page(
                "No upload found",
                "This product has not been uploaded to TikTok yet.",
                status_type="warning",
                details_html="Upload the video first, then return here to check the status.",
            )

        user = request.env.user.sudo()

        try:
            access_token = user._tiktok_get_valid_access_token()
        except Exception as exc:
            return self._render_card_page(
                "TikTok account not connected",
                "Your TikTok account is not ready for status checking.",
                status_type="error",
                details_html=str(exc),
            )

        try:
            response = requests.post(
                "https://open.tiktokapis.com/v2/post/publish/status/fetch/",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=UTF-8",
                },
                json={"publish_id": product.tiktok_publish_id},
                timeout=60,
            )
            data = response.json()
        except Exception as exc:
            _logger.exception("TikTok status fetch failed")
            return self._render_card_page(
                "Status check failed",
                "Odoo could not retrieve the latest TikTok status.",
                status_type="error",
                details_html=str(exc),
            )

        if response.status_code != 200 or data.get("error", {}).get("code") != "ok":
            product.write({
                "tiktok_last_status": "STATUS_FAILED",
                "tiktok_last_message": str(data),
            })
            return self._render_card_page(
                "Status check failed",
                "TikTok did not return a valid status response.",
                status_type="error",
                details_html=str(data),
            )

        status = data.get("data", {}).get("status")
        fail_reason = data.get("data", {}).get("fail_reason")
        uploaded_bytes = data.get("data", {}).get("uploaded_bytes")

        product.write({
            "tiktok_last_status": status,
            "tiktok_last_message": str(data),
        })

        if status == "PROCESSING_UPLOAD":
            return self._render_card_page(
                "TikTok is processing the video",
                "The upload was successful and TikTok is still preparing the video.",
                status_type="warning",
                primary_link=f"/tiktok/status/product/{product.id}",
                primary_text="Refresh Status",
                details_html=f"""
                    Please wait a little and check again.<br/><br/>
                    <strong>Uploaded bytes:</strong> {uploaded_bytes or 0}<br/>
                    <strong>Reference ID:</strong> {product.tiktok_publish_id}
                """,
            )

        if status == "SEND_TO_USER_INBOX":
            return self._render_card_page(
                "Video sent to TikTok inbox",
                "The video has been delivered successfully.",
                status_type="success",
                details_html=f"""
                    Open the TikTok app and check the inbox of the connected TikTok account.<br/><br/>
                    From there, you can review, edit, and publish the draft video.<br/><br/>
                    <strong>Reference ID:</strong> {product.tiktok_publish_id}
                """,
            )

        if status == "FAILED":
            return self._render_card_page(
                "TikTok upload failed",
                "TikTok could not complete the upload.",
                status_type="error",
                details_html=f"""
                    <strong>Reason:</strong> {fail_reason or 'Unknown reason'}<br/>
                    <strong>Reference ID:</strong> {product.tiktok_publish_id}
                """,
            )

        return self._render_card_page(
            "TikTok status updated",
            f"Current status: {status}",
            status_type="info",
            details_html=f"<strong>Reference ID:</strong> {product.tiktok_publish_id}",
        )