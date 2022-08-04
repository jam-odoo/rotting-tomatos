av_map = {}

for at_i in range(1, 6):
    att_id = env['product.attribute'].create({'name': 'ATTR-%d'%(at_i)})
    value_ids = []
    for va_i in range(1,4):
        val_id = env['product.attribute.value'].create({'name': 'VALUE-%d'%(va_i), 'attribute_id': att_id.id})
        value_ids.append(val_id.id)
    av_map.update({att_id.id: value_ids})


for pid in range(1,1000):
    pvals = {
        "type": "consu",
        "name": "Product %d"%(pid),
        "sale_ok": True,
        "purchase_ok": True,
        "active": True,
        "uom_id": 1,
        "uom_po_id": 1,
        "list_price": 1,
        "standard_price": 0,
        "categ_id": 1,
        "default_code": 'PCODE-%d'%(pid),
    }
    # raise Warning(pvals)
    pt_id = env['product.template'].create(pvals)
    
    for av_m in av_map:
        env['product.template.attribute.line'].create({
              "product_tmpl_id": pt_id.id,
              "attribute_id": av_m,
              "value_ids": [ (4, ix) for ix in av_map[av_m]]
            })
    env.cr.commit()