import logging


def make_worker(name, service, work_q, done_q, error_q):
    """
    Closure to make a worker with given params
    :param name: worker name for context, e.g. worker-rar-1
    :param service: the service that is used for doing the job
    :param work_q: q to get work from
    :param done_q: q to put done jobs on
    :param error_q: q for jobs that terminated with error
    :return: worker with given params, ready to consume jobs
    """
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
    """
    Closure to make the end of line worker - for jobs the terminated with errors
    :param name: for context, such as error-worker-1
    :param error_service: the error service that handles the errors
    :param error_q: to consume jobs from
    :return: error worker ready to work
    """
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
