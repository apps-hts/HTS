# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Hyperthink Kenya. (Website: www.hyperthinkkenya.co.ke ).           # 
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

{
    'name' : 'Customer Statement Reports',
    'version': '12.0.0.0',
    'summary': 'Customer Statement Report from customers due payment',
    'category': 'Account',
    'description': """Customer Statement Report from customers due payment""",
    'author': 'Hyperthink Kenya.',
    'website': 'http://www.hyperthinkkenya.co.ke',
    'price': 150.00,
    'currency': 'EUR',
    'depends': ['account_reports', 'account_accountant', 'account_reports_followup'],
    'data': [
        'views/report_followup.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/followup.xml',
    ],
    'installable': True,
}
