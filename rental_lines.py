from openerp import models, fields, api,_ 


class rental_lines(models.Model):

    _name = 'rental.lines'
    _rec_name = 'seq_id'

    def create(self,cr,uid,val,context={}):
        print val
        return super(rental_lines,self).create(cr,uid,val,context={})

    seq_id = fields.Many2one('stock.production.lot','Serial Number',ondelete='cascade')
    product_id = fields.Many2one(related = 'seq_id.product_id',ondelete='cascade')
    product_category = fields.Many2one(related = 'product_id.categ_id',ondelete='cascade')
    monthly_rent = fields.Float(related='product_id.mothly_rental')
    rental_order_id = fields.Many2one('rental.order',ondelete='cascade')
    description = fields.Char('Description')
    replace = fields.Boolean('Replace',default= True)
    qty = fields.Float('Qty', default= 1)
    
