 # I Hope you know what you are doingif you choose to use this.
 # Use at your own risk, I am not taking reposbiblity or answering any quearion reatled.
 # After running this scroll though all the tables to make sure their no traceback left.
 # and also run vaccum power on after this.
 
 
 def chunks(l, n):       
     for i in range(0, len(l), n):
         yield l[i:i+n]

env.cr.execute("UPDATE stock_move SET state='draft'")
env.cr.execute("UPDATE stock_move_line SET state='draft'")
env.cr.execute("UPDATE stock_picking SET state='draft'")
env.cr.execute("UPDATE stock_inventory SET state='draft'")
env.cr.execute("UPDATE stock_picking_batch SET state='draft'")
env.cr.execute("UPDATE purchase_order SET state='cancel'")
env.cr.execute("UPDATE purchase_requisition	 SET state='cancel'")
env.cr.execute("UPDATE sale_order SET state='draft'")
env.cr.execute("UPDATE sale_order_line SET state='draft'")
env.cr.execute("UPDATE mrp_production SET state='cancel'")
env.cr.execute("UPDATE mrp_workorder SET state='cancel'")
env.cr.execute("UPDATE stock_scrap SET state='draft'")
env.cr.execute("UPDATE account_payment SET state='draft'")
env.cr.execute("UPDATE account_move SET state='draft'")
env.cr.execute("UPDATE account_invoice SET state='draft', move_name=''")
env.cr.execute("UPDATE account_payment SET state='draft', move_name=''")
env.cr.execute("UPDATE account_bank_statement SET state='draft'")

env.cr.commit()
models = [
    'stock.move', 'stock.move.line', 'stock.picking', 'stock.quant',
    'stock.picking.batch',
    'stock.inventory', 'stock.inventory.line', 'change.production.qty',
    'mrp.production', 'mrp.workorder', 'stock.scrap',
    'account.invoice.line', 'account.invoice.tax', 'account.invoice',
    'account.partial.reconcile', 'account.full.reconcile',
    'account.move.line', 'account.move',
    'account.bank.statement.line','account.bank.statement',
    'account.payment',
    'sale.order.line', 'sale.order.option', 'sale.order',
    'purchase.order.line', 'purchase.order',
    'purchase.requisition.line', 'purchase.requisition',

]
for model in models:
    record_ids = env[model].search([])
    #Lets not try to overlaod the server and  unlink records gracefully.
    for chunk in chunks(record_ids, 1000):
        chunk.unlink()
        env.cr.commit()
