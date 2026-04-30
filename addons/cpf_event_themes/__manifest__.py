{
    'name': 'CPF Event Themes',
    'version': '19.0.1.0.0',
    'author': 'CPF',
    'license': 'LGPL-3',
    'depends': ['event', 'website_event'],
    'data': [
        'security/ir.model.access.csv',
        'views/event_theme_views.xml',
        'views/event_form_inherit.xml',
        'views/event_page_inherit.xml',
        'views/event_listing_custom.xml',
        'views/event_detail_custom.xml', 
   ],
    'assets': {
        'web.assets_frontend': [
            'cpf_event_themes/static/src/css/themes.css',
        ],
    },
    'installable': True,
}
