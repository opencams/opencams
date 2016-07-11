# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models
from openerp import exceptions


class RemUniCity(models.Model):
    _name = 'rem.unit.city'
    _description = 'Unit City'

    name = fields.Char(
        string='City Name', size=32, required=True, help="City Name.")
    active = fields.Boolean(string='Active', default=True,
                            help="If the active field is set to False, it will allow you to hide without removing it.")


class RemUniType(models.Model):
    _name = 'rem.unit.type'
    _description = 'Unit Type'

    name = fields.Char(string='Type Name', size=32,
                       required=True, help="Type Name.")
    notes = fields.Text(string='Notes', help="Description of the type.")
    active = fields.Boolean(string='Active', default=True,
                            help="If the active field is set to False, it will allow you to hide without removing it.")


class RemUnitContractType(models.Model):
    _name = 'contract.type'
    _description = 'Contract Type'

    name = fields.Char(string='Contract Name', size=32, required=True,
                       help="Type of contract : renting, selling, selling ..")
    sequence = fields.Integer(string='Sequence')
    is_rent = fields.Boolean(string='Is Rentable', default=False,
                             help="Set if the contract type is rent based. This will make the Unit of Rent apear in the unit (e.g.: per month, per week..).")
    notes = fields.Text(string='Notes', help="Notes for the contract type.")
    active = fields.Boolean(string='Active', default=True,
                            help="If the active field is set to False, it will allow you to hide without removing it.")


class RemUnitStage(models.Model):
    _name = 'rem.unit.stage'
    _description = 'Unit Stage'

    name = fields.Char(
        string='Stage Name', size=32, required=True, help="Stage Name.")
    sequence = fields.Integer(
        string='Sequence', help="Used to order stages. Lower is better.")
    notes = fields.Text(string='Notes', help="Description of the stage.")
    active = fields.Boolean(string='Active', default=True,
                            help="If the active field is set to False, it will allow you to hide the analytic journal without removing it.")
    contract_type_id = fields.Many2one(
        'contract.type', string='Contract Type', required=False)


class ReasonForBuy(models.Model):
    _name = 'reason.for.buy'
    _description = 'Reason for Buy'

    name = fields.Char(string='Reason for Buy', size=32,
                       required=True, help="Reason for Buy")
    active = fields.Boolean(string='Active', default=True,
                            help="If the active field is set to False, it will allow you to hide without removing it.")


class LocationPreferences(models.Model):
    _name = 'location.preferences'
    _description = 'Location Preferences'

    name = fields.Char(string='Location Preferences', size=32,
                       required=True, help="Location Preferences")
    active = fields.Boolean(string='Active', default=True,
                            help="If the active field is set to False, it will allow you to hide without removing it.")


class RemImage(models.Model):
    _name = 'rem.image'
    _description = 'Unit Image'

    name = fields.Char(string='Unit', size=32, required=True,
                       help="Unit description (like house near riverside).")
    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Image", attachment=True, help="Unit image, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", compute='_compute_images', inverse='_inverse_image_medium',
                                 store=True, attachment=True)
    image_small = fields.Binary("Small-sized image", compute='_compute_images', inverse='_inverse_image_small',
                                store=True, attachment=True)
    sequence = fields.Integer(
        index=True, help="Gives the sequence order when displaying the images.", default=1)

    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(
                rec.image, size=(512, 512), avoid_if_small=True)
            rec.image_small = tools.image_resize_image_small(
                rec.image, size=(256, 256))

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)


class RemUnit(models.Model):
    _name = 'rem.unit'
    _description = 'Real Estate Unit'

    @api.model
    def _get_stage(self):
        return self.env['rem.unit.stage'].search([('contract_type_id', '=', False)], limit=1, order='sequence')

    @api.model
    def _get_default_contract_type(self):
        return self.env['contract.type'].search([], limit=1, order='id')

    @api.one
    def add_feature(self):
        self.env.cr.execute('SELECT COUNT(rem_unit_id) FROM rem_unit_res_users_rel WHERE res_user_id=%s LIMIT 1',
                            [self.env.uid])
        for feature_units in self.env.cr.dictfetchall():
            if feature_units['count'] < 5:
                self.feature_id = [(4, self.env.uid)]
            else:
                raise exceptions.ValidationError(
                    "You can only have 5 Feature Units.")
        return True

    @api.one
    def remove_feature(self):
        self.feature_id = [(3, self.env.uid)]
        return True

    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env[
                'ir.sequence'].next_by_code('rem.unit') or 'New'
            return super(RemUnit, self).create(vals)

    @api.model
    def _is_featured(self):
        self.env.cr.execute(
            'SELECT COUNT(rem_unit_id) FROM rem_unit_res_users_rel WHERE rem_unit_id=%s AND res_user_id=%s LIMIT 1',
            [self.id, self.env.uid])
        for feature_units in self.env.cr.dictfetchall():
            if feature_units['count'] > 0:
                self.is_featured = 1
            else:
                self.is_featured = 0
        return True

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if context.get('min_garages'):
            args += [('garages', '>=', context.get('min_garages'))]

        return super(RemUnit, self).search(args, offset, limit, order, count=count)

    reference = fields.Char(string='Reference', required=True, copy=False,
                            readonly=True, index=True, default='New')
    name = fields.Char(string='Unit', size=32, required=True,
                       help="Unit description (like house near riverside).")
    user_id = fields.Many2one('res.users', string='Salesman', required=False)
    rent_unit = fields.Selection([('per_hour', 'per Hour'), ('per_day', 'per Day'), ('per_week', 'per Week'),
                                  ('per_month', 'per Month')], string='Rent Unit', change_default=True,
                                 default=lambda self: self._context.get('rent_unit', 'per_month'))
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    is_rent = fields.Boolean(
        related='contract_type_id.is_rent', string='Is Rentable')
    active = fields.Boolean(string='Active', default=True,
                            help="If the active field is set to False, it will allow you to hide the unit.")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Contract/Analytic',
                                          help="Link this asset to an analytic account.")
    image_ids = fields.One2many(
        'rem.image', 'unit_id', string='Photos', ondelete='cascade')
    feature_id = fields.Many2many(
        'res.users', 'rem_unit_res_users_rel', 'rem_unit_id', 'res_user_id')
    is_featured = fields.Boolean(compute=_is_featured, store=False)
    reason = fields.Many2one('reason.for.buy', string="Reason for Buy")
    living_area = fields.Float('Living Area')
    land_area = fields.Float('Land Area')
    unit_description = fields.Text(string="Detailed Description")
    stage_id = fields.Many2one(
        'rem.unit.stage', string='Stage', default=_get_stage)

    # General Features
    type_id = fields.Many2one('rem.unit.type', string='Type')
    bedrooms = fields.Integer(
        string='Number of bedrooms', default=1, required=True)
    bathrooms = fields.Integer(
        string='Number of bathrooms', default=1, required=True)
    is_new = fields.Boolean(string='Is New', default=True,
                            help="If the field is new is set to False, the unit is considered used.")
    contract_type_id = fields.Many2one('contract.type', string='Contract Type', required=True,
                                       default=_get_default_contract_type)
    city_id = fields.Many2one('rem.unit.city', string='City', select=True)
    price = fields.Float(string='Price', digits=(16, 2), required=True)
    points_interest = fields.Many2many(
        'location.preferences', string="Points of Interest")

    # Indoor Features

    area = fields.Integer(string='Area', default=0, required=True)
    air_conditioned = fields.Boolean(string="Air Conditioned")
    ducted_cooling = fields.Boolean(string="Ducted Cooling")
    wardrobes = fields.Boolean(string="Built-in Wardrobes")
    dishwasher = fields.Boolean(string="Dishwasher")
    living_areas = fields.Integer('Living Areas')

    # Outdoor Features
    garages = fields.Integer(
        string='Garage Spaces', default=0, required=True, help="Number of garage spaces")
    backyard = fields.Boolean(string="Backyard")
    dog_friendly = fields.Boolean(string="Dog Friendly")
    secure_parking = fields.Boolean(string="Secure Parking")
    alarm = fields.Boolean(string="Alarm System")
    sw_pool = fields.Boolean(string="Swimming Pool")
    entertaining = fields.Boolean(string="Outdoor Entertaining Area")
