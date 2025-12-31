# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    source_procurement_group_id = fields.Many2one(
        comodel_name="procurement.group",
        readonly=True,
    )
    
    @api.depends('source_procurement_group_id', 'move_finished_ids.move_dest_ids.group_id',
                 'source_procurement_group_id.sale_id', 'source_procurement_group_id.sale_id.partner_id',
                 'source_procurement_group_id.sale_id.commitment_date', 'source_procurement_group_id.sale_id.client_order_ref',
                 'move_finished_ids.move_dest_ids.group_id.sale_id', 'move_finished_ids.move_dest_ids.group_id.sale_id.partner_id',
                 'move_finished_ids.move_dest_ids.group_id.sale_id.commitment_date', 'move_finished_ids.move_dest_ids.group_id.sale_id.client_order_ref')
    def _compute_sale_info(self):
        """为现有制造订单自动计算销售信息"""
        for production in self:
            # 方法1：优先使用已有的 source_procurement_group_id
            if production.source_procurement_group_id:
                procurement_group = production.source_procurement_group_id
            else:
                # 方法2：通过成品移动链查找采购组
                procurement_group = production.move_finished_ids.move_dest_ids.group_id[:1]
                
                # 方法3：如果成品移动链没有找到，尝试通过原材料移动链查找
                if not procurement_group:
                    procurement_group = production.move_raw_ids.group_id[:1]
            
            # 设置销售信息
            if procurement_group and procurement_group.sale_id:
                production.sale_id = procurement_group.sale_id
                production.partner_id = procurement_group.sale_id.partner_id
                production.commitment_date = procurement_group.sale_id.commitment_date
                production.client_order_ref = procurement_group.sale_id.client_order_ref
            else:
                # 如果没有找到关联的销售订单，清空所有字段
                production.sale_id = False
                production.partner_id = False
                production.commitment_date = False
                production.client_order_ref = False

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
        readonly=True,
        store=True,
        compute='_compute_sale_info'
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        store=True,
        compute='_compute_sale_info'
    )
    commitment_date = fields.Datetime(
        string="Commitment Date",
        store=True,
        compute='_compute_sale_info'
    )
    client_order_ref = fields.Char(
        string="Customer Reference",
        store=True,
        compute='_compute_sale_info'
    )

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Extend search functionality to support customer reference search"""
        args = args or []
        domain = []
        
        if name:
            # Search by customer reference
            domain = ['|', ('name', operator, name), ('client_order_ref', operator, name)]
            
        return super(MrpProduction, self)._name_search(
            name, args + domain, operator=operator, limit=limit, name_get_uid=name_get_uid
        )