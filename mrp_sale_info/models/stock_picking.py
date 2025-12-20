# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # 使用sale_stock模块提供的sale_id字段，避免重复定义
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_id.partner_id",
        string="客户",
        store=True,
        help="销售订单的客户"
    )
    commitment_date = fields.Datetime(
        related="sale_id.commitment_date",
        string="承诺日期",
        store=True,
        help="销售订单的承诺交付日期"
    )
    client_order_ref = fields.Char(
        related="sale_id.client_order_ref",
        string="客户参考号",
        store=True,
        help="客户提供的参考号"
    )

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """扩展搜索功能，支持客户参考号搜索"""
        args = args or []
        domain = []
        
        if name:
            # 搜索客户参考号
            domain = ['|', ('name', operator, name), ('client_order_ref', operator, name)]
            
        return super(StockPicking, self)._name_search(
            name, args + domain, operator=operator, limit=limit, name_get_uid=name_get_uid
        )