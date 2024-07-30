# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from os.path import join, dirname, realpath
import csv

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # ==== Load l10n_mx_edi.station ====

    if not env['l10n_mx_edi.station'].search_count([]):
        csv_path = join(dirname(realpath(__file__)), 'static/data', 'l10n_mx_edi.station.csv')
        station_vals_list = []
        with open(csv_path, 'r') as csv_file:
            for row in csv.DictReader(
                    csv_file,
                    delimiter='|',
                    fieldnames=['l10n_mx_edi_transport_type', 'code', 'name', 'country_xml_id']):
                state = env.ref('base.%s' % row['country_xml_id'], raise_if_not_found=False)
                station_vals_list.append({
                    'l10n_mx_edi_transport_type': row['l10n_mx_edi_transport_type'],
                    'code': row['code'],
                    'name': row['name'],
                    'country_id': state.id if state else False,
                })

        stations = env['l10n_mx_edi.station'].create(station_vals_list)

        if stations:
            cr.execute('''
               INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
                   SELECT
                        'res_station_' || lower(res_country.code) || '_' || l10n_mx_edi_station.code,
                        l10n_mx_edi_station.id,
                        'l10n_mx_edi_tms_waybill',
                        'l10n_mx_edi.station',
                        TRUE
                   FROM l10n_mx_edi_station
                   JOIN res_country ON res_country.id = l10n_mx_edi_station.country_id
                   WHERE l10n_mx_edi_station.id IN %s
            ''', [tuple(stations.ids)])

    # ==== Load l10n_mx_edi.dangerous.material ====

    if not env['l10n_mx_edi.dangerous.material'].search_count([]):
        csv_path = join(dirname(realpath(__file__)), 'static/data', 'l10n_mx_edi.dangerous.material.csv')
        material_vals_list = []
        with open(csv_path, 'r') as csv_file:
            for row in csv.DictReader(
                    csv_file,
                    delimiter='|',
                    fieldnames=['code', 'name']):
                material_vals_list.append({
                    'code': row['code'],
                    'name': row['name'],
                })

        materials = env['l10n_mx_edi.dangerous.material'].create(material_vals_list)

        if materials:
            # Use id of the record to avoid duplicated code error.
            cr.execute('''
               INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
                   SELECT
                        'res_dangerous_material_id_' || material.id || '_' || material.code,
                        material.id,
                        'l10n_mx_edi_tms_waybill',
                        'l10n_mx_edi.dangerous.material',
                        TRUE
                   FROM l10n_mx_edi_dangerous_material AS material
                   WHERE  material.id IN %s
            ''', [tuple(materials.ids)])

        # ==== Update product.unspsc.code for dangerous material ====

        csv_path = join(dirname(realpath(__file__)), 'static/data', 'product.unspsc.code.csv')
        product_dict = {}
        with open(csv_path, 'r') as csv_file:
            for row in csv.DictReader(
                    csv_file,
                    delimiter='|',
                    fieldnames=['code', 'type']):
                product_dict.setdefault(row['type'], []).append(row['code'])
        for code_type, codes in product_dict.items():
            env.cr.execute('''
                UPDATE product_unspsc_code
                SET l10n_mx_edi_waybill_type = %(type)s
                WHERE code IN %(code)s
            ''', {'type': code_type, 'code': tuple(codes)})

    # ==== Load l10n_mx_edi.packaging ====

    if not env['l10n_mx_edi.packaging'].search_count([]):
        csv_path = join(dirname(realpath(__file__)), 'static/data', 'l10n_mx_edi.packaging.csv')
        packaging_vals_list = []
        with open(csv_path, 'r') as csv_file:
            for row in csv.DictReader(
                    csv_file,
                    delimiter='|',
                    fieldnames=['code', 'name']):
                packaging_vals_list.append({
                    'code': row['code'],
                    'name': row['name'],
                })

        packagings = env['l10n_mx_edi.packaging'].create(packaging_vals_list)

        if packagings:
            cr.execute('''
               INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
                   SELECT
                        'res_packaging_id_' || l10n_mx_edi_packaging.code,
                        l10n_mx_edi_packaging.id,
                        'l10n_mx_edi_tms_waybill',
                        'l10n_mx_edi.packaging',
                        TRUE
                   FROM l10n_mx_edi_packaging
                   WHERE  l10n_mx_edi_packaging.id IN %s
            ''', [tuple(packagings.ids)])


def uninstall_hook(cr, registry):
    cr.execute("DELETE FROM ir_model_data WHERE model='l10n_mx_edi.station';")
    cr.execute("DELETE FROM ir_model_data WHERE model='l10n_mx_edi.dangerous.material';")
    cr.execute("DELETE FROM ir_model_data WHERE model='l10n_mx_edi.packaging';")
