
from os import path
import shutil

from ojo.models.job import JobStage


class OjoError(Exception):
    pass


class MoveError(OjoError):
    pass


class MoveService(object):

    @classmethod
    def make(cls, config):
        move_dir = config["move_service"]["dir"]
        return cls(move_dir)

    def __init__(self, move_dir):
        self.move_dir = move_dir

    def do_job(self, job):
        try:
            shutil.move(job.origin_path, self.move_dir)
        except Exception as e:
            job.add_error(("cannot move", e))
            return job

        move_to_path = path.join(self.move_dir, path.basename(job.origin_path))
        if not path.exists(move_to_path):
            job.add_error(("cannot move", MoveError()))
            return job

        job.move_to_path = move_to_path
        job.stage = JobStage.moved

        return job
