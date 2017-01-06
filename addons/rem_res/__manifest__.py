# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Residential Asset Management',
    'version': '1.0',
    'author': 'Odoo GAP',
    'summary': 'Real Estate Residential Asset Management',
    'description': """
Manage real estate residential assets for sale and rent management purposes
===============================================================
This module allows to sell/rent real estate residential units


    """,
    'website': 'http://www.odoogap.com',
    'depends': ['rem'],
    'category': 'Real Estate',
    'data': [
        'data/rem_data.xml',
        'data/fields_data.xml',
        'views/rem_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
