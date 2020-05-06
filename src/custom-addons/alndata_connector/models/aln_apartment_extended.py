# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests
import base64
import logging
import time
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class ALNApartmentExtended(models.Model):
    _name = "aln.apartment.extended"
    _auto = False
    _description = "ALN Apartment Extended"

    # Fields for Apartment
    apt_id = fields.Many2one('aln.apartment', 'Apt Id')
    apartment_id_txt = fields.Char('Apartment ID')
    last_update_date = fields.Datetime(string="Last Update Date")
    last_contacted_date = fields.Datetime(string="Last Contacted Date")
    row_version = fields.Integer('Row Version')
    aln_id_txt = fields.Char('ALN')
    status = fields.Char('Status')
    apt_name = fields.Char('Apt Name')
    fka = fields.Char('FKA')
    hours = fields.Char('Hours')
    email = fields.Char('Email')
    market = fields.Char('Market')
    county = fields.Char('County')
    apt_owner_id_txt = fields.Char('Apt Owner')
    submarket_id_txt = fields.Char('Submarket')
    industry_id = fields.Many2one('res.partner.industry', 'SubMarket ID')
    corporate_mngmt_cmpny_id = fields.Many2one('res.partner', 'Corporate Mng Company')
    regional_mngmt_cmpny_id = fields.Many2one('res.partner', 'Regional Mng Company')
    num_of_units = fields.Char('Num of Units')
    year_built = fields.Char('Year Built')
    year_remodeled = fields.Char('Year Remodeled')
    timezone = fields.Char('TimeZone')
    occupancy = fields.Char('Occupancy')
    number_of_stories = fields.Char('Number Of Stories')
    directions = fields.Char('Directions')
    property_description = fields.Char('Property Description')
    apt_homepage = fields.Char('Apt Home Page')
    apt_picture_url = fields.Char('Apt Picture URL')
    curr_manager = fields.Char('Curr Manager')
    areasupervisor_id_txt = fields.Char('Area Supervisor')
    areasupervisor_id = fields.Many2one('res.partner', 'Area Supervisor ID')
    regional_management_company_id_txt = fields.Char('Regional Management Company')
    corporate_management_company_id_txt = fields.Char('Corporate Management Company')
    views = fields.Char('Views')
    ac_heating = fields.Char('AC Heating')
    map_coordinates = fields.Char('Map Coordinates')
    other_notes = fields.Char('Other Notes')
    average_rent = fields.Char('Average Rent')
    average_sqft = fields.Char('Average SqFt')
    mkt_pct_rff_rentunit = fields.Char('Mkt Pct Eff Rent Unit')
    mkt_pct_rff_rentsqft = fields.Char('Mkt Pct Eff Rent SqFt')
    sub_mkt_pct_rff_rentunit = fields.Char('Sub Mkt Pct Eff Rent Unit')
    sub_mkt_pct_rff_rentsqft = fields.Char('Sub Mkt Pct Eff Rent SqFt')
    mkt_pct_net_rentunit = fields.Char('Mkt Pct Net Rent Unit')
    mkt_pct_net_rentsqft = fields.Char('Mkt Pct Net Rent SqFt')
    sub_mkt_net_rff_rentunit = fields.Char('Sub Mkt Pct Net Rent Unit')
    sub_mkt_net_rff_rentsqft = fields.Char('Sub Mkt Pct Net Rent SqFt')
    pricing_avail_website = fields.Char('Pricing And Avail Website')
    pricing_avail_website_alt = fields.Char('Pricing And Avail Website Alt')
    rms_id_txt = fields.Char('RMS')
    rms_program = fields.Char('RMS Program')
    pricing_tier = fields.Char('Pricing Tier')
    asset_fee_managed = fields.Char('Asset Or Fee Managed')
    gps_latitude = fields.Char('GPS Latitude')
    gps_longitude = fields.Char('GPS Longitude')
    pmsa = fields.Char('PMSA')
    pmsa_description = fields.Char('PMSA Description')
    cmsa = fields.Char('CMSA')
    census_block = fields.Char('Census Block')
    census_tract = fields.Char('Census Tract')
    county_fips_code = fields.Char('County FIPS Code')
    physical_address_to = fields.Char('Physical Address To')
    physical_address_line1 = fields.Char('Physical Address Line1')
    physical_address_line2 = fields.Char('Physical Address Line2')
    physical_address_city = fields.Char('Physical Address City')
    physical_address_state = fields.Char('Physical Address State')
    physical_address_zip = fields.Char('Physical Address ZIP')
    mailing_address_to = fields.Char('Mailing Address To')
    mailing_address_line1 = fields.Char('Mailing Address Line1')
    mailing_address_line2 = fields.Char('Mailing Address Line2')
    mailing_address_city = fields.Char('Mailing Address City')
    mailing_address_state = fields.Char('Mailing Address State')
    mailing_address_zip = fields.Char('Mailing Address ZIP')
    shipping_address_to = fields.Char('Shipping Address To')
    shipping_address_line1 = fields.Char('Shipping Address Line1')
    shipping_address_line2 = fields.Char('Shipping Address Line2')
    shipping_address_city = fields.Char('Shipping Address City')
    shipping_address_state = fields.Char('Shipping Address State')
    shipping_address_zip = fields.Char('Shipping Address ZIP')
    property_phone = fields.Char('Property Phone')
    property_fax = fields.Char('Property Fax')
    apt_last_changed_date = fields.Datetime(string="Apartment Last changed Date")
    apt_published_date = fields.Datetime(string="Apartment Published Date")
    apt_published_id = fields.Many2one(
        'res.partner',
        'Apartment Published by'
    )
    apt_state = fields.Selection(
        [('published', 'Published'),
         ('unpublished', 'Unpublished')],
        string='Apartment State',
        default='unpublished'
    )
    # Fields for contact
    cont_id = fields.Many2one('aln.contact', 'Cont Id')
    contact_id_txt = fields.Char('Contact')
    contact_name = fields.Char('Contact Name')
    contact_title = fields.Char('Title')
    contact_email = fields.Char('Contact Email')
    contact_company_property = fields.Char('Company/Property')
    associated_id_txt = fields.Char('Associated Entity')
    corporate_id_txt = fields.Char('Corporate Entity')
    contact_rowversion = fields.Integer('Contact RowVersion')
    cont_last_changed_date = fields.Datetime(string="Contact Last changed Date")
    cont_published_date = fields.Datetime(string="Contact Published Date")
    cont_published_id = fields.Many2one(
        'res.partner',
        'Contact Published by'
    )
    cont_state = fields.Selection(
        [('published', 'Published'),
         ('unpublished', 'Unpublished')],
        string='Contact State',
        default='unpublished'
    )
    # Fields for Management Companies
    cmp_id = fields.Many2one('aln.management.company', 'Mng Cmpy Id')
    management_comp = fields.Char(related='cmp_id.company_name', string='Management Company')
    company_id_txt = fields.Char('Management Company ID')
    company_market = fields.Char('Comp Market')
    company_name = fields.Char('Comp Name')
    company_website = fields.Char('Comp Website')
    company_parent_id_txt = fields.Char('Comp Parent')
    company_rowversion = fields.Integer('Company RowVersion')
    cmp_last_changed_date = fields.Datetime(string="Company Last changed Date")
    cmp_published_date = fields.Datetime(string="Company Published Date")
    cmp_published_id = fields.Many2one(
        'res.partner',
        'Company Published by'
    )
    cmp_state = fields.Selection(
        [('published', 'Published'),
         ('unpublished', 'Unpublished')],
        string='Company State',
        default='unpublished'
    )
    # Fields for New Construction
    const_id = fields.Many2one('aln.new.construction', 'Const ID')
    construction_id_txt = fields.Char('Construction ID')
    # new_apartment_id_txt = fields.Char('Const. Apartment ID')
    company = fields.Char('Company')
    project_name = fields.Char('Project Name')
    project_address = fields.Char('Project Address')
    project_city = fields.Char('Project City')
    project_state = fields.Char('Project State')
    project_zip = fields.Char('Project Zip')
    new_num_of_units = fields.Char('Number Of Units')
    property_type = fields.Char('Property Type')
    construction_status = fields.Char('Construction Status')
    start_date = fields.Char('Start Date')
    lease_date = fields.Char('Lease Date')
    occupancy_date = fields.Char('Occupancy Date')
    completion_date = fields.Char('Completion Date')
    progress = fields.Text('Progress')
    new_last_changed_date = fields.Datetime(string="New Construction Last changed Date")
    new_published_date = fields.Datetime(string="New Construction Published Date")
    new_published_id = fields.Many2one(
        'res.partner',
        'New Construction Published by'
    )
    new_state = fields.Selection(
        [('published', 'Published'),
         ('unpublished', 'Unpublished')],
        string='New Construction State',
        default='unpublished'
    )
    # Fields for Owner
    own_id = fields.Many2one('aln.owner', 'Own Id')
    owner_id_txt = fields.Char('Owner')
    owner_name = fields.Char('Owner Name')
    owner_address = fields.Char('Address')
    owner_phone = fields.Char('Phone')
    own_published_date = fields.Datetime(string="Owner Published Date")
    own_published_id = fields.Many2one(
        'res.partner',
        'Owner Published by'
    )
    own_state = fields.Selection(
        [('published', 'Published'),
         ('unpublished', 'Unpublished')],
        string='Owner State',
        default='unpublished'
    )

    @api.model_cr
    def init(self):
        """ Create view for Apartment Extended """

        tools.drop_view_if_exists(self._cr, '%s' % (self._name.replace('.', '_')))
        self._cr.execute(""" CREATE OR REPLACE VIEW %s AS (
                            SELECT 
                                row_number() OVER () AS id,
                                ap.id as apt_id, ap.apartment_id_txt , ap.last_update_date , ap.last_contacted_date , ap.row_version , ap.aln_id_txt , ap.status , ap.apt_name , ap.fka , ap.hours , ap.email , ap.market , ap.county , ap.apt_owner_id_txt , ap.submarket_id_txt , ap.industry_id , ap.corporate_mngmt_cmpny_id , ap.regional_mngmt_cmpny_id ,
                                ap.num_of_units , ap.year_built , ap.year_remodeled , ap.timezone , ap.occupancy , ap.number_of_stories , ap.directions , ap.property_description , ap.apt_homepage , ap.apt_picture_url , ap.curr_manager , ap.areasupervisor_id_txt , ap.areasupervisor_id , ap.regional_management_company_id_txt ,
                                ap.corporate_management_company_id_txt , ap.views , ap.ac_heating , ap.map_coordinates , ap.other_notes , ap.average_rent , ap.average_sqft , ap.mkt_pct_rff_rentunit , ap.mkt_pct_rff_rentsqft , ap.sub_mkt_pct_rff_rentunit , ap.sub_mkt_pct_rff_rentsqft , ap.mkt_pct_net_rentunit , ap.mkt_pct_net_rentsqft ,
                                ap.sub_mkt_net_rff_rentunit , ap.sub_mkt_net_rff_rentsqft , ap.pricing_avail_website , ap.pricing_avail_website_alt , ap.rms_id_txt , ap.rms_program , ap.pricing_tier , ap.asset_fee_managed , ap.gps_latitude , ap.gps_longitude , ap.pmsa , ap.pmsa_description , ap.cmsa , ap.census_block , ap.census_tract ,
                                ap.county_fips_code , ap.physical_address_to , ap.physical_address_line1 , ap.physical_address_line2 , ap.physical_address_city , ap.physical_address_state , ap.physical_address_zip , ap.mailing_address_to , ap.mailing_address_line1 , ap.mailing_address_line2 , ap.mailing_address_city , ap.mailing_address_state ,
                                ap.mailing_address_zip , ap.shipping_address_to , ap.shipping_address_line1 , ap.shipping_address_line2 , ap.shipping_address_city , ap.shipping_address_state , ap.shipping_address_zip , ap.property_phone , ap.property_fax , ap.apt_last_changed_date , ap.apt_published_date , ap.apt_published_id , ap.apt_state ,
                                anc.id as const_id, anc.construction_id_txt , anc.new_apartment_id_txt , anc.company , anc.project_name , anc.project_address , anc.project_city , anc.project_state , anc.project_zip , anc.new_num_of_units , anc.property_type , anc.construction_status , anc.start_date , anc.lease_date , anc.occupancy_date , anc.completion_date ,
                                anc.progress , anc.new_last_changed_date , anc.new_published_date , anc.new_published_id , anc.new_state ,
                                acon.id as cont_id, acon.contact_id_txt , acon.contact_name , acon.contact_title , acon.contact_email , acon.contact_company_property , acon.associated_id_txt , acon.corporate_id_txt , acon.contact_rowversion , acon.cont_last_changed_date , acon.cont_published_date , acon.cont_published_id , acon.cont_state ,
                                amc.id as cmp_id, amc.company_id_txt , amc.company_market , amc.company_name , amc.company_website , amc.company_parent_id_txt , amc.company_rowversion , amc.cmp_last_changed_date , amc.cmp_published_date , amc.cmp_published_id , amc.cmp_state ,
                                ao.id as own_id, ao.owner_id_txt, ao.owner_name, ao.owner_address, ao.owner_phone, ao.own_published_date, ao.own_published_id, ao.own_state
                            FROM 
                                aln_apartment AS ap
                            LEFT JOIN
                                 aln_new_construction AS anc ON anc.new_apartment_id_txt = ap.apartment_id_txt
                            LEFT JOIN
                                 aln_contact AS acon ON ap.apartment_id_txt = acon.associated_id_txt
                            LEFT JOIN
                                 aln_management_company AS amc ON ap.corporate_management_company_id_txt = amc.company_id_txt
                            LEFT JOIN
                                aln_owner AS ao ON ap.owner_id_txt = ao.owner_id_txt
                            ORDER BY
                                ap.apartment_id_txt
                        )""" % (self._name.replace('.', '_')))

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

    def get_state(self, obj, state_code):
        """State.

        This method is used to search state from state code.
        """
        # Get US as country
        country_id = self.env['res.country'].search(
            [('code', '=', 'US')], limit=1).ids
        return obj.search([('code', '=', state_code),
                           ('country_id', '=', country_id or False)], limit=1)

    # 1 - synchronize owners
    def sync_owners(self, rec, updated_partner_ids, new_partner_ids):
        partner_obj = self.env['res.partner']
        state_obj = self.env['res.country.state']

        name = rec.owner_name
        ref = rec.apt_owner_id_txt
        # Prepare address data
        address = rec.owner_address
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

        # create partner values dict
        partner_vals = {
            'name': name,
            'partner_type': 'owner',
            'ref': ref,
            'street': street,
            'city': city,
            'state_id': state.id,
            'zip': owner_zip,
            'country_id': state.country_id.id,
            'phone': rec.owner_phone,
        }

        # check to see if owner exists as partner
        partner_domain = [('ref', '=', ref)]
        partner_rec = partner_obj.search(partner_domain, limit=1)

        # create/update lead and partner
        if partner_rec:
            partner_rec.write(partner_vals)
            updated_partner_ids += 1
        else:
            # Create Partner if ALN publish_id empty
            if rec.own_id and not rec.own_id.own_published_id:
                partner_obj.create(partner_vals)
                new_partner_ids += 1

        # update publish details
        rec.own_id.own_published_id = self.env.user.partner_id.id
        rec.own_id.own_published_date = datetime.now()
        rec.own_id.own_state = 'published'

        return updated_partner_ids, new_partner_ids

    # 2 synchronize management companies
    def sync_management_companies(self, rec, updated_partner_ids, new_partner_ids):
        partner_obj = self.env['res.partner']
        industry_obj = self.env['res.partner.industry']

        name = rec.company_name
        last_changed = rec.cmp_last_changed_date
        referred = rec.company_id_txt
        parent = rec.company_parent_id_txt
        lead_type = 'management_company'
        website = rec.company_website
        market = False
        if rec.company_market:
            market = industry_obj.search([
                ('name', '=', rec.company_market)], limit=1)

        # create partner values dict
        partner_vals = {}
        partner_vals.update({
            'name': name,
            'partner_type': lead_type,
            'ref': referred,
            'website': website,
            'industry_id': market and market.id or False,
            'mgmt_comp_id_txt': parent,
            'company_type': 'company'
        })

        # check to see if owner exists as partner
        partner_domain = [('ref', '=', referred)]
        partner_rec = partner_obj.search(partner_domain, limit=1)

        if parent:
            parent_domain = [('ref', '=', parent)]
            parent_partner_rec = partner_obj.search(parent_domain, limit=1)
            if parent_partner_rec:
                partner_vals['parent_id'] = parent_partner_rec.id
                updated_partner_ids += 1
            else:
                # Create partner if ALN publish_id empty
                if rec.cmp_id and not rec.cmp_id.cmp_published_id:
                    parent_id = partner_obj.create({
                        'name': parent,
                        'ref': parent,
                    })
                    partner_vals['parent_id'] = parent_id.id
                    new_partner_ids += 1

        # create/update lead and partner
        if partner_rec:
            partner_rec.write(partner_vals)
            updated_partner_ids += 1
        else:
            # Create partner if ALN publish_id empty
            if rec.cmp_id and not rec.cmp_id.cmp_published_id:
                partner_obj.create(partner_vals)
                new_partner_ids += 1

        # update publish details
        rec.cmp_id.cmp_published_id = self.env.user.partner_id.id
        rec.cmp_id.cmp_published_date = datetime.now()
        rec.cmp_id.cmp_state = 'published'

        return updated_partner_ids, new_partner_ids

    # # 3 synchronize new constructions
    # def sync_construction(self, rec, updated_partner_ids, new_partner_ids):
    #     partner_obj = self.env['res.partner']
    #     state_obj = self.env['res.country.state']
    #
    #     lead_type = "new_construction"
    #     name = rec.project_name
    #     referred = rec.construction_id_txt
    #     last_changed = rec.new_last_changed_date
    #     apartment = rec.apartment_id_txt
    #     state = self.get_state(state_obj, rec.project_state)
    #
    #     # create partner values dict
    #     partner_vals = {}
    #     partner_vals.update({
    #         'name': name,
    #         'partner_type': lead_type,
    #         'ref': referred,
    #         'street': rec.project_address,
    #         'city': rec.project_city,
    #         'state_id': state.id,
    #         'country_id': state.country_id.id,
    #         'zip': rec.project_zip,
    #         'associated_id_txt': apartment,
    #     })
    #
    #     if apartment:
    #         apartment_domain = [('ref', '=', apartment)]
    #         apartment_partner_rec = partner_obj.search(apartment_domain, limit=1)
    #         if apartment_partner_rec:
    #             partner_vals['associated_id'] = apartment_partner_rec.id
    #             updated_partner_ids += 1
    #         else:
    #             # Create partner if ALN publish_id empty
    #             if rec.const_id and not rec.const_id.new_published_id:
    #                 apartment_id = partner_obj.create({
    #                     'name': apartment,
    #                     'ref': apartment,
    #                 })
    #                 partner_vals['associated_id'] = apartment_id.id
    #                 new_partner_ids += 1
    #
    #     # check to see if owner exists as partner
    #     partner_domain = [('ref', '=', referred)]
    #     partner_rec = partner_obj.search(partner_domain, limit=1)
    #
    #     # create/update lead and partner
    #     if partner_rec:
    #         partner_rec.write(partner_vals)
    #         updated_partner_ids += 1
    #     else:
    #         # Create partner if ALN publish_id empty
    #         if rec.const_id and not rec.const_id.new_published_id:
    #             partner_obj.create(partner_vals)
    #             new_partner_ids += 1
    #
    #     # update publish details
    #     rec.const_id.new_published_id = self.env.user.partner_id.id
    #     rec.const_id.new_published_date = datetime.now()
    #     rec.const_id.new_state = 'published'
    #
    #     return updated_partner_ids, new_partner_ids

    # 4 synchronize contacts
    def sync_contacts(self, rec, updated_partner_ids, new_partner_ids, updated_lead_ids, new_lead_ids):
        lead_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']
        res_partner_title_obj = self.env['res.partner.title']

        lead_type = 'contact'
        name = rec.contact_name
        last_changed = rec.cont_last_changed_date
        referred = rec.contact_id_txt
        email = rec.contact_email
        apartment = rec.associated_id_txt
        corporate = rec.corporate_id_txt
        title = rec.contact_title

        # Prepare description
        description = ''
        if rec.start_date:
            description += "Start Date : " + rec.start_date
        if rec.lease_date:
            description += "\n" + "Lease Date : " + \
                           rec.lease_date
        if rec.occupancy_date:
            description += "\n" + "Occupancy Date : " + \
                           rec.occupancy_date
        if rec.completion_date:
            description += "\n" + "Completion Date : " + \
                           rec.completion_date
        if rec.progress:
            description += "\n" + "Progress : " + rec.progress
        if rec.market:
            description += "\n" + "Market : " + rec.market

        # create lead values dict
        lead_vals = {}
        lead_vals.update({
            'name': name,
            'lead_type': lead_type,
            'referred': apartment,
            'email_from': email,
            'partner_name': rec.contact_company_property,
            'lastdate_changed': last_changed,
            'contact_name': name,
            'description': description,
            'title': self.get_title(res_partner_title_obj,
                                    title)
        })

        # Get company data
        company = partner_obj.search([
            ('ref', '=', rec.contact_company_property)], limit=1)
        if company:
            # Update address for lead
            lead_vals.update({
                'street': company.street,
                'street2': company.street2,
                'city': company.city,
                'state_id': company.state_id,
                'zip': company.zip,
                'country_id': company.country_id,
                'website': company.website
            })

        # Get Parent
        part_parent_id = partner_obj.search([
            ('ref', '=', rec.corporate_id_txt)], limit=1)

        # create partner values dict
        partner_vals = {}
        partner_vals.update({
            'name': name,
            'partner_type': lead_type,
            'ref': referred,
            'title': lead_vals['title'],
            'parent_id': part_parent_id and part_parent_id.id or False,
        })

        # check to see if owner exists as lead and partner
        lead_domain = [('referred', '=', apartment)]
        lead_rec = lead_obj.search(lead_domain, limit=1)

        partner_domain = [('ref', '=', referred)]
        partner_rec = partner_obj.search(partner_domain, limit=1)

        # Check Corporate and edit/create partner
        if corporate:
            company_domain = [('ref', '=', corporate)]
            company_partner_rec = partner_obj.search(company_domain, limit=1)
            if company_partner_rec:
                partner_vals['parent_id'] = company_partner_rec.id
                updated_partner_ids += 1
            else:
                # Create partner if ALN publish_id empty
                if rec.cont_id and not rec.cont_id.cont_published_id:
                    parent_id = partner_obj.create({
                        'name': corporate,
                        'ref': corporate
                    })
                    partner_vals['parent_id'] = parent_id.id
                    # lead_vals['partner_id'] = parent_id.id
                    new_partner_ids += 1

        apartment_id = False
        partner_id = False
        if apartment:
            apartment_domain = [('ref', '=', apartment)]
            apartment_partner_rec = partner_obj.search(apartment_domain, limit=1)
            if apartment_partner_rec:
                partner_vals['associated_id'] = apartment_partner_rec.id
                lead_vals['partner_id'] = apartment_partner_rec.id
                updated_partner_ids += 1
            else:
                # Create partner if ALN publish_id empty
                if rec.cont_id and not rec.cont_id.cont_published_id:
                    apartment_id = partner_obj.create({
                        'name': apartment,
                        'ref': apartment,
                    })
                    partner_vals['associated_id'] = apartment_id.id
                    lead_vals['partner_id'] = apartment_id.id
                    new_partner_ids += 1

        # create/update partner
        if partner_rec:
            partner_rec.write(partner_vals)
            updated_partner_ids += 1
        else:
            # Create partner if ALN publish_id empty
            if rec.cont_id and not rec.cont_id.cont_published_id:
                partner_id = partner_obj.create(partner_vals)
                # lead_vals['partner_id'] = partner_id.id
                new_partner_ids += 1

        mgr_id = (partner_rec and partner_rec.id) or \
                 (partner_id and partner_id.id)
        if apartment_id and rec.associated_id_txt:
            apartment_id.prop_mgr_id = mgr_id

        # update publish details
        rec.cont_id.cont_published_id = self.env.user.partner_id.id
        rec.cont_id.cont_published_date = datetime.now()
        rec.cont_id.cont_state = 'published'

        # create/update lead
        if lead_rec:
            lead_rec.write(lead_vals)
            updated_lead_ids += 1
        else:
            lead_obj.create(lead_vals)
            new_lead_ids += 1

        return updated_partner_ids, new_partner_ids, updated_lead_ids, new_lead_ids

    # 5 - Process Apartment
    def sync_apartment(self, rec, updated_partner_ids, new_partner_ids, updated_location_ids, new_location_ids):
        industry_obj = self.env['res.partner.industry']
        partner_obj = self.env['res.partner']
        stage_obj = self.env['fsm.stage']
        fsm_obj = self.env['fsm.location']
        industry = False
        values = {}

        stage = stage_obj.search(
            [('sequence', '=', rec.status),
             ('stage_type', '=', 'location')],
            limit=1)

        # Get Industry
        if rec.submarket_id_txt:
            industry = industry_obj.search(
                ['|', ('ref', '=', rec.submarket_id_txt),
                 ('name', '=', rec.market)],
                limit=1)

        image_data = b''
        if rec.apt_picture_url:
            image_res = requests.get(rec.apt_picture_url)
            image_data = image_res.content

        # Get related management company
        mgmt_id = partner_obj.search([('ref', '=', rec.company_id_txt)], limit=1)

        # prepare dict
        values.update({
            'phone': rec.property_phone,
            'fax': rec.property_fax,
            'ref': rec.apartment_id_txt,
            'stage_id': stage and stage.id or False,
            'name': rec.apt_name,
            'email': rec.email,
            'industry_id': industry and industry.id or False,
            'year_built': rec.year_built,
            'year_remodeled': rec.year_remodeled,
            'direction': rec.directions,
            'notes': rec.property_description,
            'website': rec.apt_homepage,
            'image': base64.b64encode(image_data),
            'prop_mgmt_id_txt': mgmt_id and mgmt_id.ref or False,
            'prop_mgmt_id': mgmt_id and mgmt_id.id or False,
            'num_unit': rec.num_of_units,
            'company_type': 'company'
        })

        # Create Management Company if not found in db
        management_company_id = False
        if rec.corporate_management_company_id_txt:
            management_company = partner_obj.search(
                [('ref', '=', rec.corporate_management_company_id_txt),
                 ('partner_type', '=', 'management_company')],
                limit=1)

            if not management_company:
                # Create partner if ALN publish_id empty
                if rec.apt_id and not rec.apt_id.apt_published_id:
                    management_company = partner_obj.create({
                        'name': rec.corporate_management_company_id_txt,
                        'ref': rec.corporate_management_company_id_txt,
                        'partner_type': 'management_company',
                        'company_type': 'company'
                    })
            management_company_id = management_company and \
                management_company.id or False

        if management_company_id:
            values.update(
                {'commercial_partner_id': management_company_id})

        # Create Manager if not found in db
        contact_id = False
        if rec.curr_manager:
            contact = partner_obj.search(
                [('name', '=', rec.curr_manager),
                 ('partner_type', '=', 'contact')],
                limit=1)
            if not contact:
                # Create partner if ALN publish_id empty
                if rec.apt_id and not rec.apt_id.apt_published_id:
                    contact = partner_obj.create({
                        'name': rec.curr_manager,
                        'ref': rec.cont_id and rec.cont_id.contact_id_txt,
                        'associated_id_txt': rec.cont_id and rec.cont_id.associated_id_txt,
                        'partner_type': 'contact',
                        'parent_id': management_company_id
                    })
            if contact:
                # update parent
                contact.parent_id = management_company_id
                contact_id = contact.id

        # update Geo location
        latitude = rec.gps_latitude and float(rec.gps_latitude) or False
        longitude = rec.gps_longitude and float(rec.gps_longitude) or False

        # Prepare partner vals
        partner_vals = {
            'name': rec.apt_name,
            'ref': rec.apartment_id_txt,
            'partner_type': 'apartment',
            'prop_mgmt_id': mgmt_id and mgmt_id.id or False,
            'prop_mgmt_id_txt': mgmt_id and mgmt_id.ref or False,
            'prop_mgr_id': contact_id,
            'num_unit': rec.num_of_units,
            'phone': rec.property_phone,
            'fax': rec.property_fax,
            'email': rec.email,
            'industry_id': industry and industry.id or False,
            'comment': rec.property_description,
            'website': rec.apt_homepage,
            'image': base64.b64encode(image_data),
        }

        # Create FSM Partner if not found in db
        fsm_partner = partner_obj.search(
            [('ref', '=', rec.apartment_id_txt)],
            limit=1)
        if not fsm_partner:
            # Create partner if ALN publish_id empty
            if rec.apt_id and not rec.apt_id.apt_published_id:
                fsm_partner = partner_obj.create(partner_vals)
        else:
            fsm_partner.write(partner_vals)

        partner_id = fsm_partner.id
        if partner_id:
            # Update values with updated data
            values.update({'owner_id': partner_id,
                           'customer_id': partner_id or management_company_id or contact_id,
                           'partner_id': partner_id,
                           'contact_id': contact_id
                           })
            # Get address
            add_vals = self.get_addresses(values, rec)
            # Update address
            if add_vals.get('address', False):
                for add in add_vals.get('address'):
                    if add['type'] == 'contact':
                        fsm_partner.write({
                            'street': add['street'],
                            'street2': add['street2'],
                            'city': add['city'],
                            'state_id': add['state_id'],
                            'zip': add['zip'],
                            'country_id': add['country_id']
                        })
                    else:
                        # No duplication address creation
                        add_exist = False
                        for child_add in fsm_partner.child_ids:
                            if child_add.type == add['type']:
                                child_add.write({
                                    'street': add['street'],
                                    'street2': add['street2'],
                                    'city': add['city'],
                                    'state_id': add['state_id'],
                                    'zip': add['zip'],
                                    'country_id': add['country_id']
                                })
                                add_exist = True
                        if not add_exist:
                            add.update({'parent_id': fsm_partner.id})
                            fsm_partner.write({
                                'child_ids': [(0, 0, add)]
                            })
            # Update geo locations
            fsm_partner.write({
                'partner_latitude': latitude,
                'partner_longitude': longitude
            })

        # Update publish details
        rec.apt_id.apt_published_id = self.env.user.partner_id.id
        rec.apt_id.apt_published_date = datetime.now()
        rec.apt_id.apt_state = 'published'
        # Update Management companies wrt odoo's ref in ALN record
        corp_id = partner_obj.search([('ref', '=', rec.corporate_management_company_id_txt)], limit=1)
        reg_id = partner_obj.search([('ref', '=', rec.regional_management_company_id_txt)], limit=1)
        rec.apt_id.corporate_mngmt_cmpny_id = corp_id
        rec.apt_id.regional_mngmt_cmpny_id = reg_id

        # Create FSM Location if not found in db
        fsm_location = fsm_obj.search(
            [('ref', '=', rec.apartment_id_txt)],
            limit=1)
        if not fsm_location:
            fsm_obj.create(values)
            new_location_ids += 1
        else:
            fsm_location.write(values)
            updated_location_ids += 1

        return updated_partner_ids, new_partner_ids, updated_location_ids, new_location_ids

    def get_addresses(self, values, rec):
        state_obj = self.env['res.country.state']
        li = []
        if rec and rec.physical_address_to:
            state = self.get_state(state_obj,
                                   rec.physical_address_state)
            country_id = state and state.country_id.id or 0
            li.append(
                {
                    'type': 'contact',
                    'name': rec.apt_name or 'Contact Address',
                    'street': rec.physical_address_line1,
                    'street2': rec.physical_address_line2,
                    'city': rec.physical_address_city,
                    'state_id': state.id,
                    'zip': rec.physical_address_zip,
                    'country_id': country_id,
                })
        if rec and rec.mailing_address_to:
            state = self.get_state(state_obj,
                                   rec.mailing_address_state)
            country_id = state and state.country_id.id or 0
            li.append(
                {
                    'type': 'invoice',
                    'street': rec.mailing_address_line1,
                    'street2': rec.mailing_address_line2,
                    'city': rec.mailing_address_city,
                    'state_id': state.id,
                    'zip': rec.mailing_address_zip,
                    'country_id': country_id,
                })
        if rec and rec.shipping_address_to:
            state = self.get_state(state_obj,
                                   rec.shipping_address_state)
            country_id = state and state.country_id.id or 0
            li.append(
                {
                    'type': 'delivery',
                    'street': rec.shipping_address_line1,
                    'street2': rec.shipping_address_line2,
                    'city': rec.shipping_address_city,
                    'state_id': state.id,
                    'zip': rec.shipping_address_zip,
                    'country_id': country_id,
                })
        values['address'] = li
        return values

    @api.multi
    def apt_ext_publish(self):
        """ This method will publish based on following sequence
         step 1: Owners
         step 2: Management Companies
         step 3: New Construction
         step 4: Contacts
         step 5: Apartments
         Last: Update Rowversion and log updates
        """

        updated_partner_ids = new_partner_ids = 0
        updated_lead_ids = new_lead_ids = 0
        new_location_ids = updated_location_ids = 0
        apt_rowversion = cont_rowversion = mang_cmpy_rowversion = 0

        # ALN Apartment Extended Record
        for rec in self:
            # Step 1 - Process Owners
            if rec.owner_name or rec.owner_address:
                updated_partner_ids, new_partner_ids = \
                    self.sync_owners(rec, updated_partner_ids, new_partner_ids)

            # Step 2 - Process Management Companies
            if rec.company_id_txt:
                updated_partner_ids, new_partner_ids = \
                    self.sync_management_companies(
                        rec, updated_partner_ids, new_partner_ids
                    )

            ################################################################
            # MG -- Commented as requested by Wolfgang 04/17/2020
            # This creation has no scope for phase 1 as apartment would use
            # same details as new constructions.
            ################################################################
            # # Step 3 - Process Construction
            # if rec.construction_id_txt:
            #     updated_partner_ids, new_partner_ids = \
            #         self.sync_construction(
            #             rec, updated_partner_ids, new_partner_ids
            #         )

            # Step 4 - Process Contacts
            if rec.contact_id_txt:
                updated_partner_ids, new_partner_ids, updated_lead_ids, new_lead_ids = \
                    self.sync_contacts(
                        rec, updated_partner_ids,
                        new_partner_ids, updated_lead_ids, new_lead_ids
                    )

            # Step 5 - Process Apartment
            if rec.apartment_id_txt:
                updated_partner_ids, new_partner_ids, updated_location_ids, new_location_ids = \
                    self.sync_apartment(
                        rec, updated_partner_ids,
                        new_partner_ids, updated_location_ids, new_location_ids
                    )

            # Update Apartment RowVersion
            if rec.row_version > apt_rowversion:
                apt_rowversion = rec.row_version
            # Update Contact RowVersion
            if rec.contact_rowversion > cont_rowversion:
                cont_rowversion = rec.contact_rowversion
            # Update Management Company RowVersion
            if rec.company_rowversion > mang_cmpy_rowversion:
                mang_cmpy_rowversion = rec.company_rowversion

        # Log info for created/updated records
        _logger.info('*****************************************************************************')
        _logger.info('ALN Data Connector. Total Partner Created : %s', new_partner_ids)
        _logger.info('ALN Data Connector. Total Partner Updated : %s', updated_partner_ids)
        _logger.info('ALN Data Connector. Total Leads Created : %s', new_lead_ids)
        _logger.info('ALN Data Connector. Total Leads Updated : %s', updated_lead_ids)
        _logger.info('ALN Data Connector. Total FSM Location Created : %s', new_location_ids)
        _logger.info('ALN Data Connector. Total FSM Location Updated : %s', updated_location_ids)
        _logger.info('*****************************************************************************')

        return True
