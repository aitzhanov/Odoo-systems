{
    'name': 'Library Event Themes',
    'version': '19.0.1.0.0',
    'summary': 'Reusable library-inspired themes for Odoo website events',
    'author': 'Library Event Themes Contributors',
    'license': 'LGPL-3',
    'category': 'Marketing/Events',
    'depends': [
        'event',
        'website_event',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/library_event_theme_data.xml',
        'views/library_event_theme_views.xml',
        'views/event_event_views.xml',
        'views/event_listing_templates.xml',
        'views/event_detail_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'library_event_themes/static/src/css/library_themes.css',
        ],
    },
    'installable': True,
    'application': False,
}
