# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 12:29:40 2020

@author: Stagiaire
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ml-si-Flyffmario", # Replace with your own username
    version="0.0.1",
    author="Marc 'Flyffmario' ROUY-BELTRAN",
    author_email="marc.rouybeltran@gmail.com",
    description="ML-SI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Flyffmario/ML-SI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7.4',
)