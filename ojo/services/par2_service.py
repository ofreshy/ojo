import logging


from ojo.models.file_info import FileInfo
from ojo.models.job import JobStage
from ojo import services
from ojo.services import *
from ojo.services.base_service import BaseService

PAR2_COMMAND = "par2create"

BASE_RAR_ARGS = ("-R", )

# For -s option
DEFAULT_BLOCK_SIZE = 384000
# For -r option
DEFAULT_PAR_RECOVERY = 15


def is_installed():
    return services.is_installed(PAR2_COMMAND, ("-h", ))


def calc_block_size(file_info: FileInfo):
    return DEFAULT_BLOCK_SIZE


def calc_recovery_size(file_info: FileInfo):
    return DEFAULT_PAR_RECOVERY


class Par2Service(BaseService):
    @classmethod
    def make(cls, config):
        return cls(
            config["par2_service"]["dir"]
        )

    def __init__(self, to_upload_path):
        super(Par2Service, self).__init__(JobStage.rarred, JobStage.parred)
        self.to_upload_path = to_upload_path

    def do_job(self, job):
        fi = job.file_info
        to_par_parent_path = os.path.dirname(fi.to_par_path)

        extra_args = (
            "-s{}".format(calc_block_size(fi)),
            "-r{}".format(calc_recovery_size(fi)),
            fi.to_par_path,
            to_par_parent_path,
        )
        par_args = BASE_RAR_ARGS + extra_args
        logging.info(
            "running :  {0} {1}".format(
                PAR2_COMMAND,
                " ".join(par_args),
            )
        )

        """
            Runs a command from fi object such as
            >>> par2create -R -s384000 -r15 path/to/destination path/to/src
            
                -R       : Recurse into subdirectories (only useful on create)
                -r<c><n> : Redundancy target size, <c>=g(iga),m(ega),k(ilo) bytes
                -s<n>    : Set the Block-Size (don't use both -b and -s)
             note that we provide to rar the file or directory to archive. It works recursively
        """

        run_command(PAR2_COMMAND, par_args)
        par2_files = [f for f in os.listdir(to_par_parent_path) if f.endswith(".par2")]

        fi.to_upload_path = path.join(self.to_upload_path, fi.file_name)
        par2_files_destination = []
        for par2_file in par2_files:
            src = path.join(to_par_parent_path, par2_file)
            dest = path.join(fi.to_upload_path, par2_file)
            move_path(src, dest)
            par2_files_destination.append(dest)

        logging.info("created par2 files %s" % ",".join(par2_files_destination))
        fi.par2_files_destination = par2_files_destination

        return job
