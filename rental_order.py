from openerp import models, fields, api,_ 
from numpy.dual import inv


class rental_order(models.Model):

    _name = "rental.order"

    @api.model
    def create(self,val):
        seq = self.env['ir.sequence'].get('rental.code')
        print "seq----------",seq
        print seq
        val['name'] = seq
        return super(rental_order,self).create(val)
        print val


    def confirm_rental_order(self,cr, uid, ids, context={}):
         if ids:
            for id in ids:
                wizard_values_record = self.browse(cr, uid,id)
                partner_id = wizard_values_record.customer_id.id
                wizard_values_record.state='confirm_rental'
                product_dict = {}
                res= {}
                order_lines = []
                sale_order_obj = self.pool.get('sale.order')
                sale_order_line = self.pool.get('sale.order.line')
                stock_picking_object = self.pool.get('stock.picking')
                
                res_customer = sale_order_obj.onchange_partner_id(cr,uid,ids,part = partner_id,context={})
                for eq_id in wizard_values_record.eupment_rental_ids:
                    res_product = sale_order_line.product_id_change(cr,uid,ids,pricelist = res_customer['value']['pricelist_id'],product = eq_id.product_id.id,partner_id = partner_id)
                    qty = res_product['value']['product_uom']
                    price = res_product['value']['price_unit']
                    product_dict = {'price_unit': price,
                            'product_uom_qty': qty,
                            'product_id':eq_id.product_id.id
                            }
                    order_line = (0,False,product_dict)
                    order_lines.append(order_line)
                sale_id = sale_order_obj.create(cr,uid,{'partner_id':partner_id,'order_line':order_lines})
                sale_id_list =[sale_id]
                sale_order_obj.action_button_confirm(cr, uid, sale_id_list, context=None)
                #sale payment advance inv
                sale_order_advance_obj = self.pool.get('sale.advance.payment.inv')
                sale_ids = sale_id
                print res
            move_line =()
            move_lines = []
            for eq_id in wizard_values_record.eupment_rental_ids:
                product_dictionary = {'date_expected': wizard_values_record.date,
                                  'product_uos_qty': 1,
                                  'product_id':eq_id.product_id.id,
                                  'product_uom':1,
                                  'product_uom_qty':1,
                                  'location_id':1,
                                  'location_dest_id':2,
                                  'date':wizard_values_record.date,
                                  'name':eq_id.product_id.name
                                   }
            move_line = (0,False,product_dictionary)
            move_lines.append(move_line)
            stock_picking_id = stock_picking_object.create(cr,uid,{'move_lines':move_lines,
                                                        'origin': 'rental_order',
                                                        'partner_id':wizard_values_record.customer_id.id,
                                                        'picking_type_id': 2,
                                                        })

        
    def genrate_existing_products(self, cr, uid, ids, context ={}):
        print "products with the customer"
        rental_order_record = self.browse(cr, uid,ids)
        print "rentsl_order_record",rental_order_record.name
        product_line = ()
        product_lines= []
        ex_product_dict = {}
        ex_product_line = ()
        ex_product_lines = []
        existing_product_object = self.pool.get('existing.products') 
        print existing_product_object
        product_replace_wizard_object = self.pool.get('replace.product.wizard')
        for eq_id in rental_order_record.eupment_rental_ids:
                assets_lines = self.browse(cr, uid, eq_id, context)
                product_dict = {
                                
                                'product_id' : assets_lines.id.product_id.id,
                                'qty' : 1,
                                'replace': True
                              }
                product_line = (0,False,product_dict)
                print product_line
                product_lines.append(product_line)
        created_wizard_id = product_replace_wizard_object.create(cr, uid,{'partner_id':rental_order_record.customer_id.id,'existing_products_ids':product_lines,
                                                      'rental_product_ids': [],
                                                      },context)
         #now opening the newly created view 
        ir_model_data = self.pool.get('ir.model.data')
        print "model",ir_model_data
        form_res = ir_model_data.get_object_reference(cr,uid,'rental_module','replace_rental_product_form_view')
        print form_res#         
        form_id = form_res and form_res[1] or False
        print form_id
        return  {
                       'name': 'Replace Rental Products',
                       'view_type': 'form',
                       'view_mode': 'form',
                       'res_model': 'replace.product.wizard',
                       'res_id' :created_wizard_id,
                       'view_id': form_id,
                       'type': 'ir.actions.act_window',
                       'target': 'new'
                       }
 
    
    name = fields.Char('name')
    customer_id = fields.Many2one('res.partner',string = 'Customer')
    inv_address = fields.Many2one(related = 'customer_id', string ='Invoice Address')
    delivery_address = fields.Many2one(related = 'customer_id',string='Delivery Address')
    start_date = fields.Date('Start Date')
    inital_term = fields.Selection([('6','6'),('12','12')],'Initial Terms')
    billing_freq = fields.Selection([('1','1'),('3','3'),('6','6'),('12','12')], 'Billing Frequency')
    purchase_price = fields.Float('Purchase price')
    date = fields.Datetime('Date')
    reference = fields.Char('Reference')
    agg_recived = fields.Boolean('Agreement received')
    warehouse = fields.Many2one('stock.warehouse','Warehouse')
    price_list = fields.Many2one('product.pricelist','Product Price list')
    close_date = fields.Date('Close Date')
    state = fields.Selection([('draft','Draft'),('confirm_rental','Confirm Rental'),
                              ('close','Close')], default = 'draft')
    eupment_rental_ids = fields.One2many('rental.lines','rental_order_id','Assets Rental Lines')
