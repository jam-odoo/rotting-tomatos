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

for model in ['product.public.category', 'mrp.bom', 'stock.move', 'stock.move.line', 'stock.picking', 'stock.inventory', 'stock.inventory.line', 'stock.quant']:
    record_ids = env[model].search([])
    for chunk in get_chunks(record_ids, 100):
        chunk.unlink()
        env.cr.commit()

pp_ids = env['product.product'].search([])
for x in get_chunks(pp_ids, 1000):
    x.unlink()
    env.cr.commit()
  
