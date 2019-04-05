# Copyright 2018 Jose Luis Algara (Alda hotels) <osotranquilo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from odoo import api, models
from datetime import datetime
import logging


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def rm_add_customer(self, customer):
        # RoomMatik API CREACIÓN DE CLIENTE
        _logger = logging.getLogger(__name__)

        partner_res = self.env['res.partner'].search([(
            'document_number', '=',
            customer['IdentityDocument']['Number'])])

        json_response = {'Id': 0}
        if any(partner_res):
            # Change customer data
            _logger.info('ROOMMATIK %s exist in BD %s res.artner id Rewriting',
                         partner_res[0].document_number,
                         partner_res[0].id,)
            try:
                partner_res[0].update(self.rm_preare_customer(customer))
                write_custumer = partner_res[0]
            except:
                _logger.error('ROOMMATIK Rewriting %s in BD %s ID',
                              partner_res[0].document_number,
                              partner_res[0].id,)
        else:
            # Create new customer
            try:
                write_custumer = self.create(self.rm_preare_customer(customer))
                _logger.info('ROOMMATIK Create %s in BD like %s ID',
                             write_custumer.document_number,
                             write_custumer.id,)
            except:
                _logger.error('ROOMMATIK Creating %s in BD %s ID',
                              write_custumer.document_number,
                              write_custumer.id,)

        json_response = {'Id': write_custumer.id,
                         'FirstName': write_custumer.firstname,
                         'LastName1': write_custumer.lastname,
                         'LastName2': write_custumer.lastname2,
                         'Birthday': write_custumer.birthdate_date,
                         'Sex': write_custumer.gender,
                         'Address': {
                            'Nationality': write_custumer.zip,
                            'Country': write_custumer.zip,
                            'ZipCode': write_custumer.zip,
                            'City': write_custumer.city,
                            'Street': write_custumer.street,
                            'House': customer['Address']['House'],
                            'Flat': customer['Address']['Flat'],
                            'Number': customer['Address']['Number'],
                            'Province': customer['Address']['Province'],
                         },
                         'IdentityDocument': {
                            'Number': write_custumer.document_number,
                            'Type': write_custumer.document_type,
                            'ExpiryDate': customer[
                                 'IdentityDocument']['ExpiryDate'],
                            'ExpeditionDate': write_custumer.document_expedition_date,
                         },
                         'Contact': {
                            'Telephone': write_custumer.phone,
                            'Fax': customer['Contact']['Fax'],
                            'Mobile': write_custumer.mobile,
                            'Email': write_custumer.email,
                         }
                         }

        json_response = json.dumps(json_response)
        return json_response

    def rm_preare_customer(self, customer):
        # Check Sex string
        if customer['Sex'] not in {'male', 'female'}:
            customer['Sex'] = ''
        # Check state_id
        city_srch = self.env['res.country.state'].search([
            ('name', 'ilike', customer['Address']['Province'])])
        # Create Street2
        street_2 = customer['Address']['House']
        street_2 += ' ' + customer['Address']['Flat']
        street_2 += ' ' + customer['Address']['Number']
        return {
            'firstname': customer['FirstName'],
            'lastname': customer['LastName1'],
            'lastname2': customer['LastName2'],
            'birthdate_date': datetime.strptime(customer['Birthday'],
                                                "%d%m%Y").date(),
            'gender': customer['Sex'],
            'zip': customer['Address']['ZipCode'],
            'city': customer['Address']['City'],
            'street': customer['Address']['Street'],
            'street2': street_2,
            'state_id': city_srch.id,
            'phone': customer['Contact']['Telephone'],
            'mobile': customer['Contact']['Mobile'],
            'email': customer['Contact']['Email'],
            'document_number': customer['IdentityDocument']['Number'],
            'document_type': customer['IdentityDocument']['Type'],
            'document_expedition_date': datetime.strptime(customer[
                'IdentityDocument']['ExpeditionDate'],
                "%d%m%Y").date(),
            }
