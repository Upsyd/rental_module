from openerp import fields, models, api, _
from datetime import datetime


class mrp_repair(models.Model):
    _inherit = "mrp.repair"

    @api.onchange('seq_id')
    def on_change_sequance_id(self):
        rental_order_lines_obj = self.env['rental.lines']
        if self.seq_id.id:
            rental_lines =  rental_order_lines_obj.search([('seq_id','=',self.seq_id.id)])
            self.rental_order_id = rental_lines.rental_order_id.id
            self.product_id = self.seq_id.product_id

    

    seq_id = fields.Many2one('stock.production.lot', string="Serial Number")
    rental_order_id = fields.Many2one('rental.order',string = "Rental Order")

