from odoo import models, fields
from datetime import datetime, date


def get_years():
    year_list = []
    current_year = datetime.now().year
    for i in range(current_year-10, int(current_year)+1):
        year_list.append((str(i), str(i)))
    return year_list


def get_common():
    months = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
              '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}

    letters = ['A', 'B', 'C', 'D', 'E1', 'E2',
               'E3', 'F', 'G', 'H', 'J', 'K', 'L']

    return [months, letters]


class HrP9Form(models.TransientModel):
    _name = 'hr.p9.form'
    _description = 'Employee P9 Form'

    year = fields.Selection(get_years(), string='Year',
                            required=True, default=str(datetime.now().year-1))
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    def generate_multi_p9_forms(self):
        date_end = date(int(self.year), 12, 31).strftime('%Y-%m-%d')

        months, letters = get_common()

        data = {'payslips': []}

        for rec in self.employee_ids:
            val = {
                'employee': {'name': rec.name,
                             'vat': rec.tax_pin},
                'employer': {'name': rec.company_id.name,
                             'vat': rec.company_id.vat},
                'ms': months,
                'body': {},
                'year':self.year,
            }

            for m in months:
                val['body'][m] = {}
                for l in letters:
                    val['body'][m][l] = 0

            payslips = self.env['hr.payslip'].search_read([
                ('employee_id', '=', rec.id),
                 ('state','=','done'),
                ('date_from', '>=', f'{self.year}-01-01'),
                ('date_from', '<=', date_end)
            ],
                fields={'line_ids', 'date_from'})

            for slip in payslips:
                month = slip['date_from'].strftime('%m')
                if slip['line_ids']:
                    payslip_line = self.env['hr.payslip.line']
                    basic = payslip_line.search_read(
                        [('slip_id', '=', slip['id']), ('salary_rule_id', '=', self.env.ref(
                            'hr_ke.ke_rule10').id)],
                        limit=1,
                        fields={'total'}
                    ) or 0.0
                    gross = payslip_line.search_read(
                        [('slip_id', '=', slip['id']), ('salary_rule_id', '=', self.env.ref(
                            'hr_ke.ke_rule30').id)],
                        limit=1,
                        fields={'total'}
                    ) or 0.0
                    pension = payslip_line.search_read(
                        [('slip_id', '=', slip['id']), ('salary_rule_id', '=', self.env.ref(
                            'hr_ke.ke_rule66').id)],
                        limit=1,
                        fields={'total'}
                    ) or 0.0
                    nssf = payslip_line.search_read(
                        [('slip_id', '=', slip['id']), ('salary_rule_id', '=', self.env.ref(
                            'hr_ke.ke_rule55').id)],
                        limit=1,
                        fields={'total'}
                    ) or 0.0
                    gross_taxable = payslip_line.search_read(
                        [('slip_id', '=', slip['id']), ('salary_rule_id', '=', self.env.ref(
                            'hr_ke.ke_rule45').id)],
                        limit=1,
                        fields={'total'}
                    ) or 0.0
                    paye = payslip_line.search_read(
                        [('slip_id', '=', slip['id']), ('salary_rule_id', '=', self.env.ref(
                            'hr_ke.ke_rule90').id)],
                        limit=1,
                        fields={'total'}
                    ) or 0.0
                    relief = payslip_line.search_read(
                        [('slip_id', '=', slip['id']), ('salary_rule_id', '=', self.env.ref(
                            'hr_ke.ke_rule91').id)],
                        limit=1,
                        fields={'total'}
                    ) or 0.0
                    insurance_relief = payslip_line.search_read(
                        [('slip_id', '=', slip['id']), ('salary_rule_id', '=', self.env.ref(
                            'hr_ke.ke_rule96').id)],
                        limit=1,
                        fields={'total'}
                    ) or 0.0
                    net_pay = payslip_line.search_read(
                        [('slip_id', '=', slip['id']), ('salary_rule_id', '=', self.env.ref(
                            'hr_ke.ke_rule101').id)],
                        limit=1,
                        fields={'total'}
                    ) or 0.0

                    insurance_relief = int(insurance_relief[0]['total']) if type(
                        insurance_relief) == list else 0.0
                    relief = int(relief[0]['total'])if type(
                        relief) == list else 0.0

                    val['body'][month]['A'] = int(basic[0]['total']) if type(
                        basic) == list else 0.0
                    val['body'][month]['D'] = int(gross[0]['total']) if type(
                        gross) == list else 0.0
                    val['body'][month]['E1'] = int(
                        0.3 * val['body'][month]['D'])
                    val['body'][month]['E2'] = int(pension[0]['total']) if type(
                        pension) == list else 0.0
                    val['body'][month]['E3'] = int(nssf[0]['total']) if type(
                        nssf) == list else 0.0
                    val['body'][month]['G'] = int(nssf[0]['total']) if type(
                        nssf) == list else 0.0
                    val['body'][month]['H'] = int(gross_taxable[0]['total']) if type(
                        gross_taxable) == list else 0.0
                    val['body'][month]['J'] = int(paye[0]['total']) if type(
                        paye) == list else 0.0

                    val['body'][month]['K'] = relief + insurance_relief
                    val['body'][month]['L'] = int(net_pay[0]['total']) if type(
                        net_pay) == list else 0.0

            # Calculate column totals
            seen = {}
            for i in val['body']:
                for j in val['body'][i]:
                    if j in seen:
                        seen[j] += val['body'][i][j]
                    else:
                        seen[j] = val['body'][i][j]

            val['totals'] = [seen[i] for i in sorted(seen)]
            data['payslips'].append(val)
        return self.env.ref('employee_p9.action_multi_employee_p9_report').report_action(self, data=data)
