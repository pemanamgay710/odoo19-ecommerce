from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale

class EcommerceCustom(WebsiteSale):

    # ✅ Custom Landing Page (Editable)
    @http.route('/', type='http', auth='public', website=True)
    def custom_home(self, **kw):
        return http.request.render('ecommerce_custom_module.landing_page_template')

    # ✅ Shop Page (inherits Odoo’s logic)
    # Do not redefine /shop manually — let WebsiteSale handle it
