#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='pandadock-gui',
    version='1.0.0',
    author='Pritam Kumar Panda & Muzammil Kabier',
    author_email='pritam@stanford.edu',
    description='A PandaDock GUI application for molecular docking',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pritampanda15/PandaDockGUI',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    python_requires='>=3.9',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pandadock=PandaDOCK:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['Images/*', 'Test/**/*'],
    },
    zip_safe=False,
    keywords='molecular docking, pymol, rdkit, gui, chemistry, bioinformatics',
    project_urls={
        'Bug Reports': 'https://github.com/pritampanda15/PandaDockGUI/issues',
        'Source': 'https://github.com/pritampanda15/PandaDockGUI',
        'Documentation': 'https://github.com/pritampanda15/PandaDockGUI/wiki',
    },
)