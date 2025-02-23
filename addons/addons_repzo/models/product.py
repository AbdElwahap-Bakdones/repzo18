from odoo import models, fields, api


class Brand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'

    _id = fields.Char(string="_id", required=True)
    name = fields.Char(string='Brand Name', required=True)
    disabled = fields.Boolean(string='Disabled', default=False)
    company_namespace = fields.Many2many(
        'res.company', string='Company Namespace')

    created_at = fields.Datetime(
        string='Created At', readonly=True, default=fields.Datetime.now)
    updated_at = fields.Datetime(
        string='Updated At', readonly=True, default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        if 'id' in vals:
            existing_brand = self.search([('id', '=', vals['id'])])
            if existing_brand:
                raise ValueError("The ID must be unique.")

        # Set created_at and updated_at fields
        vals['created_at'] = fields.Datetime.now()
        return super(Brand, self).create(vals)

    def write(self, vals):
        # Update the updated_at field whenever the record is modified
        vals['updated_at'] = fields.Datetime.now()
        return super(Brand, self).write(vals)


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _id = fields.Char(string='_id', default="")
    disabled = fields.Boolean(string='disabled', default=False)
    position = fields.Integer(string="position")
    local_name = fields.Char(string="local Name")
    type = fields.Char(string="type")


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _id = fields.Char(string='_id', default="")
    local_name = fields.Char(string='local_name', default="")
    brand_id = fields.Many2one(
        'product.brand', string='Brand', ondelete='set null')
    frozen_pre_sales = fields.Boolean(string="frozen_pre_sales", default=True)
    frozen_sales = fields.Boolean(string="frozen_sales", default=True)
