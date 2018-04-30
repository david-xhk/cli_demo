# -*- coding: utf-8 -*-

"""This module contains exceptions for Demo."""

# For py2.7 compatibility
from __future__ import print_function

import functools
import inspect


class DemoException(Exception):
    """Base exception for any error raised in a :class:`~cli_demo.demo.Demo`.
    
    Format (if ``"{}"`` is present) or overwrite :attr:`~cli_demo.exceptions.DemoException.text` if initialized with a ``str``.
    
    Attributes:
        text (str): The text to print when an instance of :class:`~cli_demo.exceptions.DemoException` is caught in :func:`~cli_demo.exceptions.catch_exc`.
    """
    text = None
    def __init__(self, text=None):
        """Format or override the default :attr:`~cli_demo.exceptions.DemoException.text` if `text` is provided.

        Args:
            text (str, optional): A custom error text.
        """
        if text:
            if self.text and "{}" in self.text:
                self.text = self.text.format(text)
            else:
                self.text = str(text)


class DemoRestart(DemoException):
    """Raised when user wants to restarts a :class:`~cli_demo.demo.Demo`."""
    text = "Restarting."


class DemoExit(DemoException):
    """Raised when user wants to quit a :class:`~cli_demo.demo.Demo`."""
    text = "Goodbye!"


class DemoRetry(DemoException):
    """Raised when an input function in a :class:`~cli_demo.demo.Demo` should be called again."""
    text = ""


class KeyNotFoundError(DemoException):
    """Raised when a key id does not exist in a :attr:`~cli_demo.options.DemoOptions.cache`."""
    text = "'{}' id does not exist in the cache."


class OptionNotFoundError(DemoException):
    """Raised when an :class:`~cli_demo.options.Option` instance is not registered."""
    text = "Option object for '{}' not registered."


class CallbackNotFoundError(DemoException):
    """Raised when the :attr:`~cli_demo.options.Option.callback` of an :class:`~cli_demo.options.Option` instance has not been set."""
    text = "'{}' callback not registered"


class CallbackLockError(DemoException):
    """Raised when the :attr:`~cli_demo.options.Option.lock` attribute of an :class:`~cli_demo.options.Option` instance is ``True`` but its :attr:`~cli_demo.options.Option.callback` does not accept a `key` argument."""
    text = "'{}' callback does not accept `key` argument."


class CallbackResponseError(DemoException):
    """Raised when an :class:`~cli_demo.options.Option` instance is registered under an input function key but its :attr:`~cli_demo.options.Option.callback` does not accept a `response` argument."""
    text = "'{}' callback does not accept `response` argument."


def catch_exc(*demo_exc):
    """Catch instances of `demo_exc` raised while running a function.

    Args:
        *demo_exc: One or a few subclasses of :class:`~cli_demo.exceptions.DemoException`, and possibly a function to wrap.

    Returns:
        ``catch_exc_decorator()``: A decorator that takes a function and returns a wrapped function. As a shortcut, if a function was passed into `demo_exc`, the wrapped function is returned instead.
    
    Note:
        * Non-subclasses of :class:`~cli_demo.exceptions.DemoException` are ignored, aside from a function or method.

        * :class:`~cli_demo.exceptions.DemoException` is the default if no subclasses are provided.

        * Non-instances of `demo_exc` will not be caught. They should typically be handled by a higher level and more general kind of :func:`~cli_demo.exceptions.catch_exc`.

        * If a :class:`KeyboardInterrupt` is raised while running the function, it will be caught and :class:`~cli_demo.exceptions.DemoExit` will be re-raised.
    """
    func = None
    demo_exc = list(demo_exc)
    for i in range(len(demo_exc)-1, -1, -1):
        try:
            if not issubclass(demo_exc[i], DemoException):
                demo_exc.pop(i)
        except TypeError:
            obj = demo_exc.pop(i)
            if (inspect.isfunction(obj) or inspect.ismethod(obj)) and not func:
                func = obj
    if demo_exc:
        demo_exc = tuple(demo_exc)
    else:
        demo_exc = DemoException
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
    if func:
        return catch_exc_decorator(func)
    else:
        return catch_exc_decorator

