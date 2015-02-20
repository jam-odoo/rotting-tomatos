sids = self.search(cr, uid, [])
for re in self.browse(cr, uid, sids):
    re.delete_workflow()
    re.write({'state': 'draft', 'invoiced': False})
    re.create_workflow()
