# coding=utf-8
from setuptools import setup

setup(
    name="Nginx Configuration parser",
    version="0.1.0",
    author="Hamza ESSAYEGH",
    author_email="hamza.essayegh@protonmail.com",
    packages=['lib'],
    description='Python package for parsing nginx configuration file',
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
