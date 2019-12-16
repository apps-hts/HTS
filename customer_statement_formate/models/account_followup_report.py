# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           # 
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################


from odoo import api,fields,models,_
from datetime import datetime
import xlwt
import xlsxwriter
from xlsxwriter.workbook import Workbook
import io
import json


class AccountFollowupReport(models.AbstractModel):
    _inherit = "account.followup.report"

    @api.model
    def get_pdf_template(self):
        return 'customer_statement_formate.report_customer_overdue'


    @api.model
    def print_pdf_followups(self, records):
        """
        Print one or more followups in one PDF
        records contains either a list of records (come from an server.action) or a field 'ids' which contains a list of one id (come from JS)
        """
        res_ids = records['ids'] if 'ids' in records else records.ids  # records come from either JS or server.action
        self.env['res.partner'].browse(res_ids).message_post(
            body=_('Sent a followup letter'), subtype='account_reports.followup_logged_action')
        return self.env.ref('customer_statement_formate.action_report_customer_overdue').report_action(res_ids)

class account_report_context_followup(models.AbstractModel):
    _inherit = 'res.partner'

    def get_lines(self, partner_id):
        lines = self.env['account.followup.report']._get_lines({'partner_id': partner_id})
        return lines

    def get_xlsx_report(self, options):
        for context in self:
            partner = context
            context = context.with_context(lang=partner.lang)
            lines = context.env['account.followup.report']._get_lines({'partner_id': partner.id})
            company = self.env.user.company_id
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Sheet1')
            worksheet.set_paper(9)
            worksheet.set_margins(left=0.7,right=0.7, top=0.75, bottom=0.75)

            font = xlwt.Font()
            style = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 12, 'bold': True, 'font': font, 'bottom': 2, 'top': 2})
            style2 = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 12, 'font': font, 'top': 2})

            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 18)
            worksheet.set_column(3, 3, 15)
            worksheet.set_column(4, 4, 23)
            worksheet.set_column(5, 7, 11)

            worksheet.set_header()
            worksheet.write(1, 7, company.partner_id.name)
            line2 = ' '
            if company.partner_id.street and company.partner_id.zip:
                line2 = company.partner_id.street + ' - ' + company.partner_id.zip
            elif company.partner_id.street and not company.partner_id.zip:
                line2 = company.partner_id.street
            elif not company.partner_id.street and company.partner_id.zip:
                line2 = company.partner_id.zip
            else:
                line2 = ''
            worksheet.write(2, 7, line2)
            line3 = ''
            if company.partner_id.phone and company.partner_id.mobile:
                line3 = company.partner_id.phone + '/' +  company.partner_id.mobile
            elif company.partner_id.phone and not company.partner_id.mobile:
                line3 = company.partner_id.phone
            elif not company.partner_id.phone and company.partner_id.mobile:
                line3 = company.partner_id.mobile
            worksheet.write(3, 7, 'MOBILES :' + line3)
            line4 = ''
            if company.partner_id.street2 and company.partner_id.city:
                line4 = company.partner_id.street2 + ', ' + company.partner_id.city
            elif company.partner_id.street2 and not company.partner_id.city:
                line4 = company.partner_id.street2
            elif not company.partner_id.street2 and company.partner_id.city:
                line4 = company.partner_id.city
            # worksheet.write(4, 7, line4 + ',FAX:'+ company.partner_id.fax if company.partner_id.fax else '')
            worksheet.write(5, 7, company.partner_id.country_id and company.partner_id.country_id.name or '')
            worksheet.write(7, 7, 'VAT Reg. No.' + company.partner_id.vat if company.partner_id.vat else '')
            worksheet.write(10, 4, 'SALES STATEMENT')
            worksheet.write(12, 7, 'Account    '+ company.partner_id.ref if company.partner_id.ref else '')
            worksheet.write(12, 1, partner.name)

            worksheet.write(13, 1, partner.street if partner.street else '')
            worksheet.write(14, 7, 'Date   '+datetime.now().strftime('%d %b %y'))
            line6 = ''
            if partner.zip and partner.city:
                line6 = partner.zip + ' '+ partner.city
            elif partner.zip and not partner.city:
                line6 = partner.zip
            elif not partner.zip and partner.city:
                line6 = partner.city
            worksheet.write(14, 1, partner.street2 if partner.street2 else '')
            worksheet.write(15, 1, line6)
            worksheet.write(16, 1, partner.country_id.name if partner.country_id.name else '')
            line7 = ''
            if partner.phone and partner.mobile:
                line7 = partner.phone + '/' +  partner.mobile
            elif partner.phone and not partner.mobile:
                line7 = partner.phone
            elif not partner.phone and partner.mobile:
                line7 = partner.mobile
            worksheet.write(17, 1, line7)

            worksheet.write(20, 1, 'Date', style)
            worksheet.write(20, 2, 'Type', style)
            worksheet.write(20, 3, 'Reference Number', style)
            worksheet.write(20, 4, 'Description', style)
            worksheet.write(20, 5, 'Debit', style)
            worksheet.write(20, 6, 'Credit', style)
            worksheet.write(20, 7, 'Balance', style)
            line_2 = 20
            due_inv_total = 0
            thirtydays = 0
            sixtydays = 0
            ninetydays = 0
            ninetyplusdays = 0
            total_outstanding = 0
            total_credits = 0
            for line in lines:
                line_2 = line_2 + 1
                if 'type' in line and line.get('type') != 'total' and line.get('columns'):
                    a = line['columns'][-1]
                    am = a['name'].split(' ',1)
                    due_amount = float(am[-1].replace(',', ''))
                    l = context.env['account.move.line'].browse(line['id'])
                    if l.journal_id.code == 'INV':
                        due_inv_total = due_inv_total + due_amount
                        date_diff = l.date_maturity - datetime.now().date()
                        date_days = int(date_diff.days)
                        if date_days < 30:
                            thirtydays = thirtydays + due_amount
                        if date_days > 30 and date_days < 60:
                            sixtydays = sixtydays + due_amount
                        if date_days > 60 and date_days < 90:
                            ninetydays = ninetydays + due_amount
                        if date_days > 90:
                            ninetyplusdays = ninetyplusdays + due_amount
                    worksheet.write(line_2, 1, l.date.strftime('%d %b %y'))
                    worksheet.write(line_2, 2, l.journal_id.code)
                    worksheet.write(line_2, 3, l.move_id.name if l.move_id.name else '')
                    worksheet.write(line_2, 4, l.name)
                    worksheet.write(line_2, 5, l.debit)
                    worksheet.write(line_2, 6, l.credit)
                    worksheet.write(line_2, 7, due_amount)
                    total_outstanding = total_outstanding + due_amount
                    if l.journal_id.code == 'CCRN':
                        total_credits = total_credits + due_amount
            worksheet.write(line_2, 1,' ',style2)
            worksheet.write(line_2, 2,' ',style2)
            worksheet.write(line_2, 3,' ',style2)
            worksheet.write(line_2, 4,' ',style2)
            worksheet.write(line_2, 5,' ',style2)
            worksheet.write(line_2, 6,' ',style2)
            worksheet.write(line_2, 7,' ',style2)

            worksheet.write(line_2 + 1, 5, 'Total Balance Outstanding')
            worksheet.write(line_2 + 1, 7, total_outstanding)

            worksheet.write(line_2 + 5, 1,' ',style2)
            worksheet.write(line_2 + 5, 4,' ',style2)
            worksheet.write(line_2 + 5, 5,' ',style2)
            worksheet.write(line_2 + 5, 6,' ',style2)
            worksheet.write(line_2 + 5, 7,' ',style2)

            worksheet.write(line_2 + 5, 2, 'Aged Analysis', style2)
            worksheet.write(line_2 + 5, 3, '* = Disputed', style2)
            worksheet.write(line_2 + 6, 2,  'Current')
            worksheet.write(line_2 + 7, 2,  '0-30 Days')
            worksheet.write(line_2 + 8, 2,  '31-60 Days')
            worksheet.write(line_2 + 9, 2,  '61-90 Days')
            worksheet.write(line_2 + 10, 2,  '90+ Days')
            worksheet.write(line_2 + 11, 2, 'Unallocated Credits')

            worksheet.write(line_2 + 6, 3, due_inv_total)
            worksheet.write(line_2 + 7, 3, thirtydays)
            worksheet.write(line_2 + 8, 3, sixtydays)
            worksheet.write(line_2 + 9, 3, ninetydays)
            worksheet.write(line_2 + 10, 3, ninetyplusdays)
            worksheet.write(line_2 + 11, 3, total_credits)

            workbook.close()
            output.seek(0)
            options.stream.write(output.read())
            output.close()
