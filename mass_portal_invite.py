def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

partners = model.search([('user_ids', '=', False), ('email', '!=', False), ('company_type', '!=', 'company')])
for chunk in chunks(partners, 10):
    wiz_context = {
        'active_ids': chunk.ids,
        'active_id': chunk[0].id,
        'active_model': 'res.partner'
    }
    wiz_model = env['portal.wizard'].with_context(wiz_context)
    wiz_id = wiz_model.create({})
    wiz_id.user_ids.write({'in_portal': True})
    log(str(wiz_id.user_ids))
    try:
      wiz_id.action_apply()
      env.cr.commit()
    except Exception as ex:
      msg = 'Skipping failed : %s\n\nwith following error:\n=======================================\n%s'%(str(chunk),str(ex))
      log(msg, level='error')
