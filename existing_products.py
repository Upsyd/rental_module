from openerp import models, fields, api,_ 


class existing_products(models.Model):

    _name = 'existing.product'
    _rec_name = 'serial_number'

    serial_number = fields.Many2one('stock.production.lot')
    product_category = fields.Many2one(related = 'product_id.categ_id')
    monthly_rent = fields.Float(related='product_id.mothly_rental')
    replace_wizard_id = fields.Many2one('replace.order.wizard')
    product_id = fields.Many2one('product.product', domain=[('can_be_rented','=',True)])
    qty = fields.Float('Price')
    replace = fields.Boolean('Replace',Default = 1)

