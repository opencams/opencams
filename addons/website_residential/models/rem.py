# -*- coding: utf-8 -*-
import json
from odoo import tools, api, fields, models, _


class RemUnit(models.Model):
    _inherit = 'rem.unit'
    _name = 'rem.unit'
    _description = 'Real Estate Unit'

    @api.multi
    def _compute_website_url(self):
        super(RemUnit, self)._compute_website_url()
        for unit in self:
            unit.website_url = "/rem/unit/%s" % (unit.id,)