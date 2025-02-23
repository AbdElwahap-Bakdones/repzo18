from odoo import http
from odoo.http import request
from .marshmallow.ProductValidation import ProductCreateValidationSchema
from marshmallow import ValidationError
from werkzeug.wrappers import Response

import json
import logging

_logger = logging.getLogger(__name__)


class ProductEndpoint(http.Controller):
    def __init__(self):
        self.extra_errors_message = []
        self.extra_errors = False

    # @http.route('/api/get_all_products', type='json', auth='none', methods=['GET'])
    # def get_all_products(self):
    #     try:
    #         # Pagination parameters
    #         per_page = int(request.httprequest.args.get('per_page', 10))
    #         current_page = int(request.httprequest.args.get('page', 1))
    #         offset = (current_page - 1) * per_page

    #         # Fetching all products
    #         products = request.env['product.product'].sudo().search(
    #             [], offset=offset, limit=per_page)
    #         total_result = request.env['product.product'].sudo(
    #         ).search_count([])

    #         products_data = []
    #         for product in products:
    #             products_data.append({
    #                 "_id": product.id,
    #                 "name": product.name or "",
    #                 "price": product.list_price or 0.0,
    #                 "description": product.description_sale or "",
    #                 "category_id": product.categ_id.id if product.categ_id else None,
    #                 "active": product.active,
    #                 "createdAt": product.create_date.isoformat() if product.create_date else None,
    #                 "updatedAt": product.write_date.isoformat() if product.write_date else None,
    #             })

    #         # Constructing the response
    #         response = {
    #             "total_result": total_result,
    #             "current_count": len(products_data),
    #             "total_pages": (total_result + per_page - 1) // per_page,
    #             "current_page": current_page,
    #             "per_page": per_page,
    #             "data": products_data,
    #         }

    #         return response

    #     except Exception as e:
    #         return {"status": "error", "message": str(e)}

    @http.route('/api/get_all_products', type='json', auth='none', methods=['GET'])
    def get_all_products(self):
        try:
            # Pagination parameters
            per_page = int(request.httprequest.args.get('per_page', 10))
            current_page = int(request.httprequest.args.get('page', 1))
            offset = (current_page - 1) * per_page

            # Filtering parameters
            active = request.httprequest.args.get('active', None)
            category_id = request.httprequest.args.get('category', None)
            sub_category_id = request.httprequest.args.get(
                'sub_category', None)
            search_query = request.httprequest.args.get('search', None)
            with_default_variant = request.httprequest.args.get(
                'withDefaultVariant', 'false').lower() == 'true'
            sort_by = request.httprequest.args.get('sort', 'createdAt')

            # Build domain for search
            domain = []

            # Filter by active status
            if active is not None:
                domain.append(('active', '=', active.lower() == 'true'))

            # Filter by category
            if category_id:
                domain.append(('categ_id', '=', category_id))

            # Filter by sub-category
            if sub_category_id:
                # Assuming there's a sub-category field
                domain.append(('sub_categ_id', '=', sub_category_id))

            # Search by name
            if search_query:
                domain.append(('name', 'ilike', search_query))

            # Fetching products based on the domain
            products = request.env['product.product'].sudo().search(
                domain, offset=offset, limit=per_page)

            total_result = request.env['product.product'].sudo(
            ).search_count(domain)

            products_data = []
            for product in products:
                product_data = {
                    "_id": product.id,
                    "name": product.name or "",
                    "price": product.list_price or 0.0,
                    "description": product.description_sale or "",
                    "category_id": product.categ_id.id if product.categ_id else None,
                    "active": product.active,
                    "createdAt": product.create_date.isoformat() if product.create_date else None,
                    "updatedAt": product.write_date.isoformat() if product.write_date else None,
                }

                # Include default variant if specified
                if with_default_variant:
                    default_variant = product.product_tmpl_id.product_variant_ids.filtered(
                        lambda v: v.id == product.id)
                    product_data['default_variant'] = default_variant.id if default_variant else None

                products_data.append(product_data)

            # Constructing the response
            response = {
                "total_result": total_result,
                "current_count": len(products_data),
                "total_pages": (total_result + per_page - 1) // per_page,
                "current_page": current_page,
                "per_page": per_page,
                "data": products_data,
            }

            return response

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/get_product_by_id/<int:product_id>', type='json', auth='none', methods=['GET'])
    def get_product_by_id(self, product_id):
        try:
            product = request.env['product.product'].sudo().browse(product_id)
            if not product.exists():
                return {"status": "error", "message": "Product not found."}

            product_data = {
                "_id": product.id,
                "name": product.name or "",
                "price": product.list_price or 0.0,
                "description": product.description_sale or "",
                "category_id": product.categ_id.id if product.categ_id else None,
                "active": product.active,
                "createdAt": product.create_date.isoformat() if product.create_date else None,
                "updatedAt": product.write_date.isoformat() if product.write_date else None,
            }

            return {"status": "success", "data": product_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/add_product', type='json', auth='none', methods=['POST'])
    def add_product(self):
        try:
            # Load and validate incoming data
            _logger.debug("@start@: %s",)
            schema = ProductCreateValidationSchema()

            _logger.debug("@0@: %s",)

            data = json.loads(request.httprequest.data.decode('utf-8'))

            # _logger.debug("@@Data: %s", data)
            _logger.debug("@010@: %s",)

            validated_data = schema.load(data)
            _logger.debug("@1@: %s", validated_data)

            # Prepare product values
            product_vals = {
                'name': validated_data['name'],
                'local_name': validated_data.get('local_name', ''),
                'categ_id': validated_data['category'],
                'brand_id': validated_data['brand'],
                'barcode': validated_data.get('barcode', ''),
                'default_code': validated_data.get('sku', ''),
                # Convert image URL to binary
                # 'image_1920': self._get_image_binary(validated_data.get('product_img')),
                # measure_unit_ID
                # 'uom_id': validated_data.get('sv_measureUnit'),
                # 'uom_po_id': request.env.ref('uom.product_uom_unit').id,  # Set default UoM
                # tax_id
                'taxes_id': [(6, 0, validated_data.get('sv_tax', []))],
                'frozen_pre_sales': validated_data.get('frozen_pre_sales', False),
                'frozen_sales': validated_data.get('frozen_sales', False),
            }
            _logger.debug("@2@: %s", product_vals)

            # Create the new product
            new_product = request.env['product.template'].sudo().create(
                product_vals)
            _logger.debug("@3@: %s", new_product.id)

            # Handle variants
            # if 'variants' in validated_data:
            #     for variant in validated_data['variants']:
            #         variant_vals = {
            #             # 'product_tmpl_id': new_product.id,
            #             'name': variant['name'],
            #             'barcode': variant.get('barcode', ''),
            #             # price multiplied by 1000 before sending
            #             'list_price': variant['price'],
            #             'default_code': variant.get('sku', ''),
            #             'sequence': variant.get('position', 0),
            #         }
            #         request.env['product.product'].sudo().create(variant_vals)

            return {"status": "success", "product_id": new_product.id}

        except ValidationError as err:
            return {"status": "error", "errors": err.messages}
        except Exception as e:
            _logger.error("Error while adding product: %s", str(e))
            return {"status": "error", "message": str(e)}

    # def _get_image_binary(self, image_url):
    #     # Implement logic to convert image URL to binary data
    #     # For example, you can use requests to fetch the image and convert it
    #     return None  #

    @http.route('/api/update_product/<int:product_id>', type='json', auth='none', methods=['PUT'])
    def update_product(self, product_id):
        try:
            schema = ProductCreateValidationSchema()
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.debug("@@Data: %s", data)

            validated_data = schema.load(data)

            existing_product = request.env['product.product'].sudo().browse(
                product_id)
            if not existing_product:
                return {"status": "error", "message": "Product not found."}

            existing_product.write({
                'name': validated_data['name'],
                'list_price': validated_data['price'],
                'description_sale': validated_data['description'],
                'categ_id': validated_data['category_id'],
                'active': validated_data.get('active', existing_product.active),
            })

            return {"status": "success", "product_id": existing_product.id}

        except ValidationError as err:
            return {"status": "error", "errors": err.messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/delete_product/<int:product_id>', type='json', auth='none', methods=['DELETE'])
    def delete_product(self, product_id):
        try:
            existing_product = request.env['product.product'].sudo().browse(
                product_id)
            if not existing_product:
                return {"status": "error", "message": "Product not found."}

            existing_product.unlink()  # Delete the product record

            return {"status": "success", "message": "Product deleted successfully."}

        except Exception as e:
            return {"status": "error", "message": str(e)}
