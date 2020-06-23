#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os

from setuptools import setup, find_packages

HERE_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__)))


def read_file(file_path):
    with open(file_path, 'r') as f:
        output = f.read()
    return output


def get_requirements():
    requirements_file_path = '{}/{}'.format(HERE_PARENT, 'requirements.txt')
    requirements = read_file(requirements_file_path)
    requirements = re.sub(r'(?m)^ *#.*\n?', '', requirements)
    requirements_file_without_options = re.sub(r'(?m)^ *--.*\n?', '', requirements)
    requirements_file_without_options = requirements_file_without_options.split('\n')
    requirements = [r for r in requirements_file_without_options if r != '']
    return requirements


def get_version():
    version_file_path = '{}/{}'.format(HERE_PARENT, 'version')
    version = read_file(version_file_path).strip()
    return version


setup(
    name='yourltd-generate-services-table',
    version=get_version(),
    description="""Generate html-table services from nginx confs""",
    install_requires=get_requirements(),
    license="MIT",
    zip_safe=False,
    packages=find_packages(exclude=["*tests*"]),
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "services_spec_generator": ["*.conf",
             ],
    },
    # include_package_data=True,
    entry_points={
        'console_scripts': ['generate-services-table=services_spec_generator.parse_conf:main'],
    },
    # scripts=['generage-services-table'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.7',
    ],
)
