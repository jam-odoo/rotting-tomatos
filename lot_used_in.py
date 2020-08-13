move_line_ids = env['stock.move.line'].search([('state', '=', 'done'), ('location_dest_id.usage', '=', 'production'), ('lot_id', '=', record.id)])
move_ids = move_line_ids.mapped('move_id').filtered_domain([('raw_material_production_id', '!=', False)])
mo_ids = move_ids.mapped('raw_material_production_id').ids
mo_move_ids = env['stock.move'].search([('production_id', 'in', mo_ids), ('state', '=', 'done'), ('location_id.usage', '=', 'production')])

move_dest_ids = mo_move_ids.mapped('move_dest_ids').filtered_domain([('state', '=' ,'done')])
if move_dest_ids:
    move_action = env.ref('stock.stock_move_action').read()[0]
    if len(move_dest_ids) == 1:
        move_action['domain'] = [('id', '=', move_dest_ids.ids[0])]
    else:
        move_action['domain'] = [('id', 'in', move_dest_ids.ids)]
    move_action['context'] = {'search_default_done': 1, 'search_default_groupby_dest_location_id': 1}
    action = move_action
else:
    raise Warning('No stock found where the lot/serial "%s" was used'%(record.name))
