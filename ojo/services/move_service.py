
from os import path

from ojo.errors import IllegalStateError
from ojo.services import move_path
from ojo.services.base_service import BaseService
from ojo.models.file_info import FileInfo
from ojo.models.job import JobStage


class MoveService(BaseService):

    @classmethod
    def make(cls, config):
        move_dir = config["move_service"]["dir"]
        return cls(move_dir)

    def __init__(self, move_dir):
        super(MoveService, self).__init__(JobStage.created, JobStage.moved)
        self.move_dir = move_dir

    def do_inner_job(self, job):
        fi: FileInfo = job.file_info
        origin_path = fi.origin_path
        move_path(origin_path, self.move_dir)
        to_rar_path = path.join(self.move_dir, fi.base_name)
        if not path.exists(to_rar_path):
            raise IllegalStateError(
                "to_rar_path {0} does not exist after move".format(to_rar_path),
                job,
            )
        fi.to_rar_path = to_rar_path

        return job
