from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)

    property_ids = fields.One2many("estate_property", "property_type_id", string="Properties")

    _sql_constraints = [
        (
            "unique_name",
            "UNIQUE(name)",
            "The property type name must be unique.",
        ),
    ]