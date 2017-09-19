import os

from enum import Enum

from ojo.constants import MB


class JobStage(Enum):
    created = 1
    moved = 2
    rared = 3
    parred = 4
    uploaded = 5
    on_error = 100

    def is_on_error(self, state):
        return state == self.on_error


class JobFactory(object):
    """

    """
    def __init__(self, working_dir, done_dir):
        self.working_dir = working_dir
        self.done_dir = done_dir

    def make(self, src_path):
        dir_name = os.path.dirname(src_path)
        base_name = os.path.basename(src_path)
        file_name, _, extension = base_name.partition(".")
        file_size_mb = os.stat(src_path).st_size / MB
        is_dir = os.path.isdir(src_path)

        return JobInfo(
            src_path=src_path,
            dir_name = dir_name,
            base_name=base_name,
            file_name=file_name,
            extension=extension,
            is_dir=is_dir,
            file_size_mb=file_size_mb,
        )


class JobInfo(object):
    """

    """
    def __init__(
            self,
            src_path,
            dir_name,
            base_name,
            file_name,
            extension,
            is_dir,
            file_size_mb,
    ):
        self.src_path = src_path
        self.dir_name = dir_name
        self.base_name = base_name
        self.file_name = file_name
        self.extension = extension
        self.is_dir = is_dir
        self.file_size_mb = file_size_mb

        self.stage = JobStage.created

        self.rar_location = ""
        self.par_location = ""
        self.uploaded_location = ""
        self.errors = []

    @property
    def is_file(self):
        return not self.is_dir

    def add_error(self, error):
        self.errors.append(error)

    def has_error(self):
        return bool(self.errors)
