# -*- coding: utf-8 -*-

import logging

from openerp import tools, api, fields, models, _
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class RemUniType(models.Model):
    _name = 'rem.unit.type'
    _description = 'Unit Type'

    name = fields.Char(string='Type Name', size=32, required=True, help="Type Name.")
    notes = fields.Text(string='Notes', help="Description of the type.")
    active = fields.Boolean(string='Active', default=True, help="If the active field is set to False, it will allow you to hide the analytic journal without removing it.")


class RemUnitStage(models.Model):
    _name = 'rem.unit.stage'
    _description = 'Unit Stage'

    name = fields.Char(string='Stage Name', size=32, required=True, help="Stage Name.")
    sequence = fields.Integer(string='Sequence', help="Used to order stages. Lower is better.")
    notes = fields.Text(string='Notes', help="Description of the stage.")
    active = fields.Boolean(string='Active', default=True, help="If the active field is set to False, it will allow you to hide the analytic journal without removing it.")


class RemUnit(models.Model):
    _name = 'rem.unit'
    _description = 'Real Estate Unit'

    name = fields.Char(string='Unit', size=32, required=True, help="Unit description (like house near riverside).")
    active = fields.Boolean(string='Active', default=True, help="If the active field is set to False, it will allow you to hide the analytic journal without removing it.")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Contract/Analytic', help="Link this asset to an analytic account.")
    stage_id = fields.Many2one('rem.unit.stage', string='Stage', select=True)
    user_id = fields.Many2one('res.users', string='Salesman', required=False)
    bedrooms = fields.Integer(string='Number of bedrooms', default=1)
    bathrooms = fields.Integer(string='Number of bathrooms', default=1)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id)

