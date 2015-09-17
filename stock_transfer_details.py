from openerp import models, fields, api,_ 
from datetime import datetime


class stock_transfer_details(models.Model):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        stock_quant_obj =self.env['stock.quant']
        #return super(stock_transfer_details, self).do_detailed_transfer()
        for item in self.item_ids:
            id= stock_quant_obj.create({'owner_id': False, 
                                           'package_id': False, 
                                           'cost': 0.0, 
                                           'product_id': item.product_id.id, 
                                           'lot_id': item.lot_id.id, 
                                           'in_date': datetime.now(), 
                                           'location_id': 9, 
                                           'company_id': 1, 
                                           'qty': 1.0})
            id[0].status ='rented'
        

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking'), 'Bad context propagation'
        picking_id, = picking_ids
        picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
        stock_production = self.pool.get('stock.production.lot')
        items = []
        packs = []
        if not picking.pack_operation_ids:
            picking.do_prepare_partial()
        for op in picking.pack_operation_ids:
            obj= stock_production.search(cr,uid,[('product_id','=',op.product_id.id)])
            record = stock_production.browse(cr,uid,obj[0],context)
            item = {
                'packop_id': op.id,
                'product_id': op.product_id.id,
                'product_uom_id': op.product_uom_id.id,
                'quantity': op.product_qty,
                'package_id': op.package_id.id,
                'lot_id':record.id ,
                'sourceloc_id': op.location_id.id,
                'destinationloc_id': op.location_dest_id.id,
                'result_package_id': op.result_package_id.id,
                'date': op.date, 
                'owner_id': op.owner_id.id,
            }
            if op.product_id:
                items.append(item)
            elif op.package_id:
                packs.append(item)
        res.update(item_ids=items)
        res.update(packop_ids=packs)
        return res
