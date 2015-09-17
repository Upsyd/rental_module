from openerp import fields, models, api, _

class replace_product_wizard(models.Model):
    _name = 'replace.product.wizard'
    _rec_name = 'id'

        
    @api.model
    def get_current_date_time(self):
        return datetime.now()

    @api.one
    def replace_product(self):
        activated_rental_order_id= self.get_current_id()
        stock_picking_object = self.env['stock.picking']
        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']
        res_customer_sale_order = sale_order_obj.onchange_partner_id(part = self.partner_id.id)
        customer_price_list_id = res_customer_sale_order['value']['pricelist_id']
        product_dictionary = {}
        product_dict2={}
        product_line = ()
        move_lines = []
        move_lines2 = []
        for rental_products in self.existing_products_ids:
            if rental_products.replace == True:
                res_product_sale = sale_order_line_obj.product_id_change(pricelist = customer_price_list_id,product = rental_products.product_id.id,partner_id = self.partner_id.id)
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
            else:
                product_dict_2 =  {'product_id' :rental_products.product_id.id,
                                   'seq_id': rental_products.serial_number.id,
                                  'rental_order_id':activated_rental_order_id
                                        }
                move_line2= (0,False,product_dict_2)
                move_lines2.append(move_line2)
        rental_object =  self.env['rental.order']
        name = rental_object.browse(activated_rental_order_id).name 
        stock_picking_id = stock_picking_object.create({'move_lines':move_lines,
                                                        'origin':name,
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
                                   'product_uom': res_product_sale['value']['product_uom'] or False,
                                  'product_uom_qty':1,
                                  'location_id':1,
                                  'location_dest_id':9,
                                  'date':self.replace_date,
                                  'name':outgoing_products.product_id.name
                                   }
            product_dict2 = {'product_id' :outgoing_products.product_id.id,
                              'seq_id': outgoing_products.serial_number.id,
                            'rental_order_id':activated_rental_order_id
                                        }
            move_line = (0,False,product_dictionary)
            move_lines.append(move_line)
            move_line2 = (0,False,product_dict2)
            move_lines2.append(move_line2)
        stock_picking_id = stock_picking_object.create({'move_lines':move_lines,
                                                        'origin': name,
                                                        'partner_id':self.partner_id.id,
                                                        'picking_type_id': 2,
                                                        })
        rental_object = self.env['rental.order']
        current_object =rental_object.browse(activated_rental_order_id)
        rental_lines_obj = self.env['rental.lines']
        rental_lines = rental_lines_obj.search([('rental_order_id','=',activated_rental_order_id)])
        for rental_lines_obj in rental_lines:
            rental_lines_obj.unlink()
        current_object.write({'eupment_rental_ids':move_lines2})

    def get_current_id(self,cr,uid,ids,context={}):
        move_lines= []
        activated_rental_order_id = context.get('active_id')
        return activated_rental_order_id
        
    existing_products_ids = fields.One2many('existing.product','replace_wizard_id','Existing Rental Products')
    rental_product_ids = fields.One2many('replace.products', 'replace_wizard_id1',string ="Replace Products")
    replace_date = fields.Datetime('Replace Date')
    partner_id  = fields.Many2one('res.partner')
