from marshmallow import Schema, fields, validate


class InvoiceCreateValidationSchema(Schema):

    partner_id = fields.Int(required=True)  # Required: Customer ID
    # Required: List of invoice lines
    invoice_line_ids = fields.List(fields.Dict(), required=True)
    date_invoice = fields.Date(required=False)  # Optional: Invoice date
    state = fields.Str(required=False, validate=validate.OneOf(
        ["draft", "open", "paid"]))  # Optional: Invoice state
