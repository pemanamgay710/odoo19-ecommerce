# from odoo import models, fields, api


# class ecommerce_custom_module(models.Model):
#     _name = 'ecommerce_custom_module.ecommerce_custom_module'
#     _description = 'ecommerce_custom_module.ecommerce_custom_module'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

