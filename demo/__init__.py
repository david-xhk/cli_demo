# -*- coding: utf-8 -*-

"""This module contains Demo, a framework for interactive command line demonstrations, and some of its subclasses.

For example::

    # example here
"""

__author__ = 'Han Keong'
__email__ = 'hk997@live.com'
__version__ = '0.0.1'

from .demo import Demo
from .code_demo import CodeDemo
from .sandbox_demo import SandboxDemo

__all__ = ["Demo", "CodeDemo", "SandboxDemo"]

del demo, code_demo, sandbox_demo

