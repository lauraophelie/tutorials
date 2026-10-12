from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    name = fields.Char(required=True)

    property_ids = fields.One2many("estate_property", "property_type_id", string="Properties")

    _sql_constraints = [
        (
            "unique_name",
            "UNIQUE(name)",
            "The property type name must be unique.",
        ),
    ]