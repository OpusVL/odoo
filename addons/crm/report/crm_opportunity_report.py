# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.addons.crm import crm
from openerp.osv import fields, osv
from openerp import tools


class crm_opportunity_report(osv.Model):
    """ CRM Opportunity Analysis """
    _name = "crm.opportunity.report"
    _auto = False
    _description = "CRM Opportunity Analysis"
    _rec_name = 'date_deadline'
    _inherit = ["utm.mixin"]

    _columns = {
        'date_deadline': fields.date('Expected Closing', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'opening_date': fields.datetime('Assignation Date', readonly=True),
        'date_closed': fields.datetime('Close Date', readonly=True),
        'date_last_stage_update': fields.datetime('Last Stage Update', readonly=True),
        'nbr_cases': fields.integer("# of Cases", readonly=True),

        # durations
        'delay_open': fields.float('Delay to Assign',digits=(16,2),readonly=True, group_operator="avg",help="Number of Days to open the case"),
        'delay_close': fields.float('Delay to Close',digits=(16,2),readonly=True, group_operator="avg",help="Number of Days to close the case"),
        'delay_expected': fields.float('Overpassed Deadline',digits=(16,2),readonly=True, group_operator="avg"),

        'user_id':fields.many2one('res.users', 'User', readonly=True),
        'team_id':fields.many2one('crm.team', 'Sales Team', oldname='section_id', readonly=True),
        'country_id':fields.many2one('res.country', 'Country', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'probability': fields.float('Probability',digits=(16,2),readonly=True, group_operator="avg"),
        'total_revenue': fields.float('Total Revenue',digits=(16,2),readonly=True),
        'expected_revenue': fields.float('Expected Revenue', digits=(16,2),readonly=True),
        'stage_id': fields.many2one ('crm.stage', 'Stage', readonly=True, domain="[('team_ids', '=', team_id)]"),
        'partner_id': fields.many2one('res.partner', 'Partner' , readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'priority': fields.selection(crm.AVAILABLE_PRIORITIES, 'Priority'),
        'type':fields.selection([
            ('lead','Lead'),
            ('opportunity','Opportunity'),
        ],'Type', help="Type is used to separate Leads and Opportunities"),
        'lost_reason': fields.many2one('crm.lost.reason', 'Lost Reason', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'crm_opportunity_report')
        cr.execute("""
            CREATE OR REPLACE VIEW crm_opportunity_report AS (
                SELECT
                    id,
                    c.date_deadline,
                    count(id) as nbr_cases,

                    c.date_open as opening_date,
                    c.date_closed as date_closed,

                    c.date_last_stage_update as date_last_stage_update,

                    c.user_id,
                    c.probability,
                    c.stage_id,
                    c.type,
                    c.company_id,
                    c.priority,
                    c.team_id,
                    c.campaign_id,
                    c.source_id,
                    c.medium_id,
                    c.partner_id,
                    c.country_id,
                    c.planned_revenue as total_revenue,
                    c.planned_revenue*(c.probability/100) as expected_revenue,
                    c.create_date as create_date,
                    extract('epoch' from (c.date_closed-c.create_date))/(3600*24) as  delay_close,
                    abs(extract('epoch' from (c.date_deadline - c.date_closed))/(3600*24)) as  delay_expected,
                    extract('epoch' from (c.date_open-c.create_date))/(3600*24) as  delay_open,
                    c.lost_reason
                FROM
                    crm_lead c
                WHERE c.active = 'true'
                GROUP BY c.id
            )""")
