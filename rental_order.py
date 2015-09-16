from openerp import models, fields, api,_ 
from datetime import datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from dateutil import relativedelta


class rental_order(models.Model):

    _name = "rental.order"

    @api.onchange('eupment_rental_ids')
    def check_serial_number(self):
        rental_order_records = self.search([])
        list_sequance_id = []
        list_product_id =  []
        for record in rental_order_records:
            if record.eupment_rental_ids:
                for rental_products_ids in record.eupment_rental_ids:
                    list_sequance_id.append(rental_products_ids.seq_id.id)
        print list_sequance_id
        for rental_products in self.eupment_rental_ids:
                list_product_id.append(rental_products.product_id) 
                if rental_products.seq_id.id in list_sequance_id:
                    raise Warning(_('Duplicate Serial Number Not Allowed'))
        
    @api.model
    def create(self,val):
        seq = self.env['ir.sequence'].get('rental.code')
        val['name'] = seq
        subscription_obj = self.env['subscription.subscription']
        return super(rental_order,self).create(val)

    @api.model
    def get_current_date_time(self):
        return datetime.now()

    @api.one
    def close_rental(self):
        #preparing incoming shipment for all products
        self.state  = 'close'
        self.close_date =self.get_current_date_time()
        move_line = ()
        move_lines = []
        sale_order_line_obj = self.env['sale.order.line']
        sale_order_obj = self.env['sale.order']
        res_customer_sale_order = sale_order_obj.onchange_partner_id(part = self.customer_id.id,context={})
        customer_price_list_id = res_customer_sale_order['value']['pricelist_id']
        stock_picking_object = self.env['stock.picking']

        for products in self.eupment_rental_ids:
            products.product_id.name
            res_product_sale = sale_order_line_obj.product_id_change(pricelist = customer_price_list_id,product = products.product_id.id,partner_id = self.customer_id.id)
            product_dictionary = {'date_expected': self.get_current_date_time(),
                                  'product_uos_qty': 1,
                                  'product_uom': res_product_sale['value']['product_uom'],
                                  'product_id':products.product_id.id,
                                  'product_uom_qty':1,
                                  'location_id':2,
                                  'location_dest_id':1,
                                  'date':self.close_date,
                                  'name':products.product_id.name
                                  }
            move_line= (0,False,product_dictionary)
            move_lines.append(move_line)
        stock_picking_id = stock_picking_object.create({'move_lines':move_lines,
                                                        'origin': 'rental_order',
                                                        'partner_id':self.customer_id.id,
                                                        'picking_type_id': 1,
                                                        })
        subscription_object = self.env['subscription.subscription']
        subscription_object = subscription_object.browse(self.releated_subscription_id.id)
        subscription_object.set_done()

    def confirm_rental_order(self,cr, uid, ids, context={}):
        if ids:
            for id in ids:
                wizard_values_record = self.browse(cr, uid,id)
                renatal_order_name = wizard_values_record.name
                partner_id = wizard_values_record.customer_id.id
                wizard_values_record.state='confirm_rental'
                product_dict = {}
                res= {}
                order_lines = []
                #creating invoice from product and customer
                sale_order_obj = self.pool.get('sale.order')
                inv_object = self.pool.get('account.invoice')
                inv_line_object = self.pool.get('account.invoice.line')
                stock_picking_object = self.pool.get('stock.picking')
                sale_order_line_obj = self.pool.get('sale.order.line')

                res_customer_sale_order = sale_order_obj.onchange_partner_id(cr,uid,ids,part = partner_id,context={})
                customer_price_list_id = res_customer_sale_order['value']['pricelist_id']
                res_customer = inv_object.onchange_partner_id(cr, uid, ids, type='out_invoice',partner_id =partner_id,
                                                              date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False)
                account_id = res_customer['value']['account_id']
                for eq_id in wizard_values_record.eupment_rental_ids:
                    res_product_sale = sale_order_line_obj.product_id_change(cr,uid,ids,pricelist = customer_price_list_id,product = eq_id.product_id.id,partner_id = partner_id)
                    res_product_inv =  inv_line_object.product_id_change(cr,uid,ids,product=eq_id.product_id.id ,uom_id =res_product_sale['value']['product_uom'], qty=0, name='', type='out_invoice',partner_id=partner_id)
                    product_dict = {'uos_id': res_product_inv['value']['uos_id'],
                                  'product_id':eq_id.product_id.id,
                                   'price_unit': eq_id.monthly_rent,
                                   'account_id': res_product_inv['value']['account_id'],
                                   'name' : eq_id.product_id.name,
                                   'quantity': 1,
                                   }
                    order_line = (0,False,product_dict)
                    order_lines.append(order_line)
                inv_id = inv_object.create(cr,uid,{'account_id':account_id,
                                                      'partner_id':partner_id,
                                                      'invoice_line':order_lines,
                                                      'date_invoice':wizard_values_record.start_date})
                invoice = inv_object.browse(cr,uid,inv_id,context= {})

                #creating d/o for the same 
                move_line =()
                move_lines = []
                for eq_id in wizard_values_record.eupment_rental_ids:
                    product_dictionary = {'date_expected': wizard_values_record.date,
                                  'product_uos_qty': 1,
                                  'product_id':eq_id.product_id.id,
                                  'product_uom':1,
                                  'product_uom_qty':1,
                                  'location_id':1,
                                  'location_dest_id':9,
                                  'date':wizard_values_record.date,
                                  'name':eq_id.product_id.name
                                   }
                    move_line = (0,False,product_dictionary)
                    move_lines.append(move_line)
                stock_picking_id = stock_picking_object.create(cr,uid,{'move_lines':move_lines,
                                                        'origin' : renatal_order_name,
                                                        'partner_id':wizard_values_record.customer_id.id,
                                                        'picking_type_id': 2,
                                                        })
        subscription_obj = self.pool.get('subscription.subscription')
        subscription_name = 'Invoicing- '+ renatal_order_name
        doc_obj =  self.pool.get('subscription.document')
        doc_id= doc_obj.create(cr,uid,{'name':'invoice',
                                       'model':216
                                       })
        newdate = (datetime.strptime(wizard_values_record.date, '%Y-%m-%d %H:%M:%S')+relativedelta.relativedelta(months=wizard_values_record.billing_freq)).strftime('%Y-%m-%d %H:%M:%S')
        print "new date", newdate 
        print "type of new date",type(newdate)
        newdate = datetime.strptime(newdate,DEFAULT_SERVER_DATETIME_FORMAT)
        print "*****type of new date",type(newdate)
        print "---------after adding months to date",newdate
                
        ir_corn_object =  self.pool.get('ir.cron')
        print partner_id
        sub_id = subscription_obj.create(cr,uid,{'name':subscription_name,
                                'interval_number':wizard_values_record.billing_freq,
                                'notes': False,
                            
                                'doc_source': 'account.invoice,'+ str(inv_id),
                                'interval_type': 'months',
                                'partner_id': partner_id,
                                'date_init': wizard_values_record.date,
                                 },context={})
        wizard_values_record.releated_subscription_id = sub_id
        corn_id = ir_corn_object.create(cr,uid,{'name': subscription_name,
                                                        'priority':5,
                                                        'interval_number':wizard_values_record.billing_freq,
                                                        'nextcall': newdate})
        subscription_obj.set_process(cr, uid, [sub_id], context={})
        subscription_obj.write(cr,uid,[sub_id],{'cron_id':corn_id},context={})

    def genrate_existing_products(self, cr, uid, ids, context ={}):
        rental_order_record = self.browse(cr, uid,ids)
        product_line = ()
        product_lines= []
        ex_product_dict = {}
        ex_product_line = ()
        ex_product_lines = []
        existing_product_object = self.pool.get('existing.products') 
        product_replace_wizard_object = self.pool.get('replace.product.wizard')
        for eq_id in rental_order_record.eupment_rental_ids:
                assets_lines = self.browse(cr, uid, eq_id, context)
                product_dict = {
                                'serial_number':assets_lines.id.seq_id.id,
                                'product_id' : assets_lines.id.product_id.id,
                                'qty' : 1,
                                'replace': True
                              }
                product_line = (0,False,product_dict)
                product_lines.append(product_line)
        created_wizard_id = product_replace_wizard_object.create(cr,uid,{},context)
        product_replace_wizard_object.write(cr, uid,created_wizard_id,{'partner_id':rental_order_record.customer_id.id,
                                                                          'existing_products_ids':product_lines,
                                                                          'rental_product_ids':[]
                                                      },context)
         #now opening the newly created view 
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr,uid,'rental_module','replace_rental_product_form_view')
        form_id = form_res and form_res[1] or False
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
    customer_id = fields.Many2one('res.partner',string = 'Customer',ondelete='cascade')
    inv_address = fields.Many2one(related = 'customer_id', string ='Invoice Address',ondelete='cascade')
    delivery_address = fields.Many2one(related = 'customer_id',string='Delivery Address',ondelete='cascade')
    start_date = fields.Date('Start Date')
    inital_term = fields.Selection([('6','6'),('12','12')],'Initial Terms')
    billing_freq = fields.Selection([(1,1),(3,3),(6,6),(12,12)], 'Billing Frequency')
    purchase_price = fields.Float('Purchase price')
    date = fields.Datetime('Date')
    reference = fields.Char('Reference')
    agg_recived = fields.Boolean('Agreement received')
    warehouse = fields.Many2one('stock.warehouse','Warehouse',ondelete='cascade')
    price_list = fields.Many2one('product.pricelist','Product Price list',ondelete='cascade')
    close_date = fields.Datetime('Close Date')
    state = fields.Selection([('draft','Draft'),('confirm_rental','Confirm Rental'),
                              ('close','Close')], default = 'draft')
    eupment_rental_ids = fields.One2many('rental.lines','rental_order_id','Assets Rental Lines',ondelete='cascade')
    source_document_id = fields.Many2one('subscription.document','Source Document',ondelete='cascade')
    releated_subscription_id = fields.Many2one( 'subscription.subscription','Releated Subscription',ondelete='cascade')

