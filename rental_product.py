from openerp import models, fields, api,_ 


class rental_product(models.Model):

    _inherit = 'product.product'

    can_be_rented = fields.Boolean('Can be rented')
    income_account = fields.Char('Income Account')
    mothly_rental = fields.Float('Monthly Rental')
    replacement_value = fields.Float('Replacement Value')
    asset_comment = fields.Text('Asset comment ')
