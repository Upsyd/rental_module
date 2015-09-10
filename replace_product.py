from openerp import models, fields, api,_ 


class replace_products(models.Model):
    
    _name = 'replace.products'
    _rec_name = 'serial_number'
    
    serial_number = fields.Many2one('stock.production.lot')
    product_id = fields.Many2one(related = 'serial_number.product_id')
    replace_wizard_id = fields.Many2one('replace.order.wizard')
    price = fields.Float(related = 'product_id.list_price')
    

