# This file is part stock_invoice_not_origin module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import invoice
from . import stock

def register():
    Pool.register(
        invoice.InvoiceLine,
        stock.Move,
        stock.ShipmentOut,
        stock.ShipmentOutReturn,
        module='stock_invoice_not_origin', type_='model')
