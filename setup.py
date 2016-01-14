# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup

projectName="clipwdmgr"
scriptFile="%s/%s.py" % (projectName,projectName)
description="Command Line Password Manager."


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open(scriptFile).read(),
    re.M
    ).group(1)
 
 
with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")
 
 
setup(
    name = projectName,
    packages = [projectName],
    entry_points = {
        "console_scripts": ['%s = %s.%s:main' % (projectName,projectName,projectName)]
        },
    version = version,
    description = description,
    long_description = long_descr,
    install_requires = ['cryptography','pyperclip==1.5.11'],
    author = "Sami Salkosuo",
    author_email = "dev@rnd-dev.com",
    url = "https://github.com/samisalkosuo/clipasswordmgr",
    license='MIT',
    classifiers=[
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Environment :: Console",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Security",
    "Topic :: Utilities"
    ],
    )