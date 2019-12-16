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
import StringIO





class Report_account_followup_report(models.AbstractModel):
    _inherit = "account.followup.report"

    @api.model
    def get_pdf_template(self):
        return 'customer_statement_formate.report_customer_overdue'



class account_report_context_followup(models.TransientModel):
    _inherit = 'account.report.context.followup'


    def get_pdf_report(self, log=False):
        bodies = []
        headers = []
        footers = []
        for context in self:
            context = context.with_context(lang=context.partner_id.lang)
            report_obj = context.get_report_obj()
            lines = report_obj.get_lines(context, public=True)
            for line in lines:
                a = line['columns'][-1].replace("&nbsp;", ' ')
                am = a.split(' ',1)
                due_amount = float(am[-1].encode('utf-8').replace(',',''))
                line['columns'][-1] = due_amount
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            rcontext = {
                'context': context,
                'report': report_obj,
                'lines': lines,
                'mode': 'print',
                'base_url': base_url,
                'css': '',
                'o': self.env.user,
                'today': context._formatLangDate(datetime.today()),
                'company': self.env.user.company_id,
                'res_company': self.env.user.company_id,
            }
            html = context.env['ir.ui.view'].render_template(report_obj.get_pdf_template(), rcontext)
            bodies.append((0, html))
            header = self.env['ir.ui.view'].render_template("customer_statement_formate.customer_due_stmt_custom_layout_header", rcontext)
            rcontext['body'] = header
            header = self.env['ir.ui.view'].render_template("report.minimal_layout", rcontext)
            footer = self.env['ir.ui.view'].render_template("customer_statement_formate.customer_stmt_due_custom_layout_footer", rcontext)
            rcontext['body'] = footer
            rcontext['subst'] = True
            footer = self.env['ir.ui.view'].render_template("report.minimal_layout", rcontext)
            headers.append(header)
            footers.append(footer)

            rcontext['subst'] = True
            if log:
                msg = _('Sent a followup letter')
                context.partner_id.message_post(body=msg, subtype='account_reports.followup_logged_action')

        return self.env['report']._run_wkhtmltopdf(headers, footers, bodies, False, self.env.user.company_id.paperformat_id)


    def get_xlsx_report(self, response):
        for context in self:
            context = context.with_context(lang=context.partner_id.lang)
            report_obj = context.get_report_obj()
            lines = report_obj.get_lines(context, public=True)
            company = self.env.user.company_id
            output = StringIO.StringIO()
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
            worksheet.write(4, 7, line4 + ',FAX:'+ company.partner_id.fax if company.partner_id.fax else '')
            worksheet.write(5, 7, company.partner_id.country_id and company.partner_id.country_id.name or '')
            worksheet.write(7, 7, 'VAT Reg. No.' + company.partner_id.vat if company.partner_id.vat else '')
            worksheet.write(10, 4, 'SALES STATEMENT')
            worksheet.write(12, 7, 'Account    '+ company.partner_id.ref if company.partner_id.ref else '')
            worksheet.write(12, 1, context.partner_id.name)

            worksheet.write(13, 1, context.partner_id.street if context.partner_id.street else '')
            worksheet.write(14, 7, 'Date   '+datetime.now().strftime('%d %b %y'))
            line6 = ''
            if context.partner_id.zip and context.partner_id.city:
                line6 = context.partner_id.zip + ' '+ context.partner_id.city
            elif context.partner_id.zip and not context.partner_id.city:
                line6 = context.partner_id.zip
            elif not context.partner_id.zip and context.partner_id.city:
                line6 = context.partner_id.city
            worksheet.write(14, 1, context.partner_id.street2 if context.partner_id.street2 else '')
            worksheet.write(15, 1, line6)
            worksheet.write(16, 1, context.partner_id.country_id.name if context.partner_id.country_id.name else '')
            line7 = ''
            if context.partner_id.phone and context.partner_id.mobile:
                line7 = context.partner_id.phone + '/' +  context.partner_id.mobile
            elif context.partner_id.phone and not context.partner_id.mobile:
                line7 = context.partner_id.phone
            elif not context.partner_id.phone and context.partner_id.mobile:
                line7 = context.partner_id.mobile
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
                if line['type'] != 'total':
                    a = line['columns'][-1].replace("&nbsp;", ' ')
                    am = a.split(' ',1)
                    due_amount = float(am[-1].encode('utf-8').replace(',',''))
                    l = context.env['account.move.line'].browse(line['id'])
                    if l.journal_id.code == 'INV':
                        due_inv_total = due_inv_total + due_amount
                        date_diff = datetime.strptime(l.date_maturity, '%Y-%m-%d') - datetime.now()
                        date_days = int(date_diff.days)
                        if date_days < 30:
                            thirtydays = thirtydays + due_amount
                        if date_days > 30 and date_days < 60:
                            sixtydays = sixtydays + due_amount
                        if date_days > 60 and date_days < 90:
                            ninetydays = ninetydays + due_amount
                        if date_days > 90:
                            ninetyplusdays = ninetyplusdays + due_amount
                    worksheet.write(line_2, 1, datetime.strptime(l.date, '%Y-%m-%d').strftime('%d %b %y'))
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
            response.stream.write(output.read())
            output.close()




