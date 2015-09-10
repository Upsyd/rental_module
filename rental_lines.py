from openerp import models, fields, api,_ 


class rental_lines(models.Model):

    _name = 'rental.lines'
    _rec_name = 'product_id'

    seq_id = fields.Many2one('stock.production.lot','Serial Number')
    product_id = fields.Many2one(related = 'seq_id.product_id')
    product_category = fields.Many2one(related = 'product_id.categ_id')
    monthly_rent = fields.Float(related='product_id.mothly_rental')
    rental_order_id = fields.Many2one('rental.order')
    description = fields.Char('Description')
    replace = fields.Boolean('Replace',default= True)
    qty = fields.Float('Qty', default= 1)
    
