# -*- coding: utf-8 -*-
##############################################################################
#
# Part of  Hyperthink Systems Limited. (Website: www.hyperthinkkenya.co.ke).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'VAT Report',
    'version': '12.0.1.0',
    'summary': 'VAT report for importing in iTAX',
    'description': """
    """,
    'author': 'Hyperthink Systems Limited',
    'website': 'www.hyperthinkkenya.co.ke',
    'category': 'Reports',
    'depends': [ 'account', 'account_accountant'],
    'data': [
        
        'wizard/vat_report_view.xml',
        
    ],
    'installable': True,
}
