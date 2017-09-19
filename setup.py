import sys

from setuptools import find_packages, setup


if sys.version_info[:2] < (2, 7):
    raise Exception("ojo project only works on Python 2.7 and greater or PyPy")


install_requires = []
setup_requires = ["vcversioner"]

setup(
    name="ojo",
    description="Utility to manage files",
    url="https://github.com/ofreshy/ojo",
    author="ME",
    author_email="sharoffer@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=setup_requires,
    vcversioner={"version_module_paths": ["ojo/_version.py"]},
)
