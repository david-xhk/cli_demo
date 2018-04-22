# -*- coding: utf-8 -*-

"""This module contains Demo, a framework for interactive command line demonstrations, and some of its subclasses.

For example::

    # example here
"""

__author__ = 'Han Keong'
__email__ = 'hk997@live.com'
__version__ = '0.0.1'

from .options import DemoOptions
from .demo import Demo
from .code_demo import CodeDemo
from .sandbox_demo import SandboxDemo

__all__ = ["DemoOptions", "Demo", "CodeDemo", "SandboxDemo"]

del options, demo, code_demo, sandbox_demo

