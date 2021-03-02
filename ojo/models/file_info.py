import collections
import os
import re
import subprocess
import tempfile

# FileInfo stores all paths for a given media file
FileInfo = collections.namedtuple(
    'FileInfo',
    [
        'origin_path',
        'parent_path',
        'base_name',
        'file_name',
        'file_extension',
        'file_size_mb',
        'working_path',
        'normalized_file_name',
        'nfo_file_path',
        'rar_file_path',
        'rar_files_path_wildcard',
        'par_file_path',
        'nzb_file_path',
    ]
)

"""
constants
"""
MEDIA_FILES_EXT = (".avi", ".mkv", ".mp4", ".mpg", ".py")
MB = 1000000

# defaults
BASE_DIR = "/home/auto/"
WATCH_DIR = BASE_DIR + "downloads/"
MEDIA_INFO_DIR = BASE_DIR + "nzb/"
RSYNC_PATH = "dnzb:/temp"

# TODO - read this from a json file or similar
SERVERS = [
    dict(host="eu.newsdemon.com", user="p12004454", password="79rc25nz", connections=20, port=563),
]


def _run_command(cmd):
    print(cmd)
    # check True means that it will exit if there is an error in subprocess
    return subprocess.run(cmd, shell=True, check=True)


def get_media_files(root):
    for base_dir, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(MEDIA_FILES_EXT):
                yield os.path.join(base_dir, filename)


def generate_file_info(origin_path, working_path):
    """

    :param origin_path:
    :param working_path:
    :return:
    """
    origin_path = os.path.abspath(origin_path)
    parent_path = os.path.dirname(origin_path)
    base_name = os.path.basename(origin_path)
    file_name, file_extension = os.path.splitext(base_name)
    file_size_mb = int(os.stat(origin_path).st_size / MB)

    name = file_name.strip()
    name = re.sub("[^0-9a-z.-]", ".", name)
    name = name.replace(".-.", "-")
    normalized_file_name = name.replace("..", ".")

    nfo_file_path = os.path.join(MEDIA_INFO_DIR, normalized_file_name + ".nfo")
    rar_file_path = os.path.join(working_path, normalized_file_name + ".rar")
    rar_files_path_wildcard = os.path.join(working_path, normalized_file_name + ".*.rar")
    par_file_path = os.path.join(working_path, normalized_file_name + ".par")
    nzb_file_path = os.path.join(MEDIA_INFO_DIR, normalized_file_name + ".nzb")

    fi = FileInfo(
        origin_path=origin_path,
        parent_path=parent_path,
        base_name=base_name,
        file_name=file_name,
        file_extension=file_extension,
        file_size_mb=file_size_mb,
        working_path=working_path,
        normalized_file_name=normalized_file_name,
        nfo_file_path=nfo_file_path,
        rar_file_path=rar_file_path,
        rar_files_path_wildcard=rar_files_path_wildcard,
        par_file_path=par_file_path,
        nzb_file_path=nzb_file_path,
    )
    print(fi)
    return fi


def generate_media_file(fi: FileInfo):
    cmd = "mediainfo --LogFile={} {}".format(
        fi.nfo_file_path,
        fi.origin_path,
    )
    _run_command(cmd)

    with open(fi.nfo_file_path, "r") as reader:
        lines = reader.read()

    lines = lines.replace(fi.parent_path, "")
    with open(fi.nfo_file_path, "w") as writer:
        writer.write(lines)

    print("created media file in - ", fi.nfo_file_path)


def generate_rar_files(fi: FileInfo):
    rar_vol_size_mb = "200M"
    if 0 < fi.file_size_mb < 700:
        rar_vol_size_mb = "20M"
    elif 700 < fi.file_size_mb < 3000:
        rar_vol_size_mb = "50M"
    elif 3000 < fi.file_size_mb < 5000:
        rar_vol_size_mb = "100M"
    print("file size is {}, rar vol size is {}".format(fi.file_size_mb, rar_vol_size_mb))

    rar_cmd = "rar a -m0 -ep -ed -r -y {} {} {}".format(
        "-V" + rar_vol_size_mb,
        fi.rar_file_path,
        fi.origin_path,
    )
    _run_command(rar_cmd)


def generate_par_files(fi: FileInfo):
    # TODO ojo, let me know what is the logic here for the parameters
    par_cmd = 'parpar -n -O -d pow2 -r"20%" --input-slices=1536000b -m 2000M -o {} {}'.format(
        fi.par_file_path,
        fi.rar_files_path_wildcard,
    )
    _run_command(par_cmd)


def upload_files(fi: FileInfo, servers=SERVERS):
    template = "nyuu -S -h {host} -P {port} -n{connections} -u {user} -p {password} -s {serial}  -o {outf} {inf}"
    for server in servers:
        print("uploading to host {}".format(server["host"]))
        args = dict(serial="'${rand(38)}'", outf=fi.nzb_file_path, inf=fi.working_path)
        args.update(server)
        cmd = template.format(**args)
        _run_command(cmd)


def backup_files(fi: FileInfo, backup_path=RSYNC_PATH):
    cmd = "rclone copy -P {} {}".format(
        fi.nzb_file_path,
        backup_path,
    )
    _run_command(cmd)


if __name__ == "__main__":
    print("START O V3 script")
    for media_file in get_media_files(WATCH_DIR):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_info = generate_file_info(media_file, temp_dir)
            generate_rar_files(file_info)
            generate_par_files(file_info)
            upload_files(file_info)
            backup_files(file_info)

