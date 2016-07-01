# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Asset Management',
    'version': '1.0',
    'author': 'Odoo GAP',
    'summary': 'Real Estate Asset Management',
    'description': """
Manage real estate assets for sale and rent management purposes
===============================================================
This module allows to sell/rent real estate units


    """,
    'website': 'http://www.odoogap.com',
    'depends': ['account', 'crm'],
    'category': 'Real Estate',
    'demo': [
		'data/rem_demo.xml'
    ],
    'data': [
		'data/rem_data.xml',
        'security/ir.model.access.csv',
		'views/crm_view.xml',
		'views/rem_menu.xml',
		'views/rem_unit_sequence.xml',
		'views/rem_view.xml',
        'views/stage_history_form.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
