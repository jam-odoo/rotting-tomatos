qty = 200.0
times = 200
product = env['product.product'].search([('default_code', '=','ZXZX')], limit=1)

slpr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

if not product:
    product = env['product.product'].create({
      "active": True,
      "sale_ok": True,
      "purchase_ok": True,
      "type": "product",
      "categ_id": 1,
      "version": 1,
      "list_price": 9.99,
      "company_id": 1,
      "uom_id": 1,
      "uom_po_id": 1,
      "invoice_policy": "order",
      "service_type": "manual",
      "tracking": "serial",
      'name': 'Tiny Important Screw',
      'default_code': 'ZXZX',
      "route_ids": [(4, 1),(4, 23)],
    })

log(str(product))

i = 1
for poi in range(0,41):
    po = env['purchase.order'].create({
        "date_order": datetime.datetime.now(),
        "picking_type_id": 1,
        "partner_id": env.ref('base.res_partner_address_16').id,
        "partner_ref": 'SA',
        "origin": 'ACTION',
        "order_line": [(0,"virtual_921",{
              "sequence": 10,
              "product_id": product.id,
              "name": product.display_name,
              "date_planned": datetime.datetime.now(),
              "account_analytic_id": False,
              "product_qty": qty,
              "product_uom": 1,
              "price_unit": 9.99,
            })]
      })
    po.button_confirm()
    pickings = po.picking_ids.filtered(lambda sp: sp.state == 'assigned')
    for picking in pickings:
        for move in picking.move_ids_without_package:
            log(str(len(move.move_line_ids)))
            for line in move.move_line_ids:
                line.write({'lot_name': 'SL-%s-%d'%(slpr, i), 'qty_done': 1.0})
                i = i+1
        picking.button_validate()
    env.cr.commit()
    log('{} {} {}'.format(str(product), str(po), str(pickings)))
