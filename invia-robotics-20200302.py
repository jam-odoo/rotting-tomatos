# ó_ò --> ¯\(°_o)/¯
ia_datetime_final = record.date
ia_date_final = record.date.strftime('%Y-%m-%d')
log_it = ""
for stock_move in record.move_ids:
    move_fields = ['date', 'date_expected']
    for account_move in stock_move.account_move_ids:
        for account_move_line in account_move.line_ids:
            env.cr.execute("UPDATE account_move_line set date= '%s' WHERE id=%s"%(ia_date_final, account_move_line.id))
        env.cr.execute("UPDATE account_move set date='%s' WHERE id=%s"%(ia_date_final, account_move.id))
    for stock_move_line in stock_move.move_line_ids:
        env.cr.execute("UPDATE stock_move_line set date='%s' WHERE id=%s"%(ia_datetime_final, stock_move_line.id))
    env.cr.execute("UPDATE stock_move set date='%s',date_expected='%s' WHERE id=%s"%(ia_datetime_final,ia_datetime_final, stock_move.id))
    log_it = "{}\n {:30}  => {}".format(log_it, str(stock_move), str(stock_move.account_move_ids))
log(log_it)
