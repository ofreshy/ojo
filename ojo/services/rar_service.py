import logging

from ojo.constants import MB
from ojo.errors import RarError
from ojo.models.job import JobStage
from ojo.models.file_info import FileInfo
from ojo.services import *

RAR_COMMAND = "rar"

BASE_RAR_ARGS = ("a", "-m0", "-ep", "-ed")


def is_installed():
    return is_installed(RAR_COMMAND)


def execute(fi: FileInfo):
    """
    Runs a command from fi object such as
    >>> rar a -m0 -ep -ed -v100000 path/to/destination path/to/src
    :param fi: with vol_size, to_par_path and abs_path initialized
    :return: result code of sub process code, raises an error if not 0
    """
    extra_args = ("-v%s" % fi.vol_size, fi.to_par_path, fi.to_rar_path)
    return run_command(RAR_COMMAND, BASE_RAR_ARGS + extra_args)


def calc_rar_volume_size(file_size_kb):
    file_size_mb = file_size_kb / MB

    if 0 < file_size_mb < 700:
        rar_vol_size_mb = 10
    elif 700 < file_size_mb < 3000:
        rar_vol_size_mb = 40
    elif 3000 < file_size_mb < 5000:
        rar_vol_size_mb = 100
    else:
        rar_vol_size_mb = 200

    # *MB so we get size in kb
    return rar_vol_size_mb * MB


class RarService(object):
    @classmethod
    def make(cls, config):
        return cls(
            config["rar_service"]["dir"]
        )

    def __init__(self, to_par_path):
        self.to_par_path = to_par_path

    def do_job(self, job):
        if job.stage != JobStage.moved:
            job.add_error(RarError())
            return job
        try:
            fi = job.file_info
            to_par_path = path.join(self.to_par_path, fi.file_name, fi.file_name)
            create_path(to_par_path)
            vol_size = calc_rar_volume_size(fi.file_size_mb)
            fi.to_par_path = to_par_path
            fi.vol_size = vol_size
            logging.info("got file info : {0}".format(fi))
            execute(fi)

            job.stage = JobStage.rarred
            return job
        except Exception as e:
            job.add_error(e)
            logging.error(e)
            return job
