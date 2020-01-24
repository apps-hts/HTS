# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Hyperthink Systems Ltd 
# See LICENSE file for full copyright and licensing details.
#
##############################################################################
from odoo import fields, models, api, _
import base64
import datetime
from odoo.exceptions import ValidationError
import csv
import calendar
import os
import tempfile
import logging


_logger = logging.getLogger(__name__)


class VatReportWizard(models.TransientModel):
    _name = 'vat.report.wizard'

    month_of = fields.Selection([
        ('1','January'),
        ('2','February'),
        ('3','March'),
        ('4','April'),
        ('5','May'),
        ('6','Jun'),
        ('7','July'),
        ('8','August'),
        ('9','September'),
        ('10','October'),
        ('11','November'),
        ('12','December')
    ], string="Month")
    year_of = fields.Char(string="Year")
    tax_id = fields.Many2one('account.tax', string="tax")


    def print_sale_vat_xlsx_report(self):
        lastDayOfMonth = calendar.monthrange(int(self.year_of), int(self.month_of))[1]
        startDate = '%s-%s-01'%(self.year_of, self.month_of)
        endDate = '%s-%s-%s'%(self.year_of, self.month_of, lastDayOfMonth)

        invoice_objs = self.env['account.invoice'].search([
            ('state','in',['open','paid']),
            ('type','in',['out_invoice','out_refund']),
            ('date_invoice','>=',startDate),
            ('date_invoice','<=',endDate)
        ])
        file_fd, file_path = tempfile.mkstemp(suffix='.csv', prefix='sale_vat_report')
        csv_data = []
        if invoice_objs:
            for inv in invoice_objs:
                rInv = False
                has_tax = False
                if inv.type == 'out_refund' and inv.origin:
                    rInv = self.env['account.invoice'].search([
                        ('number', '=', inv.origin)])
                amount = 0.0
                for invoice_line in inv.invoice_line_ids:
                    # price_unit = invoice_line.price_unit * (1 - (invoice_line.discount or 0.0) / 100.0)
                    # taxes = self.tax_id.compute_all(
                    #     price_unit,
                    #     inv.currency_id,
                    #     invoice_line.quantity,
                    #     invoice_line.product_id,
                    #     inv.partner_id)['taxes']
                    for tax in invoice_line.invoice_line_tax_ids:
                        if self.tax_id.id == tax.id:
                            has_tax = True
                            if inv.type == 'out_refund':
                                amount += (-1 * invoice_line.price_subtotal)
                            else:
                                amount += invoice_line.price_subtotal
                            # for amount in taxes:
                            #     tax_amount += amount['amount']
                if has_tax:
                    data = [inv.partner_id.vat,
                            inv.partner_id.name,
                            inv.company_id.company_registry,
                            inv.date_invoice,
                            inv.number,
                            inv.name if inv.type == 'out_refund' else 'Sale of Stocks',
                            amount,
                            rInv.number if rInv else '',
                            rInv.date_invoice if rInv else '',
                            rInv.name if rInv else '',]

                    csv_data.append(data)

            with open(file_path, "w") as writeFile:
                writer = csv.writer(writeFile)
                # writer.writerows([[
                #     'PIN Number',
                #     'Customer Name',
                #     'ETR Number',
                #     'Invoice Date',
                #     'Invoice Number',
                #     'Discription of Goods/Services',
                #     'Taxable Amount'
                # ]])
                writer.writerows(csv_data)
            writeFile.close()

            result_file = open(file_path, 'rb').read()
            attachment_id = self.env['wizard.excel.report'].create({
                'name': 'Sales - %s %s.csv'%(calendar.month_name[int(self.month_of)], self.year_of),
                'report': base64.encodestring(result_file)
            })
            try:
                os.unlink(file_path)
            except (OSError, IOError):
                _logger.error('Error when trying to remove file %s' % file_path)

            return {
                'name': _('Odoo'),
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.excel.report',
                'res_id': attachment_id.id,
                'data': None,
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
             raise ValidationError(_('Invoice are Not Present in this month!!!'))

    def print_purchase_vat_xlsx_report(self):
        lastDayOfMonth = calendar.monthrange(int(self.year_of), int(self.month_of))[1]
        startDate = '%s-%s-01'%(self.year_of, self.month_of)
        endDate = '%s-%s-%s'%(self.year_of, self.month_of, lastDayOfMonth)

        invoice_objs = self.env['account.invoice'].search([
            ('state','in',['open','paid']),
            ('type','in',['in_invoice','in_refund']),
            ('date_invoice','>=',startDate),
            ('date_invoice','<=',endDate)
        ])
        file_fd, file_path = tempfile.mkstemp(suffix='.csv', prefix='purchase_vat_report')
        csv_data = []
        if invoice_objs:
            for inv in invoice_objs:
                rInv = False
                has_tax = False
                if inv.type == 'in_refund' and inv.origin:
                    rInv = self.env['account.invoice'].search([
                        ('number', '=', inv.origin)])
                amount = 0.0
                for tax in inv.tax_line_ids:
                    if self.tax_id.id == tax.tax_id.id:
                        has_tax = True
                        if inv.type == 'in_refund':
                            amount += (-1 * tax.base)
                        else:
                            amount += tax.base
                if has_tax:
                    data = [inv.partner_id.customer_flag if inv.partner_id.customer_flag else '',
                            inv.partner_id.vat,
                            inv.partner_id.name,
                            inv.date_invoice,
                            inv.reference,
                            inv.number if inv.type == 'in_refund' else 'purchase of stock',
                            inv.custom_entry_number if inv.custom_entry_number else '',
                            amount,
                            rInv.number if rInv else '',
                            rInv.date_invoice if rInv else '',
                            rInv.name if rInv else '',]

                    csv_data.append(data)

            with open(file_path, "w") as writeFile:
                writer = csv.writer(writeFile)
                # writer.writerows([[
                #     'Flag',
                #     'PIN Number',
                #     'Vandor Name',
                #     'Bill Date',
                #     'Invoice',
                #     'Discription of Goods/Services',
                #     'Custom Entry Number',
                #     'Taxable Amount'
                # ]])
                writer.writerows(csv_data)
            writeFile.close()

            result_file = open(file_path, 'rb').read()
            attachment_id = self.env['wizard.excel.report'].create({
                'name': 'Purchases - %s %s.csv'%(calendar.month_name[int(self.month_of)], self.year_of),
                'report': base64.encodestring(result_file)
            })
            try:
                os.unlink(file_path)
            except (OSError, IOError):
                _logger.error('Error when trying to remove file %s' % file_path)
            return {
                'name': _('Odoo'),
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.excel.report',
                'res_id': attachment_id.id,
                'data': None,
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
             raise ValidationError(_('Invoice are Not Present in this month!!!'))

class WizardExcelReport(models.TransientModel):
    _name = 'wizard.excel.report'

    name = fields.Char('File Name', size=64)
    report = fields.Binary('Excel Report', readonly=True)
