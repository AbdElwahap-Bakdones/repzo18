from odoo import http
from odoo.http import request
from marshmallow import ValidationError
import json
import logging

_logger = logging.getLogger(__name__)


class InvoiceEndpoint(http.Controller):
    def __init__(self):
        self.extra_errors_message = []
        self.extra_errors = False

    @http.route('/api/get_all_invoices', type='json', auth='none', methods=['GET'])
    def get_all_invoices(self):
        try:
            # Pagination parameters
            per_page = int(request.httprequest.args.get('per_page', 10))
            current_page = int(request.httprequest.args.get('page', 1))
            offset = (current_page - 1) * per_page

            # Fetching invoices
            invoices = request.env['account.move'].sudo().search(
                [], offset=offset, limit=per_page)
            total_result = request.env['account.move'].sudo().search_count([])

            invoices_data = []
            for invoice in invoices:
                invoices_data.append({
                    "_id": invoice.id,
                    "invoice_number": invoice.name or "",
                    "amount_total": invoice.amount_total or 0.0,
                    "state": invoice.state or "",
                    "partner_id": invoice.partner_id.id if invoice.partner_id else None,
                    "createdAt": invoice.create_date.isoformat() if invoice.create_date else None,
                    "updatedAt": invoice.write_date.isoformat() if invoice.write_date else None,
                })

            # Constructing the response
            response = {
                "total_result": total_result,
                "current_count": len(invoices_data),
                "total_pages": (total_result + per_page - 1) // per_page,
                "current_page": current_page,
                "per_page": per_page,
                "data": invoices_data,
            }

            return response

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/get_invoice_by_id/<int:invoice_id>', type='json', auth='none', methods=['GET'])
    def get_invoice_by_id(self, invoice_id):
        try:
            invoice = request.env['account.move'].sudo().browse(invoice_id)
            if not invoice.exists():
                return {"status": "error", "message": "Invoice not found."}

            invoice_data = {
                "_id": invoice.id,
                "invoice_number": invoice.name or "",
                "amount_total": invoice.amount_total or 0.0,
                "state": invoice.state or "",
                "partner_id": invoice.partner_id.id if invoice.partner_id else None,
                "createdAt": invoice.create_date.isoformat() if invoice.create_date else None,
                "updatedAt": invoice.write_date.isoformat() if invoice.write_date else None,
            }

            return {"status": "success", "data": invoice_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/add_invoice', type='json', auth='user', methods=['POST'])
    def create_invoice(self, **kwargs):
        # Custom logic to process the data
        try:
            invoice_data = {
                'partner_id': kwargs.get('partner_id'),
                'move_type': 'out_invoice',
                'invoice_line_ids': [(0, 0, {
                    'product_id': kwargs.get('product_id'),
                    'quantity': kwargs.get('quantity'),
                    'price_unit': kwargs.get('price_unit'),
                })]
            }
            invoice = request.env['account.move'].create(invoice_data)
            return {'invoice_id': invoice.id}
        except ValidationError as err:
            return {"status": "error", "errors": err.messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/update_invoice/<int:invoice_id>', type='json', auth='none', methods=['PUT'])
    def update_invoice(self, invoice_id):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            existing_invoice = request.env['account.move'].sudo().browse(
                invoice_id)
            if not existing_invoice:
                return {"status": "error", "message": "Invoice not found."}

            existing_invoice.write({
                'partner_id': data.get('partner_id', existing_invoice.partner_id.id),
                'invoice_line_ids': [(0, 0, {
                    'product_id': line['product_id'],
                    'quantity': line['quantity'],
                    'price_unit': line['price_unit'],
                }) for line in data.get('invoice_lines', [])],
            })

            return {"status": "success", "invoice_id": existing_invoice.id}

        except ValidationError as err:
            return {"status": "error", "errors": err.messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/delete_invoice/<int:invoice_id>', type='json', auth='none', methods=['DELETE'])
    def delete_invoice(self, invoice_id):
        try:
            existing_invoice = request.env['account.move'].sudo().browse(
                invoice_id)
            if not existing_invoice:
                return {"status": "error", "message": "Invoice not found."}

            existing_invoice.unlink()  # Delete the invoice record

            return {"status": "success", "message": "Invoice deleted successfully."}

        except Exception as e:
            return {"status": "error", "message": str(e)}
