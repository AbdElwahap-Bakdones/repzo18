from marshmallow import Schema, fields, validate, ValidationError


def validate_quantity(value):
    """Allow both positive (normal order) and negative (return) quantities."""
    if value == 0:
        raise ValidationError("Quantity cannot be zero.")


class OrderLineSchema(Schema):
    product_id = fields.Int(required=True, error_messages={
        "required": "Product ID is required."
    })
    quantity = fields.Int(required=True, validate=validate_quantity, error_messages={
        "required": "Quantity is required.",
        "invalid": "Quantity must be a valid integer."
    })
    price_unit = fields.Float(required=True, error_messages={
        "required": "Price unit is required.",
        "invalid": "Price unit must be a valid number."
    })


class OrderCreateValidationSchema(Schema):
    partner_id = fields.Int(required=True, error_messages={
        "required": "Partner ID is required."
    })
    order_line = fields.List(fields.Nested(OrderLineSchema), required=True, error_messages={
        "required": "Order lines are required."
    })
    qty_done = fields.Float(required=False, error_messages={
        "invalid": "Quantity done must be a valid number."
    })  # Allows tracking actual moved quantity for inventory updates
    date_order = fields.Date(required=False)
    state = fields.Str(required=False, validate=validate.OneOf(
        ["draft", "sent", "sale", "done", "cancel"]
    ), error_messages={"invalid": "Invalid order state."})
    invoice_policy = fields.Str(
        required=False,
        validate=validate.OneOf(["order", "delivery"]),
        error_messages={
            "invalid": "Invoice policy must be 'order' or 'delivery'."}
    )  # Supports invoicing policy for order validation
