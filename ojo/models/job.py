from itertools import chain
from time import time
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

    @staticmethod
    def make(src_path):
        file_info = FileInfo.make(src_path)
        return JobInfo.make(file_info)

class JobInfo(object):
    """

    """
    counter = 0

    @classmethod
    def make(cls, file_info):
        JobInfo.counter += 1

        return cls(
            id=JobInfo.counter,
            stage=JobStage.created,
            file_info=file_info,
            start_time=time(),
        )

    def __init__(self, id, stage, file_info, start_time, end_time=None):
        self.id = id
        self.stage = stage
        self.file_info = file_info
        self.start_time = start_time
        self.end_time = end_time
        self.errors = []

    def add_error(self, error):
        self.errors.append(error)

    def has_error(self):
        return bool(self.errors)


class FileInfo(object):
    @classmethod
    def make(cls, src_path):
        dir_name = os.path.dirname(src_path)
        base_name = os.path.basename(src_path)
        file_name, _, extension = base_name.partition(".")
        file_size_mb = os.stat(src_path).st_size / MB
        is_dir = os.path.isdir(src_path)
        children = [
            FileInfo.make(os.path.join(src_path, f))
            for f in os.listdir(src_path)
            if f not in ("\\", "±")
        ] if is_dir else []
        return cls(
            src_path=src_path,
            dir_name=dir_name,
            base_name=base_name,
            file_name=file_name,
            extension=extension,
            is_dir=is_dir,
            file_size_mb=file_size_mb,
            children=children,
        )

    def __init__(
            self,
            src_path,
            dir_name,
            base_name,
            file_name,
            extension,
            is_dir,
            file_size_mb,
            children,
    ):
        self.src_path = src_path
        self.dir_name = dir_name
        self.base_name = base_name
        self.file_name = file_name
        self.extension = extension
        self.is_dir = is_dir
        self.file_size_mb = file_size_mb

        self.rar_location = ""
        self.par_location = ""
        self.uploaded_location = ""

        self.children = children

    def file_children(self):
        return [c for c in self.children if c.is_file]

    def all_file_children(self):
        return list(chain((c.all_file_children for c in self.children)))

    @property
    def is_file(self):
        return not self.is_dir


