
from os import path

from ojo.errors import MoveError
from ojo.services import move_path
from ojo.models.file_info import FileInfo
from ojo.models.job import JobStage


class MoveService(object):

    @classmethod
    def make(cls, config):
        move_dir = config["move_service"]["dir"]
        return cls(move_dir)

    def __init__(self, move_dir):
        self.move_dir = move_dir

    def do_job(self, job):
        fi: FileInfo = job.file_info
        origin_path = fi.origin_path
        try:
            move_path(origin_path, self.move_dir)
        except Exception as e:
            job.add_error(("cannot move", e))
            return job

        to_rar_path = path.join(self.move_dir, fi.base_name)
        if not path.exists(to_rar_path):
            job.add_error(("cannot move", MoveError()))
            return job

        fi.to_rar_path = to_rar_path
        job.stage = JobStage.moved

        return job
