import time
from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, except_orm, Warning, RedirectWarning, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import odoo.addons.decimal_precision as dp


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

class Partner(models.Model):
    _inherit = 'res.partner'
    
    ktp = fields.Char('KTP')
    fax = fields.Char('Fax')
    owner_name = fields.Char('Nama Pemilik')
    invoice_limit = fields.Float('Invoice Limit')
    total_receivable = fields.Float('Total Receivable', compute='_compute_total_receivable', digits=dp.get_precision('Product Unit of Measure'))
    total_giro = fields.Float('Total Giro', compute='_compute_total_giro', digits=dp.get_precision('Product Unit of Measure'))
    
    @api.one
    def _compute_total_receivable(self):
        invoice_ids = self.env['account.invoice'].search([('partner_id','=',self.id),('state','=','open')])
        # sale_ids = self.env['sale.order'].search([('partner_id','=',self.id),('invoice_status','=','no')])
        total_receivable = 0

        # if sale_ids:
        #     for sale in sale_ids:
        #         total_receivable += sale.amount_total

        if invoice_ids:
            for invoice in invoice_ids:
                total_receivable += invoice.residual
            
        self.total_receivable = total_receivable
            
    @api.one
    def _compute_total_giro(self):
        giro_ids = self.env['bsc.giro'].search([('partner_id','=',self.id),('state','=','Baru')])
        total_giro = 0        
        if giro_ids:                    
            for giro in giro_ids:
                total_giro += giro.amount
            self.total_giro = total_giro    
                    
    @api.multi
    def action_view_receivable(self):      
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['domain'] = [('partner_id', '=', self.id),('state', '=', 'open')]
        action['context'] = {}
        return action
    
    @api.multi
    def action_view_giro(self):      
        action = self.env.ref('v10_bsc_sms.action_bsc_giro_form').read()[0]
        action['domain'] = [('partner_id', '=', self.id),('state', '=', 'Baru')]
        action['context'] = {}
        return action

class ProductTemplate(models.Model):
    _inherit = "product.template"

    tax_name = fields.Char('Name for Tax')

class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    user_id = fields.Many2one('res.users', compute="_get_user_id", string='Salesperson', store=True)
    is_change = fields.Boolean('Trigger')
    
    @api.depends('partner_id','is_change')
    def _get_user_id(self):
        for res in self:
            user_id = False
            if res.partner_id:                
                user_id = res.partner_id.user_id.id
            res.user_id = user_id 
    
    # def _create_payment_entry(self, amount):
    #     """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
    #         Return the journal entry.
    #     """
    #     aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
    #     invoice_currency = False
    #     if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
    #         #if all the invoices selected share the same currency, record the paiement in that currency too
    #         invoice_currency = self.invoice_ids[0].currency_id
    #     debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)

    #     move = self.env['account.move'].create(self._get_move_vals())

    #     #Write line corresponding to invoice payment
    #     counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
    #     counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
    #     counterpart_aml_dict.update({'currency_id': currency_id})
    #     counterpart_aml = aml_obj.create(counterpart_aml_dict)

    #     #Reconcile with the invoices
    #     if self.payment_difference_handling == 'reconcile' and self.payment_difference:
    #         writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #         debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)
    #         writeoff_line['name'] = _('Counterpart')
    #         writeoff_line['account_id'] = self.writeoff_account_id.id
    #         writeoff_line['debit'] = debit_wo
    #         writeoff_line['credit'] = credit_wo
    #         writeoff_line['amount_currency'] = amount_currency_wo
    #         writeoff_line['currency_id'] = currency_id
    #         writeoff_line = aml_obj.create(writeoff_line)
    #         if counterpart_aml['debit']:
    #             counterpart_aml['debit'] += credit_wo - debit_wo
    #         if counterpart_aml['credit']:
    #             counterpart_aml['credit'] += debit_wo - credit_wo
    #         counterpart_aml['amount_currency'] -= amount_currency_wo
    #     self.invoice_ids.register_payment(counterpart_aml)

    #     #Write counterpart lines
    #     if not self.currency_id != self.company_id.currency_id:
    #         amount_currency = 0
    #     liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
    #     liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
    #     aml_obj.create(liquidity_aml_dict)

    #     move.post()
    #     return move
    
    
# class account_register_payments(models.TransientModel):
#     _inherit = "account.register.payments"    

#     def get_payment_vals(self):
#         """ Hook for extension """
                
#         writeoff_account_id = ''
#         if self.payment_difference_handling:
#             payment_difference_handling = self.payment_difference_handling
#         if self.writeoff_account_id:
#             writeoff_account_id = self.writeoff_account_id.id
        
#         return {
#             'journal_id': self.journal_id.id,
#             'payment_method_id': self.payment_method_id.id,
#             'payment_date': self.payment_date,
#             'communication': self.communication,
#             'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices()],
#             'payment_type': self.payment_type,
#             'amount': self.amount,
#             'currency_id': self.currency_id.id,
#             'partner_id': self.partner_id.id,
#             'partner_type': self.partner_type,
#             'payment_difference_handling': payment_difference_handling,
#             'writeoff_account_id': writeoff_account_id,
#         }
        
#     @api.model
#     def default_get(self, fields):
#         rec = super(account_register_payments, self).default_get(fields)
#         context = dict(self._context or {})
#         active_model = context.get('active_model')
#         active_ids = context.get('active_ids')

#         # Checks on context parameters
#         if not active_model or not active_ids:
#             raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))
#         if active_model != 'account.invoice':
#             raise UserError(_("Programmation error: the expected model for this action is 'account.invoice'. The provided one is '%d'.") % active_model)

#         # Checks on received invoice records
#         invoices = self.env[active_model].browse(active_ids)
#         if any(invoice.state != 'open' for invoice in invoices):
#             raise UserError(_("You can only register payments for open invoices"))
#         if any(inv.commercial_partner_id != invoices[0].commercial_partner_id for inv in invoices):
#             raise UserError(_("In order to pay multiple invoices at once, they must belong to the same commercial partner."))
#         if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] for inv in invoices):
#             raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))
#         if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
#             raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))

#         total_amount = sum(inv.residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoices)
#         communication = ' '.join([ref for ref in invoices.mapped('reference') if ref])

#         rec.update({
#             'amount': abs(total_amount),
#             'real_amount': abs(total_amount),
#             'currency_id': invoices[0].currency_id.id,
#             'payment_type': total_amount > 0 and 'inbound' or 'outbound',
#             'partner_id': invoices[0].commercial_partner_id.id,
#             'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
#             'communication': communication,
#         })
#         return rec
    
class account_abstract_payment(models.AbstractModel):
    _inherit = "account.abstract.payment"
    
    real_amount = fields.Monetary('Invoice Amount')
    is_giro = fields.Boolean('Use Giro')
    giro_id = fields.Many2one('bsc.giro', 'Nomor Giro')
    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True)
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')], default='open', string="Payment Difference", copy=False)
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", domain=[('deprecated', '=', False)], copy=False)    

    @api.one
    @api.depends('real_amount', 'amount')
    def _compute_payment_difference(self):                
        self.payment_difference = self.amount - self.real_amount        
            
    @api.onchange('partner_id')
    def _onchange_partner_id(self):        
        result = {}            
        if self.partner_id:                
            result['domain'] = {'giro_id': [('partner_id', '=', self.partner_id.id),('state', '=', 'Baru')]}
        return result

    @api.onchange('giro_id')
    def _onchange_giro_id(self):                
        if self.giro_id:
            self.amount = self.giro_id.amount

    # @api.multi
    # def create_payment(self):
    #     payment = self.env['account.payment'].create(self.get_payment_vals())
    #     payment.write({                       
    #                    'payment_difference_handling': self.payment_difference_handling,
    #                    'writeoff_account_id': self.writeoff_account_id.id,
    #                    })
    #     payment.post()
    #     if self.is_giro and self.giro_id:
    #         giro = self.env['bsc.giro'].browse(self.giro_id.id)        
    #         giro.write({'state':'Cair','date_due':self.payment_date})
    #     return {'type': 'ir.actions.act_window_close'}
                    
# class ReportAgedPartnerBalance(models.AbstractModel):
#     _inherit = 'report.account.report_agedpartnerbalance'

#     def _get_partner_move_lines(self, account_type, date_from, target_move, period_length, partner_id):
#         periods = {}
#         start = datetime.strptime(date_from, "%Y-%m-%d")
#         for i in range(5)[::-1]:
#             stop = start - relativedelta(days=period_length)
#             periods[str(i)] = {
#                 'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
#                 'stop': start.strftime('%Y-%m-%d'),
#                 'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
#             }
#             start = stop - relativedelta(days=1)

#         res = []
#         total = []
#         cr = self.env.cr
#         user_company = self.env.user.company_id.id
#         move_state = ['draft', 'posted']
#         if target_move == 'posted':
#             move_state = ['posted']
#         arg_list = (tuple(move_state), tuple(account_type))
#         #build the reconciliation clause to see what partner needs to be printed
#         reconciliation_clause = '(l.reconciled IS FALSE)'
#         cr.execute('SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where create_date > %s', (date_from,))
#         reconciled_after_date = []
#         for row in cr.fetchall():
#             reconciled_after_date += [row[0], row[1]]
#         if reconciled_after_date:
#             reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
#             arg_list += (tuple(reconciled_after_date),)
            
#         if partner_id:
#             arg_list += (date_from, user_company, partner_id)
#         else:
#             arg_list += (date_from, user_company)
            
#         query = ''
#         if partner_id:        
#             query = '''
#                 SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
#                 FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
#                 WHERE (l.account_id = account_account.id)
#                     AND (l.move_id = am.id)
#                     AND (am.state IN %s)
#                     AND (account_account.internal_type IN %s)
#                     AND ''' + reconciliation_clause + '''
#                     AND (l.date <= %s)
#                     AND l.company_id = %s
#                     AND l.partner_id = %s                
#                 ORDER BY UPPER(res_partner.name)'''
#         else:
#             query = '''
#                 SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
#                 FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
#                 WHERE (l.account_id = account_account.id)
#                     AND (l.move_id = am.id)
#                     AND (am.state IN %s)
#                     AND (account_account.internal_type IN %s)
#                     AND ''' + reconciliation_clause + '''
#                     AND (l.date <= %s)
#                     AND l.company_id = %s                                
#                 ORDER BY UPPER(res_partner.name)'''
#         cr.execute(query, arg_list)

#         partners = cr.dictfetchall()
#         # put a total of 0
#         for i in range(7):
#             total.append(0)

#         # Build a string like (1,2,3) for easy use in SQL query
#         partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
#         lines = dict((partner['partner_id'] or False, []) for partner in partners)
#         if not partner_ids:
#             return [], [], []

#         # This dictionary will store the not due amount of all partners
#         undue_amounts = {}
#         query = ''
#         if partner_id:
#             query = '''SELECT l.id
#                     FROM account_move_line AS l, account_account, account_move am
#                     WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
#                         AND (am.state IN %s)
#                         AND (account_account.internal_type IN %s)
#                         AND (COALESCE(l.date_maturity,l.date) > %s)\
#                         AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
#                     AND (l.date <= %s)
#                     AND l.partner_id = %s                
#                     AND l.company_id = %s'''
#         else:
#             query = '''SELECT l.id
#                 FROM account_move_line AS l, account_account, account_move am
#                 WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
#                     AND (am.state IN %s)
#                     AND (account_account.internal_type IN %s)
#                     AND (COALESCE(l.date_maturity,l.date) > %s)\
#                     AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
#                 AND (l.date <= %s)                            
#                 AND l.company_id = %s'''
#         if partner_id:
#             cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, partner_id, user_company))
#         else:
#             cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, user_company))
            
#         aml_ids = cr.fetchall()
#         aml_ids = aml_ids and [x[0] for x in aml_ids] or []
#         for line in self.env['account.move.line'].browse(aml_ids):
#             partner_id = line.partner_id.id or False
#             if partner_id not in undue_amounts:
#                 undue_amounts[partner_id] = 0.0
#             line_amount = line.balance
#             if line.balance == 0:
#                 continue
#             for partial_line in line.matched_debit_ids:
#                 if partial_line.create_date[:10] <= date_from:
#                     line_amount += partial_line.amount
#             for partial_line in line.matched_credit_ids:
#                 if partial_line.create_date[:10] <= date_from:
#                     line_amount -= partial_line.amount
#             if not self.env.user.company_id.currency_id.is_zero(line_amount):
#                 undue_amounts[partner_id] += line_amount
#                 lines[partner_id].append({
#                     'line': line,
#                     'amount': line_amount,
#                     'period': 6,
#                 })

#         # Use one query per period and store results in history (a list variable)
#         # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
#         history = []
#         for i in range(5):
#             args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
#             dates_query = '(COALESCE(l.date_maturity,l.date)'

#             if periods[str(i)]['start'] and periods[str(i)]['stop']:
#                 dates_query += ' BETWEEN %s AND %s)'
#                 args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
#             elif periods[str(i)]['start']:
#                 dates_query += ' >= %s)'
#                 args_list += (periods[str(i)]['start'],)
#             else:
#                 dates_query += ' <= %s)'
#                 args_list += (periods[str(i)]['stop'],)
            
#             if partner_id:
#                 args_list += (date_from, partner_id, user_company)
#             else:
#                 args_list += (date_from, user_company)

#             query = ''
#             if partner_id:
#                 query = '''SELECT l.id
#                         FROM account_move_line AS l, account_account, account_move am
#                         WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
#                             AND (am.state IN %s)
#                             AND (account_account.internal_type IN %s)
#                             AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
#                             AND ''' + dates_query + '''
#                         AND (l.date <= %s)          
#                         AND l.partner_id = %s                    
#                         AND l.company_id = %s'''
#             else:
#                 query = '''SELECT l.id
#                     FROM account_move_line AS l, account_account, account_move am
#                     WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
#                         AND (am.state IN %s)
#                         AND (account_account.internal_type IN %s)
#                         AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
#                         AND ''' + dates_query + '''
#                     AND (l.date <= %s)                                              
#                     AND l.company_id = %s'''
#             cr.execute(query, args_list)
#             partners_amount = {}
#             aml_ids = cr.fetchall()
#             aml_ids = aml_ids and [x[0] for x in aml_ids] or []
#             for line in self.env['account.move.line'].browse(aml_ids):
#                 partner_id = line.partner_id.id or False
#                 if partner_id not in partners_amount:
#                     partners_amount[partner_id] = 0.0
#                 line_amount = line.balance
#                 if line.balance == 0:
#                     continue
#                 for partial_line in line.matched_debit_ids:
#                     if partial_line.create_date[:10] <= date_from:
#                         line_amount += partial_line.amount
#                 for partial_line in line.matched_credit_ids:
#                     if partial_line.create_date[:10] <= date_from:
#                         line_amount -= partial_line.amount

#                 if not self.env.user.company_id.currency_id.is_zero(line_amount):
#                     partners_amount[partner_id] += line_amount
#                     lines[partner_id].append({
#                         'line': line,
#                         'amount': line_amount,
#                         'period': i + 1,
#                         })
#             history.append(partners_amount)

#         for partner in partners:
#             if partner['partner_id'] is None:
#                 partner['partner_id'] = False
#             at_least_one_amount = False
#             values = {}
#             undue_amt = 0.0
#             if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
#                 undue_amt = undue_amounts[partner['partner_id']]

#             total[6] = total[6] + undue_amt
#             values['direction'] = undue_amt
#             if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
#                 at_least_one_amount = True

#             for i in range(5):
#                 during = False
#                 if partner['partner_id'] in history[i]:
#                     during = [history[i][partner['partner_id']]]
#                 # Adding counter
#                 total[(i)] = total[(i)] + (during and during[0] or 0)
#                 values[str(i)] = during and during[0] or 0.0
#                 if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
#                     at_least_one_amount = True
#             values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
#             ## Add for total
#             total[(i + 1)] += values['total']
#             values['partner_id'] = partner['partner_id']
#             if partner['partner_id']:
#                 browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
#                 values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[0:40] + '...' or browsed_partner.name
#                 values['trust'] = browsed_partner.trust
#             else:
#                 values['name'] = _('Unknown Partner')
#                 values['trust'] = False

#             if at_least_one_amount:
#                 res.append(values)

#         return res, total, lines

#     @api.model
#     def render_html(self, docids, data=None):
#         total = []        
#         model = self.env.context.get('active_model')
#         docs = self.env[model].browse(self.env.context.get('active_id'))

#         target_move = data['form'].get('target_move', 'all')
#         date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
#         partner_id = data['form']['partner_id']
        
#         print "Partner ID ", partner_id
        
#         if data['form']['result_selection'] == 'customer':
#             account_type = ['receivable']
#         elif data['form']['result_selection'] == 'supplier':
#             account_type = ['payable']
#         else:
#             account_type = ['payable', 'receivable']

#         movelines, total, dummy = self._get_partner_move_lines(account_type, date_from, target_move, data['form']['period_length'], partner_id)
#         docargs = {
#             'doc_ids': self.ids,
#             'doc_model': model,
#             'data': data['form'],
#             'docs': docs,
#             'time': time,
#             'get_partner_lines': movelines,
#             'get_direction': total,
#         }
#         return self.env['report'].render('account.report_agedpartnerbalance', docargs)

    
# class AccountAgedTrialBalance(models.TransientModel):
#     _inherit = 'account.aged.trial.balance'        
    
#     partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer','=',True)])
    
#     def _print_report(self, data):
#         res = {}        
#         data = self.pre_print_report(data)
#         data['form'].update(self.read(['period_length'])[0])
#         period_length = data['form']['period_length']
#         if period_length<=0:
#             raise UserError(_('You must set a period length greater than 0.'))
#         if not data['form']['date_from']:
#             raise UserError(_('You must set a start date.'))

#         start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")

#         for i in range(5)[::-1]:
#             stop = start - relativedelta(days=period_length - 1)
#             res[str(i)] = {
#                 'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
#                 'stop': start.strftime('%Y-%m-%d'),
#                 'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),                
#             }
#             start = stop - relativedelta(days=1)
#         data['form'].update(res)
#         data['form'].update({
#                              'partner_id': self.partner_id.id
#                              })
        
#         return self.env['report'].with_context(landscape=True).get_action(self, 'account.report_agedpartnerbalance', data=data)
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def action_confirm(self):
        for order in self:
            # Check Invoice Limit
            if order.partner_id.invoice_limit < order.partner_id.total_receivable:
                raise ValidationError(_("This Customer has reached the Limit of Outstanding Invoices"))
            elif order.partner_id.invoice_limit < order.amount_total:
                raise ValidationError(_("This order is more than this Customer Limit"))

            # Check Overdue invoices
            outstanding_invoice = self.env['account.invoice'].search([
                ('partner_id','=',order.partner_id.id), 
                ('state','=','open'), 
                ('date_due','<',fields.Date.today())])

            if outstanding_invoice:
                raise ValidationError(_("There are Overdue Invoices for this Customer"))   

        return super(SaleOrder, self).action_confirm()
        #     order.state = 'sale'
        #     order.confirmation_date = fields.Datetime.now()
        #     if self.env.context.get('send_email'):
        #         self.force_quotation_send()
        #     order.order_line._action_procurement_create()
        # if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
        #     self.action_done()
        # return True

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or 'New'

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])            
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)            
        
        # print "Amount Total ", vals.get('amount_total')

        # # Check Invoice Limit
        # partner = self.env['res.partner'].browse(vals.get('partner_id'))
        # if partner.invoice_limit < partner.total_receivable:
        #     raise ValidationError(_("This Customer has reached the Limit of Outstanding Invoices"))
        # elif partner.invoice_limit < vals.get('amount_total'):
        #     raise ValidationError(_("This order is more than this Customer Limit"))

        # # Check Overdue invoices
        # outstanding_invoice = self.env['account.invoice'].search([
        #     ('partner_id','=',vals['partner_id']), 
        #     ('state','=','open'), 
        #     ('date_due','>=',fields.Date.today())])

        # if outstanding_invoice:
        #     raise ValidationError(_("There are Overdue Invoices for this Customer"))        
            
        result = super(SaleOrder, self).create(vals)
        return result
    
    
class BscGiro(models.Model):
    _name = 'bsc.giro'
    
    name = fields.Char('Nomor Giro')
    date = fields.Date('Tanggal Terbit', default=fields.date.today())
    date_due = fields.Date('Tanggal Pencairan Giro')
    amount = fields.Float('Nominal')
    partner_id = fields.Many2one('res.partner', 'Customer')
    jadwal_cair = fields.Date('Jadwal Cair')    
    state = fields.Selection([('Baru','Baru'),('Cair','Cair'),('Batal','Batal')], string='Status', default='Baru')
    
    @api.multi
    def button_cancel(self):
        self.state = 'Batal'

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    is_giro = fields.Boolean('Use Giro')
    giro_id = fields.Many2one('bsc.giro', 'Nomor Giro')
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):        
        result = {}        
        result['domain'] = {'giro_id': [('partner_id', '=', self.partner_id.id),('state', '=', 'Baru')]}
        return result
    
    @api.onchange('giro_id')
    def _onchange_giro_id(self):                
        if self.giro_id:
            self.amount = self.giro_id.amount            
    
    # @api.multi
    # def post(self):                             
    #     """ Create the journal items for the payment and update the payment's state to 'posted'.
    #         A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
    #         and another in the destination reconciliable account (see _compute_destination_account_id).
    #         If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
    #         If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
    #     """
    #     for rec in self:

    #         if rec.state != 'draft':
    #             raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

    #         if any(inv.state != 'open' for inv in rec.invoice_ids):
    #             raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

    #         # Use the right sequence to set the name
    #         if rec.payment_type == 'transfer':
    #             sequence_code = 'account.payment.transfer'
    #         else:
    #             if rec.partner_type == 'customer':
    #                 if rec.payment_type == 'inbound':
    #                     sequence_code = 'account.payment.customer.invoice'
    #                 if rec.payment_type == 'outbound':
    #                     sequence_code = 'account.payment.customer.refund'
    #             if rec.partner_type == 'supplier':
    #                 if rec.payment_type == 'inbound':
    #                     sequence_code = 'account.payment.supplier.refund'
    #                 if rec.payment_type == 'outbound':
    #                     sequence_code = 'account.payment.supplier.invoice'
    #         rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)

    #         # Create the journal entry
    #         amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
    #         move = rec._create_payment_entry(amount)

    #         # In case of a transfer, the first journal entry created debited the source liquidity account and credited
    #         # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
    #         if rec.payment_type == 'transfer':
    #             transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
    #             transfer_debit_aml = rec._create_transfer_entry(amount)
    #             (transfer_credit_aml + transfer_debit_aml).reconcile()

    #         rec.write({'state': 'posted', 'move_name': move.name})
    #         giro = self.env['bsc.giro'].browse(self.giro_id.id)        
    #         giro.write({'state':'Cair','date_due':self.payment_date})
                    
    #     return True
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
        
    amount_usd = fields.Float('Amount USD')
    attachment_id = fields.Binary('Attachment', attachment=True)
    total_qty = fields.Integer(compute="_get_total_qty", string='Total Qty')
    new_partner_id = fields.Many2one('res.partner', 'New Partner')
    
    @api.depends('invoice_line_ids')
    def _get_total_qty(self):
        for res in self:
            total_qty = 0
            for line in res.invoice_line_ids:
                total_qty += line.quantity
            res.total_qty = total_qty

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(round(line.price_subtotal) for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(round(line.amount)) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    _order = 'product_id asc'    

    amount_usd = fields.Float('Amount USD')

class Companies(models.Model):
    _inherit = 'res.company'
    
    bank_number1 = fields.Char('Invoice Text 1')
    bank_number2 = fields.Char('Invoice Text 2')
    bank_number3 = fields.Char('Invoice Text 3')
    bank_number4 = fields.Char('Invoice Text 4')
    bank_number5 = fields.Char('Invoice Text 5')
    
    