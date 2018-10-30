# coding=utf-8
from distutils.core import setup

setup(
    name="Nginx Configuration parser",
    version="0.1.0",
    author="Hamza ESSAYEGH",
    author_email="hamza.essayegh@protonmail.com",
    packages=['nginx-conf-parser'],
    include_package_data=True,
    description='Python package for parsing nginx configuration file',
    long_description=open('README').read(),
    install_requires=[
        #
    ]
)
