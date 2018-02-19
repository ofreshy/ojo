
try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

import os
from os import path

import logging

THIS_DIR = path.dirname(path.abspath(__file__))
CONFIG_FILE = path.join(THIS_DIR, "config.ini")


def load(config_file=CONFIG_FILE):
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(config_file, "UTF-8")
    return load_from_config(config)


def load_from_config(config):
    _setup_logging(config)
    _setup_dirs(config)
    return config


def _setup_logging(config):
    level = config.get("logging", "level").upper()

    logging.basicConfig(
        level=logging.getLevelName(level),
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def _setup_dirs(config):
    for _, v in config["dirs"].items():
        os.makedirs(v, exist_ok=True)
