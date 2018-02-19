import logging
import os
from os import path

from ojo.services import move_path
from ojo.models.file_info import FileInfo
from ojo.models.job import JobStage

# TODO fill those in


def _created_handler(job, error_dir):
    """

    :param job:
    :param error_dir:
    :return:
    """
    fi: FileInfo = job.file_info

    if not path.exists(fi.origin_path):
        logging.warning("error service has nothing to do with job, as path {} does not exist.".format(
                fi.origin_path,
            )
        )
        return

    try:
        error_path = path.join(error_dir, str(job.id))
        os.makedirs(error_path)
        move_path(fi.origin_path, error_path)
        logging.info(
            "error service moved files from {0} to {1}".format(
                fi.origin_path,
                fi.error_path,
            )
        )
        fi.error_path = error_path
    except Exception as e:
        logging.warning(
            "error service cannot move files in job {}, {}".format(
                job,
                e,
            )
        )


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
