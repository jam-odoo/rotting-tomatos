
env.cr.execute("UPDATE procurement_order SET state='cancel'")
env.cr.execute("UPDATE stock_move SET state='draft'")
env.cr.execute("UPDATE stock_picking SET state='draft'")
env.cr.execute("UPDATE stock_inventory SET state='draft'")

env["procurement.order"].sudo().search([]).unlink()
env["stock.pack.operation"].sudo().search([]).unlink()
env["stock.move"].sudo().search([]).unlink()
env["stock.picking"].sudo().search([]).unlink()
env["stock.inventory"].sudo().search([]).unlink()

env.cr.execute("TRUNCATE stock_quant CASCADE")
env["stock.production.lot"].sudo().search([]).unlink()
env["stock.quant.package"].sudo().search([]).unlink()

env.cr.execute("UPDATE sale_order SET state='draft'")
env["sale.order.line"].sudo().search([]).unlink()
env["sale.order"].sudo().search([]).unlink()

env.cr.execute("UPDATE purchase_order SET state='cancel'")
env["purchase.order.line"].sudo().search([]).unlink()
env["purchase.order"].sudo().search([]).unlink()

env.cr.execute("UPDATE account_move SET state='draft'")
env.cr.execute("UPDATE account_invoice SET state='draft', move_name=''")
env.cr.execute("UPDATE account_payment SET state='draft'")

move_ids = env["account.move.line"].sudo().search([])
wiz_id = env["account.unreconcile"].sudo().create({})
wiz_id.sudo().with_context(active_ids=[mv.id for mv in move_ids ]).trans_unrec()

env["account.invoice.line"].sudo().search([]).unlink()
env["account.invoice"].sudo().search([]).unlink()
env["account.move.line"].sudo().search([]).unlink()
env["account.move"].sudo().search([]).unlink()
env["account.payment"].sudo().search([]).unlink()

env.cr.execute("UPDATE mrp_production SET state='draft'")
env["mrp.production"].sudo().search([]).unlink()
env["mrp.production.workcenter.line"].sudo().search([]).unlink()

env["workflow.instance"].sudo().search([("res_type", "in", ("account.invoice", "mrp.production.workcenter.line", "mrp.production") )]).unlink()
