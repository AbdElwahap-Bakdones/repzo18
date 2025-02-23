import secrets
from odoo import http
from odoo.http import request
from .marshmallow.ContactsValidation import ContactCreateValidationSchema
from marshmallow import ValidationError
from werkzeug.wrappers import Response

import json
import logging
_logger = logging.getLogger(__name__)


class ContactCustomerEndpoint(http.Controller):
    def __init__(self):
        self.extra_errors_message = []
        self.extra_errors = False

    def existing_email_partner(self, validated_data):
        email = request.env['res.partner'].sudo().search([
            ('email', '=', validated_data['email']),
        ], limit=1)
        if email:
            self.extra_errors_message.append(
                {"email": ["This email is already in use."]})
            self.extra_errors = True
            return True
        return False

    def existing_phone_partner(self, validated_data):
        phone = request.env['res.partner'].sudo().search([
            ('phone', '=', validated_data['phone']),
        ], limit=1)
        if phone:
            self.extra_errors_message.append(
                {"phone": ["This phone number is already in use."]})
            self.extra_errors = True

            return True
        return False

    @http.route('/api/get_all_users', type='json', auth='none', methods=['GET'])
    def get_all_users(self):
        try:
            # Pagination parameters
            per_page = int(request.httprequest.args.get('per_page', 10))
            current_page = int(request.httprequest.args.get('page', 1))
            offset = (current_page - 1) * per_page

            # Fetching all partners
            partners = request.env['res.partner'].sudo().search(
                [], offset=offset, limit=per_page)
            total_result = request.env['res.partner'].sudo().search_count([])

            users_data = []
            for partner in partners:
                users_data.append({
                    "_id": partner.id,
                    # Assuming tags are stored in a many2many field
                    # "tags": partner.tags_ids.mapped('id'),
                    "disabled": partner.active is False,
                    "formatted_address": partner.contact_address or "No location",
                    "lat": partner.partner_latitude or 0,
                    "lng": partner.partner_longitude or 0,
                    # "location_verified": partner.location_verified,  # Custom field
                    # Assuming there's a relation to reps
                    # "assigned_to": partner.assigned_reps_ids.mapped('id'),
                    # "profile_pic": partner.profile_pic or None,
                    # "logo": partner.logo or None,
                    "website": partner.website or "",
                    "email": partner.email or "",
                    "comment": partner.comment or "",
                    "parent_client_id": partner.parent_id.id if partner.parent_id else None,
                    # "target_visit": partner.target_visit or 0,
                    # "geofencing_radius": partner.geofencing_radius or None,
                    # "price_tag": partner.price_tag or None,
                    # "status": partner.status or None,
                    # Assuming job_category is many2many
                    # "job_category": partner.job_category_ids.mapped('name'),
                    # Assuming availability_msl is many2many
                    # "availability_msl": partner.availability_msl_ids.mapped('id'),
                    # "territory": partner.territory or None,
                    # Assuming there's a relation to media
                    # "assigned_media": partner.assigned_media_ids.mapped('id'),
                    # Assuming there's a relation to products
                    # "assigned_products": partner.assigned_product_ids.mapped('id'),
                    # "company_namespace": partner.company_namespace or [],
                    # Assuming teams are stored in a many2many field
                    # "teams": partner.teams_ids.mapped('id'),
                    "name": partner.name or "",
                    # "client_code": partner.client_code or "",
                    "phone": partner.phone or "",
                    "city": partner.city or "",
                    # "state": partner.state or "",
                    "country": partner.country_id.name if partner.country_id else "",
                    # "contact_name": partner.contact_name or "",
                    # "contact_title": partner.contact_title or "",
                    "zip": partner.zip or "",
                    # "credit_limit": partner.credit_limit or 0,
                    # "isChain": partner.is_chain or False,
                    # Assuming there's a relation to channel
                    # "channel": partner.channel_id.id if partner.channel_id else None,
                    "sv_price_list_id": partner.sv_price_list_id.id if partner.sv_price_list_id else None,  # Custom field
                    "payment_type": partner.payment_type or "",  # Custom field
                    "id_repzo": partner.id_repzo or "",  # Custom field
                    "__v": 0,  # This can be removed if not needed
                    "createdAt": partner.create_date.isoformat() if partner.create_date else None,
                    "updatedAt": partner.write_date.isoformat() if partner.write_date else None,
                })

            # Calculate total pages
            total_pages = (total_result + per_page -
                           1) // per_page  # Ceiling division

            # Constructing the response
            response = {
                "total_result": total_result,
                "current_count": len(users_data),
                "total_pages": total_pages,
                "current_page": current_page,
                "per_page": per_page,
                "first_page_url": request.httprequest.host_url + "api/get_all_users?per_page={}&page=1".format(per_page),
                "last_page_url": request.httprequest.host_url + "api/get_all_users?per_page={}&page={}".format(per_page, total_pages),
                "next_page_url": request.httprequest.host_url + "api/get_all_users?per_page={}&page={}".format(per_page, current_page + 1) if current_page < total_pages else None,
                "prev_page_url": request.httprequest.host_url + "api/get_all_users?per_page={}&page={}".format(per_page, current_page - 1) if current_page > 1 else None,
                "path": request.httprequest.host_url + "api/get_all_users",
                "data": users_data,
            }

            return response

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/add_customer', type='json', auth='none', methods=['POST'])
    def add_customer(self):
        try:
            self.extra_errors_message = []
            self.extra_errors = False
            schema = ContactCreateValidationSchema()
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.debug("@@Data: %s", data)

            validated_data = schema.load(data)

            self.existing_email_partner(validated_data)
            self.existing_phone_partner(validated_data)
            if self.extra_errors:
                raise ValidationError(self.extra_errors_message)

            partner_vals = {
                'name': validated_data['name'],
                'email': validated_data['email'],
                'phone': validated_data['phone'],
                'partner_latitude': validated_data['partner_latitude'],
                'partner_longitude': validated_data['partner_longitude'],
                'location_verified': validated_data['location_verified'],
                'payment_type': validated_data['payment_type'],
                'id_repzo': validated_data['id_repzo'],
            }

            new_partner = request.env['res.partner'].sudo().create(
                partner_vals)
            # response_data = {
            #     "user info": new_partner,

            # }
            return Response(
                response=json.dumps({'response_data': ''}),
                status=201,
                # content_type="application/json"
            )
            return {"status": "success", "partner_id": new_partner.id}

        except ValidationError as err:
            return {"status": "error", "errors": err.messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/update_customer/<int:partner_id>', type='json', auth='none', methods=['PUT'])
    def update_customer(self, partner_id):
        try:
            self.extra_errors_message = []
            schema = ContactCreateValidationSchema()
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.debug("@@Data: %s", data)

            validated_data = schema.load(data)

            # Check for uniqueness only if email or phone is being updated
            existing_partner = request.env['res.partner'].sudo().browse(
                partner_id)
            if not existing_partner:
                return {"status": "error", "message": "Partner not found."}

            if validated_data['email'] != existing_partner.email:
                if self.existing_email_partner(validated_data):
                    raise ValidationError(self.extra_errors_message)

            if validated_data['phone'] != existing_partner.phone:
                if self.existing_phone_partner(validated_data):
                    raise ValidationError(self.extra_errors_message)

            # Update partner values
            existing_partner.write({
                'name': validated_data['name'],
                'email': validated_data['email'],
                'phone': validated_data['phone'],
                'partner_latitude': validated_data['partner_latitude'],
                'partner_longitude': validated_data['partner_longitude'],
                'location_verified': validated_data['location_verified'],
                'payment_type': validated_data['payment_type'],
                'id_repzo': validated_data['id_repzo'],
            })

            return {"status": "success", "partner_id": existing_partner.id}

        except ValidationError as err:
            return {"status": "error", "errors": err.messages}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/delete_customer/<int:partner_id>', type='json', auth='none', methods=['DELETE'])
    def delete_customer(self, partner_id):
        try:
            existing_partner = request.env['res.partner'].sudo().browse(
                partner_id)
            if not existing_partner:
                return {"status": "error", "message": "Partner not found."}

            existing_partner.unlink()  # Delete the partner record

            return {"status": "success", "message": "Partner deleted successfully."}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    @http.route('/api/get_user/<int:partner_id>', type='json', auth='none', methods=['GET'])
    def get_user(self, partner_id):
        try:
            # Fetching the partner by ID
            partner = request.env['res.partner'].sudo().browse(partner_id)

            if not partner.exists():
                return {"status": "error", "message": "Partner not found."}

            # Constructing the user data
            user_data = {
                "_id": partner.id,
                "disabled": partner.active is False,
                "formatted_address": partner.contact_address or "No location",
                "lat": partner.partner_latitude or 0,
                "lng": partner.partner_longitude or 0,
                "website": partner.website or "",
                "email": partner.email or "",
                "comment": partner.comment or "",
                "parent_client_id": partner.parent_id.id if partner.parent_id else None,
                "name": partner.name or "",
                "phone": partner.phone or "",
                "city": partner.city or "",
                "country": partner.country_id.name if partner.country_id else "",
                "zip": partner.zip or "",
                "sv_price_list_id": partner.sv_price_list_id.id if partner.sv_price_list_id else None,
                "payment_type": partner.payment_type or "",
                "id_repzo": partner.id_repzo or "",
                "createdAt": partner.create_date.isoformat() if partner.create_date else None,
                "updatedAt": partner.write_date.isoformat() if partner.write_date else None,
            }

            return {"status": "success", "data": user_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}
