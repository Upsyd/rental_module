from openerp import fields, models, api, _
from datetime import datetime


class mrp_repair(models.Model):
    _inherit = 'mrp.repair'

    def action_repair_end(self, cr, uid, ids, context=None):
        move_line =()
        move_lines = []
        record = self.browse(cr,uid,ids,context ={})
        stock_picking_object  = self.pool.get('stock.picking')
        product_dictionary = {'date_expected': datetime.now(),
                                  'product_uos_qty': 1,
                                  'product_id':record.product_id.id,
                                  'product_uom':1,
                                  'product_uom_qty':1,
                                  'location_id':1,
                                  'location_dest_id':9,
                                  'date':datetime.now(),
                                  'name':record.product_id.name
                                   }
        move_line = [(0,False,product_dictionary)]
        stock_picking_id = stock_picking_object.create(cr,uid,{'move_lines':move_line,
                                                        'origin' :record.name ,
                                                        'partner_id':record.rental_order_id.customer_id.id,
                                                        'picking_type_id': 2,
                                                        })
        return super(mrp_repair,self).action_repair_end(cr, uid, ids)
    
    def action_confirm(self, cr, uid, ids, *args):
        #creating incoming shipment 
        move_line =()
        move_lines = []
        record = self.browse(cr,uid,ids,context ={})
        stock_picking_object  = self.pool.get('stock.picking')
        product_dictionary = {'date_expected': datetime.now(),
                                  'product_uos_qty': 1,
                                  'product_id':record.product_id.id,
                                  'product_uom':1,
                                  'product_uom_qty':1,
                                  'location_id':1,
                                  'location_dest_id':9,
                                  'date':datetime.now(),
                                  'name':record.product_id.name
                                   }
        move_line = [(0,False,product_dictionary)]
        stock_picking_id = stock_picking_object.create(cr,uid,{'move_lines':move_line,
                                                        'origin' :record.name ,
                                                        'partner_id':record.rental_order_id.customer_id.id,
                                                        'picking_type_id': 1,
                                                        })
        return super(mrp_repair,self).action_confirm(cr, uid, ids)

    @api.onchange('seq_id')
    def on_change_sequance_id(self):
        rental_order_lines_obj = self.env['rental.lines']
        if self.seq_id.id:
            rental_lines =  rental_order_lines_obj.search([('seq_id','=',self.seq_id.id)])
            self.rental_order_id = rental_lines.rental_order_id.id
            self.product_id = self.seq_id.product_id

    seq_id = fields.Many2one('stock.production.lot', string="Serial Number")
    rental_order_id = fields.Many2one('rental.order',string = "Rental Order")

