# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
import datetime

MATCH_RE = {
    're_contract_type_id': 'contract_type_id',
    're_type': 'type_id',
    're_rooms': 'rooms',
    're_bathrooms': 'bathrooms',
    're_reason': 'reason',
    're_garages_spaces': 'garages',
    're_city': 'city_id',
    're_pool': 'sw_pool'
}


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    planned_revenue = fields.Float('Costumer Badget', track_visibility='always')
    unit_lead = fields.Many2many('rem.unit', string='Units')
    re_reason = fields.Many2one('reason.for.buy', string='Reason for Buy')

    # General Features
    re_contract_type_id = fields.Many2one(
        'contract.type', string='Contract Type')
    re_type = fields.Many2many('rem.unit.type', string='Property Type')
    re_min_bedrooms = fields.Integer(
        'Min Bedrooms', help="Min number of bedrooms")
    re_max_bedrooms = fields.Integer(
        'Max Bedrooms', help="Max number of bedrooms")
    re_bathrooms = fields.Integer(
        'Min Bathrooms', help="Min Number of bathrooms", re_field='bathrooms')
    re_city = fields.Many2one(
        'rem.unit.city', string='City', help='place in order of gratest zone e.g. US, CA, Los Angeles, Beverly Hills')
    re_points_interest = fields.Many2many(
        'location.preferences', string='Points of Interest')
    re_is_new = fields.Boolean(string='Is New', help='Active if you want to search for units new.')

    # Indoor Features
    re_air_conditioned = fields.Boolean(
        string='Air Conditioned', help='Active if you want to search for units with air conditioned.')
    re_ducted_cooling = fields.Boolean(
        string='Ducted Cooling', help='Active if you want to search for units with ducted cooling.')
    re_wardrobes = fields.Boolean(
        string='Built-in Wardrobes', help='Active if you want to search for units with built-in wardrobes.')
    re_dishwasher = fields.Boolean(
        string='Dishwasher', help='Active if you want to search for units with dishwasher.')
    re_living_areas = fields.Integer(
        'Min living Areas', help='Min number of living areas')

    # Outdoor Features
    re_backyard = fields.Boolean(
        string='Backyard', help='Active if you want to search for units with backyard.')
    re_dog_friendly = fields.Boolean(
        string='Dog Friendly', help='Active if you want to search for units with dog friendly.')
    re_garage_spaces = fields.Integer(
        'Min Garage Spaces', help='Number of garage spaces')
    re_secure_parking = fields.Boolean(
        string='Secure Parking', help='Active if you want to search for units with secure parking.')
    re_alarm = fields.Boolean(
        string='Alarm System', help='Active if you want to search for units with alarm system.')
    re_pool = fields.Boolean(
        string='Swimming Pool', help='Active if you want to search for units with swimming pool.')
    re_entertaining = fields.Boolean(
        string='Outdoor Entertaining Area', help='Active if you want to search for units with outdoor entertaining area.')



    @api.multi
    def action_find_matching_units(self):
        c_budget = self.planned_revenue
        # General Features
        c_types = self.re_contract_type_id
        cities = self.re_city
        p_types = self.re_type
        min_rooms = self.re_min_bedrooms
        max_rooms = self.re_max_bedrooms
        min_bath = self.re_bathrooms
        new = self.re_is_new
        interest = self.re_points_interest
        # Indoor Features
        air = self.re_air_conditioned
        ducted = self.re_ducted_cooling
        b_wardrobes = self.re_wardrobes
        dishwashers = self.re_dishwasher
        min_areas = self.re_living_areas
        # Outdoor Features
        backyards = self.re_backyard
        dogs = self.re_dog_friendly
        garage_spaces = self.re_garage_spaces
        s_parking = self.re_secure_parking
        alarms = self.re_alarm
        pools = self.re_pool
        entertainings = self.re_entertaining

        

        context = {}
        if c_budget:
            context.update({'max_planned_revenue': c_budget * 0.1 + c_budget})
        # General Features
        if c_types:
            context.update({'search_default_contract_type_id': c_types.id})
        if cities:
            context.update({'search_default_city_id': cities.id})
        if p_types:
            context.update({'search_default_type_id': p_types.id})
        if max_rooms:
            context.update({'max_bedrooms': max_rooms})
        if min_rooms:
            context.update({'min_bedrooms': min_rooms})
        if min_bath > 0:
            context.update({'min_bathrooms': min_bath})
        if new == True:
            context.update({'search_default_is_new': new})
        if interest:
                context.update({'search_default_points_interest': interest.id})

        # Indoor Features
        if air == True:
            context.update({'search_default_air_condicioned': air})
        if ducted == True:
            context.update({'search_default_ducted_cooling': ducted})
        if b_wardrobes == True:
            context.update({'search_default_wardrobes': b_wardrobes})
        if dishwashers == True:
            context.update({'search_default_dishwasher': dishwashers})
        if min_areas > 0:
            context.update({'min_living_areas': min_areas})
        # Outdoor Features
        if backyards == True:
            context.update({'search_default_backyard': backyards})
        if alarms == True:
            context.update({'search_default_alarm': alarms})
        if entertainings == True:
            context.update({'search_default_entertaining': entertainings})
        if pools == True:
            context.update({'search_default_sw_pool': pools})
        if garage_spaces > 0:
            context.update({'min_garages': garage_spaces})
        if s_parking == True:
            context.update({'search_default_secure_parking': s_parking})
        if dogs == True:
            context.update({'search_default_air_dog_friendly': dogs})


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

    def write(self, cr, uid, ids, vals, context=None):

        if 'stage_id' in vals:
            lead = self.browse(cr, uid, ids, context)
            stage_history = self.pool['stage.history']
            stage_history.create(cr, uid, {
                'lead_id': lead.id,
                'stage_id': lead.stage_id.id,
                'date': datetime.datetime.now(),
                'new_stage': vals.get('stage_id'),
                'user_id': uid,
            }, context=context)

        return super(CrmLead, self).write(cr, uid, ids, vals, context=context)


class StageHistory(models.Model):
    _name = 'stage.history'
    _rec_name = 'create_date'
    _order = 'create_date'

    new_stage = fields.Many2one('crm.stage', 'To Stage')
    stage_id = fields.Many2one('crm.stage', 'From Stage')
    date = fields.Datetime('Date Time', default=lambda self: fields.Datetime.now(), readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson')
    lead_id = fields.Many2one('crm.lead', 'Lead')
