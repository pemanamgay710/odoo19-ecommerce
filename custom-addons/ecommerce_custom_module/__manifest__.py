{
    'name': 'Ecommerce Custom Module',
    'version': '1.1',
    'summary': 'Custom eCommerce Website with Editable Landing Page',
    'description': """
        Adds a custom landing page and enhances the shop view while keeping Odoo’s default shop layout and editor support.
    """,
    'author': 'Pema Namgay',
    'license': 'LGPL-3',
    'depends': ['base', 'website', 'website_sale'],
    'data': [
        'views/landing_page.xml',
        'views/shop_inherit.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ecommerce_custom_module/static/src/css/custom_styles.css',
            'ecommerce_custom_module/static/src/js/custom_scripts.js',
        ],
    },
    'installable': True,
    'application': True,
}
