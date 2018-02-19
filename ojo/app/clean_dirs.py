
from ojo.config import config
import shutil
import logging

if __name__ == "__main__":
    con = config.load()
    to_watch_dir = con["dirs"]["to_watch_dir"]
    to_rar_dir = con["dirs"]["to_rar_dir"]
    to_par_dir = con["dirs"]["to_par_dir"]

    def on_error(_, path, exec_info):
        logging.warning("Error deleting {0}".format(path))
        logging.warning(exec_info)

    for d in (to_watch_dir, to_rar_dir, to_par_dir):
        shutil.rmtree(d, True, on_error)