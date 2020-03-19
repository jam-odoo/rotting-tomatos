quant_ids = env['stock.quant'].search([('location_id.usage','=', 'internal'), ('lot_id', '=', False)])
LotModel = env['stock.production.lot']

for quant in quant_ids:
    lot_id = LotModel.search([('product_id', '=', quant.product_id.id), ('name', '=', 'No Lot')], limit=1)
    if not lot_id:
        lot_id = LotModel.create({'product_id': quant.product_id.id, 'name': 'No Lot'})
    quant.write({'lot_id': lot_id.id})
