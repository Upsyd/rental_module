from openerp import fields, models, api, _

class replace_product_wizard(models.Model):
    _name = 'replace.product.wizard'
    _rec_name = 'id'

    @api.model
    def get_current_date_time(self):
        return datetime.now()

    @api.one
    def replace_product(self):
        print "partner_name",self.partner_id.name
        stock_picking_object = self.env['stock.picking']
        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']
        res_customer_sale_order = sale_order_obj.onchange_partner_id(part = self.partner_id.id)
        customer_price_list_id = res_customer_sale_order['value']['pricelist_id']
        print "getting customer price list",customer_price_list_id
        
        product_dictionary = {}
        product_line = ()
        move_lines = []
        for rental_products in self.existing_products_ids:
            if rental_products.replace == True:
                res_product_sale = sale_order_line_obj.product_id_change(pricelist = customer_price_list_id,product = rental_products.product_id.id,partner_id = self.partner_id.id)
                print res_product_sale['value']['product_uom']
                product_dictionary = {'date_expected': self.replace_date,
                                      'product_uos_qty': 1,
                                      'product_uom': res_product_sale['value']['product_uom'],
                                      'product_id':rental_products.product_id.id,
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
            res_product_sale = sale_order_line_obj.product_id_change(pricelist = customer_price_list_id,product = outgoing_products.product_id.id,partner_id = self.partner_id.id)
            product_dictionary = {'date_expected': self.replace_date,
                                  'product_uos_qty': 1,
                                  'product_id':outgoing_products.product_id.id,
                                   'product_uom': res_product_sale['value']['product_uom'],
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
