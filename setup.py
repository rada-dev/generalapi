from setuptools import setup, find_packages
import os

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))


def get_install_requires():
    """Returns requirements.txt parsed to a list"""
    fname = os.path.join(SCRIPT_FOLDER, 'requirements.txt')
    targets = []
    if os.path.isfile(fname):
        with open(fname, 'r') as f:
            targets = f.read().splitlines()
    return targets


setup(
    name='generalapi',
    version='0.1',
    install_requires=get_install_requires(),
    packages=find_packages(),
    include_package_data=True,
    license='GPLv3',
    long_description=open('README.rst').read(),
)