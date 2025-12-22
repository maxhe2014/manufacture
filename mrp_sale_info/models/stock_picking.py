# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Use sale_id field provided by sale_stock module to avoid duplicate definition
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_id.partner_id",
        string="Customer",
        store=True,
        help="Customer of the sale order"
    )
    commitment_date = fields.Datetime(
        related="sale_id.commitment_date",
        string="Commitment Date",
        store=True,
        help="Promised delivery date of the sale order"
    )
    client_order_ref = fields.Char(
        related="sale_id.client_order_ref",
        string="Customer Reference",
        store=True,
        help="Reference number provided by the customer"
    )

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Extend search functionality to support customer reference search"""
        args = args or []
        domain = []
        
        if name:
            # Search by customer reference
            domain = ['|', ('name', operator, name), ('client_order_ref', operator, name)]
            
        return super(StockPicking, self)._name_search(
            name, args + domain, operator=operator, limit=limit, name_get_uid=name_get_uid
        )