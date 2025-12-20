# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    source_procurement_group_id = fields.Many2one(
        comodel_name="procurement.group",
        readonly=True,
    )
    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
        readonly=True,
        store=True,
        related="source_procurement_group_id.sale_id",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_id.partner_id",
        string="Customer",
        store=True,
    )
    commitment_date = fields.Datetime(
        related="sale_id.commitment_date", string="Commitment Date", store=True
    )
    client_order_ref = fields.Char(
        related="sale_id.client_order_ref", string="Customer Reference", store=True
    )

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """扩展搜索功能，支持客户参考号搜索"""
        args = args or []
        domain = []
        
        if name:
            # 搜索客户参考号
            domain = ['|', ('name', operator, name), ('client_order_ref', operator, name)]
            
        return super(MrpProduction, self)._name_search(
            name, args + domain, operator=operator, limit=limit, name_get_uid=name_get_uid
        )