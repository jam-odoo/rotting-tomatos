def _do_job(self, use_new_cursor=False, raise_user_error=True):
    """ 
    :param bool use_new_cursor: if set, use a dedicated cursor and auto-commit 
                                after processing next batch of record
    """
    #cron exist logic
    start_time = fields.Datetime.now()
    worker_timeout = start_time + relativedelta(minutes=14)
    batch_times = []

    for batch_ids in split_every(1000, self.ids):
       # Some logic here
        while batch_ids:
            if use_new_cursor:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))
        
            #cron exist logic, if cron projected to cross worker timeout by worst batch time then 
            # break the while and let cron exit safely
            batch_start_time = fields.Datetime.now()
            if batch_times and (batch_start_time + relativedelta(seconds=max(batch_times))) > worker_timeout:
                break
            try:
                with self.env.cr.savepoint():
                    for record in batch_ids:
                        # Some logic here
                        pass
            except Exception as ex:
                if use_new_cursor:
                    cr.rollback()
                    _logger.error('import_message_format: failed importing batch, traceback below')
                    _logger.error(traceback.format_stack())
                    continue
                if not raise_user_error:
                    raise
            finally:
                if use_new_cursor:
                    try:
                        cr.commit()
                    finally:
                        cr.close()
            #cron exist logic
            batch_end_time = fields.Datetime.now()
            batch_times.append((batch_end_time - batch_start_time).seconds)
    return {}
