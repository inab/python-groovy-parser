#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: Apache-2.0
# groovy-parser, a proof of concept Groovy parser based on Pygments and Lark
# Copyright (C) 2023 Barcelona Supercomputinh Center, José M. Fernández
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import os
import sys
import setuptools

# In this way, we are sure we are getting
# the installer's version of the library
# not the system's one
setupDir = os.path.dirname(__file__)
sys.path.insert(0, setupDir)

from groovy_parser import __version__ as gp_version
from groovy_parser import __author__ as gp_author
from groovy_parser import __license__ as gp_license

# Populating the long description
readme_path = os.path.join(setupDir, "README.md")
with open(readme_path, "r") as fh:
    long_description = fh.read()

# Populating the install requirements
requirements = []
requirements_path = os.path.join(setupDir, "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, mode="r", encoding="utf-8") as f:
        egg = re.compile(r"#[^#]*egg=([^=&]+)")
        for line in f.read().splitlines():
            print(f"R {line}")
            m = egg.search(line)
            requirements.append(line if m is None else m.group(1))

setuptools.setup(
    name="groovy-parser",
    version=gp_version,
    author=gp_author,
    author_email="jose.m.fernandez@bsc.es",
    license=gp_license,
    description="Groovy 3.0.x parser based on Pygments and Lark",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/inab/python-groovy-parser",
    project_urls={"Bug Tracker": "https://github.com/inab/python-groovy-parser/issues"},
    packages=setuptools.find_packages(),
    package_data={
        "groovy_parser": [
            "py.typed",
            "GROOVY_3_0_X/master_groovy_parser.g",
        ]
    },
    scripts=[
        "cached-translated-groovy3-parser.py",
        "translated-groovy3-parser.py",
    ],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
