from os import path
import os
import shutil

import subprocess
from subprocess import CalledProcessError

try:
    from subprocess import DEVNULL # py3k
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


def move_path(src, dest):
    os.makedirs(path.dirname(dest), exist_ok=True)
    shutil.move(src, dest)


def create_path(dest):
    os.makedirs(path.dirname(dest), exist_ok=True)


def is_installed(cmd, args=()):
    try:
        return bool(subprocess.check_call([cmd] + list(args)) == 0)
    except CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def run_command(cmd, args_list):
    return subprocess.check_call([cmd] + list(args_list), stdout=DEVNULL)