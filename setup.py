#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import versioneer
from setuptools import setup

# # Create list of data files
# def find_data_files(directory):

#     paths = []

#     for (path, directories, filenames) in os.walk(directory):

#         for filename in filenames:

#             paths.append(os.path.join("..", path, filename))

#     return paths


#extra_files = find_data_files("telefilebot/data")

setup(

    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    py_modules=["listen"],
    entry_points={
        "console_scripts": [
            "telefilebot = listen:listen"

            ]


        }
    #        package_data={"": extra_files},
)
