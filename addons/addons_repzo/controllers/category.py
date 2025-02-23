from odoo import http
from odoo.http import request
from marshmallow import ValidationError
import json
import logging
from .marshmallow.ProductValidation import CategorySchema

_logger = logging.getLogger(__name__)


class CategoryEndpoint(http.Controller):
    def __init__(self):
        self.extra_errors_message = []
        self.extra_errors = False

    @http.route('/api/get_all_categories', type='json', auth='none', methods=['GET'])
    def get_all_categories(self):
        try:
            categories = request.env['product.category'].sudo().search([])
            categories_data = [{
                "id": category.id,
                "_id": category._id,
                "name": category.name or "",
                "local_name": category.local_name or "",
                "type": category.type or "",
                # "photo": category.photo or "",
                # "icon": category.icon or "",
                "position": category.position or 0,  # Assuming a default position of 0
                "createdAt": category.create_date.isoformat() if category.create_date else None,
                "updatedAt": category.write_date.isoformat() if category.write_date else None,
            } for category in categories]

            return {
                "status": "success",
                "data": categories_data,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/get_category_by_id/<int:category_id>', type='json', auth='none', methods=['GET'])
    def get_category_by_id(self, category_id):
        try:
            category = request.env['product.category'].sudo().browse(
                category_id)
            if not category.exists():
                return {"status": "error", "message": "Category not found."}

            category_data = {
                "id": category.id,
                "_id": category._id,
                "name": category.name or "",
                "type": category.type or "",
                "local_name": category.local_name or "",
                # "photo": category.photo or "",
                # "icon": category.icon or "",
                "position": category.position or 0,  # Assuming a default position of 0
                "createdAt": category.create_date.isoformat() if category.create_date else None,
                "updatedAt": category.write_date.isoformat() if category.write_date else None,
            }

            return {"status": "success", "data": category_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/add_category', type='json', auth='none', methods=['POST'])
    def add_category(self):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.debug("@@Data: %s", data)

            # Validate the data using Marshmallow
            schema = CategorySchema()
            # This will raise a ValidationError if validation fails
            schema.load(data)

            category_vals = {
                "_id": data.get('_id'),
                'name': data.get('name'),
                'local_name': data.get('local_name'),
                # 'photo': data.get('photo'),
                'local_name': data.get('local_name'),
                'type': data.get('type'),

            }

            new_category = request.env['product.category'].sudo().create(
                category_vals)

            return {
                "status": "success",
                "category": {
                    "id": new_category.id,
                    "name": new_category.name,
                    "local_name": new_category.local_name or "",
                    "type": new_category.type or "",
                    # "photo": new_category.photo or "",
                    # "icon": new_category.icon or "",
                    "createdAt": new_category.create_date.isoformat() if new_category.create_date else None,
                    "updatedAt": new_category.write_date.isoformat() if new_category.write_date else None,
                }
            }

        except ValidationError as err:
            return {"status": "error", "message": err.messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/update_category/<int:category_id>', type='json', auth='none', methods=['PUT'])
    def update_category(self, category_id):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.debug("@@Data: %s", data)

            # Validate the data using Marshmallow
            schema = CategorySchema()
            # This will raise a ValidationError if validation fails
            schema.load(data)

            existing_category = request.env['product.category'].sudo().browse(
                category_id)
            if not existing_category.exists():
                return {"status": "error", "message": "Category not found."}

            existing_category.write({
                'name': data.get('name', existing_category.name),
                'local_name': data.get('local_name', existing_category.local_name),
                'photo': data.get('photo', existing_category.photo),
                'icon': data.get('icon', existing_category.icon),
                'position': data.get('position', existing_category.position),
            })

            return {
                "status": "success",
                "category": {
                    "id": existing_category.id,
                    "name": existing_category.name,
                    "local_name": existing_category.local_name or "",
                    "photo": existing_category.photo or "",
                    "icon": existing_category.icon or "",
                    "position": existing_category.position or 0,
                    "createdAt": existing_category.create_date.isoformat() if existing_category.create_date else None,
                    "updatedAt": existing_category.write_date.isoformat() if existing_category.write_date else None,
                }
            }

        except ValidationError as err:
            return {"status": "error", "message": err.messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/delete_category/<int:category_id>', type='json', auth='none', methods=['DELETE'])
    def delete_category(self, category_id):
        try:
            existing_category = request.env['product.category'].sudo().browse(
                category_id)
            if not existing_category.exists():
                return {"status": "error", "message": "Category not found."}

            existing_category.unlink()  # Delete the category record

            return {"status": "success", "message": "Category deleted successfully."}

        except Exception as e:
            return {"status": "error", "message": str(e)}
