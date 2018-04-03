import logging

from ojo.constants import MB
from ojo.models.job import JobStage
from ojo import services
from ojo.services import *
from ojo.services.base_service import BaseService

RAR_COMMAND = "rar"

BASE_RAR_ARGS = ("a", "-m0", "-ep", "-ed", "-df", "-r")


def is_installed():
    return services.is_installed(RAR_COMMAND)


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
            
            -m0 - compression level 0
            -ep - Exclude paths from names
            -ed - Do not add empty directories
            -r -  Recurse subdirectories
            -df - Delete files after archiving
            -v{vol_size} - Create volumes with size=<size>*1000 [*1024, *1]
            
             note that we provide to rar the file or directory to archive. It works recursively
        """

        run_command(RAR_COMMAND, rar_args)
        logging.info("deleting rar path after job {}".format(fi.to_rar_path))
        #shutil.rmtree(fi.to_rar_path)
        return job
