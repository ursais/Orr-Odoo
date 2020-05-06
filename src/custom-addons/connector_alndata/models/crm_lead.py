# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import threading
import logging
import requests
import json
import base64

from odoo import api, fields, models, _, sql_db
from odoo.exceptions import RedirectWarning
from numpy import fv

_logger = logging.getLogger(__name__)

us_timezone = {
    'M': 'US/Mountain',
    'C': 'US/Central',
    'E': 'US/Eastern',
    'P': 'US/Pacific',
    'H': 'US/Hawaii',
}


class Lead(models.Model):
    _inherit = "crm.lead"

    lastdate_changed = fields.Datetime('LastDateChanged')
    industry_id = fields.Many2one('res.partner.industry', 'Market')
    lead_type = fields.Selection(
        [('owner', 'Owner'),
         ('management_company', 'Management Company'),
         ('contact', 'Contact'),
         ('new_construction', 'New Constructions')],
        'Lead Type')

    def aln_auth_login(self, data_key='', data_params=None):
        """Aln Connector.

        This method is used to connect with ALN and fetch the data.
        """
        config_obj = self.env['ir.config_parameter']
        url = config_obj.get_param('alndata.api.url')
        api_key = config_obj.get_param('alndata.api.key')
        full_content = []

        url = url + data_key
        count = 0
        flag = True
        params = {
            'apikey': api_key,
            'Accept': 'application/json',
        }
        _logger.info('ALN Data Connector Data Key: %s', data_key)
        if not data_params:
            data_params = {}
        params.update(data_params)

        # use count to fetch all data related filter by multiple request
        while flag:
            try:
                if count > 0:
                    params.update({'$skip': count})
                response = requests.get(url, params=params)
                response.raise_for_status()
            except Exception as e:
                _logger.error('%s', e)
            content = response.content.decode('utf8')
            if content:
                content = json.loads(content).get('value')
                if len(content or []) > 0:
                    count += len(content)
                    full_content += content
                else:
                    flag = False
                    count = 0
        _logger.info('ALN Data Connector. Number of records: %s',
                     len(full_content))
        return full_content or []

    def remove_data(self, model, datas, origin=''):
        """Removed Data.

        This method is used to removed data from odoo database.
        which deleted from ALN Data.
        """
        obj = self.env[model]
        removed_ids = []
        rem = obj
        domain = []
        if model == 'res.partner':
            domain += [('partner_type', '=', origin)]
        elif origin and model == 'crm.lead':
            domain += [('lead_type', '=', origin)]
        for rec in obj.search(domain):
            if model == 'crm.lead' and rec.referred not in datas:
                removed_ids.append(rec.id)
                rem += rec
            elif model in ['res.partner', 'fsm.location'] and \
                    rec.ref not in datas:
                removed_ids.append(rec.id)
                rem += rec
        rem.write({'active': False})
        return removed_ids

    def get_state(self, obj, state_code):
        """State.

        This method is used to search state from state code.
        """
        return obj.search([('code', '=', state_code)], limit=1)

    def get_market(self, obj, market):
        """Market/Submarket.

        This method is used to search market or submarket base on name.
        """
        return obj.search([('name', '=', market)], limit=1)

    @api.model
    def _prepare_industry_values(self, industry=None, origin='market'):
        if not industry:
            return {}
        values = {
            'name': industry.get('MarketId'),
            'full_name': industry.get('MarketDescription'),
        }
        if origin == 'submarket':
            values.update({
                'name': industry.get('SubMarketDescription'),
                'ref': industry.get('SubmarketId'),
            })
        return values

    @api.model
    def sync_market_data(self):
        """Synchronize Market Data.

        This method is used to sync market data.
        """
        industry_obj = self.env['res.partner.industry']
        market_ids = []
        updated_market_ids = []
        markets = self.aln_auth_login('Markets')
        for market in markets:
            available_market = self.get_market(industry_obj,
                                               market.get('MarketId'))
            market_vals = self._prepare_industry_values(market)
            if available_market:
                available_market.write(market_vals)
                updated_market_ids.append(available_market.id)
            else:
                market = industry_obj.create(market_vals)
                market_ids.append(market.id)
        _logger.info('ALN Data Connector.Created Market Ids : %s', market_ids)
        _logger.info('ALN Data Connector.Updated Market Ids : %s',
                     updated_market_ids)

    @api.model
    def sync_submarket_data(self):
        """Synchronize Submarket Data.

        This method is used to sync submarket data.
        """
        industry_obj = self.env['res.partner.industry']
        submarket_ids = []
        updated_submarket_ids = []
        for submarket in self.aln_auth_login('Submarkets'):
            available_submarket = self.get_market(
                industry_obj, submarket.get('SubMarketDescription'))
            market_id = self.get_market(industry_obj,
                                        submarket.get('Market'))
            submarket_vals = self._prepare_industry_values(
                submarket, 'submarket')
            if market_id:
                submarket_vals.update({
                    'parent_id': market_id.id})
            if not available_submarket:
                submarket = industry_obj.create(submarket_vals)
                submarket_ids.append(submarket.id)
            else:
                available_submarket.write(submarket_vals)
                updated_submarket_ids.append(available_submarket.id)
        _logger.info(
            'ALN Data Connector.Created SubMarket Ids : %s', submarket_ids)
        _logger.info('ALN Data Connector.Updated SubMarket Ids : %s',
                     updated_submarket_ids)

    @api.model
    def sync_status_code_data(self):
        """Synchronize Status Codes Data.

        This method is used to sync status code data.
        """
        status_obj = self.env['fsm.stage']
        stage_ids = []
        for state in self.aln_auth_login('StatusCodes'):
            available_state = self.get_market(status_obj,
                                              state.get('StatusDescription'))
            if not available_state:
                state_vals = {
                    'name': state.get('StatusDescription'),
                    'stage_type': 'location',
                    'sequence': state.get('Status'),
                }
                state = status_obj.create(state_vals)
                stage_ids.append(state.id)
        _logger.info(
            'ALN Data Connector.Created FSM Stage Ids : %s', stage_ids)

    @api.model
    def get_title(self, obj, title):
        """Get Title.

        This method is used to get title from odoo database
        if it is not exist then create a title.
        """
        title_id = obj.search([('name', '=', title)], limit=1)
        if not title_id:
            title_id = obj.create({'name': title})
        return title_id.id

    def write_feed(self, feed_vals):
        "This method will create ALN Feed record"
        aln_feed_obj = self.env['aln.feed']
        if feed_vals:
            aln_feed_obj.create(feed_vals)
        return

    # update results on the logger
    def update_results(self, 
                       new_lead_ids=False,
                       updated_lead_ids=False,
                       new_partner_ids=False,
                       updated_partner_ids=False,
                       new_location_ids=False,
                       updated_location_ids = False,
                       rowversion_list=False,
                       message=''):

        config_obj = self.env['ir.config_parameter']

        row_version = rowversion_list and max(rowversion_list) or 0

        # update system parameters at the end of the run
        if row_version:
            config_obj.sudo().set_param(
                'alndata.managementcompanies.rowversion', row_version)

        if new_lead_ids and len(new_lead_ids):
            _logger.info('ALN Data Connector.Created %s Leads : %d',
                        message, len(new_lead_ids))
        if updated_lead_ids and len(updated_lead_ids):
            _logger.info('ALN Data Connector.Updated %s Leads : %d',
                        message, len(updated_lead_ids))
        if new_partner_ids and len(new_partner_ids):
            _logger.info('ALN Data Connector.Created %s Partners : %d',
                        message, len(new_partner_ids))
        if updated_partner_ids and len(updated_partner_ids):
            _logger.info('ALN Data Connector.Updated %s Partners : %d',
                        message, len(updated_partner_ids))
        if new_location_ids and len(new_location_ids):
            _logger.info('ALN Data Connector.Created %s Locatons : %d',
                        message, len(new_location_ids))
        if updated_location_ids and len(updated_location_ids):
            _logger.info('ALN Data Connector.Updated %s Locations : %d',
                        message, len(updated_location_ids))

    # synchronize owners
    def sync_owners(self):

        lead_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']
        state_obj = self.env['res.country.state']
        new_partner_ids = []
        new_lead_ids = []
        updated_partner_ids = []
        updated_lead_ids = []

        # read record from ALN
        datas = self.aln_auth_login('Owners')

        for data in datas:

            address = data.get('OwnerAddress', '')
            address_lst = address and address.split('\r\n') or []
            street = city = state_code = owner_zip = ''
            if len(address_lst) > 1:
                street = address_lst[0]
                city_state = address_lst[1].split(',')
                if len(city_state) > 1:
                    city = city_state[0]
                    state_zip = (city_state[1].strip()).split(' ')
                    if len(state_zip) > 1:
                        state_code = state_zip[0]
                        owner_zip = state_zip[1]
            state = self.get_state(state_obj, state_code)

            # create lead values dict
            lead_vals = {}
            lead_vals.update({
                'name': data.get('OwnerName'),
                'lead_type': 'owner',
                'lastdate_changed': False,
                'referred':  data.get('OwnerId'),
                'street': street,
                'city': city,
                'state_id': state.id,
                'zip': owner_zip,
                'country_id': state.country_id.id,
                'phone': data.get('OwnerPhone'),
                'contact_name': data.get('OwnerName')
            })

            # create partner values dict
            partner_vals = {}
            partner_vals.update({
                'name': data.get('OwnerName'),
                'partner_type': 'owner',
                'ref':  data.get('OwnerId'),
                'street': street,
                'city': city,
                'state_id': state.id,
                'zip': owner_zip,
                'country_id': state.country_id.id,
                'phone': data.get('OwnerPhone'),
            })

            # check to see if owner exists as lead and partner
            lead_domain = [('referred','=', data.get('OwnerId'))]
            partner_domain = [('ref','=',data.get('OwnerId'))]

            lead_rec = lead_obj.search(lead_domain)
            partner_rec = partner_obj.search(partner_domain)

            # create/update lead and partner
            if partner_rec:
                partner_rec.write(partner_vals)
                updated_partner_ids.append(partner_rec.id)
                # Create ALN Feed status update
                self.write_feed({
                    'partner_id': partner_rec.id,
                    'status': 'update',
                    'note': 'Sync Owners',
                    'raw_aln_feed': data
                })
            else:
                partner_id = partner_obj.create(partner_vals)
                new_partner_ids.append(partner_id.id)
                lead_vals['partner_id'] = partner_id.id
                # Create ALN Feed status create
                self.write_feed({
                    'partner_id': partner_id.id,
                    'status': 'create',
                    'note': 'Sync Owners',
                    'raw_aln_feed': data
                })

            if lead_rec:
                lead_rec.write(lead_vals)
                updated_lead_ids.append(lead_rec.id)
            else:
                lead_id = lead_obj.create(lead_vals)
                new_lead_ids.append(lead_id.id)

        self.update_results(new_lead_ids = new_lead_ids, 
                            updated_lead_ids = updated_lead_ids, 
                            new_partner_ids = new_partner_ids, 
                            updated_partner_ids = updated_partner_ids, 
                            rowversion_list=False,
                            message='Owner')

    # synchronize management companies
    def sync_management_companies(self):
        config_obj = self.env['ir.config_parameter']
        lead_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']
        industry_obj = self.env['res.partner.industry']
        new_partner_ids = []
        new_lead_ids = []
        updated_partner_ids = []
        updated_lead_ids = []
        rowversion_list = []

        params={}

        management_company_key = config_obj.get_param(
            'alndata.managementcompanies.rowversion')
        params.update({'$expand': 'Addresses,PhoneNumbers'})
        if management_company_key != '0':
            params.update(
                {'$filter': 'RowVersion gt ' + management_company_key,
                 '$orderby': 'RowVersion'})

        datas = self.aln_auth_login(
            'ManagementCompanies', params)

        for data in datas:

            name = data.get('ManagementCompanyName')
            rowversion = int(data.get('RowVersion', 0))
            rowversion_list.append(rowversion)
            last_changed = data.get('ManagementCompanyLastDateChanged')
            referred = data.get('ManagementCompanyEntityId')
            parent = data.get('ManagementCompanyParentId')
            lead_type = 'management_company'
            website = data.get('ManagementCompanyWebSite')
            market = self.get_market(
                industry_obj, data.get('ManagementCompanyMarket'))

            # create lead values dict
            lead_vals = {}
            lead_vals.update({
                'name':name,
                'lead_type':lead_type,
                'lastdate_changed':last_changed,
                'referred':referred
            })

            # create partner values dict
            partner_vals = {}
            partner_vals.update({
                'name': name,
                'partner_type': lead_type,
                'ref': referred,
                'website': website,
                'industry_id': market.id
            })

            addresses = data.get('Addresses')
            phonenumbers = data.get('PhoneNumbers')
            partner_vals = self.get_addresses(partner_vals, addresses)
            partner_vals = self.get_phonenumbers(partner_vals, phonenumbers)

            # check to see if owner exists as lead and partner
            lead_domain = [('referred','=', referred)]
            lead_rec = lead_obj.search(lead_domain)

            partner_domain = [('ref','=',referred)]
            partner_rec = partner_obj.search(partner_domain)

            if parent:
                parent_domain=[('ref','=', parent)]            
                parent_partner_rec = partner_obj.search(parent_domain)
                if parent_partner_rec:
                    partner_vals['parent_id'] = parent_partner_rec.id
                    updated_partner_ids.append(parent_partner_rec.id)
                else:
                    parent_id = partner_obj.create({
                        'name': parent,
                        'ref': parent,
                    })
                    partner_vals['parent_id'] = parent_id.id
                    new_partner_ids.append(parent_id.id)

            # create/update lead and partner
            if partner_rec:
                partner_rec.write(partner_vals)
                updated_partner_ids.append(partner_rec.id)
                # Create ALN Feed status update
                self.write_feed({
                    'partner_id': partner_rec.id,
                    'status': 'update',
                    'note': 'Sync Management Comp.',
                    'raw_aln_feed': data
                })

            else:
                partner_id = partner_obj.create(partner_vals)
                new_partner_ids.append(partner_id.id)
                lead_vals['partner_id'] = partner_id.id
                # Create ALN Feed status create
                self.write_feed({
                    'partner_id': partner_id.id,
                    'status': 'create',
                    'note': 'Sync Management Comp.',
                    'raw_aln_feed': data
                })

            if lead_rec:
                lead_rec.write(lead_vals)
                updated_lead_ids.append(lead_rec.id)
            else:
                lead_id = lead_obj.create(lead_vals)
                new_lead_ids.append(lead_id.id)

        self.update_results(new_lead_ids = new_lead_ids, 
                            updated_lead_ids = updated_lead_ids, 
                            new_partner_ids = new_partner_ids, 
                            updated_partner_ids = updated_partner_ids, 
                            rowversion_list=rowversion_list,
                            message='Management Company')

    # synchronize new constructions
    def sync_construction(self):
        config_obj = self.env['ir.config_parameter']
        lead_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']
        state_obj = self.env['res.country.state']
        new_partner_ids = []
        new_lead_ids = []
        updated_partner_ids = []
        updated_lead_ids = []

        params={}
        last_update_date=[]

        construction_key = config_obj.get_param(
            'alndata.newconstructions.rowversion')
        if construction_key != '0':
            params.update(
                {'$filter': "LastDateNewConstructionChanged gt datetime'" +
                    construction_key + "'",
                    '$orderby': "LastDateNewConstructionChanged"})
        datas = self.aln_auth_login('NewConstructions', params)

        for data in datas:

            lead_type = "new_construction"
            name = data.get('ProjectName')
            referred = data.get('NewConstructionId')
            last_changed = data.get('LastDateNewConstructionChanged')
            apartment = data.get('ApartmentId')
            state = self.get_state(state_obj, data.get('ProjectState'))
            description = ''
            if data.get('StartDate'):
                description += "Start Date : " + data.get('StartDate')
            if data.get('LeaseDate'):
                description += "\n" + "Lease Date : " + \
                    data.get('LeaseDate')
            if data.get('OccupancyDate'):
                description += "\n" + "Occupancy Date : " + \
                    data.get('OccupancyDate')
            if data.get('CompletionDate'):
                description += "\n" + "Completion Date : " + \
                    data.get('CompletionDate')
            if data.get('Progress'):
                description += "\n" + "Progress : " + data.get('Progress')
            if data.get('Market'):
                description += "\n" + "Market : " + data.get('Market')

            if last_changed:
                last_update_date.append(last_changed)

            # create lead values dict
            lead_vals = {}
            lead_vals.update({
                'name': name,
                'lead_type': lead_type,
                'lastdate_changed': last_changed,
                'referred': referred,
                'street': data.get('ProjectAddress'),
                'city': data.get('ProjectCity'),
                'state_id': state.id,
                'country_id': state.country_id.id,
                'zip': data.get('ProjectZIP'),
                'partner_name': data.get('Company'),
                'description': description,
            })

            # create partner values dict
            partner_vals = {}
            partner_vals.update({
                'name': name,
                'partner_type': lead_type,
                'ref': referred,
                'street': data.get('ProjectAddress'),
                'city': data.get('ProjectCity'),
                'state_id': state.id,
                'country_id': state.country_id.id,
                'zip': data.get('ProjectZIP'),
                'comment': description,
            })

            # check to see if owner exists as lead and partner
            lead_domain = [('referred','=', referred)]
            lead_rec = lead_obj.search(lead_domain)

            partner_domain = [('ref','=',referred)]
            partner_rec = partner_obj.search(partner_domain)

            if apartment:
                apartment_domain=[('ref','=', apartment)]            
                apartment_partner_rec = partner_obj.search(apartment_domain)
                if apartment_partner_rec:
                    partner_vals['associated_id'] = apartment_partner_rec.id
                    updated_partner_ids.append(apartment_partner_rec.id)
                else:
                    apartment_id = partner_obj.create({
                        'name': apartment,
                        'ref': apartment,
                    })
                    partner_vals['associated_id'] = apartment_id.id
                    new_partner_ids.append(apartment_id.id)

            # create/update lead and partner
            if partner_rec:
                partner_rec.write(partner_vals)
                updated_partner_ids.append(partner_rec.id)
                # Create ALN Feed status update
                self.write_feed({
                    'partner_id': partner_rec.id,
                    'status': 'update',
                    'note': 'Sync Construction',
                    'raw_aln_feed': data
                })
            else:
                partner_id = partner_obj.create(partner_vals)
                new_partner_ids.append(partner_id.id)
                lead_vals['partner_id'] = partner_id.id
                # Create ALN Feed status create
                self.write_feed({
                    'partner_id': partner_id.id,
                    'status': 'create',
                    'note': 'Sync Construction',
                    'raw_aln_feed': data
                })

            if lead_rec:
                lead_rec.write(lead_vals)
                updated_lead_ids.append(lead_rec.id)
            else:
                lead_id = lead_obj.create(lead_vals)
                new_lead_ids.append(lead_id.id)

        self.update_results(new_lead_ids = new_lead_ids, 
                            updated_lead_ids = updated_lead_ids, 
                            new_partner_ids = new_partner_ids, 
                            updated_partner_ids = updated_partner_ids, 
                            rowversion_list=last_update_date,
                            message='New Construction')

    # synchronize contacts
    def sync_contacts(self):
        config_obj = self.env['ir.config_parameter']
        lead_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']
        new_partner_ids = []
        new_lead_ids = []
        updated_partner_ids = []
        updated_lead_ids = []

        res_partner_title_obj = self.env['res.partner.title']
        params={}
        rowversion_list=[]
        last_update_date=[]

        contact_key = config_obj.get_param('alndata.contacts.rowversion')
        params.update({'$expand': 'Addresses,PhoneNumbers,JobCategories'})
        if contact_key != '0':
            params.update({'$filter': 'RowVersion gt ' + contact_key,
                            '$orderby': 'RowVersion'})
        datas = self.aln_auth_login('Contacts', params)

        for data in datas:
            lead_type = 'contact'
            name = data.get('ContactName')
            last_changed = data.get('ContactLastDateChanged')
            referred = data.get('ContactId')
            email = data.get('ContactEMail')
            company = data.get('ContactCompanyOrProperty')
            apartment = data.get('AssociatedEntity')
            corporate = data.get('CorporateEntityId')
            title = data.get('ContactTitle')
            rowversion = int(data.get('RowVersion', 0))
            rowversion_list.append(rowversion)

            # create lead values dict
            lead_vals = {}
            lead_vals.update({
                'lead_type': lead_type,
                'email_from': email,
                'partner_name': company,
                'lastdate_changed': last_changed,
                'contact_name': name,
                'title': self.get_title(res_partner_title_obj,
                                        title),
            })

            # create partner values dict
            partner_vals = {}
            partner_vals.update({
                'name': name,
                'partner_type': lead_type,
                'ref': referred,
                'title': self.get_title(res_partner_title_obj,
                                        title),
            })

            # check to see if owner exists as lead and partner
            lead_domain = [('referred','=', corporate)]
            lead_rec = lead_obj.search(lead_domain)

            partner_domain = [('ref','=',referred)]
            partner_rec = partner_obj.search(partner_domain)

            if corporate:
                company_domain=[('ref','=', corporate)]            
                company_partner_rec = partner_obj.search(company_domain)
                if company_partner_rec:
                    partner_vals['parent_id'] = company_partner_rec.id
                    updated_partner_ids.append(company_partner_rec.id)
                else:
                    parent_id = partner_obj.create({
                        'name': company,
                        'ref': company,
                    })
                    partner_vals['parent_id'] = parent_id.id
                    new_partner_ids.append(parent_id.id)
            apartment_id = False
            if apartment:
                apartment_domain=[('ref','=', apartment)]
                apartment_partner_rec = partner_obj.search(apartment_domain)
                if apartment_partner_rec:
                    partner_vals['associated_id'] = apartment_partner_rec.id
                    updated_partner_ids.append(apartment_partner_rec.id)
                else:
                    apartment_id = partner_obj.create({
                        'name': apartment,
                        'ref': apartment,
                    })
                    partner_vals['associated_id'] = apartment_id.id
                    new_partner_ids.append(apartment_id.id)

            # create/update lead and partner
            if partner_rec:
                partner_rec.write(partner_vals)
                updated_partner_ids.append(partner_rec.id)
                # Create ALN Feed status update
                self.write_feed({
                    'partner_id': partner_rec.id,
                    'status': 'update',
                    'note': 'Sync Contacts',
                    'raw_aln_feed': data
                })
            else:
                partner_id = partner_obj.create(partner_vals)
                new_partner_ids.append(partner_id.id)
                lead_vals['partner_id'] = partner_id.id
                # Create ALN Feed status create
                self.write_feed({
                    'partner_id': partner_id.id,
                    'status': 'create',
                    'note': 'Sync Contacts',
                    'raw_aln_feed': data
                })
            if apartment_id and data.get('AssociatedEntity'):
               apartment_id.prop_mgr_id = partner_rec.id or partner_id.id
            if lead_rec:
                lead_rec.write(lead_vals)
                updated_lead_ids.append(lead_rec.id)
            else:
                lead_id = lead_obj.create(lead_vals)
                new_lead_ids.append(lead_id.id)

        self.update_results(new_lead_ids = new_lead_ids, 
                            updated_lead_ids = updated_lead_ids, 
                            new_partner_ids = new_partner_ids, 
                            updated_partner_ids = updated_partner_ids, 
                            rowversion_list=rowversion_list,
                            message='Contacts')

    def get_addresses(self, values, addresses):
        state_obj = self.env['res.country.state']
        if addresses:
            address = addresses[0]
            state = self.get_state(state_obj,
                                    address.get('AddressState'))
            country_id = state and state.country_id.id or 0
            values.update(
                {
                    'street': address.get('AddressLine1'),
                    'street2': address.get('AddressLine2'),
                    'city': address.get('AddressCity'),
                    'state_id': state.id,
                    'zip': address.get('AddressZIP'),
                    'country_id': country_id,
                })
        return values

    def get_phonenumbers(self, values, phonenumbers):
        if phonenumbers:
            numbers = phonenumbers
            for num in numbers:
                if num.get('IsPrimary') == 'Y':
                    values.update({
                        'phone': num.get('Number')
                    })
                if (num.get('PhoneNumberType') == "Fax Number"):
                    values.update({
                        'fax': num.get('Number')
                    })        
        return values
    @api.model
    def sync_apartment_data(self):
        """Synchronize Apartments Data.

        This method is used to synchronize apartment data.
        """

        aln_feed_obj = self.env['aln.feed']
        config_obj = self.env['ir.config_parameter']
        industry_obj = self.env['res.partner.industry']
        partner_obj = self.env['res.partner']
        stage_obj = self.env['fsm.stage']
        fsm_obj = self.env['fsm.location']
        new_location_ids = []
        updated_location_ids = []

        rowversion_list = []

        params = {'$expand': 'Addresses,PhoneNumbers'}
        apartment_key = config_obj.get_param(
            'alndata.apartments.rowversion')
        if apartment_key != '0':
            params.update({'$filter': 'RowVersion gt ' + apartment_key,
                           '$orderby': 'RowVersion'})

        datas = self.aln_auth_login('Apartments', params)

        for data in datas:

            values = {}
            addresses = data.get('Addresses')
            phonenumbers = data.get('PhoneNumbers')
            values = self.get_addresses(values, addresses)
            values = self.get_phonenumbers(values, phonenumbers)
            referred = data.get('ApartmentId')
            industry = False

            prop = data.get('Property')
            rowversion_list.append(int(data.get('RowVersion')))
            stage = stage_obj.search(
                [('sequence', '=', prop.get('Status')),
                 ('stage_type', '=', 'location')],
                limit=1)
            if prop.get('SubmarketId'):
                industry = industry_obj.search(
                    [('ref', '=', prop.get('SubmarketId'))],
                    limit=1)
                if not industry:
                    industry = self.get_market(
                        industry_obj, prop.get('Market'))

            image_data = b''
            if prop.get('AptPictureURL'):
                image_res = requests.get(prop.get('AptPictureURL'))
                image_data = image_res.content
            values.update({
                'ref': referred,
                'stage_id': stage.id,
                'name': prop.get('AptName'),
                'email': prop.get('EMailAddress'),
                'industry_id': industry and industry.id or False,
                'year_built': prop.get('YearBuilt'),
                'year_remodeled': prop.get('YearRemodeled'),
                'direction': prop.get('Directions'),
                'notes': prop.get('PropertyDescription'),
                'website': prop.get('AptHomePage'),
                'image': base64.b64encode(image_data),
                'tz': us_timezone.get(prop.get('TimeZone', '').strip(), ''),
            })

            if prop.get('CurrManager'):
                contact = partner_obj.search(
                    [('name', '=', prop.get('CurrManager')),
                     ('partner_type', '=', 'contact')],
                    limit=1)
                if not contact:
                    contact = partner_obj.create({
                        'name': prop.get('CurrManager'),
                        'ref': prop.get('CurrManager'),
                        'partner_type': 'contact',
                    })
                contact_id = contact.id

            management_company_id = False
            if prop.get('CorporateManagementCompanyId'):
                management_company = partner_obj.search(
                    [('ref', '=', prop.get('CorporateManagementCompanyId')),
                     ('partner_type', '=', 'management_company')],
                    limit=1)

                if not management_company:
                    management_company = partner_obj.create({
                        'name': prop.get('CorporateManagementCompanyId'),
                        'ref': prop.get('CorporateManagementCompanyId'),
                        'partner_type': 'management_company',
                    })
                management_company_id = management_company.id

                values.update(
                    {'commercial_partner_id': management_company_id})

#             owner_id = False
#             if prop.get('OwnerId'):
#                 owner = partner_obj.search(
#                     [('ref', '=', prop.get('OwnerId')),
#                      ('partner_type', '=', 'owner')],
#                     limit=1)
#                 if not owner:
#                     owner = partner_obj.create({
#                         'name': prop.get('OwnerId'),
#                         'ref': prop.get('OwnerId'),
#                         'partner_type': 'owner',
#                     })
# 
#                 owner_id = owner.id

            fsm_partner = partner_obj.search(
                [('ref','=', data.get('ApartmentId'))],
                limit=1)
            fsm_location = fsm_obj.search(
                [('ref', '=', data.get('ApartmentId'))],
                limit=1)
            geolocation = data.get('GeoLocation')
            if not fsm_partner:
                name = data.get('AptName') or data.get('ApartmentId')
                fsm_partner = partner_obj.create({
                    'name': name,
                    'ref': data.get('ApartmentId'),
                    'prop_mgmt_id': management_company_id,
                    'partner_latitude':geolocation and geolocation.get('GPSLatitude') or False,
                    'partner_longitude':geolocation and geolocation.get('GPSLongitude') or False,
                    'num_unit': prop.get('NumUnits'),
                })
                partner_id = fsm_partner.id
                self.write_feed({
                'partner_id': fsm_partner.id,
                'status': 'create',
                'note': 'Apartment Data',
                'raw_aln_feed': data
                })
            else:
                partner_id = fsm_partner.id
                fsm_partner.update({
                    'prop_mgmt_id': management_company_id,
                    'partner_latitude':geolocation and geolocation.get('GPSLatitude') or False,
                    'partner_longitude':geolocation and geolocation.get('GPSLongitude') or False,
                })                
                self.write_feed({
                    'partner_id': fsm_partner.id,
                    'status': 'update',
                    'note': 'Apartment Data',
                    'raw_aln_feed': data
                })
            values.update({'owner_id': partner_id,
                        'customer_id': partner_id or management_company_id or contact_id,
                        'partner_id': partner_id,
            })
            if not fsm_location:
                fsm = fsm_obj.create(values)
                new_location_ids.append(fsm.id)
            else:
                fsm_location.write(values)
                updated_location_ids.append(fsm_location.id)

        self.update_results(new_location_ids=new_location_ids, 
                            updated_location_ids=updated_location_ids, 
                            rowversion_list=rowversion_list,
                            message='Apartments')

    # synchronize router
    def synchronize_router(self, origin=''):
        ''' Main router that synchronizes data '''

        # step 1: Owners
        self.sync_owners()

        # step 2: Management Companies
        self.sync_management_companies()

        # step 3: New Construction
        self.sync_construction()

        # step 4: Contacts
        self.sync_contacts()

    @api.model
    def sync_aln_data_with_threading(self):
        """Synchronize data with ALN Data By Threading.

        This method is used to get data from ALN Data usinf threading.
        """
        _logger.info('ALN Data Connector. Starting the synchronization...')
        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with api.Environment.manage():
            self.env = api.Environment(new_cr, uid, context)
            # Get Market Data
            self.sync_market_data()

            # Get Sub-Market Data
            self.sync_submarket_data()

            # Synchronize Router
            self.synchronize_router()

            # Get the Apartment Data
            self.sync_apartment_data()

            new_cr.commit()
            new_cr.close()
        _logger.info('ALN Data Connector. Synchronization successful.')

    @api.model
    def _cron_sync_with_aln(self):
        """Synchronize data with ALN Data.

        This method is used to get data from ALN Data and create data in odoo.
        """
        api_key = self.env['ir.config_parameter'].get_param('alndata.api.key')
        if api_key == '0':
            action = self.env.ref('base.ir_config_list_action')
            msg = _('Cannot find a ALN Data URL and API key, '
                    'You should configure it. '
                    '\nPlease go to System Parameters.')
            raise RedirectWarning(msg, action.id,
                                  _('Go to the configuration panel'))
        thread_cal = threading.Thread(
            target=self.sync_aln_data_with_threading)
        thread_cal.start()
