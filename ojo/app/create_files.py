import tempfile
from os import path
import os
from ojo.config import config
import shutil
import logging

if __name__ == "__main__":
    con = config.load()
    to_watch_dir = con["dirs"]["to_watch_dir"]
    to_rar_dir = con["dirs"]["to_rar_dir"]
    files_dir = con["dirs"]["src_files_dir"]

    dirs_to_cp = os.listdir(files_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        for d in dirs_to_cp:
            if path.isfile(d):
                continue
            src = path.join(files_dir, d)
            temp_dest = path.join(temp_dir, d)
            dest = path.join(to_watch_dir, d)

            logging.info("copying from {0} to {1}".format(src, temp_dest))
            shutil.copytree(src, temp_dest)
            logging.info("moving from {0} to {1}".format(temp_dest, dest))
            shutil.move(temp_dest, dest)
