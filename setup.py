from setuptools import setup, find_packages
from pathlib import Path


def get_install_requires() -> list:
    """Returns requirements.txt parsed to a list"""
    fname = Path(__file__).parent / 'requirements.txt'
    targets = []
    if fname.exists():
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
    long_description=open('README.md').read(),
)