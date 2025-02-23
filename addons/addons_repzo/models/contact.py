from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    location_verified = fields.Boolean(string="is location verified")
    sv_price_list_id = fields.Many2one(
        'product.pricelist',
        string="Service Price List",
        help="Pricelist associated with this partner"
    )
    payment_type = fields.Char(string="Payment Type", help="credit Or cash")

    id_repzo = fields.Char(string="Repzo Id", required=True)

    @api.constrains('email')
    def _check_unique_email(self):
        for record in self:
            if record.email:
                existing_partners = self.search([
                    ('email', '=', record.email),
                    ('id', '!=', record.id)  # Exclude the current record
                ])
                if existing_partners:
                    raise ValidationError("The email address must be unique.")

    @api.constrains('phone')
    def _check_unique_phone(self):
        for record in self:
            if record.phone:
                existing_partners = self.search([
                    ('phone', '=', record.phone),
                    ('id', '!=', record.id)  # Exclude the current record
                ])
                if existing_partners:
                    raise ValidationError("The phone number must be unique.")

    # @api.constrains('id_repzo')
    # def _check_unique_id_repzo(self):
    #     for record in self:
    #         if record.id_repzo:
    #             existing_partners = self.search([
    #                 ('id_repzo', '=', record.id_repzo),
    #                 ('id', '!=', record.id)  # Exclude the current record
    #             ])
    #             if existing_partners:
    #                 raise ValidationError("The Repzo Id must be unique.")
