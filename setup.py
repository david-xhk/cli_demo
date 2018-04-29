#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import re

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [ ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Han Keong",
    author_email='hk997@live.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Interactive demonstrations for command line interface.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
<<<<<<< HEAD
    keywords='command-line-interface demo interactive',
    name='cli_demo',
    packages=find_packages(include=['cli_demo']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/han-keong/cli_demo',
    version=re.search(r'__version__ = [\'"]([^\'"]*)[\'"]', open('cli_demo/__init__.py').read()).group(1),
=======
    keywords='command-line demo interactive',
    name='demo',
    packages=find_packages(include=['demo']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/han-keong/demo',
    version=re.search(r'__version__ = [\'"]([^\'"]*)[\'"]', open('demo/__init__.py').read()).group(1),
>>>>>>> 4ad383388e7e1ba7bf9b253439e011ef33d646b9
    zip_safe=False,
)
