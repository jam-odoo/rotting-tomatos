#TRY THIS YOUR OWN RISK, NO GURANTEE OF WORKING :P
# I hope you know what you are doing

def get_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

env.cr.execute("UPDATE stock_move SET state='draft'")
env.cr.execute("UPDATE stock_move_line SET state='draft'")
env.cr.execute("UPDATE stock_picking SET state='draft'")
env.cr.execute("UPDATE stock_inventory SET state='draft'")
env.cr.commit()
models = [
    'product.public.category', 'mrp.bom', 'mrp.bom.line',
    'stock.move', 'stock.move.line', 'stock.picking', 'stock.quant',
    'stock.inventory', 'stock.inventory.line', 
    'delivery.carrier', 'product.product'
]
for model in models:
    record_ids = env[model].search([])
    #Lets not try to overlaod the server and  unlink records gracefully.
    for chunk in get_chunks(record_ids, 1000):
        chunk.unlink()
        env.cr.commit()
