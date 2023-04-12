import time
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError

class InventoryMovement(models.TransientModel):
    _name = 'inventory_movement.report'
    _description = 'Inventory stock movement Report'

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,default=lambda self: self.env.user.company_id.id)
    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'),required=True)
    date_to = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'),required=True)
    product = fields.Many2one('product.product',string='Product',required=True)
    stock_warehouse = fields.Many2one('stock.warehouse',string='Warehouse',required=True)
    warehouse_id = fields.Integer()
    stock_location = fields.Many2one('stock.location', string='Location',required=True,domain="['&', ('usage', '=', 'internal'),('location_id', '=', warehouse_id)]")
    stock_move_id = fields.Many2one('stock.move')

    @api.onchange('stock_warehouse')
    def warehouse_location_change(self):
        if self.stock_warehouse:
            self.warehouse_id = self.stock_warehouse.view_location_id
            self.stock_location = ''
        else:
            self.warehouse_id = ''
            self.stock_location = ''

    def report_values(self,data):
        company_id = data['company']
        start = data['date_from']
        end = data['date_to']
        stock_location = data['stock_location']
        stock_warehouse = data['stock_warehouse']
        product = data['product_id']

        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.max.time())

        # code commented by jagadishmagesh1999@gmail.com
        value_in = self.env['stock.valuation.layer'].search(
            [
                ('product_id', '=', product.id),
                ('company_id', '=', company_id.id),
                ("quantity", '>', 0),
                ('value', '>', 0),
                ('create_date', '>=', start),
                ('create_date', '<=', end),
            ])
        value_out = self.env['stock.valuation.layer'].search(
            [
                ('product_id', '=', product.id),
                ('company_id', '=', company_id.id),
                ("quantity", '<=', 0),
                ('value', '<=', 0),
                ('create_date', '>=', start),
                ('create_date', '<=', end),
            ])

        data['cost_in_values'] = self.cost_in_values(value_in)
        data['out_values'] = self.cost_out_values(value_out)

        return data

    # code commented by jagadishmagesh1999@gmail.com

    def cost_in_values(self,cost_vals):
        vals = []
        for rec in cost_vals:
            cost_vals = {}
            cost_vals['create_date'] = rec.stock_move_id.date
            cost_vals['value'] = rec.value
            cost_vals['quantity'] = rec.quantity
            cost_vals['origin'] = rec.stock_move_id.origin
            cost_vals['inventory_move'] = rec.stock_move_id.reference
            cost_vals['location_id'] = rec.stock_move_id.location_id.name
            cost_vals['location_dest_id'] = rec.stock_move_id.location_dest_id.name
            vals.append(cost_vals)
            if rec.stock_move_id.partner_id:
                cost_vals['partner_name'] = rec.stock_move_id.partner_id.name
            elif rec.stock_move_id.picking_id.partner_id:
                cost_vals['partner_name'] = rec.stock_move_id.picking_id.partner_id.name
            else:
                cost_vals['partner_name'] = '-'
        return vals

    def cost_out_values(self, cost_vals):
        vals = []
        for rev in cost_vals:
                cost_vals = {}
                # cost_vals['voucher_number'] = rev.description
                cost_vals['create_date'] = rev.stock_move_id.date
                cost_vals['value'] = rev.value
                cost_vals['quantity'] = rev.quantity
                cost_vals['stock_move'] = rev.stock_move_id.origin
                cost_vals['inventory_move'] = rev.stock_move_id.reference
                # cost_vals['partner_name'] = rev.stock_move_id.group_id.button_box.partner_id
                cost_vals['location_id'] = rev.stock_move_id.location_id.name
                cost_vals['location_dest_id'] = rev.stock_move_id.location_dest_id.name
                vals.append(cost_vals)
                if rev.stock_move_id.partner_id:
                    cost_vals['partner_name'] = rev.stock_move_id.partner_id.name
                elif rev.stock_move_id.picking_id.partner_id:
                    cost_vals['partner_name'] = rev.stock_move_id.picking_id.partner_id.name
                else:
                    cost_vals['partner_name'] = '-'
        return vals

    def aged_report_xlx(self):
        if self.date_from > self.date_to:
            raise UserError(_('Sorry,From date must be greater than To date !'))
        data = {}
        opening_qty_in = 0
        opening_qty_out = 0
        closing_qty_in = 0
        closing_qty_out = 0
        invent_adjust_cl = 0
        invent_adjust_op = 0
        dest_invent_adjust_cl = 0
        dest_invent_adjust_op = 0
        mo_cl = 0
        mo_op = 0
        scrap_dest_cl = 0
        scrap_dest_op = 0
        purchase_transfer_dest_cl= 0
        purchase_transfer_dest_op= 0
        opening_in = self.env['stock.move'].sudo().search([
            # (('reference', '=', ('INV:Inventory', 'Product Quantity Updated')) and
            ('picking_type_id.code','=','incoming'),
            ('product_id','=',self.product.id),
            ('location_dest_id','=',self.stock_location.id),
            ('state', '=', 'done'),
            ('warehouse_id','=',self.stock_warehouse.id),('date','<',self.date_from)])
        opening_out = self.env['stock.move'].sudo().search([
            # (('reference', '=', ('INV:Inventory', 'Product Quantity Updated')) and
            ('picking_type_id.code', 'in', ('outgoing','mrp_operation')), ('product_id', '=', self.product.id),
            ('location_id', '=', self.stock_location.id), ('warehouse_id', '=', self.stock_warehouse.id),
            ('state', '=', 'done'),
            ('date', '<', self.date_from)])
        closing_in = self.env['stock.move'].sudo().search([
            # (('reference', '=', ('INV:Inventory', 'Product Quantity Updated')) and
            ('picking_type_id.code', '=', 'incoming'), ('product_id', '=', self.product.id),
            ('location_dest_id', '=', self.stock_location.id), ('warehouse_id', '=', self.stock_warehouse.id),
            ('state', '=', 'done'),
            ('date', '<=', self.date_to)])
        closing_out = self.env['stock.move'].sudo().search([
            # [(('reference', '=', ('INV:Inventory', 'Product Quantity Updated')) and
            ('picking_type_id.code', 'in', ('outgoing','mrp_operation')), ('product_id', '=', self.product.id),
            ('location_id', '=', self.stock_location.id), ('warehouse_id', '=', self.stock_warehouse.id),
            ('state', '=', 'done'),
            ('date', '<=', self.date_to)])

        inv_adju_id = self.env['stock.location'].search([('usage', '=', 'inventory')], limit=1)
        closing_inven_adjust = self.env['stock.move'].sudo().search(
            [('product_id', '=', self.product.id), ('location_id', '=', inv_adju_id.id),
             ('state', '=', 'done'),('date', '<=', self.date_to)])
        # below codes are commented by jagadishmagesh1999@gmail.com
        opening_inven_adjust = self.env['stock.move'].sudo().search(
            [('product_id', '=', self.product.id), ('location_id', '=', inv_adju_id.id),
             ('state', '=', 'done'),('date', '<', self.date_from)])
        dest_closing_inven_adjust = self.env['stock.move'].sudo().search(
            [('product_id', '=', self.product.id), ('location_dest_id', '=', inv_adju_id.id),
             ('state', '=', 'done'),
             ('date', '<=', self.date_to)])
        dest_opening_inven_adjust = self.env['stock.move'].sudo().search(
            [('product_id', '=', self.product.id), ('location_dest_id', '=', inv_adju_id.id),('state', '=', 'done'),
             ('date', '<', self.date_from)])

        manufacturing_order_id = self.env['stock.location'].search([('usage', '=', 'production')], limit=1)
        mo_open = self.env['stock.move'].sudo().search([
            ('product_id', '=', self.product.id),
            ('location_id', '=', manufacturing_order_id.id),
            ('state', '=', 'done'),
            ('date', '<', self.date_from)])
        mo_close = self.env['stock.move'].sudo().search([
            ('product_id', '=', self.product.id),
            ('location_id', '=', manufacturing_order_id.id),
            ('state', '=', 'done'),
            ('date', '<=', self.date_to)])

        scrap_id = self.env['stock.location'].search([('name', '=', 'Scrap'),
                                                               ('complete_name', '=', 'Virtual Locations/Scrap'),
                                                               ('usage', '=', 'inventory')
                                                               ], limit=1)
        scrap_dest_closing = self.env['stock.move'].sudo().search(
            [('product_id', '=', self.product.id), ('location_dest_id', '=', scrap_id.id),
             ('state', '=', 'done'),
             ('date', '<=', self.date_to)])
        scrap_dest_opening = self.env['stock.move'].sudo().search(
            [('product_id', '=', self.product.id), ('location_dest_id', '=', scrap_id.id),
             ('state', '=', 'done'),
             ('date', '<', self.date_from)])

        purchase_transfer_id = self.env['stock.location'].search([('name', '=', 'Vendors'),
                                                                           ('complete_name', '=',
                                                                            'Partner Locations/Vendors'),
                                                                           ('usage', '=', 'supplier')
                                                                           ], limit=1)
        purchase_transfer_dest_closing = self.env['stock.move'].sudo().search(
            [('product_id', '=', self.product.id), ('location_dest_id', '=', purchase_transfer_id.id),
             ('state', '=', 'done'),
             ('date', '<=', self.date_to)])
        purchase_transfer_dest_opening = self.env['stock.move'].sudo().search(
            [('product_id', '=', self.product.id), ('location_dest_id', '=', purchase_transfer_id.id),
             ('state', '=', 'done'),
             ('date', '<', self.date_from)])

        for rec in closing_inven_adjust:
            invent_adjust_cl += rec.product_qty
        for rec_1 in opening_inven_adjust:
            invent_adjust_op += rec_1.product_qty

        for rec in dest_closing_inven_adjust:
            dest_invent_adjust_cl += rec.product_qty
        for rec_1 in dest_opening_inven_adjust:
            dest_invent_adjust_op += rec_1.product_qty

        for rec in mo_close:
            mo_cl += rec.product_qty
        for rec_1 in mo_open:
            mo_op += rec_1.product_qty

        for rec in scrap_dest_closing:
            scrap_dest_cl += rec.product_qty
        for rec_1 in scrap_dest_opening:
            scrap_dest_op += rec_1.product_qty

        for rec in purchase_transfer_dest_closing:
            purchase_transfer_dest_cl += rec.product_qty
        for rec_1 in purchase_transfer_dest_opening:
            purchase_transfer_dest_op += rec_1.product_qty

        for rec in opening_in:
            opening_qty_in += rec.product_qty
        for rec in opening_out:
            opening_qty_out += rec.product_qty
        for rec in closing_in:
            closing_qty_in += rec.product_qty
        for rec in closing_out:
            closing_qty_out += rec.product_qty

        opening_balance = (opening_qty_in + invent_adjust_op + mo_op
                           - dest_invent_adjust_op
                           - scrap_dest_op
                           - purchase_transfer_dest_op) - opening_qty_out
        closing_balance = (closing_qty_in + invent_adjust_cl + mo_cl - dest_invent_adjust_cl
                           - scrap_dest_cl
                           - purchase_transfer_dest_cl) - closing_qty_out

        open_balance = format(opening_balance, '.3f')
        close_balance = format(closing_balance, '.3f')

        _in_value = self.env['stock.valuation.layer'].search([
            ("product_id", "=", self.product.id),
            ("quantity", '>', 0),
            ('value', '>', 0),
            ('create_date', '<=', self.date_to)
        ])
        _out_value = self.env['stock.valuation.layer'].search([
            ("product_id", "=", self.product.id),
            ("quantity", '<', 0),
            ('value', '<', 0),
            ('create_date', '<=', self.date_to)
        ])

        _in_val = 0
        _out_val = 0
        for rec in _in_value:
            _in_val += rec.value
        for rec in _out_value:
            _out_val += rec.value

        t_out = _in_val + _out_val
        total_value = format(t_out, '.2f')

        data['date_from'] =self.date_from
        data['date_to'] =self.date_to
        data['company'] =self.company_id
        # data['logo'] =self.logo
        data['product_id'] =self.product
        data['product_default_code'] =self.product.default_code
        data['product_name_without_defaultcode'] =self.product.name
        data['product_name'] =self.product.display_name
        data['stock_location'] =self.stock_location
        data['stock_warehouse'] =self.stock_warehouse
        data["stock_move_id"] =self.stock_move_id
        data['open_balance'] = str(open_balance)
        data['close_balance'] = str(close_balance)
        data['t_out'] = str(total_value)
        # data['opening_balance'] = str(opening_balance)
        # data['closing_balance'] = str(closing_balance)
        data = self.report_values(data)
        return self.env.ref('stock_movement_and_valuation_report.inventory_movement').with_context(landscape=True).report_action(self, data=data)