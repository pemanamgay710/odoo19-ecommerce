{
    "name": "Customer Order Tracking",
    "version": "1.0",
    "category": "Website",
    "summary": "Enhanced portal order detail tracking with product images (3-step delivery).",
    "depends": ["sale_management", "website_sale", "portal", "stock"],
    "data": [
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "customer_order_tracking/static/src/css/customer_order_tracking.css",
        ],
    },
    "installable": True,
}