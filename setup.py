# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup,find_packages

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
    packages = [projectName,"%s/commands" % projectName,"%s/crypto" % projectName,"%s/database" % projectName,"%s/utils" % projectName],
    #packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    entry_points = {
        "console_scripts": ['%s = %s.%s:main' % (projectName,projectName,projectName)]
        },
    version = version,
    description = description,
    long_description = long_descr,
    install_requires = ['cryptography','pyperclip'],
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
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Security",
    "Topic :: Utilities"
    ],
    )