from odoo import http
from odoo.http import request
from marshmallow import ValidationError
import json
import logging
from .marshmallow.ProductValidation import BrandSchema

_logger = logging.getLogger(__name__)


class BrandEndpoint(http.Controller):
    def __init__(self):
        self.extra_errors_message = []
        self.extra_errors = False

    @http.route('/api/get_all_brands', type='json', auth='none', methods=['GET'])
    def get_all_brands(self):
        try:
            brands = request.env['product.brand'].sudo().search([])
            brands_data = [{
                "id": brand.id,
                "_id": brand._id,
                "name": brand.name or "",
                "company_namespace": [company.name for company in brand.company_namespace],
                "createdAt": brand.create_date.isoformat() if brand.create_date else None,
                "updatedAt": brand.write_date.isoformat() if brand.write_date else None,

            } for brand in brands]

            return {
                "status": "success",
                "data": brands_data,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/get_brand_by_id/<int:brand_id>', type='json', auth='none', methods=['GET'])
    def get_brand_by_id(self, brand_id):
        try:
            brand = request.env['product.brand'].sudo().browse(brand_id)
            if not brand.exists():
                return {"status": "error", "message": "Brand not found."}

            brand_data = {
                "id": brand.id,
                "name": brand.name or "",
                "company_namespace": [company.name for company in brand.company_namespace],
                "createdAt": brand.create_date.isoformat() if brand.create_date else None,
                "updatedAt": brand.write_date.isoformat() if brand.write_date else None,

            }

            return {"status": "success", "data": brand_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/add_brand', type='json', auth='none', methods=['POST'])
    def add_brand(self):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.debug("@@Data: %s", data)
            schema = BrandSchema()
            schema.load(data)
            brand_vals = {
                '_id': data.get('_id'),
                'name': data.get('name'),
                'disabled': data.get('disabled', False),
                # 'company_namespace': [(6, 0, data.get('company_namespace', []))],
            }

            new_brand = request.env['product.brand'].sudo().create(brand_vals)

            return {
                "status": "success",
                "brand": {
                    "_id": new_brand.id,
                    "name": new_brand.name,
                    "disabled": new_brand.disabled,
                    # "company_namespace": [company.name for company in new_brand.company_namespace],
                    "createdAt": new_brand.create_date.isoformat() if new_brand.create_date else None,
                    "updatedAt": new_brand.write_date.isoformat() if new_brand.write_date else None,
                }
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/update_brand/<int:brand_id>', type='json', auth='none', methods=['PUT'])
    def update_brand(self, brand_id):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.debug("@@Data: %s", data)

            existing_brand = request.env['product.brand'].sudo().browse(
                brand_id)
            if not existing_brand:
                return {"status": "error", "message": "Brand not found."}

            existing_brand.write({
                'name': data.get('name', existing_brand.name),
                'disabled': data.get('disabled', existing_brand.disabled),
                # Update company namespaces
                'company_namespace': [(6, 0, data.get('company_namespace', []))],
            })

            return {
                "status": "success",
                "brand": {
                    "_id": existing_brand.id,
                    "name": existing_brand.name,
                    "disabled": existing_brand.disabled,
                    "company_namespace": [company.name for company in existing_brand.company_namespace],
                    "createdAt": existing_brand.create_date.isoformat() if existing_brand.create_date else None,
                    "updatedAt": existing_brand.write_date.isoformat() if existing_brand.write_date else None,
                }
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/delete_brand/<int:brand_id>', type='json', auth='none', methods=['DELETE'])
    def delete_brand(self, brand_id):
        try:
            existing_brand = request.env['product.brand'].sudo().browse(
                brand_id)
            if not existing_brand:
                return {"status": "error", "message": "Brand not found."}

            existing_brand.unlink()  # Delete the brand record

            return {"status": "success", "message": "Brand deleted successfully."}

        except Exception as e:
            return {"status": "error", "message": str(e)}
