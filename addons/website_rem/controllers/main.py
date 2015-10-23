# -*- coding: utf-8 -*-

import werkzeug
import openerp

from openerp import SUPERUSER_ID
from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug

PPG = 20 # Products Per Page

class website_rem(http.Controller):

    @http.route(['/rem', '/rem/page/<int:page>'], type='http', auth="public", website=True)
    def rem(self, page=0, type='', is_new='', beds=0, baths=0, min_price=0, max_price=0, search='', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        domain = []

        # Query type
        try:
            type = int(type)
            domain += [('contract_type_id.id', '=', type)]
        except ValueError:
            pass

        # Query is_new
        try:
            is_new = int(is_new)
            if (is_new == 0 or is_new == 1):
                domain += [('is_new', '=', is_new)]
        except ValueError:
            pass

        # Query bedrooms
        try:
            beds = int(beds)
            if (beds >= 1 and beds <= 10):
                domain += [('bedrooms', '=', beds)]
        except ValueError:
            pass

        # Query bathrooms
        try:
            baths = int(baths)
            if (baths >= 1 and baths <= 10):
                domain += [('bathrooms', '=', baths)]
        except ValueError:
            pass

        # Query price
        try:
            min_price = int(min_price)
            if (min_price > 0):
                domain += [('price', '>=', min_price)]
        except ValueError:
            pass

        try:
            max_price = int(max_price)
            if (max_price > 0):
                domain += [('price', '<=', max_price)]
        except ValueError:
            pass

        # Query name
        if search:
            for srch in search.split(" "):
                domain += [('name', 'ilike', srch)]
                # domain += [
                #     '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                #     ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]

        url = "/rem"

        units_obj = pool.get('rem.unit')
        units_count = units_obj.search_count(cr, uid, domain, context=context)
        pager = request.website.pager(url=url, total=units_count, page=page, step=PPG, scope=7, url_args=post)
        unit_ids = units_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], context=context)
        units = units_obj.browse(cr, uid, unit_ids, context=context)

        types_obj = pool.get('rem.unit.type')
        type_ids = types_obj.search(cr, uid, [], context=context)
        types = types_obj.browse(cr, uid, type_ids, context=context)

        values = {
            'units': units,
            'types': types,
            'pager': pager,
            'search_type': type,
            'search_is_new': is_new,
            'search_beds': beds,
            'search_baths': baths,
            'search_min_price': min_price,
            'search_max_price': max_price,
            'search': search
        }

        return request.website.render("website_rem.rem_list_page", values)

    @http.route(['/rem/unit/<model("rem.unit"):unit>'], type='http', auth="public", website=True)
    def unit(self, unit, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        values = {
            'unit': unit
        }

        return request.website.render("website_rem.rem_unit_page", values)