# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import datetime

MATCH_RE = {}


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    unit_ids = fields.Many2many('rem.unit', 'crm_lead_rem_unit_rel1', 'unit_id', 'lead_id', string='Units')
    re_reason = fields.Many2one('reason.for.buy', string='Reason for Buy')

    @api.multi
    def action_schedule_meeting(self):
        for lead in self:
            res1 = super(CrmLead, self).action_schedule_meeting()
            res1['context'].update({
                'default_unit_ids': lead.unit_ids.ids,
            })
            return res1

    @api.multi
    def action_find_matching_units(self):
        context = dict(self._context or {})
        for conditions in MATCH_RE:
            if eval(conditions):
                for key, val in MATCH_RE[conditions].iteritems():
                    context[key] = eval(val)
        context['from_lead_id'] = self.id
        res = {
            'name': _('Search results'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form,graph',
            'res_model': 'rem.unit',
            'context': context,
        }

        return res

    @api.multi
    def action_stage_history(self):
        return {
            'name': _('Get stage history'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form,graph',
            'res_model': 'stage.history',
            'domain': "[('lead_id','=',active_id)]",
        }

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            for lead in self:
                stage_history = self.env['stage.history']
                stage_history.create({
                    'lead_id': lead.id,
                    'stage_id': lead.stage_id.id,
                    'date': datetime.datetime.now(),
                    'new_stage': vals.get('stage_id'),
                    'user_id': self._uid,
                })
        return super(CrmLead, self).write(vals)


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    @api.model
    def rename_crm_stages(self):
        stages = self.env['crm.stage'].search([('id', '<', 5)])
        for stage in stages:
            if stage.id == 1:
                stage.update({'name': 'Showing', 'sequence': 1})
            elif stage.id == 2:
                stage.update({'name': 'Offer submitted', 'sequence': 2})
            elif stage.id == 3:
                stage.update({'name': 'Pending', 'sequence': 3})
            elif stage.id == 4:
                stage.update({'name': 'Closed', 'sequence': 4})


class StageHistory(models.Model):
    _name = 'stage.history'
    _rec_name = 'create_date'
    _order = 'create_date'

    new_stage = fields.Many2one('crm.stage', 'To Stage')
    stage_id = fields.Many2one('crm.stage', 'From Stage')
    date = fields.Datetime('Date Time', default=lambda self: fields.Datetime.now(), readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson')
    lead_id = fields.Many2one('crm.lead', 'Lead')
