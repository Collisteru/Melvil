# Helps the submodules import from a parent directory without sys.os hacks.
# See: https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder

from setuptools import setup, find_packages

setup(name='myproject', version='1.0', packages=find_packages())