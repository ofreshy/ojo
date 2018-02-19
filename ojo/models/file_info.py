import os
import attr

from ojo.constants import MB


@attr.s
class FileInfo(object):

    @classmethod
    def make(cls, origin_path):
        origin_path = os.path.abspath(origin_path)
        parent_path = os.path.dirname(origin_path)
        base_name = os.path.basename(origin_path)
        file_name, _, extension = base_name.partition(".")
        file_size_mb = os.stat(origin_path).st_size / MB

        rel_path = os.path.relpath(origin_path, parent_path)
        rel_path = "/".join(rel_path.split("/")[:-1] + [file_name])

        return cls(
            origin_path,
            parent_path,
            rel_path,
            base_name,
            file_name,
            extension,
            file_size_mb,
        )

    origin_path = attr.ib()
    parent_path = attr.ib()
    rel_path = attr.ib()
    base_name = attr.ib()
    file_name = attr.ib()
    extension = attr.ib()
    file_size_mb = attr.ib()

    # Added by move service
    to_rar_path = attr.ib(default=None)

    # Added by rar service
    to_par_path = attr.ib(default=None)
    vol_size = attr.ib(default=None)

    # Added by error service if on error
    error_path = attr.ib(default=None)
