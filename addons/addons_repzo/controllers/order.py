from odoo import http
from odoo.http import request
import json
import logging
from .marshmallow.OrderValidation import OrderCreateValidationSchema
from marshmallow import ValidationError
_logger = logging.getLogger(__name__)


class OrderEndpoint(http.Controller):
    @http.route('/api/get_all_orders', type='json', auth='none', methods=['GET'])
    def get_all_orders(self):
        try:
            # Pagination parameters
            per_page = int(request.httprequest.args.get('per_page', 10))
            current_page = int(request.httprequest.args.get('page', 1))
            offset = (current_page - 1) * per_page

            # Fetching orders
            orders = request.env['sale.order'].sudo().search(
                [], offset=offset, limit=per_page)
            total_result = request.env['sale.order'].sudo().search_count([])

            orders_data = []
            for order in orders:
                orders_data.append({
                    "_id": order.id,
                    "order_name": order.name or "",
                    "amount_total": order.amount_total or 0.0,
                    "state": order.state or "",
                    "partner_id": order.partner_id.id if order.partner_id else None,
                    "createdAt": order.create_date.isoformat() if order.create_date else None,
                    "updatedAt": order.write_date.isoformat() if order.write_date else None,
                })

            # Constructing the response
            response = {
                "total_result": total_result,
                "current_count": len(orders_data),
                "total_pages": (total_result + per_page - 1) // per_page,
                "current_page": current_page,
                "per_page": per_page,
                "data": orders_data,
            }

            return response

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/get_order_by_id/<int:order_id>', type='json', auth='none', methods=['GET'])
    def get_order_by_id(self, order_id):
        try:
            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                return {"status": "error", "message": "Order not found."}

            order_data = {
                "_id": order.id,
                "order_name": order.name or "",
                "amount_total": order.amount_total or 0.0,
                "state": order.state or "",
                "partner_id": order.partner_id.id if order.partner_id else None,
                "createdAt": order.create_date.isoformat() if order.create_date else None,
                "updatedAt": order.write_date.isoformat() if order.write_date else None,
            }

            return {"status": "success", "data": order_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/add_order', type='json', auth='user', methods=['POST'])
    def create_order(self, **kwargs):
        schema = OrderCreateValidationSchema()
        try:
            # Validate the incoming data
            print("@!@!")
            data = json.loads(request.httprequest.data.decode('utf-8'))
            validated_data = schema.load(data)

            # Process the validated data
            order_data = {
                'partner_id': validated_data['partner_id'],
                'order_line': [(0, 0, line) for line in validated_data['order_line']],
            }
            order = request.env['sale.order'].create(order_data)
            order.action_confirm()
            return {'order_id': order.id}
        except ValidationError as err:
            return {"status": "error", "errors": err.messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/add_order_invoice', type='json', auth='user', methods=['POST'])
    def create_order_with_invoice_and_picking(self, **kwargs):
        schema = OrderCreateValidationSchema()

        try:
            # Decode and validate the incoming data
            data = json.loads(request.httprequest.data.decode('utf-8'))
            validated_data = schema.load(data)

            # Step 1: Create the order
            order_data = {
                'partner_id': validated_data['partner_id'],
                'order_line': [(0, 0, {
                    'product_id': line['product_id'],
                    'product_uom_qty': line.get('quantity', 1),
                    'price_unit': line['price_unit']
                }) for line in validated_data['order_line']],
            }

            order = request.env['sale.order'].create(order_data)

            # Step 2: Confirm the order
            order.action_confirm()

            # Step 3: Validate stock picking (Inventory Movement)
            for picking in order.picking_ids:
                if picking.state == 'draft':
                    picking.action_confirm()  # Confirm picking if it's in draft

                if picking.state in ['confirmed', 'waiting', 'assigned']:
                    picking.action_assign()  # Assign stock (if available)

                if picking.state == 'assigned':  # Stock is assigned, now validate
                    for move in picking.move_ids_without_package:
                        move_qty = move.product_uom_qty  # Get quantity from stock.move
                        for move_line in move.move_line_ids:
                            # Set qty_done on move lines using move's product_uom_qty
                            move_line.write({'qty_done': move_qty})
                    picking.button_validate()  # Validate the picking (complete delivery)

            # Step 4: Create an invoice
            invoice = None
            if order.invoice_status != 'no':
                invoice = order._create_invoices()
                invoice.action_post()  # Post the invoice

            return {
                "status": "success",
                "order_id": order.id,
                "invoice_id": invoice.id if invoice else None,
                "picking_ids": [picking.id for picking in order.picking_ids],
            }

        except ValidationError as err:
            return {"status": "error", "errors": err.messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/update_order/<int:order_id>', type='json', auth='none', methods=['PUT'])
    def update_order(self, order_id):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            existing_order = request.env['sale.order'].sudo().browse(order_id)
            if not existing_order.exists():
                return {"status": "error", "message": "Order not found."}

            existing_order.write({
                'partner_id': data.get('partner_id', existing_order.partner_id.id),
                'order_line': [(0, 0, {
                    'product_id': line['product_id'],
                    'product_uom_qty': line['quantity'],
                    'price_unit': line['price_unit'],
                }) for line in data.get('order_lines', [])],
            })

            return {"status": "success", "order_id": existing_order.id}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/delete_order/<int:order_id>', type='json', auth='none', methods=['DELETE'])
    def delete_order(self, order_id):
        try:
            existing_order = request.env['sale.order'].sudo().browse(order_id)
            if not existing_order.exists():
                return {"status": "error", "message": "Order not found."}

            existing_order.unlink()

            return {"status": "success", "message": "Order deleted successfully."}

        except Exception as e:
            return {"status": "error", "message": str(e)}
