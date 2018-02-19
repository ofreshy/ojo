import logging

from ojo.constants import MB
from ojo.models.job import JobStage
from ojo.services import *
from ojo.services.base_service import BaseService

RAR_COMMAND = "rar"

BASE_RAR_ARGS = ("a", "-m0", "-ep", "-ed")


def is_installed():
    return is_installed(RAR_COMMAND)


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


class RarService(BaseService):
    @classmethod
    def make(cls, config):
        return cls(
            config["rar_service"]["dir"]
        )

    def __init__(self, to_par_path):
        super(RarService, self).__init__(JobStage.moved, JobStage.rarred)
        self.to_par_path = to_par_path

    def do_job(self, job):
        fi = job.file_info
        to_par_path = path.join(self.to_par_path, fi.file_name, fi.file_name)
        create_path(to_par_path)
        vol_size = calc_rar_volume_size(fi.file_size_mb)
        fi.to_par_path = to_par_path
        fi.vol_size = vol_size

        extra_args = ("-v%s" % fi.vol_size, fi.to_par_path, fi.to_rar_path)
        rar_args = BASE_RAR_ARGS + extra_args
        logging.info(
            "running :  {0} {1}".format(
                RAR_COMMAND,
                " ".join(rar_args),
            )
        )

        """
            Runs a command from fi object such as
            >>> rar a -m0 -ep -ed -v100000 path/to/destination path/to/src
        """

        run_command(RAR_COMMAND, BASE_RAR_ARGS + extra_args)

        return job
