# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _
from openerp import exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError


class RemContractType(models.Model):
    _name = 'rem.contract.type'
    _description = 'Contract Type'

    name = fields.Char(string='Type Name', size=32,
                       required=True, help='Type Name.')
    notes = fields.Text(string='Description', help='Brief description.')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class RemBuyerContractType(models.Model):
    _name = 'rem.buyer.contract.type'
    _description = 'Buyer Contract Type'
    _inherit = ['rem.contract.type']


class RemListingContractType(models.Model):
    _name = 'rem.listing.contract.type'
    _description = 'Listing Contract Type'
    _inherit = ['rem.contract.type']


class RemListingContract(models.Model):
    _name = 'rem.listing.contract'
    _description = 'Listing Contract'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'auto_renew' in init_values and self.auto_renew:
            return 'rem.mt_listing_created'
        return super(RemListingContract, self)._track_subtype(init_values)

    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    partner_id = fields.Many2one(related='unit_id.partner_id', string='Seller', store=True)
    type_id = fields.Many2one('rem.listing.contract.type', string='Type')
    date_start = fields.Date('Start Date', required=True, default=lambda self: self._context.get('date', fields.Date.context_today(self)))
    date_end = fields.Date('End Date', required=True)
    auto_renew = fields.Boolean(string='Auto Renew?', default=True,
                                help='Check for automatically renew for same period and log in the chatter')
    notice_date = fields.Date('Notice Date')
    period = fields.Integer('Period', default=1)
    period_unit = fields.Selection([('days', 'Day(s)'), ('months', 'Month(s)')], string='Period Unit', change_default=True,
                                   default='months')
    notice_period = fields.Integer('Notice Period', default=1)
    ordering = fields.Integer('Ordering Field', default=1)
    notice_period_unit = fields.Selection([('days', 'Days'), ('months', 'Months')], string='Notice Unit', change_default=True,
                                          default='months')
    current = fields.Boolean(string='Current Contract', default=True,
                             help='This contract is the current one for this unit?')
    # TODO: scheduled action for auto renewal or just trigger when unit is read

    @api.multi
    def unlink(self):
        for ct1 in self:
            id1 = ct1.id
            unit_id = ct1.unit_id.id
            self.env.cr.execute('update rem_listing_contract set current=True where id=( '
                                'select id from rem_listing_contract '
                                'where id <> %s and unit_id=%s '
                                'order by date_end desc limit 1);'
                                'update rem_listing_contract set current=False where ids in ( '
                                'select id from rem_listing_contract '
                                'where id <> %s and unit_id=%s);', [id1, unit_id, id1, unit_id])
        ret = super(RemListingContract, self).unlink()
        return ret

    @api.model
    def create(self, vals):
        ct = super(RemListingContract, self).create(vals)
        for ct2 in ct.unit_id.listing_contract_ids:
            if ct2.id != ct.id:
                ct2.current = False
        return ct

    @api.multi
    @api.constrains('date_start', 'period')
    def _check_dates(self):
        for ct1 in self:
            for ct2 in ct1.unit_id.listing_contract_ids:
                if ct2.id != ct1.id:
                    if ct2.date_end > ct1.date_start:
                        raise ValidationError(_('The last contract date for this unit is %s. please chose a following start date.') % ct2.date_end)

    @api.onchange('date_start', 'period', 'period_unit')
    def onchange_period(self):
        date_calc = False
        if self.period_unit == 'months':
            date_calc = datetime.strptime(self.date_start + ' 00:00:00',
                                          DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(months=self.period)
        else:
            date_calc = datetime.strptime(self.date_start + ' 00:00:00',
                                          DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=self.period)
        self.date_end = date_calc
        return {}

    @api.onchange('date_end', 'notice_period_unit', 'notice_period')
    def onchange_period_unit(self):
        date_calc = False
        if self.notice_period_unit == 'months':
            date_calc = datetime.strptime(self.date_end + ' 00:00:00',
                                          DEFAULT_SERVER_DATETIME_FORMAT) - relativedelta(months=self.notice_period)
        else:
            date_calc = datetime.strptime(self.date_end + ' 00:00:00',
                                          DEFAULT_SERVER_DATETIME_FORMAT) - timedelta(days=self.notice_period)
        self.notice_date = date_calc

    @api.multi
    @api.depends('date_start', 'period', 'period_unit')
    def name_get(self):
        units = []
        for rec in self:
            name = rec.type_id.name or _("Listing Agreement")
            if rec.date_start and rec.period and rec.period_unit:
                name += " %s - %s %s" % (rec.date_start
                                         , rec.period, rec.period_unit)
            units.append((rec.id, name))
        return units