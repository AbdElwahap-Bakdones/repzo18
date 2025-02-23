from marshmallow import Schema, fields, validate, EXCLUDE


class BrandSchema(Schema):
    _id = fields.Str(required=False)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    disabled = fields.Boolean(required=False, default=False)


class CategorySchema(Schema):
    _id = fields.Str(required=False)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    local_name = fields.Str(required=False, allow_none=True)
    photo = fields.Str(required=False, allow_none=True)
    icon = fields.Str(required=False, allow_none=True)
    type = fields.Str(required=False, allow_none=True)
    position = fields.Int(required=False, default=0)


class ProductCreateValidationSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields

    name = fields.Str(required=True, validate=validate.Length(min=1))
    local_name = fields.Str(required=False, allow_none=True)
    # Assuming CATEGORY_ID is a string
    category = fields.Int(required=True)
    brand = fields.Int(required=True)
    sub_category = fields.List(fields.Str(), required=False, allow_none=True)
    barcode = fields.Str(required=False, allow_none=True)
    sku = fields.Str(required=False, allow_none=True)
    # URL for the product image
    product_img = fields.Str(required=False, allow_none=True)
    # Assuming measure family ID is a string
    measureunit_family = fields.Str(required=False, allow_none=True)
    sv_measureUnit = fields.Str(
        required=False, allow_none=True)  # Measure unit ID
    sv_tax = fields.List(fields.Str(), required=False,
                         allow_none=True)  # List of tax IDs
    # variants = fields.List(fields.Nested('VariantSchema'),
    #                        required=True)  # List of variants

    class VariantSchema(Schema):
        name = fields.Str(required=True, validate=validate.Length(min=1))
        barcode = fields.Str(required=False, allow_none=True)
        default = fields.Bool(required=False, default=False)
        local_name = fields.Str(required=False, allow_none=True)
        # Price should be positive
        price = fields.Float(required=True, validate=validate.Range(min=0))
        sku = fields.Str(required=False, allow_none=True)
        # Default to 0 if not provided
        position = fields.Int(required=False, default=0)
