import logging


def make_worker(name, service, work_q, done_q, error_q):
    def worker():
        while True:
            job = work_q.get()
            try:
                if job is None:
                    logging.info("{name} is done! ".format(name=name))
                    break
                logging.info("{name} got job {job} ".format(name=name, job=job))
                done_job = service.do_job(job)
                if done_job.has_error():
                    logging.error("{name} done job with error {job} ".format(name=name, job=done_job))
                    error_q.put(done_job)
                else:
                    done_q.put(done_job)
                    logging.info("{name} done job successfully {job} ".format(name=name, job=job))
            except Exception as e:
                logging.error("{name} got exception from job {e} ".format(name=name, job=job, e=e))
                job.add_error(e)
                error_q.put(job)
            finally:
                work_q.task_done()
    return worker


def make_error_worker(name, error_service, error_q):
    def worker():
        while True:
            job = error_q.get()
            try:
                if job is None:
                    logging.info("{name} is done! ".format(name=name))
                    break
                logging.info("{name} got job {job} ".format(name=name, job=job))
                error_service.do_job(job)
            except Exception as e:
                logging.error("{name} got exception from job {e} ".format(name=name, job=job, e=e))
            finally:
                error_q.task_done()
    return worker
