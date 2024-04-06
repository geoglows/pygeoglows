import re

from setuptools import setup, find_packages

NAME = 'geoglows'
DESCRIPTION = 'Package for accessing data from the GEOGLOWS Hydrological Model'
URL = 'https://data.geoglows.org'
AUTHOR = 'Riley Hales PhD'
REQUIRES_PYTHON = '>=3.10.0'
LICENSE = 'BSD 3-Clause Clear License'

with open("README.md", "r") as readme:
    LONG_DESCRIPTION = readme.read()

with open(f'./{NAME}/__init__.py') as f:
    version_pattern = r'__version__ = [\'"](.+)[\'"]'
    VERSION = re.search(version_pattern, f.read()).group(1)

with open('./requirements.txt') as f:
    INSTALL_REQUIRES = f.read().splitlines()

setup(
    name=NAME,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    url=URL,
    project_urls=dict(
        Homepage='https://data.geoglows.org',
        Documentation='https://geoglows.readthedocs.io',
        Source='https://github.com/geoglows/pygeoglows',
    ),
    license=LICENSE,
    license_family='BSD',
    package_data={'': ['*.ipynb', '*.html']},
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Hydrology',
        'Topic :: Scientific/Engineering :: Visualization',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
    ],
    install_requires=INSTALL_REQUIRES,
    python_requires=REQUIRES_PYTHON,
)
