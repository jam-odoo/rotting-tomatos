if not object.partner_id:
    raise Warning('Can Not Process Repair\nReason being No Partner Selected in Picking !')
if not object.x_sub_contractor_id:
    raise Warning('Can Not Process Repair\nReason being No Sub-contractor Selected in Picking !')

subcontra = object.x_sub_contractor_id

sale_model = pool.get('sale.order')
saleline_model = pool.get('sale.order.line')
po_model = pool.get('purchase.order')
poline_model = pool.get('purchase.order.line')
mrp_model = pool.get('mrp.production')
prod_line_model = self.pool.get('mrp.production.product.line')
bom_model = pool.get('mrp.bom')
prodlot_model = pool.get('stock.production.lot')
out_model = pool.get('stock.picking.out')
move_model = pool.get('stock.move')
test_model = pool.get('x_testing')
uom_model = pool.get('product.uom')
product_model = pool.get('product.product')
acc_pos_model = pool.get('account.fiscal.position')

sequence_model = pool.get('ir.sequence')

if not object.x_tag:
    tag = sequence_model.next_by_code(cr, 1, 'picking.tag', context)
    object.write({'x_tag': tag})
else:
    tag = object.x_tag
products =   [ line.product_id for line in object.move_lines if line.product_id]

date_order = object.min_date and object.min_date[:10] or time.strftime("%Y-%m-%d")

order_id = False
test_id = False
mrp_id = False
delivery_id = False
po_id = False
serial = False
#Create the Delivery Order
if object.x_do_id:
    delivery_id = object.x_do_id.id
    delivery = object.x_do_id
else:
    if products:
        delivery = {
            'origin': object.name,
            'x_tag': tag,
            'date': date_order,
            'type': 'out',
            'move_type': 'direct',
            'partner_id': object.x_sub_contractor_id.id,
            'note': object.note,
            'invoice_state': 'none',
            'company_id': object.company_id.id,
            'x_rfq': object.x_rfq_num,
            'x_vendor': object.x_vendor,
            'x_misc': object.x_misc,
            'x_customer_ref': object.x_customer_ref,
            'x_customer_part': object.x_customer_part,
        }
        delivery_id = out_model.create(cr, uid, delivery)
        delivery = out_model.browse(cr, uid, delivery_id)

        for line in object.move_lines:
            linevals = {
                'name': line.name,
                'picking_id': delivery_id,
                'product_id': line.product_id.id,
                'date': delivery.date,
                'date_expected': delivery.min_date or  delivery.date,
                'product_qty': line.product_qty,
                'prodlot_id': line.prodlot_id and line.prodlot_id.id or False,
                'product_uom': line.product_uom.id,
                'product_uos_qty': line.product_uos_qty,
                'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
                'product_packaging': line.product_packaging and line.product_packaging.id or False,
                'partner_id': line.partner_id and line.partner_id.id or delivery.partner_id.id,
                'location_id': line.location_dest_id.id,
                'location_dest_id': subcontra.property_stock_supplier.id,
                'tracking_id': line.tracking_id and line.tracking_id.id or False,
                'state': 'draft',
                'company_id': object.company_id.id,
                'price_unit': line.product_id.standard_price or 0.0
            }
            move_model.create(cr, uid, linevals)

#DOCUMENT: Create Purchase
if object.x_ref_po_id:
    po_id = object.x_ref_po_id.id
    purchase = object.x_ref_po_id
else:
    if products:
        name = sequence_model.get(cr, uid, 'purchase.order') or tag
        po_vals = {
            'name': name,
            'x_tag': tag,
            'origin': tag,
            'partner_id': subcontra.id,
            'location_id': po_model.onchange_dest_address_id(cr, uid, False, subcontra.id)['value']['location_id'],
            'date_order': date_order,
            'company_id': object.company_id.id,
        }
        po_vals.update(po_model.onchange_partner_id(cr, uid, [], subcontra.id)['value'])

        po_id = po_model.create(cr, uid, po_vals)
        purchase = po_model.browse(cr, uid, po_id, context=context)
        po_vals = po_model.onchange_warehouse_id(cr, uid, po_id, purchase.warehouse_id.id)['value']
        purchase.write(po_vals)
        for line in object.move_lines:
            if line.product_id:
                new_context = context.copy()
                new_context.update({'lang': subcontra.lang, 'partner_id': subcontra.id})
                product_id = line.product_id.x_switch_id and line.product_id.x_switch_id.id or line.product_id.id
                product_rec = product_model.browse(cr, uid, product_id, context=new_context)
                taxes_ids = line.product_id.supplier_taxes_id
                taxes = acc_pos_model.map_tax(cr, uid, subcontra.property_account_position, taxes_ids)
                somevals = poline_model.onchange_product_id(cr, uid, [], purchase.pricelist_id.id, product_id, line.product_qty, line.product_uom.id, subcontra.id, date_order=date_order, fiscal_position_id=purchase.fiscal_position or purchase.fiscal_position.id or False, date_planned=False, context=new_context)
                line_vals = {
                        'product_id': product_id,
                        'product_qty':line.product_qty,
                        'order_id': po_id,
                        'name': product_rec.partner_ref,
                        'product_uom': line.product_uom.id,
                        'price_unit': line.product_id.standard_price or 0.0,
                        'date_planned': date_order,
                        'taxes_id': [(6,0,taxes)],
                }
                line_vals.update(somevals)
                poline_model.create(cr, uid, line_vals)


# Document : PROCESS SALE
if object.x_ref_so_id:
    order_id = object.x_ref_so_id.id
    sale = object.x_ref_so_id
else:
    if products:
        sale_vals = {
            'x_tag': tag,
            'partner_id': object.partner_id.id,
            'date_order': date_order,
            'user_id': uid,
            'template_id': object.x_quote_template.id,
            'x_carrier_in': object.x_carrier_in,
            'origin': object.name,
            'state': 'draft',
            'partner_invoice_id': object.partner_id.id,
            'partner_shipping_id': object.partner_id.id,
            'x_rfq': object.x_rfq_num,
            'x_purchase': object.x_po_num,
            'x_shipper_num': object.x_shipper_num,
            'x_vendor_num': object.x_vendor,
            'x_misc': object.x_misc,
            'x_partner_part_num': object.x_customer_ref,
            'client_order_ref': object.x_customer_part,
        }
        order_id = sale_model.create(cr, uid, sale_vals, context=context)
        sale = sale_model.browse(cr, uid, order_id, context=context)
        for line in object.move_lines:
            if line.product_id:
                product_id = line.product_id.x_switch_id and line.product_id.x_switch_id.id or line.product_id.id
                product_rec = product_model.browse(cr, uid, [product_id], context=context)[0]
                line_vals = {
                    'product_id': product_id,
                    'product_qty':line.product_qty,
                    'order_id': sale.id,
                }
                line_vals.update(saleline_model.product_id_change(cr, uid, [], sale.pricelist_id.id, line_vals['product_id'], qty=line_vals['product_qty'], uom=product_rec.uom_id.id, qty_uos=0, uos=False, name='', partner_id=object.partner_id.id, date_order=sale.date_order, fiscal_position=sale.fiscal_position.id, context=context)['value'])
                if line_vals.get('taxes_id'):
                    line_vals['taxes_id'] = [[6, 0, line_vals['taxes_id']]]
                line_id = saleline_model.create(cr, uid, line_vals, context=context)
    #Prepare the x_testing record
    serial = [line.prodlot_id for line in object.move_lines if line.prodlot_id] and [line.prodlot_id for line in object.move_lines if line.prodlot_id][0] or False

#Second DocumentPROCESS TESTING RECORD
if object.x_testing:
    test_id = object.x_testing.id
else:
    if products:
        test_vals = {
            'x_name' :  tag,
            'x_order': order_id,
            'x_date': date_order,
            'x_product': products[0].x_switch_id and products[0].x_switch_id.id or product[0].id,
            'x_serial_num': serial and serial.id or False,
            'x_tech': uid,
        }
        #Creating the Test Record
        test_id = test_model.create(cr, uid, test_vals, context=context)

if order_id:
    #Updating the Test on Sale Order
    sale_model.write(cr, uid, order_id, {'x_test': test_id})

#End with putting right links
object.write({"x_ref_prod_id": mrp_id, "x_ref_so_id": order_id, "x_testing": test_id, 'x_ref_po_id': po_id, 'x_do_id': delivery_id})
