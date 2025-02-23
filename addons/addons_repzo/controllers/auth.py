import secrets
from odoo import http
from odoo.http import request


class ContactCustomerEndpoint(http.Controller):

    @http.route('/api/authenticate', type='json', auth='none', methods=['POST'])
    def authenticate(self, email, password):
        # Authenticate the user
        user = request.env['res.users'].sudo().search(
            [('login', '=', email)], limit=1)

        if not user or not user._check_credentials(password):
            return {"error": "Invalid email or password."}

        # Fetch the user's API key if it exists
        param_key = f"auth.api_key.{user.id}"
        api_key = request.env['ir.config_parameter'].sudo(
        ).get_param(param_key)

        # Generate a new API key if none exists
        if not api_key:
            api_key = secrets.token_hex(32)  # Generate a 32-byte hex token
            request.env['ir.config_parameter'].sudo(
            ).set_param(param_key, api_key)

        return {"success": True, "api_key": api_key}

    @http.route('/api/test', type='http', auth='none', methods=['GET'])
    def authenticate(self):
        return "ok"
