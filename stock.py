# This file is part stock_invoice_not_origin module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.pool import Pool, PoolMeta

__all__ = ['Move', 'ShipmentOut', 'ShipmentOutReturn']


class Move:
    __metaclass__ = PoolMeta
    __name__ = 'stock.move'

    @classmethod
    def check_origin_types(cls):
        types = super(Move, cls).check_origin_types()
        # remove customer type because we invoice moves that not has an origin
        if 'customer' in types:
            types.remove('customer')
        return types


class StockInvoiceNotOriginMixin(object):
    '''Stock Invoice Not Origin Mixin'''

    @classmethod
    def _get_invoice_line_not_origin(cls, move):
        'Return a list of invoice lines for sale line'
        InvoiceLine = Pool().get('account.invoice.line')

        invoice_line = InvoiceLine()
        invoice_line.type = 'line'
        invoice_line.product = move.product
        invoice_line.quantity = (move.quantity * -1
            if move.shipment.__name__ == 'stock.shipment.out.return'
            else move.quantity)
        invoice_line.unit = move.uom
        invoice_line.invoice_type = 'out'
        invoice_line.origin = move
        invoice_line.party = move.shipment.customer
        invoice_line.on_change_product()
        if not hasattr(invoice_line, 'unit_price'):
            invoice_line.unit_price = move.product.list_price or Decimal('0.0')
        invoice_line.stock_moves = [move]
        return invoice_line


class ShipmentOut(StockInvoiceNotOriginMixin):
    __metaclass__ = PoolMeta
    __name__ = 'stock.shipment.out'

    @classmethod
    def done(cls, shipments):
        InvoiceLine = Pool().get('account.invoice.line')

        super(ShipmentOut, cls).done(shipments)

        to_create = []
        moves_not_origin = []
        for shipment in shipments:
            for move in shipment.outgoing_moves:
                if not move.origin:
                    moves_not_origin.append(move)

            if moves_not_origin:
                for move in moves_not_origin:
                    to_create.append(
                        cls._get_invoice_line_not_origin(move)._save_values)

        if to_create:
            InvoiceLine.create(to_create)


class ShipmentOutReturn(StockInvoiceNotOriginMixin):
    __metaclass__ = PoolMeta
    __name__ = 'stock.shipment.out.return'

    @classmethod
    def done(cls, shipments):
        InvoiceLine = Pool().get('account.invoice.line')

        super(ShipmentOutReturn, cls).done(shipments)

        to_create = []
        moves_not_origin = []
        for shipment in shipments:
            for move in shipment.incoming_moves:
                if not move.origin:
                    moves_not_origin.append(move)

            if moves_not_origin:
                for move in moves_not_origin:
                    to_create.append(
                        cls._get_invoice_line_not_origin(move)._save_values)

        if to_create:
            InvoiceLine.create(to_create)
