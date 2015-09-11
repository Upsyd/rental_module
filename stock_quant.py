from openerp import models, fields, api,_ 


class stock_quant(models.Model):

    _inherit = 'stock.quant'

    status = fields.Selection([('ready_to_transfer','Ready To Transfer'),('rented','Rented'),('new','New-Inventory'),('used_ready_to_go','Used Ready to go')])
    used_value = fields.Float('Used Value')
    mothly_rental = fields.Float(related = 'product_id.mothly_rental',string = "Monthly Rent")
    total_rent_collection_this_location = fields.Float('Total rent collection this location')
    total_rent_collected = fields.Float('Total rent collected')
    asset_comment = fields.Text(related="product_id.asset_comment",string = 'Asset Comment')

