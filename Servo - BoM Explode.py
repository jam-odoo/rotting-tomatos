bom_pool = self.pool.get('mrp.bom')
uom_pool = self.pool.get('product.uom')
orderline_pool = self.pool.get('sale.order.line')
product_pool = self.pool.get('product.product')
to_create = []
to_write = {}

for line in object.order_line:
    if line.product_id and line.product_id.supply_method == 'produce':
        bom_point = bom_pool._bom_find(cr, uid, line.product_id.id, line.product_uom.id)
        parts=orderline_pool.search(cr, uid, [('x_parent_part_id', '=', line.id)],context=context)
        unit_price = line.price_unit or 0.0
        if bom_point and not parts:
            bom_point = bom_pool.browse(cr, uid, [bom_point])[0]
            factor = uom_pool._compute_qty(cr, uid, line.product_uom.id, line.product_uom_qty, bom_point.product_uom.id)
            result = bom_pool._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, routing_id=bom_point.routing_id.id)
            for res in result[0]:
                values = orderline_pool.product_id_change(cr, uid, line.id, pricelist=object.pricelist_id.id, product=res['product_id'],  qty=res['product_qty'], uom=res['product_uom'], qty_uos=res['product_uos_qty'], uos=res['product_uos'], name=line.product_id.name, partner_id=object.partner_id.id, date_order=object.date_order, context=context)
                product_id = product_pool.browse(cr, uid, res['product_id'], context=context)
                if 'price_unit' in values['value'].keys():
                    unit_price += values['value']['price_unit']
                vals = {
                    'name': values['value']['name'],
                    'order_id': object.id,
                    'product_id': res['product_id'],
                    'product_uom_qty': res['product_qty'] or 0.0,
                    'product_uom': res['product_uom'] or False,
                    'product_uos_qty': res['product_uos_qty'] or 0.0,
                    'product_uos': res['product_uos'] or False,
                    'price_unit': 0.0,
                    'purchase_price': product_id.standard_price or 0.0,
                    'tax_id': values['value']['tax_id'] or False,
                    'type': product_id.procure_method,
                    'th_weight': values['value']['th_weight'] or 0.0,
                    'x_categ_id': product_id.categ_id and product_id.categ_id.id or False,
                    'x_parent_part_id': line.id,
                    'x_standard_prod': True,
                }
                exists_id = orderline_pool.search(cr, uid, [('order_id', '=', object.id), ('x_parent_part_id', '=', line.id), ('product_id', '=', product_id.id)], context=context)
                if not exists_id:
                    to_create.append(vals)
                else:
                    to_write.update({exists_id[0]: vals})
new_lines = []
for line in to_create:
    new_lines.append(orderline_pool.create(cr, uid, line, context=context))
to_bomcreate = []
# res = {'product_uos_qty': False, 'name': u'Windows 7 Professional', 'product_uom': 1, 'product_qty': 1.0, 'product_uos': False, 'product_id': 41}
for xline in orderline_pool.browse(cr, uid, new_lines):
    product_id =xline.product_id
    if product_id and product_id.supply_method == 'produce':
        bom_point = bom_pool._bom_find(cr, uid, product_id.id, xline.product_uom.id)
        if bom_point:
            bom_point = bom_pool.browse(cr, uid, [bom_point])[0]
            factor = uom_pool._compute_qty(cr, uid, xline.product_uom.id, xline.product_uom_qty, bom_point.product_uom.id)
            result = bom_pool._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, level=10, routing_id=bom_point.routing_id.id)
            unit_price = line.price_unit or 0.0
            for res in result[0]:
                values = orderline_pool.product_id_change(cr, uid, [], pricelist=object.pricelist_id.id, product=res['product_id'],  qty=res['product_qty'], uom=res['product_uom'], qty_uos=res['product_uos_qty'], uos=res['product_uos'], name=product_id.name, partner_id=object.partner_id.id, date_order=object.date_order, context=context)
                product_id = product_pool.browse(cr, uid, res['product_id'], context=context)
                if 'price_unit' in values['value'].keys():
                    unit_price += values['value']['price_unit']
                vals = {
                    'name': values['value']['name'],
                    'order_id': object.id,
                    'product_id': res['product_id'],
                    'product_uom_qty': res['product_qty'] or 0.0,
                    'product_uom': res['product_uom'] or False,
                    'product_uos_qty': res['product_uos_qty'] or 0.0,
                    'product_uos': res['product_uos'] or False,
                    'price_unit': values['value']['price_unit'] or 0.0,
                    'purchase_price': product_id.standard_price or 0.0,
                    'tax_id': values['value']['tax_id'] or False,
                    'type': product_id.procure_method,
                    'th_weight': values['value']['th_weight'] or 0.0,
                    'x_categ_id': product_id.categ_id and product_id.categ_id.id or False,
                    'x_parent_part_id': xline.id,
                    'x_standard_prod': True,
                }
                exists_id = orderline_pool.search(cr, uid, [('order_id', '=', object.id), ('x_parent_part_id', '=', xline.x_parent_part_id.id), ('product_id', '=', product_id.id)], context=context)
                if not exists_id:
                    to_bomcreate.append(vals)
                else:
                    to_write.update({exists_id[0]: vals})

for line in to_bomcreate:
    orderline_pool.create(cr, uid, line, context=context)
for key in to_write:
    orderline_pool.write(cr, uid, [key], to_write[key], context=context)
