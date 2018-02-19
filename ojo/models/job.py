from time import time
import uuid

from enum import Enum

import attr

from collections import OrderedDict


class JobStage(Enum):
    created = 1
    moved = 2
    rarred = 3
    parred = 4
    uploaded = 5


@attr.s
class Job(object):
    id = attr.ib()
    start_time = attr.ib()
    origin_path = attr.ib()
    move_to_path = attr.ib(default=None)
    to_par_path = attr.ib(default=None)
    file_info = attr.ib(default=None)

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


def make_new_job(origin_path):
    return Job(
        id=uuid.uuid4(),
        start_time=time(),
        origin_path=origin_path
    )
