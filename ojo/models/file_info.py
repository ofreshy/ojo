
import os
import attr
from ojo.constants import MB


def create_files_info(origin_path):
    files_info = []

    def make_file_info(src_path):
        abs_path = os.path.abspath(src_path)
        parent_path = os.path.dirname(src_path)
        base_name = os.path.basename(src_path)
        rel_path = os.path.relpath(origin_path, src_path)
        file_name, _, extension = base_name.partition(".")
        file_size_mb = os.stat(src_path).st_size / MB
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

    def add_file_info(current_path):
        if os.path.isfile(current_path):
            files_info.append(make_file_info(current_path))
            return

        for f in os.listdir(current_path):
            if f not in ("\\", "±"):
                add_file_info(f)

    add_file_info(origin_path)
    return files_info


@attr.s
class FileInfo(object):
    origin = attr.ib()
    abs_path = attr.ib()
    parent_path = attr.ib()
    rel_path = attr.ib()
    base_name = attr.ib()
    file_name = attr.ib()
    extension = attr.ib()
    file_size_mb = attr.ib()
    # we add these in rar service
    to_par_path = attr.ib(default=None)
    vol_size = attr.ib(default=None)
