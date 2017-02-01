# -*- coding: utf-8 -*-
{
    'name': 'REM SimplyRETS Connector',
    'version': '10.0.1.0',
    'author': 'OdooGap',
    'summary': 'REM SimplyRETS Connector',
    'description': """
REM SimplyRETS Connector
========================
This Module allows to sync the listings from MLS through SimpleRETS Service API

    """,
    'website': 'http://www.odoogap.com',
    'depends': ['rem'],
    'category': 'Real Estate',
    'demo': [
    ],
    'data': [
        'views/res_config_view.xml',
        'data/convert_data.xml',
        'data/re.connector.rets.csv'
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
