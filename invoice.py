# This file is part stock_invoice_not_origin module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import PoolMeta

__all__ = ['InvoiceLine']


class InvoiceLine:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice.line'

    @classmethod
    def _get_origin(cls):
        models = super(InvoiceLine, cls)._get_origin()
        if not 'stock.move' in models:
            models.append('stock.move')
        return models
