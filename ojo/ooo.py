import argparse
import datetime
import json
import os
import math
import random
import re
import shutil
import sys
import subprocess
import tempfile


class FileInfo(object):

    mb = 1000000  # we use os.stat that gives the file size in kb

    @staticmethod
    def normalize_name(name):
        """

        :param name: a file name
        :return: name that is clean of non ascii characters.
        """

        # Remove leading and trailing spaces
        name = name.strip()
        # Replace any character which is not in the set 0-9a-zA-Z.- with a dot '.'
        name = re.sub("[^0-9a-zA-Z.-]", ".", name)
        # Replace '.-.' with '.'
        name = name.replace(".-.", "-")
        # Remove any number of dots from the beginning of the name
        name = re.sub("^\\.+", "", name)
        # Replace 2 or more subsequent dots with one dot
        normalized_file_name = re.sub("\\.{2,}", ".", name)

        return normalized_file_name

    def __init__(self, source_path, working_path, media_info_path):
        """

        :param source_path: absolute path to file/directory to work on
        :param working_path: path to place temporary files such as rar
        :param media_info_path: path to place permanent files like nzb
        """
        base_name = os.path.basename(source_path)
        base_name = base_name.replace("'", "").replace('"', '')
        origin_path = os.path.join(os.path.dirname(source_path), base_name)
        os.rename(src=source_path, dst=origin_path)
        is_file = os.path.isfile(origin_path)
        if is_file:
            file_name, file_extension = os.path.splitext(base_name)
            size_mb = int(os.stat(origin_path).st_size / self.mb)
        else:
            file_name, file_extension = base_name, ""
            size_mb = sum(
                int(os.stat(os.path.join(origin_path, f)).st_size / self.mb)
                for f in os.listdir(origin_path)
                if os.path.isfile(os.path.join(origin_path, f))
            )

        self.source_path = source_path
        self.origin_path = origin_path
        self.working_path = working_path
        self.media_info_path = media_info_path
        self.file_name = file_name
        self.file_extension = file_extension
        self.is_file = is_file
        self.size_mb = size_mb
        self.normalized_file_name = FileInfo.normalize_name(file_name)

    @property
    def parent_path(self):
        return os.path.dirname(self.origin_path)

    @property
    def is_media_file(self):
        return self.file_extension in (".avi", ".mkv", ".mp4", ".mpg")

    @property
    def nfo_file_path(self):
        return os.path.join(self.media_info_path, self.normalized_file_name + ".nfo")

    @property
    def rar_file_path(self):
        return os.path.join(self.working_path, self.normalized_file_name + ".rar")

    @property
    def rar_files_path_wildcard(self):
        return os.path.join(self.working_path, self.normalized_file_name + ".*.rar")

    @property
    def par_file_path(self):
        return os.path.join(self.working_path, self.normalized_file_name + ".par")

    @property
    def nzb_file_path(self):
        return os.path.join(self.media_info_path, self.normalized_file_name + ".nzb")

    def __str__(self):
        fields = ("{} = '{}'".format(k, v) for k, v in self.__dict__.items())
        return "FileInfo[\n{}\n]".format(",\n".join(fields))


"""
Globals - populated in def setup
"""
SERVERS = []
BASE_DIR = ""
WATCH_DIR = ""
MEDIA_INFO_DIR = ""
RAM_GB = 2
DELETE_SOURCE = False
HEB_LIST = []
PUBLISH_API_KEY = ""
RSYNC_DIR = "dnzb:/temp/" + datetime.datetime.today().strftime('%Y-%m-%d')


def generate_media_file(fi: FileInfo):
    cmd = "mediainfo --LogFile={} '{}'".format(
        fi.nfo_file_path,
        fi.origin_path,
    )

    print("Running '{}'".format(cmd))
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL)

    with open(fi.nfo_file_path, "r") as reader:
        lines = reader.read()

    lines = lines.replace(fi.parent_path + "/", "")
    with open(fi.nfo_file_path, "w") as writer:
        writer.write(lines)

    print("created media file in - ", fi.nfo_file_path)


def generate_rar_files(fi: FileInfo):
    rar_vol_size_mb = "200M"
    if 0 < fi.size_mb < 700:
        rar_vol_size_mb = "20M"
    elif 700 < fi.size_mb < 3000:
        rar_vol_size_mb = "50M"
    elif 3000 < fi.size_mb < 5000:
        rar_vol_size_mb = "100M"
    print("file size is {}MB, rar vol size is {}B".format(fi.size_mb, rar_vol_size_mb))

    cmd = "rar a -m0 -ep -ed -r -y -V{} {} '{}'".format(
        rar_vol_size_mb,
        fi.rar_file_path,
        fi.origin_path,
    )
    print("Running '{}'".format(cmd))
    subprocess.run(cmd, shell=True, check=True)


def generate_par_files(fi: FileInfo):
    if 0 < fi.size_mb < 700:
        par_input_slice_mb = 10
    elif 700 < fi.size_mb < 3000:
        par_input_slice_mb = 15
    elif 3000 < fi.size_mb < 5000:
        par_input_slice_mb = 25
    else:
        par_input_slice_mb = 100

    # set memory used to RAM-1GB or min of 2G
    memory_mb = max(2, (math.floor(RAM_GB) - 1)) * 1000

    cmd = 'parpar -n -O -d pow2 -r"20%" --input-slices={}M -m {}M -o {} {}'.format(
        par_input_slice_mb,
        memory_mb,
        fi.par_file_path,
        fi.rar_files_path_wildcard,
    )
    print("Running '{}'".format(cmd))
    subprocess.run(cmd, shell=True, check=True)


def upload_files(fi: FileInfo, servers):
    server = random.choice(servers)
    parameters = dict(serial="'${rand(38)}'", outf=fi.nzb_file_path, inf=fi.working_path)
    parameters.update(server)
    template = "nyuu -S -h {host} -P {port} -n{connections} -u {user} -p {password} -s {serial}  -o {outf} {inf}"
    cmd = template.format(**parameters)

    print("uploading to host='{}', # of connections='{}'".format(server["host"], server["connections"]))
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL)


def backup_files(fi: FileInfo, backup_path=RSYNC_DIR):
    cmd = "rclone copy -P {} {}".format(
        fi.nzb_file_path,
        backup_path,
    )
    print("Running '{}'".format(cmd))
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL)


def setup(file_path, delete_source):
    """
    Reads the file path into global variables
    :param file_path: absolute path to JSON config file
    :param delete_source: flag to indicate whether to delete source file
    :return: None. side effects of populating the global variables
    """
    print("using configurations from file", file_path)
    with open(file_path) as f:
        config = json.load(f)
    global SERVERS, BASE_DIR, DELETE_SOURCE, MEDIA_INFO_DIR, PUBLISH_API_KEY, RAM_GB, WATCH_DIR, HEB_LIST
    DELETE_SOURCE = delete_source
    PUBLISH_API_KEY = config["publish_api_key"]
    SERVERS = config["servers"]
    BASE_DIR = config["base_dir"]
    MEDIA_INFO_DIR = config["media_info_dir"]
    WATCH_DIR = config["watch_dir"]
    print("using hosts =", ",".join([s["host"] for s in SERVERS]))
    print("using BASE_DIR =", BASE_DIR)
    print("Will delete source files={}".format(DELETE_SOURCE))

    HEB_LIST = config["heb_list"]
    print("Using hebrew list: {}".format(",".join(HEB_LIST)))

    # calculate the RAM on the server
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')  # e.g. 4015976448
    RAM_GB = mem_bytes / (1024.**3)
    print("found RAM={:.2f}GB".format(RAM_GB))

    # clear the media info dir and recreate it before working
    shutil.rmtree(MEDIA_INFO_DIR, ignore_errors=True)
    os.makedirs(MEDIA_INFO_DIR)


def check_commands_installed():
    """
    Checks that required commands are installed.
    Exists if any dependency is not installed
    """

    def is_installed(cmd):
        try:
            res = subprocess.run(cmd, shell=True, check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            return res.returncode == 0
        except Exception as e:
            print(e)
            return False

    commands_state = [
        (cmd, is_installed(cmd)) for cmd in [
            "mediainfo -Help",
            "rar -?",
            "parpar --help",
            "nyuu --help",
            "rclone version",
        ]
    ]
    installed_commands = [cmd for cmd, state in commands_state if state]
    if len(installed_commands) == len(commands_state):
        print("'{}' commands are installed".format(" , ".join(installed_commands)))
    else:
        uninstalled_commands = [cmd for cmd, state in commands_state if not state]
        print("'{}' commands are NOT installed".format(" , ".join(uninstalled_commands)))
        sys.exit(-10)


def cleanup(fi: FileInfo):
    if DELETE_SOURCE:
        print("Deleting source file from '{}'".format(fi.origin_path))
        if fi.is_file:
            os.remove(fi.origin_path)
        else:
            shutil.rmtree(fi.origin_path)
    else:
        print("Delete source flag is turned off, so nothing to do here")


def publish(fi: FileInfo):
    """
    publishes nzb file to omgwtfnzbs.me.

    Deduce the category id (tv or movie) from file name
    Deduce if in heb from name using the HEB_LIST
    """
    rlsname = fi.normalized_file_name
    parameters = {
        "rlsname": rlsname,
        "nzb": "@"+fi.nzb_file_path,
        "upload": "upload",
    }

    tv = re.compile(".*S[0-9][0-9].*|.*complete.*", re.IGNORECASE)
    catid = "tv" if tv.match(rlsname) else "movie"
    parameters["catid"] = catid

    if fi.is_media_file:
        parameters["nfo"] = "@" + fi.nfo_file_path

    is_heb = any((heb_word in rlsname for heb_word in HEB_LIST))
    if is_heb:
        parameters["language"] = "12"

    parameters_cmd = " ".join('-F "{}={}"'.format(k, v) for k, v in parameters.items())
    url = "https://omgwtfnzbs.me/api-upload?user=mshare&api={}".format(PUBLISH_API_KEY)
    cmd = "curl -k -s -L -i -m60 {parameters_cmd} '{url}'".format(
        parameters_cmd=parameters_cmd,
        url=url,
    )
    print("Running '{}'".format(cmd))
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL)


def process_file_info(source_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_info = FileInfo(source_path, temp_dir, MEDIA_INFO_DIR)
        print(file_info)
        if file_info.is_media_file:
            generate_media_file(file_info)
        generate_rar_files(file_info)
        generate_par_files(file_info)
        upload_files(file_info, SERVERS)
        backup_files(file_info)
        publish(file_info)
        cleanup(file_info)
        return file_info


def read_args():
    """
    Reads command line parameters.
    """
    parser = argparse.ArgumentParser(description="""
        Uploads media files to servers in an archive format.""")
    parser.add_argument('-c', '--config_file', help="a JSON format config file. Default is a config.json",
                        default="config.json")
    parser.add_argument('-d', '--delete_source', action='store_true',
                        help="A boolean flag, when provided, will delete the source file")
    return parser.parse_args()


if __name__ == "__main__":
    print("START O V3 script")
    check_commands_installed()
    args = read_args()
    setup(file_path=args.config_file, delete_source=args.delete_source)

    source_files = (os.path.join(WATCH_DIR, f) for f in os.listdir(WATCH_DIR))
    for source in source_files:
        start = datetime.datetime.now()
        fi = process_file_info(source)
        delta = datetime.datetime.now() - start
        print(
            "file_name='{}' | size='{}MB' | process time='{}'".format(
                fi.normalized_file_name,
                fi.size_mb,
                delta,
            )
        )
    print("FINISHED O V3 script")
