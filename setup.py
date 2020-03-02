#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import setup


ptr_params = {
    "entry_point_module": "tgsign",
    "test_suite": "tgsign_tests",
    "test_suite_timeout": 120,
    "required_coverage": {"tgsign.py": 20},
    "run_black": True,
    "run_mypy": True,
    "run_flake8": True,
}


setup(
    name=ptr_params["entry_point_module"],
    version="20.3.2",
    description="Sign Public keys for TG Access",
    py_modules=["tgsign", "tgsign_tests"],
    url="http://github.com/cooperlees/tgsign",
    author="Cooper Ry Lees",
    author_email="me@cooperlees.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.7",
    install_requires=None,
    entry_points={"console_scripts": ["tgsign = tgsign:main"]},
    test_suite=ptr_params["test_suite"],
)
