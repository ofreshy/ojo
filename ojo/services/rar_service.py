import logging

from ojo.constants import MB
from ojo.errors import RarError
from ojo.models.job import JobStage, Job
from ojo.models.file_info import FileInfo
from ojo.services import *

RAR_COMMAND = "rar"

BASE_RAR_ARGS = ("a", "-m0", "-ep", "-ed")


def is_installed():
    return is_installed(RAR_COMMAND)


def execute(fi: FileInfo):
    extra_args = ("-v%s" % fi.vol_size, fi.to_par_path, fi.abs_path)
    run_command(RAR_COMMAND, BASE_RAR_ARGS + extra_args)


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


def make_file_info(job: Job):
    origin_path, src_path = job.origin_path, job.move_to_path
    abs_path = os.path.abspath(src_path)
    parent_path = os.path.dirname(src_path)
    base_name = os.path.basename(src_path)
    file_name, _, extension = base_name.partition(".")
    file_size_mb = os.stat(src_path).st_size / MB

    rel_path = os.path.relpath(src_path, parent_path)
    rel_path = "/".join(rel_path.split("/")[:-1] + [file_name])

    return FileInfo(
        origin_path,
        abs_path,
        parent_path,
        rel_path,
        base_name,
        file_name,
        extension,
        file_size_mb,
    )


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
            fi = make_file_info(job)
            to_par_path = path.join(self.to_par_path, fi.file_name, fi.file_name)
            create_path(to_par_path)
            vol_size = calc_rar_volume_size(fi.file_size_mb)
            fi.to_par_path = to_par_path
            fi.vol_size = vol_size
            logging.info("got file info : {0}".format(fi))
            execute(fi)
            job.to_par_path = to_par_path
            job.file_info = fi
            job.stage = JobStage.rarred
            return job
        except Exception as e:
            job.add_error(e)
            logging.error(e)
            return job
