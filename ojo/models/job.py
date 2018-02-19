from time import time
import uuid

from enum import Enum

import attr

from collections import OrderedDict

from ojo.models.file_info import FileInfo


class JobStage(Enum):
    created = 1
    moved = 2
    rarred = 3
    parred = 4
    uploaded = 5


@attr.s
class Job(object):

    @classmethod
    def make(cls, origin_path):
        return cls(
            id=uuid.uuid4(),
            start_time=time(),
            file_info=FileInfo.make(origin_path),
        )

    id = attr.ib()
    start_time = attr.ib()
    file_info = attr.ib()

    _current_stage = attr.ib(default=JobStage.created)
    stage = attr.ib(default=JobStage.created)
    completed_stages = attr.ib(default=attr.Factory(OrderedDict))
    _errors = attr.ib(default=attr.Factory(list))

    def add_error(self, error):
        self._errors.append(error)

    def has_error(self):
        return bool(self._errors)

    @property
    def stage(self):
        return self._current_stage

    @stage.setter
    def stage(self, stage):
        self.completed_stages[self._current_stage] = time()
        self._current_stage = stage

