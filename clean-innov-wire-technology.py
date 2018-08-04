def get_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

env.cr.execute("UPDATE stock_move SET state='draft'")
env.cr.execute("UPDATE stock_move_line SET state='draft'")
env.cr.execute("UPDATE stock_picking SET state='draft'")
env.cr.execute("UPDATE stock_inventory SET state='draft'")
env.cr.execute("UPDATE purchase_order SET state='draft'")
env.cr.execute("UPDATE sale_order SET state='draft'")
env.cr.execute("UPDATE mrp_production SET state='cancel'")
env.cr.execute("UPDATE mrp_workorder SET state='cancel'")
env.cr.execute("UPDATE stock_scrap SET state='draft'")


env.cr.commit()
models = [
    'stock.move', 'stock.move.line', 'stock.picking', 'stock.quant',
    'stock.inventory', 'stock.inventory.line', 'change.production.qty',
    'mrp.production', 'mrp.workorder', 'stock.scrap'
    
]
for model in models:
    record_ids = env[model].search([])
    #Lets not try to overlaod the server and  unlink records gracefully.
    for chunk in get_chunks(record_ids, 1000):
        chunk.unlink()
        env.cr.commit()
