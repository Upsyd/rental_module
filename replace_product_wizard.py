from openerp import fields, models, api, _

class replace_product_wizard(models.Model):
    _name = 'replace.product.wizard'
    _rec_name = 'id'
    

        
    @api.one
    def replace_product(self):
        print "partner_name",self.partner_id.name
        stock_picking_object = self.env['stock.picking']
        product_dictionary = {}
        product_line = ()
        move_lines = []
        for rental_products in self.existing_products_ids:
            if rental_products.replace == True:
                product_dictionary = {'date_expected': self.replace_date,
                                  'product_uos_qty': 1,
                                  'product_id':rental_products.product_id.id,
                                  'product_uom':1,
                                  'product_uom_qty':1,
                                  'location_id':2,
                                  'location_dest_id':1,
                                  'date':self.replace_date,
                                  'name':rental_products.product_id.name
                                  }
            move_line= (0,False,product_dictionary)
            move_lines.append(move_line)
        print move_lines
        stock_picking_id = stock_picking_object.create({'move_lines':move_lines,
                                                        'origin': 'rental_order',
                                                        'partner_id':self.partner_id.id,
                                                        'picking_type_id': 1,
                                                        })
        move_line = ()
        move_lines = []
        counter= 0
        for outgoing_products in self.rental_product_ids:
            counter =counter +1
            product_dictionary = {'date_expected': self.replace_date,
                                  'product_uos_qty': 1,
                                  'product_id':outgoing_products.product_id.id,
                                  'product_uom':1,
                                  'product_uom_qty':1,
                                  'location_id':1,
                                  'location_dest_id':2,
                                  'date':self.replace_date,
                                  'name':outgoing_products.product_id.name
                                   }
            move_line = (0,False,product_dictionary)
            move_lines.append(move_line)
        stock_picking_id = stock_picking_object.create({'move_lines':move_lines,
                                                        'origin': 'rental_order',
                                                        'partner_id':self.partner_id.id,
                                                        'picking_type_id': 2,
                                                        })

        
            
    existing_products_ids = fields.One2many('existing.product','replace_wizard_id','Existing Rental Products')
    rental_product_ids = fields.One2many('replace.products', 'replace_wizard_id',string ="Replace Products")
    replace_date = fields.Datetime('Replace Date')
    partner_id  = fields.Many2one('res.partner')
