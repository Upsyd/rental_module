from openerp import models, fields, api,_ 


class existing_products(models.Model):

    _name = 'existing.product'
    _rec_name = 'serial_number'

    serial_number = fields.Many2one('stock.production.lot')
    product_id = fields.Many2one(related ='serial_number.product_id')
    product_category = fields.Many2one(related = 'product_id.categ_id')
    monthly_rent = fields.Float(related='product_id.mothly_rental')
    replace_wizard_id = fields.Many2one('replace.order.wizard',ondelete='cascade')
    qty = fields.Float('Qty')
    replace = fields.Boolean('Replace')

