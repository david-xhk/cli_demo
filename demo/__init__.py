# -*- coding: utf-8 -*-

"""This module contains Demo, a framework for interactive command line demonstrations, and some of its extensions."""

__author__ = 'Han Keong'
__email__ = 'hk997@live.com'
__version__ = '0.0.1'

from .options import DemoOptions
from .demo import Demo
from .code import CodeDemo
from .sandbox import SandboxDemo

__all__ = ["DemoOptions", "Demo", "CodeDemo", "SandboxDemo"]

del options, demo, code, sandbox

