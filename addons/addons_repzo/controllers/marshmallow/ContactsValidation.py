from marshmallow import Schema, fields, validate, ValidationError


class ContactCreateValidationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))

    email = fields.Email(required=False)

    phone = fields.Str(
        required=False, validate=validate.Length(min=10, max=15))

    partner_latitude = fields.Float(required=False)

    partner_longitude = fields.Float(required=False)

    location_verified = fields.Bool(required=False)

    payment_type = fields.Str(
        required=False, validate=validate.OneOf(['credit', 'cash']))
    id_repzo = fields.Str(required=True, validate=validate.Length(max=50))

    def validate_latitude_longitude(self, data, **kwargs):
        if not (-90 <= data['partner_latitude'] <= 90):
            raise ValidationError(
                "Latitude must be between -90 and 90 degrees.")
        if not (-180 <= data['partner_longitude'] <= 180):
            raise ValidationError(
                "Longitude must be between -180 and 180 degrees.")

        return data
