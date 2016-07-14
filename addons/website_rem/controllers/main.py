# -*- coding: utf-8 -*-
import openerp
import werkzeug
from openerp import http
from openerp.http import request

PPG = 8  # Units Per Page


class WebsiteRem(http.Controller):

    @http.route(['/page/homepage'], type='http', auth='public', website=True)
    def homepage(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        contracts_type_obj = pool.get('contract.type')
        contracts_type_ids = contracts_type_obj.search(cr, uid, [], context=context)
        contracts_type = contracts_type_obj.browse(cr, uid, contracts_type_ids, context=context)

        units_types_obj = pool.get('rem.unit.type')
        units_types_ids = units_types_obj.search(cr, uid, [], context=context)
        units_types = units_types_obj.browse(cr, uid, units_types_ids, context=context)

        try:
            selected_contract_type = contracts_type[0].id
        except ValueError:
            selected_contract_type = 0

        values = {
            'contracts_type': contracts_type,
            'units_types': units_types,
            'selected_contract_type': selected_contract_type,
        }

        return request.website.render('website_rem.homepage_rem', values)

    @http.route(['/rem',
                 '/rem/page/<int:page>'], type='http', auth='public', website=True)
    def rem(self, page=0, contract_type=0, unit_type=0, states_cities_zones='', min_beds=0, max_beds=0, min_price='0', max_price='0', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        domain = []

        # Query contract type
        try:
            contract_type = int(contract_type)
            domain += [('contract_type_id.id', '=', contract_type)]
        except ValueError:
            contract_type=0

        # Query unit type
        try:
            unit_type = int(unit_type)
            domain += [('type_id.id', '=', unit_type)]
        except ValueError:
            unit_type=0

        # Bedrooms
        try:
            min_beds = int(min_beds)
        except ValueError:
            min_beds=0

        try:
            max_beds = int(max_beds)
        except ValueError:
            max_beds=0

        # Switch min to max and vice-versa if min > max
        if min_beds > 0 and max_beds > 0 and min_beds > max_beds:
            temp = max_beds
            max_beds = min_beds
            min_beds = temp

        # Query bedrooms
        if min_beds > 0:
            domain += [('bedrooms', '>=', min_beds)]

        if max_beds > 0:
            domain += [('bedrooms', '<=', max_beds)]

        # Price
        try:
            min_price = int(min_price.replace(',', ''))
        except ValueError:
            min_price=0

        try:
            max_price = int(max_price.replace(',', ''))
        except ValueError:
            max_price=0

        # Switch min to max and vice-versa if min > max
        if min_price > 0 and max_price > 0 and min_price > max_price:
            temp = max_price
            max_price = min_price
            min_price = temp

        # Query price
        if min_price > 0:
            domain += [('price', '>=', min_price)]

        if max_price > 0:
            domain += [('price', '<=', max_price)]

        # Query state, city and zone
        if states_cities_zones:
            for state_citie_zone in states_cities_zones.split(' '):
                domain += ['|', '|',
                           ('state_id.name', 'ilike', state_citie_zone),
                           ('city_id.name', 'ilike', state_citie_zone),
                           ('zone_id.name', 'ilike', state_citie_zone)]

        url = '/rem'

        units_obj = pool.get('rem.unit')
        units_count = units_obj.search_count(cr, uid, domain, context=context)
        pager = request.website.pager(url=url, total=units_count, page=page, step=PPG, scope=7, url_args=post)
        unit_ids = units_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], context=context)
        units = units_obj.browse(cr, uid, unit_ids, context=context)

        contracts_type_obj = pool.get('contract.type')
        contracts_type_ids = contracts_type_obj.search(cr, uid, [], context=context)
        contracts_type = contracts_type_obj.browse(cr, uid, contracts_type_ids, context=context)

        units_types_obj = pool.get('rem.unit.type')
        units_types_ids = units_types_obj.search(cr, uid, [], context=context)
        units_types = units_types_obj.browse(cr, uid, units_types_ids, context=context)

        try:
            if contract_type > 0:
                selected_contract_type = contract_type
            else:
                selected_contract_type = contracts_type[0].id
        except ValueError:
            selected_contract_type = 0

        values = {
            'units': units,
            'contracts_type': contracts_type,
            'units_types': units_types,
            'pager': pager,
            'result_contract_type': contract_type,
            'result_unit_type': unit_type,
            'result_states_cities_zones': states_cities_zones,
            'result_min_beds': min_beds,
            'result_max_beds': max_beds,
            'result_min_price': str(min_price),
            'result_max_price': str(max_price),
            'selected_contract_type': selected_contract_type,
        }

        return request.website.render('website_rem.rem_units_list_page', values)

    @http.route(['/rem/unit/<model("rem.unit"):unit>'], type='http', auth='public', website=True)
    def unit(self, unit):

        values = {
            'unit': unit
        }

        return request.website.render('website_rem.rem_unit_page', values)


class WebsiteContact(openerp.addons.web.controllers.main.Home):

    @http.route(['/contact-us'], type='http', auth='public', website=True)
    def website_rem_contact(self):
        return request.website.render('website_rem.contact_us_page')

    @http.route(['/page/contactus'], type='http', auth='none')
    def website_contact(self):
        return werkzeug.utils.redirect('/contact-us', 303)