# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           # 
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from odoo.addons.account_reports.controllers.main import FinancialReportController

import json


class FinancialReportControllerNew(FinancialReportController):


    @http.route('/account_reports/followup_report/<string:output_format>/<string:partners>/', type='http', auth='user')
    def followupme(self, output_format, partners, token, **kw):
        uid = request.session.uid
        try:
            context_obj = request.env['account.report.context.followup']
            partners = request.env['res.partner'].browse([int(i) for i in partners.split(',')])
            context_ids = context_obj.search([('partner_id', 'in', partners.ids), ('create_uid', '=', uid)])
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', 'attachment; filename=payment_reminder.xlsx;')
                    ]
                )
                context_ids.get_xlsx_report(response)
                response.set_cookie('fileToken', token)
                return response
            else:
                response = request.make_response(
                    context_ids.with_context(public=True).get_pdf_report(log=True),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', 'attachment; filename=payment_reminder.pdf;')
                    ]
                )
                response.set_cookie('fileToken', token)
                return response
        except Exception, e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))