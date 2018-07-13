=================================
Stock Invoice Not Origin Scenario
=================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules, set_user
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, create_tax_code
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences
    >>> today = datetime.date.today()
    >>> yesterday = today - relativedelta(days=1)

Install stock Module::

    >>> config = activate_modules('stock_invoice_not_origin')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]
    >>> period_ids = [p.id for p in fiscalyear.periods]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> account_tax = accounts['tax']
    >>> account_cash = accounts['cash']

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('20')
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.save()
    >>> product, = template.products

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> customer_loc, = Location.find([('code', '=', 'CUS')])
    >>> output_loc, = Location.find([('code', '=', 'OUT')])
    >>> in_loc, = Location.find([('code', '=', 'IN')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])

Make 10 unit of the product available::

    >>> StockMove = Model.get('stock.move')
    >>> incoming_move = StockMove()
    >>> incoming_move.product = product
    >>> incoming_move.uom = unit
    >>> incoming_move.quantity = 1
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.company = company
    >>> incoming_move.unit_price = Decimal('1')
    >>> incoming_move.currency = company.currency
    >>> incoming_move.click('do')

Create Shipment Out::

    >>> ShipmentOut = Model.get('stock.shipment.out')
    >>> shipment_out = ShipmentOut()
    >>> shipment_out.planned_date = today
    >>> shipment_out.customer = customer
    >>> shipment_out.warehouse = warehouse_loc
    >>> shipment_out.company = company
    >>> move = StockMove()
    >>> shipment_out.outgoing_moves.append(move)
    >>> move.product = product
    >>> move.uom = unit
    >>> move.quantity = 1
    >>> move.from_location = output_loc
    >>> move.to_location = customer_loc
    >>> move.company = company
    >>> move.unit_price = Decimal('2')
    >>> move.currency = company.currency
    >>> shipment_out.save()
    >>> shipment_out.click('wait')
    >>> shipment_out.click('assign_try')
    True
    >>> shipment_out.click('pack')
    >>> shipment_out.click('done')

Create Shipment Out Return::

    >>> ShipmentOut = Model.get('stock.shipment.out.return')
    >>> shipment_out_return = ShipmentOut()
    >>> shipment_out_return.planned_date = today
    >>> shipment_out_return.customer = customer
    >>> shipment_out_return.warehouse = warehouse_loc
    >>> shipment_out_return.company = company
    >>> move = StockMove()
    >>> shipment_out_return.incoming_moves.append(move)
    >>> move.product = product
    >>> move.uom = unit
    >>> move.quantity = 1
    >>> move.from_location = customer_loc
    >>> move.to_location = in_loc
    >>> move.company = company
    >>> move.unit_price = Decimal('2')
    >>> move.currency = company.currency
    >>> shipment_out_return.save()
    >>> shipment_out_return.click('receive')
    >>> shipment_out_return.click('done')

Search Invoice Line::

    >>> Line = Model.get('account.invoice.line')
    >>> line1, line2 = Line.find([])
    >>> line1.party == customer
    True
    >>> line1.unit_price ==  Decimal('20')
    True
    >>> line1.quantity == Decimal(1.0)
    True
    >>> line2.party == customer
    True
    >>> line2.unit_price ==  Decimal('20')
    True
    >>> line2.quantity == Decimal(-1.0)
    True
