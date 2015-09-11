from openerp import models, fields, api,_ 


class replace_products(models.Model):
    
    _name = 'replace.products'
    _rec_name = 'serial_number'

    def onchange_product_id(self,cr,uid,ids,product_id,context={}):
        print "product_id changed  method is called ------------"
        product_obj = self.pool.get('product.product')
        product_record = product_obj.browse(cr,uid,product_id,context)
        print product_record
    
    serial_number = fields.Many2one('stock.production.lot')
    product_id = fields.Many2one(related = 'serial_number.product_id', domain=[('can_be_rented','=',True)])
    replace_wizard_id1 = fields.Many2one('replace.order.wizard')
    price = fields.Float(related = 'product_id.list_price')

