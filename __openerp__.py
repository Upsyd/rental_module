{
    'name': 'Rental Module',
    'version': '1.0',
    'description': """
                    This module includes managing of rent paid by the customer,
                     products,repair and replacement of rented products  paid by customers  .
                    """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'images': [],
    'depends': ['base', 'product',
                'sale', 'account', 'stock',
                ],
    'data': [
             'rental_product_view.xml',
             'rental_lines_view.xml',
             'rental_order_view.xml',
             'rental_seq.xml',
             'stock_quants_inherited_view.xml',
             'replace_product_form.xml',
             ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
