# -*- coding: utf-8 -*-

"""This module contains exceptions for Demo."""

# For py2.7 compatibility
from __future__ import print_function

import functools


class DemoException(Exception):
    text = None
    def __init__(self, text=None):
        if text:
            self.text = text


class DemoRestart(DemoException):
    text = "Restarting."


class DemoExit(DemoException):
    text = "Goodbye!"


class DemoRetry(DemoException):
    text = ""


class ResponseError(DemoException):
    def __init__(self, response):
        self.text = self.text.format(response)


class CallbackError(ResponseError):
    text = "'{}' callback not registered"


class CallbackNotLockError(ResponseError):
    text = "'{}' callback not lock, key rejected"


def catch_exc(*demo_exc):
    try:
        all_demo_exc = all(issubclass(exc, DemoException) for exc in demo_exc)
    except TypeError:
        all_demo_exc = False
    if not all_demo_exc:
        return catch_exc(DemoException)(demo_exc[0])
    def catch_exc_decorator(func):
        @functools.wraps(func)
        def inner(demo, *args, **kwargs):
            while True:
                try:
                    try:
                        return func(demo, *args, **kwargs)
                    except KeyboardInterrupt:
                        print()
                        demo.quit()
                except demo_exc as exc:
                    if exc.text:
                        print(exc.text)
                        print()
                    if isinstance(exc, DemoExit):
                        break
        return inner
    return catch_exc_decorator

