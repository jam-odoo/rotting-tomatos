if not object.partner_id:
    raise Warning('Can Not Process Repair\nReason being No Partner Selected in Picking !')

if not object.x_tag:
    tag = pool['ir.sequence'].next_by_code(cr, 1, 'picking.tag', context)
    object.write({'x_tag': tag})
else:
    tag = object.x_tag

sale_model = pool.get('sale.order')
saleline_model = pool.get('sale.order.line')
mrp_model = pool.get('mrp.production')
prod_line_model = self.pool.get('mrp.production.product.line')
bom_model = pool.get('mrp.bom')
prodlot_model = pool.get('stock.production.lot')
uom_model = pool.get('product.uom')
product_model = pool.get('product.product')
test_model = pool.get('x_testing')

order_id = False
test_id = False
mrp_id = False

products =   [line.product_id for line in object.move_lines if line.product_id]
date_order = object.min_date and object.min_date or time.strftime("%Y-%m-%d")

#First Document : PROCESS SALE
if object.x_ref_so_id:
    order_id = object.x_ref_so_id.id
    sale = object.x_ref_so_id
else:
    sale_vals = {
        'x_tag': tag,
        'template_id': object.x_quote_template.id,
        'partner_id': object.partner_id.id,
        'date_order': date_order,
        'user_id': uid,
        'origin': object.name,
        'state': 'draft',
        'partner_invoice_id': object.partner_id.id,
        'partner_shipping_id': object.partner_id.id,
        'x_rfq': object.x_rfq_num,
        'x_carrier_in': object.x_carrier_in,
        'x_purchase': object.x_po_num,
        'x_shipper_num': object.x_shipper_num,
        'x_vendor_num': object.x_vendor,
        'x_misc': object.x_misc,
        'x_partner_part_num': object.x_customer_part,
        'client_order_ref': object.x_customer_ref,
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
            line_vals['name'] =  tag +" - "+ line_vals['name'] 
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
        }
        #Creating the Test Record
        test_id = test_model.create(cr, uid, test_vals, context=context)

#Updating the Test on Sale Order
sale_model.write(cr, uid, order_id, {'x_test': test_id})

#Third Document: PROCESS MRP PRODUCTION
if object.x_ref_prod_id:
    mrp_id = object.x_ref_prod_id.id
else:
    #Collect all Parent Product Line assuming they are to be produced.
    to_produce_product = [ line for line in sale.order_line if not line.x_parent_part_id]
    #Process all To Produce Lines and Trigger MO for it, 
    for produce in to_produce_product:
        bom_id = bom_model._bom_find(cr, uid, produce.product_id.id, produce.product_uom.id, properties=[prop.id for prop in produce.property_ids])
        if serial:
            serialnum = prodlot_model.create(cr, uid, {'name': serial.name, 'product_id': produce.product_id.id, 'ref': tag})
        if not bom_id:
            continue
        bom = bom_model.browse(cr, uid, bom_id, context=context)
        mrp_vals = {
            'bom_id': bom_id,
            'x_tag':  tag,
            'origin': sale.name,
            'product_id': produce.product_id.id,
            'product_qty': produce.product_uom_qty,
            'product_uom': produce.product_uom.id,
            'product_uos_qty': produce.product_uos_qty,
            'product_uos': produce.product_uos.id,
            'state': 'draft',
            'x_serial_fg': serialnum
        }
        mrp_id = mrp_model.create(cr, uid, mrp_vals, context=context)
        mrp_model.action_compute(cr, uid, [mrp_id], [prop.id for prop in produce.property_ids], context)
        #Updating the Test on Sale Order
        test_model.write(cr, uid, test_id, {'x_manufacturing': mrp_id})

#End with putting right links
object.write({"x_ref_prod_id": mrp_id, "x_ref_so_id": order_id, "x_testing": test_id})
