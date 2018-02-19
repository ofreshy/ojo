import logging

from ojo.errors import OjoError, JobStageError, UnderlyingExceptionError


class BaseService(object):

    def __init__(self, job_stage_before, job_stage_after):
        self.job_stage_before = job_stage_before
        self.job_stage_after = job_stage_after

    def do_inner_job(self, job):
        raise NotImplemented

    def do_job(self, job):
        name = self.__class__.__name__

        if job.has_error():
            logging.warning("service {0} got a job with error on work q!".format(name))
            return job

        if job.stage != self.job_stage_before:
            logging.warning("service {0} got a job in unexpected stage {1} q!".format(name, job.stage))
            job.add_error(
                JobStageError(
                    "expected job stage {} but got {}",
                    job,
                )
            )
            return job

        try:
            job = self.do_inner_job(job)
        except OjoError as oj:
            job.add_error(oj)
        except Exception as e:
            logging.warning("service {0} unexpected exception {1}!".format(name, e))
            job.add_error(
                UnderlyingExceptionError(
                    "in do inner job",
                    job,
                    e,
                )
            )

        if job.has_error():
            return job

        job.stage = self.job_stage_after
        return job

