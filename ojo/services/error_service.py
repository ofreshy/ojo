import logging


from ojo.models.job import JobStage

# TODO fill those in

def _created_handler(job, error_dir):
    pass


def _moved_handler(job, error_dir):
    pass


def _rarred_handler(job, error_dir):
    pass


def _parred_handler(job, error_dir):
    pass


def _end_of_world_handler(job, error_dir):
    pass


job_to_handlers = {
    JobStage.created: _created_handler,
    JobStage.moved: _moved_handler,
    JobStage.rarred: _rarred_handler,
    JobStage.parred: _parred_handler,
}


class ErrorService(object):
    @classmethod
    def make(cls, config):
        error_dir = config["error_service"]["dir"]
        return cls(error_dir)

    def __init__(self, error_dir):
        self.error_dir = error_dir

    def do_job(self, job):
        logging.info("got job error in stage {0} ".format(job.stage))
        handler = job_to_handlers.get(job.stage, _end_of_world_handler)
        return handler(job, self.error_dir)
