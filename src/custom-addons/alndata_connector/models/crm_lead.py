# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import threading
import logging
import requests
import json
import datetime

from odoo import api, fields, models, _, sql_db
from odoo.exceptions import RedirectWarning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


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

    def aln_auth_login(self, data_key='', data_params=None, stop_count=1000):
        """Aln Connector.

        This method is used to connect with ALN and fetch the data.
        """
        config_obj = self.env['ir.config_parameter']
        url = config_obj.get_param('alndata.api.url')
        api_key = config_obj.get_param('alndata.api.key')
        full_content = []

        url = url + data_key
        count = 0
        read_count = 0
        result_flag = False

        if data_params:
            read_count = data_params.get('$skip', False)
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
                    params.update({'$skip': count + read_count})
                response = requests.get(url, params=params)
                response.raise_for_status()

                content = response.content.decode('utf8')
                if content:
                    content = json.loads(content).get('value')
                    if len(content) > 0:
                        full_content += content
                        if len(full_content) >= stop_count:
                            flag = False
                            count = 0
                            result_flag = True
                        else:
                            count += len(content)
                    else:
                        flag = False
                        count = 0

            except Exception as e:
                _logger.error('%s', e)

        _logger.info('ALN Data Connector. Data Key: %s, Number of records: %s',
                     data_key, len(full_content))
        # return full_content or []
        return result_flag, full_content or []

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
        params = {}

        read_count = 0
        stop_count = 2000
        flag = True
        while flag:
            # update with last counts
            params.update({'$skip': read_count})
            # Read aln records for contacts
            flag, markets = self.aln_auth_login('Markets', params, stop_count)
            read_count += len(markets)

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
        params = {}

        read_count = 0
        stop_count = 2000
        flag = True
        while flag:
            # update with last counts
            params.update({'$skip': read_count})
            # Read aln records for contacts
            flag, submarkets = self.aln_auth_login('Submarkets', params, stop_count)
            read_count += len(submarkets)

            for submarket in submarkets:
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

    # load owners
    def load_owners_data(self):
        params = {}
        flag = True
        flag_exc = False
        stop_count = 2000
        total_records = 0
        total_updated = 0
        read_count = 0

        # Get existing records
        self._cr.execute("""SELECT owner_id_txt, id FROM aln_owner""")
        ext_own_data = self._cr.fetchall()
        ext_data = dict(ext_own_data)

        while flag:
            # update with last counts
            params.update({'$skip': read_count})
            # Read aln records for owners
            flag, datas = self.aln_auth_login('Owners', params, stop_count)
            read_count += len(datas)

            owner_create = []
            owner_update = []
            for data in datas:
                # Prepare data
                create_vals = {
                    'name': data.get('OwnerName'),
                    'address': data.get('OwnerAddress', ''),
                    'phone': data.get('OwnerPhone'),
                }

                # Check if record already exist
                rec_ids = [k for k, v in enumerate(ext_data) if data.get('OwnerId') == v]
                if rec_ids:
                    update_vals = {}
                    update_vals.update({
                        'id': rec_ids[0]
                    }, **create_vals)
                    owner_update.append(update_vals)
                else:
                    # update create vals
                    create_vals.update({
                        'id': data.get('OwnerId'),
                        'own_state': 'unpublished'
                    })
                    owner_create.append(create_vals)

            # Create bulk records
            try:
                if owner_create:
                    own_create_query = """INSERT INTO aln_owner (owner_id_txt, owner_name, owner_address, owner_phone, own_state)
                                                 VALUES 
                                                     (%(id)s, %(name)s, %(address)s, %(phone)s, %(own_state)s)"""
                    self._cr.executemany(own_create_query, owner_create)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to insert ALN Owner: %s", str(e))

            # Update bulk records
            try:
                if owner_update:
                    own_update_query = """UPDATE aln_owner SET 
                                                        owner_name = %(name)s, owner_address = %(address)s, owner_phone = %(phone)s
                                                    WHERE
                                                        id = %(id)s"""
                    self._cr.executemany(own_update_query, owner_update)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to Update ALN Owner: %s", str(e))

            if not flag_exc:
                total_records += len(owner_create)
                total_updated += len(owner_update)
                _logger.info('***** Batch ALN Owner Successfully Created : %d  *****',
                             len(owner_create))
                _logger.info('***** Batch ALN Owner Successfully Updated : %d  *****',
                             len(owner_update))

        if not flag_exc:
            _logger.info(
                '------- ALN Owner Execution completed!  Total ALN Owner Successfully Created : %d and Updated: %d -------',
                total_records, total_updated)

    # load management companies
    def load_management_companies(self):
        params = {}
        flag_exc = False
        flag = True
        stop_count = 2000
        total_records = 0
        total_updated = 0
        read_count = 0
        config_obj = self.env['ir.config_parameter']
        industry_obj = self.env['res.partner.industry']

        # Get rowversion key from parameters
        management_company_key = config_obj.get_param(
            'alndata.managementcompanies.rowversion')
        params.update({'$expand': 'Addresses,PhoneNumbers'})
        if management_company_key != '0':
            params.update(
                {'$filter': 'RowVersion gt ' + management_company_key,
                 '$orderby': 'RowVersion'})

        # Get existing records
        self._cr.execute("""SELECT company_id_txt, id FROM aln_management_company""")
        ext_cmp_data = self._cr.fetchall()
        ext_data = dict(ext_cmp_data)

        while flag:
            # update with last counts
            params.update({'$skip': read_count})
            # Read aln records for contacts
            flag, datas = self.aln_auth_login('ManagementCompanies', params, stop_count)
            read_count += len(datas)

            management_comp_list = []
            cmp_update = []
            for data in datas:
                market = self.get_market(
                    industry_obj, data.get('ManagementCompanyMarket'))
                row = 0
                if data.get('RowVersion', False):
                    row = data.get('RowVersion')

                # Prepare data
                create_vals = {
                    'market': market and market.id or '',
                    'name': data.get('ManagementCompanyName'),
                    'website': data.get('ManagementCompanyWebSite'),
                    'date': data.get('ManagementCompanyLastDateChanged'),
                    'parent': data.get('ManagementCompanyParentId'),
                    'row': row
                }
                # Check if record already exist
                rec_ids = [k for k, v in enumerate(ext_data) if data.get('ManagementCompanyEntityId') == v]
                if rec_ids:
                    update_vals = {}
                    update_vals.update({
                        'id': rec_ids[0],
                    }, **create_vals)
                    cmp_update.append(update_vals)
                else:
                    create_vals.update({
                        'id': data.get('ManagementCompanyEntityId'),
                        'cmp_state': 'unpublished'
                    })
                    management_comp_list.append(create_vals)

            # Create bulk records
            try:
                query = """INSERT INTO aln_management_company
                                        (company_id_txt, company_market, company_name, company_website,
                                        cmp_last_changed_date, company_parent_id_txt , company_rowversion, cmp_state)
                                     VALUES 
                                         (%(id)s, %(market)s, %(name)s, %(website)s, 
                                         %(date)s, %(parent)s, %(row)s, %(cmp_state)s)"""
                self._cr.executemany(query, management_comp_list)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to insert ALN Management Companies: %s", str(e))

            # Update bulk records
            try:
                if cmp_update:
                    update_query = """UPDATE aln_management_company SET
                                                    company_market = %(market)s, company_name =  %(name)s,
                                                    company_website = %(website)s, cmp_last_changed_date = %(date)s,
                                                    company_parent_id_txt = %(parent)s, company_rowversion = %(row)s
                                                 WHERE
                                                    id = %(id)s
                                                     """
                    self._cr.executemany(update_query, cmp_update)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to insert ALN Management Companies: %s", str(e))

            if not flag_exc:
                total_records += len(management_comp_list)
                total_updated += len(cmp_update)
                _logger.info('***** Batch ALN Management Companies Successfully Created : %d  *****',
                             len(management_comp_list))
                _logger.info('***** Batch ALN Management Companies Successfully Updated : %d  *****',
                             len(cmp_update))

        if not flag_exc:
            _logger.info(
                '------- ALN Management Companies Execution completed!  Total ALN Management Companies Successfully Created : %d '
                'and Updated: %d -------',
                total_records, total_updated)

    # load constructions
    def load_construction(self):
        params = {}
        flag = True
        flag_exc = False
        stop_count = 2000
        total_records = 0
        total_updated = 0
        read_count = 0
        config_obj = self.env['ir.config_parameter']

        # Get rowversion key from parameters
        construction_key = config_obj.get_param(
            'alndata.newconstructions.rowversion')
        if construction_key != '0':
            params.update(
                {'$filter': "LastDateNewConstructionChanged gt datetime'" +
                            construction_key + "'",
                 '$orderby': "LastDateNewConstructionChanged"})

        # Get existing records
        self._cr.execute("""SELECT construction_id_txt, id FROM aln_new_construction""")
        ext_cmp_data = self._cr.fetchall()
        ext_data = dict(ext_cmp_data)

        while flag:
            # update with last counts
            params.update({'$skip': read_count})
            # Read aln records for constructions
            flag, datas = self.aln_auth_login('NewConstructions', params, stop_count)
            read_count += len(datas)

            construction_list = []
            const_update = []
            for data in datas:
                # Prepare data
                create_vals = {
                    'apt_id': data.get('ApartmentId'),
                    'last_date': data.get('LastDateNewConstructionChanged'),
                    'company': data.get('Company'),
                    'proj_name': data.get('ProjectName'),
                    'proj_address': data.get('ProjectAddress'),
                    'proj_city': data.get('ProjectCity'),
                    'proj_state': data.get('ProjectState'),
                    'proj_zip': data.get('ProjectZIP'),
                    'new_num_of_units': data.get('NumberOfUnits'),
                    'type': data.get('PropertyType'),
                    'status': data.get('NewConstructionStatus'),
                    'start_date': data.get('StartDate'),
                    'lease_date': data.get('LeaseDate'),
                    'occ_date': data.get('OccupancyDate'),
                    'comp_date': data.get('CompletionDate'),
                    'progress': data.get('Progress')
                }
                # Check if record already exist
                rec_ids = [k for k, v in enumerate(ext_data) if data.get('NewConstructionId') == v]
                if rec_ids:
                    update_vals = {}
                    update_vals.update({
                        'id': rec_ids[0]
                    }, **create_vals)
                    const_update.append(update_vals)
                else:
                    create_vals.update({
                        'id': data.get('NewConstructionId'),
                        'new_state': 'unpublished'
                    })
                    construction_list.append(create_vals)

            # Create bulk records
            try:
                query = """INSERT INTO aln_new_construction
                                        (construction_id_txt, new_apartment_id_txt, new_last_changed_date, company, project_name,
                                        project_address , project_city, project_state, project_zip, new_num_of_units, property_type,
                                        construction_status, start_date, lease_date, occupancy_date, completion_date, progress, new_state)
                                    VALUES 
                                     (%(id)s, %(apt_id)s, %(last_date)s, %(company)s, %(proj_name)s, %(proj_address)s, %(proj_city)s, %(proj_state)s, 
                                     %(proj_zip)s, %(new_num_of_units)s, %(type)s, %(status)s, %(start_date)s, %(lease_date)s, %(occ_date)s, %(comp_date)s,
                                     %(progress)s, %(new_state)s)"""
                self._cr.executemany(query, construction_list)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to insert ALN New Construction: %s", str(e))

            # Update bulk records
            try:
                if const_update:
                    update_query = """UPDATE aln_new_construction SET
                                                new_apartment_id_txt = %(apt_id)s, new_last_changed_date = %(last_date)s, company = %(company)s,
                                                project_name = %(proj_name)s, project_address = %(proj_address)s, project_city = %(proj_city)s,
                                                project_state = %(proj_state)s, project_zip = %(proj_zip)s, new_num_of_units = %(new_num_of_units)s,
                                                property_type = %(type)s, construction_status = %(status)s, start_date = %(start_date)s, lease_date =%(lease_date)s,
                                                occupancy_date = %(occ_date)s, completion_date = %(comp_date)s, progress = %(progress)s
                                             WHERE
                                                id = %(id)s """
                    self._cr.executemany(update_query, const_update)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to update ALN New Construction: %s", str(e))

            if not flag_exc:
                total_records += len(construction_list)
                total_updated += len(const_update)
                _logger.info('***** Batch ALN New Construction Successfully Created : %d  *****',
                             len(construction_list))
                _logger.info('***** Batch ALN New Construction Successfully Updated : %d  *****',
                             len(const_update))

        if not flag_exc:
            _logger.info(
                '------- ALN New Construction Execution completed!  Total ALN New Construction Successfully Created : %d  '
                'and Updated : %d -------',
                total_records, total_updated)

    # load contacts
    def load_contacts(self):
        params = {}
        flag = True
        flag_exc = False
        stop_count = 2000
        total_records = 0
        total_updated = 0
        read_count = 0
        config_obj = self.env['ir.config_parameter']

        # Get rowversion key from parameters
        contact_key = config_obj.get_param('alndata.contacts.rowversion')
        params.update({'$expand': 'Addresses,PhoneNumbers,JobCategories'})
        if contact_key != '0':
            params.update({'$filter': 'RowVersion gt ' + contact_key,
                           '$orderby': 'RowVersion'})

        # Get existing records
        self._cr.execute("""SELECT contact_id_txt, id FROM aln_contact""")
        ext_cmp_data = self._cr.fetchall()
        ext_data = dict(ext_cmp_data)

        while flag:
            # update with last counts
            params.update({'$skip': read_count})
            # Read aln records for contacts
            flag, datas = self.aln_auth_login('Contacts', params, stop_count)
            read_count += len(datas)

            contact_list = []
            contact_update = []
            for data in datas:
                row = 0
                if data.get('RowVersion', False):
                    row = data.get('RowVersion')

                # Prepare data
                create_vals = {
                    'name': data.get('ContactName'),
                    'title': data.get('ContactTitle'),
                    'email': data.get('ContactEMail'),
                    'company': data.get('ContactCompanyOrProperty'),
                    'date': data.get('ContactLastDateChanged'),
                    'assoc_id': data.get('AssociatedEntity'),
                    'corp_id': data.get('CorporateEntityId'),
                    'row': row
                }

                # Check if record already exist
                rec_ids = [k for k, v in enumerate(ext_data) if data.get('ContactId') == v]
                if rec_ids:
                    update_vals = {}
                    update_vals.update({
                        'id': rec_ids[0],
                    }, **create_vals)
                    contact_update.append(update_vals)
                else:
                    create_vals.update({
                        'id': data.get('ContactId'),
                        'cont_state': 'unpublished'
                    })
                    contact_list.append(create_vals)

            # Create bulk records
            try:
                query = """INSERT INTO aln_contact
                                             (contact_id_txt, contact_name, contact_title, contact_email,
                                             contact_company_property, cont_last_changed_date , associated_id_txt,
                                             corporate_id_txt, contact_rowversion, cont_state)
                                         VALUES 
                                             (
                                             %(id)s, %(name)s, %(title)s, %(email)s, %(company)s,
                                             %(date)s, %(assoc_id)s, %(corp_id)s, %(row)s, %(cont_state)s
                                         )"""
                self._cr.executemany(query, contact_list)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to insert ALN Contact: %s", str(e))

            # Update bulk records
            try:
                if contact_update:
                    update_query = """UPDATE aln_contact SET
                                             contact_name = %(name)s, contact_title = %(title)s, contact_email = %(email)s,
                                             contact_company_property = %(company)s, cont_last_changed_date = %(date)s,
                                             associated_id_txt = %(assoc_id)s, corporate_id_txt = %(corp_id)s, contact_rowversion = %(row)s
                                         WHERE
                                            id = %(id)s
                                         """
                    self._cr.executemany(update_query, contact_update)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to update ALN Contact: %s", str(e))

            if not flag_exc:
                total_records += len(contact_list)
                total_updated += len(contact_update)
                _logger.info('***** Batch ALN Contact Successfully Created : %d  *****',
                             len(contact_list))
                _logger.info('***** Batch ALN Contact Successfully Updated : %d  *****',
                             len(contact_update))

        if not flag_exc:
            _logger.info('------- ALN Contact Execution completed!  Total ALN Contact Successfully Created : %d  '
                         'and Updated : %d-------',
                         total_records, total_updated)

    @api.model
    def sync_apartment_data(self):
        """Load Apartments Data.

        This method is used to load apartment data.
        """
        total_records = 0
        total_updated = 0
        read_count = 0
        flag = True
        flag_exc = False
        stop_count = 1000
        partner_obj = self.env['res.partner']
        config_obj = self.env['ir.config_parameter']
        industry_obj = self.env['res.partner.industry']

        # Get rowversion key from parameters
        params = {'$expand': 'Addresses,PhoneNumbers'}
        apartment_key = config_obj.get_param(
            'alndata.apartments.rowversion')
        if apartment_key != '0':
            params.update({'$filter': 'RowVersion gt ' + apartment_key,
                           '$orderby': 'RowVersion'})

        # Get existing records
        self._cr.execute("""SELECT apartment_id_txt, id FROM aln_apartment""")
        ext_cmp_data = self._cr.fetchall()
        ext_data = dict(ext_cmp_data)

        while flag:
            # update with last counts
            params.update({'$skip': read_count})
            # read aln record for Apartment
            flag, datas = self.aln_auth_login('Apartments', params, stop_count)
            read_count += len(datas)

            apartment_list = []
            apartment_update = []
            for data in datas:
                # Fetch appropriate data set
                addresses = data.get('Addresses')
                phonenumbers = data.get('PhoneNumbers')
                referred = data.get('ApartmentId')
                prop = data.get('Property')
                geolocation = data.get('GeoLocation')

                submarket = reg_mng = crp_mng = sup = lud = lcd = lcontd = False
                # Get Submarket
                if prop.get('SubmarketId', False):
                    submarket = industry_obj.search(
                        [('ref', '=', prop.get('SubmarketId'))],
                        limit=1)
                    if not submarket:
                        submarket = industry_obj.search(
                            [('name', '=', prop.get('Market'))],
                            limit=1)
                # Get Regional Management Company
                if data.get('RegionalManagementCompanyId', False):
                    reg_mng = partner_obj.search([('ref', '=', data.get('RegionalManagementCompanyId'))], limit=1)
                # Get Corporate Management Company
                if data.get('CorporateManagementCompanyId', False):
                    crp_mng = partner_obj.search([('ref', '=', data.get('CorporateManagementCompanyId'))], limit=1)
                # Get Area Supervisor
                if data.get('AreaSupervisorId', False):
                    sup = partner_obj.search([('ref', '=', data.get('AreaSupervisorId'))], limit=1)

                # Reformat datetime to Odoo compatible
                if data.get('LastDateUpdated', False):
                    dt = data.get('LastDateUpdated').replace("T", " ")
                    lud = datetime.datetime.strptime(dt.split('.')[0], DEFAULT_SERVER_DATETIME_FORMAT)
                if data.get('LastDateChanged', False):
                    dt = data.get('LastDateChanged').replace("T", " ")
                    lcd = datetime.datetime.strptime(dt.split('.')[0], DEFAULT_SERVER_DATETIME_FORMAT)
                if data.get('LastDateContacted', False):
                    dt = data.get('LastDateContacted').replace("T", " ")
                    lcontd = datetime.datetime.strptime(dt.split('.')[0], DEFAULT_SERVER_DATETIME_FORMAT)

                values = {
                    'last_update_date': lud or None,
                    'apt_last_changed_date': lcd or None,
                    'last_contacted_date': lcontd or None,
                    'row_version': data.get('RowVersion'),
                    'aln_id_txt': prop.get('ALNId'),
                    'status': prop.get('Status'),
                    'apt_name': prop.get('AptName'),
                    'fka': prop.get('FKA'),
                    'hours': prop.get('Hours'),
                    'email': prop.get('EMailAddress'),
                    'market': prop.get('Market'),
                    'apt_owner_id_txt': prop.get('AptOwnerId'),
                    'submarket_id_txt': prop.get('SubmarketId'),
                    'num_of_units': prop.get('NumUnits'),
                    'year_built': prop.get('YearBuilt'),
                    'year_remodeled': prop.get('YearRemodeled'),
                    'timezone': prop.get('TimeZone'),
                    'occupancy': prop.get('Occupancy'),
                    'number_of_stories': prop.get('NumberOfStories'),
                    'directions': prop.get('Directions'),
                    'property_description': prop.get('PropertyDescription'),
                    'apt_homepage': prop.get('AptHomePage'),
                    'apt_picture_url': prop.get('AptPictureURL'),
                    'curr_manager': prop.get('CurrManager'),
                    'areasupervisor_id_txt': prop.get('AreaSupervisorId'),
                    'regional_management_company_id_txt': prop.get('RegionalManagementCompanyId'),
                    'corporate_management_company_id_txt': prop.get('CorporateManagementCompanyId'),
                    'owner_id_txt': prop.get('OwnerId'),
                    'views': prop.get('Views'),
                    'ac_heating': prop.get('ACHeating'),
                    'map_coordinates': prop.get('MapCoordinates'),
                    'other_notes': prop.get('OtherNotes'),
                    'average_rent': prop.get('AverageRent'),
                    'average_sqft': prop.get('AverageSqFt'),
                    'mkt_pct_rff_rentunit': prop.get('MktPctEffRentUnit'),
                    'mkt_pct_rff_rentsqft': prop.get('MktPctEffRentSqFt'),
                    'sub_mkt_pct_rff_rentunit': prop.get('SubMktPctEffRentUnit'),
                    'sub_mkt_pct_rff_rentsqft': prop.get('SubMktPctEffRentSqFt'),
                    'mkt_pct_net_rentunit': prop.get('MktPctNetRentUnit'),
                    'mkt_pct_net_rentsqft': prop.get('MktPctNetRentSqFt'),
                    'sub_mkt_net_rff_rentunit': prop.get('SubMktPctNetRentUnit'),
                    'sub_mkt_net_rff_rentsqft': prop.get('SubMktPctNetRentSqFt'),
                    'pricing_avail_website': prop.get('PricingAndAvailWebsite'),
                    'pricing_avail_website_alt': prop.get('PricingAndAvailWebsiteAlt'),
                    'rms_id_txt': prop.get('RMSId'),
                    'rms_program': prop.get('RMSProgram'),
                    'pricing_tier': prop.get('PricingTier'),
                    'asset_fee_managed': prop.get('AssetOrFeeManaged'),
                    'county': geolocation.get('County'),
                    'gps_latitude': geolocation.get('GPSLatitude'),
                    'gps_longitude': geolocation.get('GPSLongitude'),
                    'pmsa': geolocation.get('PMSA'),
                    'pmsa_description': geolocation.get('PMSADescription'),
                    'cmsa': geolocation.get('CMSA'),
                    'census_block': geolocation.get('CensusBlock'),
                    'census_tract': geolocation.get('CensusTract'),
                    'county_fips_code': geolocation.get('CountyFIPSCode'),
                    'industry_id': submarket and submarket.id or None,
                    'corporate_mngmt_cmpny_id': crp_mng and crp_mng.id or None,
                    'regional_mngmt_cmpny_id': reg_mng and reg_mng.id or None,
                    'areasupervisor_id': sup and sup.id or None,
                    'physical_address_to': '',
                    'physical_address_line1': '',
                    'physical_address_line2': '',
                    'physical_address_city': '',
                    'physical_address_state': '',
                    'physical_address_zip': '',
                    'mailing_address_to': '',
                    'mailing_address_line1': '',
                    'mailing_address_line2': '',
                    'mailing_address_city': '',
                    'mailing_address_state': '',
                    'mailing_address_zip': '',
                    'shipping_address_to': '',
                    'shipping_address_line1': '',
                    'shipping_address_line2': '',
                    'shipping_address_city': '',
                    'shipping_address_state': '',
                    'shipping_address_zip': '',
                    'property_phone': '',
                    'property_fax': ''
                }

                # Update property phone/fax
                for pn in phonenumbers:
                    if pn['PhoneNumberType'] == 'Property Phone':
                        values.update({'property_phone': pn['Number']})
                    if pn['PhoneNumberType'] == 'Property Fax':
                        values.update({'property_fax': pn['Number']})

                # Update address to vals
                for add in addresses:
                    if add['AddressType'] == 'Physical Address':
                        values.update({
                            'physical_address_to': add['AddressType'],
                            'physical_address_line1': add['AddressLine1'],
                            'physical_address_line2': add['AddressLine2'],
                            'physical_address_city': add['AddressCity'],
                            'physical_address_state': add['AddressState'],
                            'physical_address_zip': add['AddressZIP'],
                        })
                    elif add['AddressType'] == 'Billing Address':
                        values.update({
                            'mailing_address_to': add['AddressType'],
                            'mailing_address_line1': add['AddressLine1'],
                            'mailing_address_line2': add['AddressLine2'],
                            'mailing_address_city': add['AddressCity'],
                            'mailing_address_state': add['AddressState'],
                            'mailing_address_zip': add['AddressZIP'],
                        })
                    elif add['AddressType'] == 'Mailing Address':
                        values.update({
                            'shipping_address_to': add['AddressType'],
                            'shipping_address_line1': add['AddressLine1'],
                            'shipping_address_line2': add['AddressLine2'],
                            'shipping_address_city': add['AddressCity'],
                            'shipping_address_state': add['AddressState'],
                            'shipping_address_zip': add['AddressZIP'],
                        })

                # Check if record already exist
                rec_ids = [k for k, v in enumerate(ext_data) if data.get('ApartmentId') == v]
                if rec_ids:
                    update_vals = {}
                    # Append updated values
                    update_vals.update({
                        'id': rec_ids[0]
                    }, **values)
                    apartment_update.append(update_vals)
                else:
                    values.update({
                        'apartment_id_txt': data.get('ApartmentId'),
                        'apt_state': 'unpublished',
                    })
                    apartment_list.append(values)

            # Query to insert data in apartment
            query = """INSERT INTO aln_apartment
                                    (
                                    apartment_id_txt,
                                    last_update_date,
                                    apt_last_changed_date,
                                    last_contacted_date,
                                    row_version,
                                    aln_id_txt,
                                    status,
                                    apt_name,
                                    fka,
                                    hours,
                                    email,
                                    market,
                                    apt_owner_id_txt,
                                    submarket_id_txt,
                                    num_of_units,
                                    year_built,
                                    year_remodeled,
                                    timezone,
                                    occupancy,
                                    number_of_stories,
                                    directions,
                                    property_description,
                                    apt_homepage,
                                    apt_picture_url,
                                    curr_manager,
                                    areasupervisor_id_txt,
                                    regional_management_company_id_txt,
                                    corporate_management_company_id_txt,
                                    owner_id_txt,
                                    views,
                                    ac_heating,
                                    map_coordinates,
                                    other_notes,
                                    average_rent,
                                    average_sqft,
                                    mkt_pct_rff_rentunit,
                                    mkt_pct_rff_rentsqft,
                                    sub_mkt_pct_rff_rentunit,
                                    sub_mkt_pct_rff_rentsqft,
                                    mkt_pct_net_rentunit,
                                    mkt_pct_net_rentsqft,
                                    sub_mkt_net_rff_rentunit,
                                    sub_mkt_net_rff_rentsqft,
                                    pricing_avail_website,
                                    pricing_avail_website_alt,
                                    rms_id_txt,
                                    rms_program,
                                    pricing_tier,
                                    asset_fee_managed,
                                    county,
                                    gps_latitude,
                                    gps_longitude,
                                    pmsa,
                                    pmsa_description,
                                    cmsa,
                                    census_block,
                                    census_tract,
                                    county_fips_code,
                                    physical_address_to,
                                    physical_address_line1,
                                    physical_address_line2,
                                    physical_address_city,
                                    physical_address_state,
                                    physical_address_zip,
                                    mailing_address_to,
                                    mailing_address_line1,
                                    mailing_address_line2,
                                    mailing_address_city,
                                    mailing_address_state,
                                    mailing_address_zip,
                                    shipping_address_to,
                                    shipping_address_line1,
                                    shipping_address_line2,
                                    shipping_address_city,
                                    shipping_address_state,
                                    shipping_address_zip,
                                    property_phone,
                                    property_fax,
                                    industry_id,
                                    corporate_mngmt_cmpny_id,
                                    regional_mngmt_cmpny_id,
                                    areasupervisor_id,
                                    apt_state
                                    )
                                VALUES 
                                    (
                                     %(apartment_id_txt)s,
                                     %(last_update_date)s,
                                     %(apt_last_changed_date)s,
                                     %(last_contacted_date)s,
                                     %(row_version)s,
                                     %(aln_id_txt)s,
                                     %(status)s,
                                     %(apt_name)s,
                                     %(fka)s,
                                     %(hours)s,
                                     %(email)s,
                                     %(market)s,
                                     %(apt_owner_id_txt)s,
                                     %(submarket_id_txt)s,
                                     %(num_of_units)s,
                                     %(year_built)s,
                                     %(year_remodeled)s,
                                     %(timezone)s,
                                     %(occupancy)s,
                                     %(number_of_stories)s,
                                     %(directions)s,
                                     %(property_description)s,
                                     %(apt_homepage)s,
                                     %(apt_picture_url)s,
                                     %(curr_manager)s,
                                     %(areasupervisor_id_txt)s,
                                     %(regional_management_company_id_txt)s,
                                     %(corporate_management_company_id_txt)s,
                                     %(owner_id_txt)s,
                                     %(views)s,
                                     %(ac_heating)s,
                                     %(map_coordinates)s,
                                     %(other_notes)s,
                                     %(average_rent)s,
                                     %(average_sqft)s,
                                     %(mkt_pct_rff_rentunit)s,
                                     %(mkt_pct_rff_rentsqft)s,
                                     %(sub_mkt_pct_rff_rentunit)s,
                                     %(sub_mkt_pct_rff_rentsqft)s,
                                     %(mkt_pct_net_rentunit)s,
                                     %(mkt_pct_net_rentsqft)s,
                                     %(sub_mkt_net_rff_rentunit)s,
                                     %(sub_mkt_net_rff_rentsqft)s,
                                     %(pricing_avail_website)s,
                                     %(pricing_avail_website_alt)s,
                                     %(rms_id_txt)s,
                                     %(rms_program)s,
                                     %(pricing_tier)s,
                                     %(asset_fee_managed)s,
                                     %(county)s,
                                     %(gps_latitude)s,
                                     %(gps_longitude)s,
                                     %(pmsa)s,
                                     %(pmsa_description)s,
                                     %(cmsa)s,
                                     %(census_block)s,
                                     %(census_tract)s,
                                     %(county_fips_code)s,
                                     %(physical_address_to)s,
                                     %(physical_address_line1)s,
                                     %(physical_address_line2)s,
                                     %(physical_address_city)s,
                                     %(physical_address_state)s,
                                     %(physical_address_zip)s,
                                     %(mailing_address_to)s,
                                     %(mailing_address_line1)s,
                                     %(mailing_address_line2)s,
                                     %(mailing_address_city)s,
                                     %(mailing_address_state)s,
                                     %(mailing_address_zip)s,
                                     %(shipping_address_to)s,
                                     %(shipping_address_line1)s,
                                     %(shipping_address_line2)s,
                                     %(shipping_address_city)s,
                                     %(shipping_address_state)s,
                                     %(shipping_address_zip)s,
                                     %(property_phone)s,
                                     %(property_fax)s,
                                     %(industry_id)s,
                                     %(corporate_mngmt_cmpny_id)s,
                                     %(regional_mngmt_cmpny_id)s,
                                     %(areasupervisor_id)s,
                                     %(apt_state)s
                                 )"""

            # Create bulk records
            try:
                self._cr.executemany(query, apartment_list)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to insert ALN Apartment: %s", str(e))

            if apartment_update:
                # Prepare update query for apartment
                update_query = """
                                UPDATE aln_apartment SET
                                    last_update_date=%(last_update_date)s,
                                    apt_last_changed_date=%(apt_last_changed_date)s,
                                    last_contacted_date=%(last_contacted_date)s,
                                    row_version=%(row_version)s,
                                    aln_id_txt=%(aln_id_txt)s,
                                    status=%(status)s,
                                    apt_name=%(apt_name)s,
                                    fka=%(fka)s,
                                    hours=%(hours)s,
                                    email=%(email)s,
                                    market=%(market)s,
                                    apt_owner_id_txt=%(apt_owner_id_txt)s,
                                    submarket_id_txt=%(submarket_id_txt)s,
                                    num_of_units=%(num_of_units)s,
                                    year_built=%(year_built)s,
                                    year_remodeled=%(year_remodeled)s,
                                    timezone=%(timezone)s,
                                    occupancy=%(occupancy)s,
                                    number_of_stories=%(number_of_stories)s,
                                    directions=%(directions)s,
                                    property_description=%(property_description)s,
                                    apt_homepage=%(apt_homepage)s,
                                    apt_picture_url=%(apt_picture_url)s,
                                    curr_manager=%(curr_manager)s,
                                    areasupervisor_id_txt=%(areasupervisor_id_txt)s,
                                    regional_management_company_id_txt=%(regional_management_company_id_txt)s,
                                    corporate_management_company_id_txt=%(corporate_management_company_id_txt)s,
                                    owner_id_txt=%(owner_id_txt)s,
                                    views=%(views)s,
                                    ac_heating=%(ac_heating)s,
                                    map_coordinates=%(map_coordinates)s,
                                    other_notes=%(other_notes)s,
                                    average_rent=%(average_rent)s,
                                    average_sqft=%(average_sqft)s,
                                    mkt_pct_rff_rentunit=%(mkt_pct_rff_rentunit)s,
                                    mkt_pct_rff_rentsqft=%(mkt_pct_rff_rentsqft)s,
                                    sub_mkt_pct_rff_rentunit=%(sub_mkt_pct_rff_rentunit)s,
                                    sub_mkt_pct_rff_rentsqft=%(sub_mkt_pct_rff_rentsqft)s,
                                    mkt_pct_net_rentunit=%(mkt_pct_net_rentunit)s,
                                    mkt_pct_net_rentsqft=%(mkt_pct_net_rentsqft)s,
                                    sub_mkt_net_rff_rentunit=%(sub_mkt_net_rff_rentunit)s,
                                    sub_mkt_net_rff_rentsqft=%(sub_mkt_net_rff_rentsqft)s,
                                    pricing_avail_website=%(pricing_avail_website)s,
                                    pricing_avail_website_alt=%(pricing_avail_website_alt)s,
                                    rms_id_txt=%(rms_id_txt)s,
                                    rms_program=%(rms_program)s,
                                    pricing_tier=%(pricing_tier)s,
                                    asset_fee_managed=%(asset_fee_managed)s,
                                    county=%(county)s,
                                    gps_latitude=%(gps_latitude)s,
                                    gps_longitude=%(gps_longitude)s,
                                    pmsa=%(pmsa)s,
                                    pmsa_description=%(pmsa_description)s,
                                    cmsa=%(cmsa)s,
                                    census_block=%(census_block)s,
                                    census_tract=%(census_tract)s,
                                    county_fips_code=%(county_fips_code)s,
                                    physical_address_to=%(physical_address_to)s,
                                    physical_address_line1=%(physical_address_line1)s,
                                    physical_address_line2=%(physical_address_line2)s,
                                    physical_address_city=%(physical_address_city)s,
                                    physical_address_state=%(physical_address_state)s,
                                    physical_address_zip=%(physical_address_zip)s,
                                    mailing_address_to=%(mailing_address_to)s,
                                    mailing_address_line1=%(mailing_address_line1)s,
                                    mailing_address_line2=%(mailing_address_line2)s,
                                    mailing_address_city=%(mailing_address_city)s,
                                    mailing_address_state=%(mailing_address_state)s,
                                    mailing_address_zip=%(mailing_address_zip)s,
                                    shipping_address_to=%(shipping_address_to)s,
                                    shipping_address_line1=%(shipping_address_line1)s,
                                    shipping_address_line2=%(shipping_address_line2)s,
                                    shipping_address_city=%(shipping_address_city)s,
                                    shipping_address_state=%(shipping_address_state)s,
                                    shipping_address_zip=%(shipping_address_zip)s,
                                    property_phone=%(property_phone)s,
                                    property_fax=%(property_fax)s,
                                    industry_id=%(industry_id)s,
                                    corporate_mngmt_cmpny_id=%(corporate_mngmt_cmpny_id)s,
                                    regional_mngmt_cmpny_id=%(regional_mngmt_cmpny_id)s,
                                    areasupervisor_id=%(areasupervisor_id)s
                                WHERE
                                    id = %(id)s
                            """

            # Update bulk records
            try:
                if apartment_update:
                    self._cr.executemany(update_query, apartment_update)
            except Exception as e:
                flag_exc = True
                _logger.error("Failed to update ALN Apartment: %s", str(e))

            if not flag_exc:
                total_records += len(apartment_list)
                total_updated += len(apartment_update)
                _logger.info('***** Batch ALN Apartment Successfully Created : %d  *****',
                             len(apartment_list))
                _logger.info('***** Batch ALN Apartment Successfully Updated : %d  *****',
                             len(apartment_update))

        if not flag_exc:
            _logger.info(
                '------- ALN Apartment Execution completed!  Total ALN Apartment Successfully Created : %d  '
                'and Updated : %d  -------',
                total_records, total_updated)

    # load router
    def synchronize_router(self, origin=''):
        """ Main router that loads data """

        # step 1: Load Owners
        self.load_owners_data()

        # step 2: Load Management Companies
        self.load_management_companies()

        # step 3: Load New Construction
        self.load_construction()

        # step 4: Load Contacts
        self.load_contacts()

    # update rowversion
    def sync_rowversion(self):
        """This method updates rowversion after loading data in ALN tables"""
        config_obj = self.env['ir.config_parameter']

        # Apartment update
        self._cr.execute("""select max(row_version) from aln_apartment""")
        apt_data = self._cr.dictfetchall()
        config_obj.sudo().set_param(
            'alndata.apartments.rowversion', apt_data[0]['max'])

        # Contact update
        self._cr.execute("""select max(contact_rowversion) from aln_contact""")
        contact_data = self._cr.dictfetchall()
        config_obj.sudo().set_param(
            'alndata.contacts.rowversion', contact_data[0]['max'])

        # Management Companies update
        self._cr.execute("""select max(company_rowversion) from aln_management_company""")
        company_data = self._cr.dictfetchall()
        config_obj.sudo().set_param(
            'alndata.managementcompanies.rowversion', company_data[0]['max'])

    @api.model
    def sync_aln_data_with_threading(self):
        """Synchronize data with ALN Data By Threading.

        This method is used to get data from ALN Data using threading.
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

            # Update Rowversion
            self.sync_rowversion()

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
