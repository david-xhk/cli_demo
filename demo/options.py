# -*- coding: utf-8 -*-

"""This module contains DemoOptions, used for the options object in Demo."""

# For py2.7 compatibility
from __future__ import print_function

import functools
import inspect
from .exceptions import (DemoException, DemoRetry, CallbackError,
                         CallbackNotLockError, catch_exc)


class DemoOptions(object):
    def __init__(self):
        self.demo = None
        self.cache = {}
        self.callbacks = {}

    @staticmethod
    def get_option_name(obj):
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            return obj.__name__ + str(id(obj))
        else:
            return str(obj)

    def __contains__(self, option_name):
        return self.get_option_name(option_name) in self.cache

    def __getitem__(self, option_name):
        return self.cache[self.get_option_name(option_name)]

    def __setitem__(self, option_name, opts):
        option_name = self.get_option_name(option_name)
        if option_name not in self.cache:
            self.cache[option_name] = [None, None]
        for i, expected_type in enumerate([list, dict]):
            self.cache[option_name][i] = expected_type(opts[i])

    def insert(self, option_name, kw, opt, **kw_opts):
        option_name = self.get_option_name(option_name)
        for kw, opt in dict(kw_opts, **{kw:opt}).items():
            if isinstance(kw, str) and not kw.isdigit():
                self.cache[option_name][1][kw] = opt
            else:
                self.cache[option_name][0].insert(int(kw), opt)
    
    def __call__(self, *opts, **kw_opts):
        retry = kw_opts.pop("retry", "Please try again.")
        key = kw_opts.pop("key", None)
        def options_decorator(input_func):
            option_name = key or input_func
            self[option_name] = [opts, kw_opts]
            @functools.wraps(input_func)
            @catch_exc(DemoRetry)
            def inner(demo, *args, **kwargs):
                response = input_func(demo, *args, **kwargs)
                opts, kw_opts = demo.options[option_name]
                if response in opts or response in kw_opts:
                    callback_name = kw_opts.get(response) or response
                    if not demo.options.has_callback(callback_name):
                        raise CallbackError(response)
                    elif demo.options.is_lock(callback_name):
                        try:
                            return demo.options.call(callback_name, key=key)
                        except TypeError as exc:
                            raise CallbackNotLockError(response)
                    else:
                        return demo.options.call(callback_name)
                elif key:
                    return demo.options.call(key, response=response)
                else:
                    demo.retry(retry)
            return inner
        return options_decorator

    def register(self, callback_name, desc="", **kwargs):
        newline = kwargs.pop("newline", False)
        retry = kwargs.pop("retry", False)
        lock = kwargs.pop("lock", False)
        def register_decorator(func):
            @functools.wraps(func)
            def callback(demo, *args, **kwargs):
                did_return = False
                if newline:
                    print()
                try:
                    result = func(demo, *args, **kwargs)
                    did_return = True
                    return result
                finally:
                    if did_return and retry:
                        demo.retry()
            callback.lock = lock
            callback.desc = desc
            self.callbacks[callback_name] = callback
            return func
        return register_decorator

    def has_callback(self, callback_name):
        return callback_name in self.callbacks
    
    def get_callback(self, callback_name):
        if not self.has_callback(callback_name):
            raise CallbackError(callback_name)
        else:
            return self.callbacks[callback_name]

    def is_lock(self, callback_name):
        return self.get_callback(callback_name).lock is True

    def call(self, callback_name, *args, **kwargs):
        if not self.demo:
            raise DemoException("Demo not set yet.")
        else:
            callback = self.get_callback(callback_name)
            return callback(self.demo, *args, **kwargs)

    def copy(self):
        new_options = DemoOptions()
        for option_name, [opts, kw_opts] in self.cache.items():
            new_options[option_name] = [opts, kw_opts]
        new_options.callbacks.update(self.callbacks)
        return new_options

