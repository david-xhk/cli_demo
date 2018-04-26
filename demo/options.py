# -*- coding: utf-8 -*-

"""This module contains DemoOptions- the `options` delegate for Demo, and Option- a class that holds information about a registered option."""

# For py2.7 compatibility
from __future__ import print_function

import functools
import inspect
from .exceptions import (DemoException, DemoRetry, KeyNotFoundError,
                         OptionNotFoundError, CallbackNotFoundError,
                         CallbackNotLockError, catch_exc)


class Option(object):
    """Holds information about a registered option.

    Attributes:
        name (str): The name of the option.
        desc (str): A description of the option.
        callback (function): The callback of the option.
        newline (bool): Whether a new line should be printed before the callback is executed.
        retry (bool): Whether an input function should be called again once the callback has returned.
        lock (bool): Whether the `key` of a trigerring input function should be received by the callback.
        args (tuple): The default arguments when the callback is called.
        kwargs (dict): The default keyword arguments when the callback is called.
    """
    __slots__ = ["name", "desc", "callback", "newline",
                 "retry", "lock", "args", "kwargs"]

    def __init__(self, **kwargs):
        for attr in ["name", "desc", "callback", "newline", 
                     "retry", "lock", "args", "kwargs"]:
            value = kwargs.get(attr, None)
            setattr(self, attr, value)

    def call(self, demo, *args, **kwargs):
        """Call the registered callback.

        Args:
            demo (Demo): The demo instance passed to the callback.
            *args: The arguments passed to the callback.
            **kwargs: The keyword arguments passed to the callback.

        Note:
            * self.args is used if `args` is empty.
            * self.kwargs is used if `kwargs` is empty.
            * A newline is printed beforehand if self.newline is ``True``.
            * DemoRetry will be raised if self.retry is ``True`` and the callback successfully returned.
        """
        if not args:
            args = self.args
        if not kwargs:
            kwargs = self.kwargs
        if self.newline:
            print()
        did_return = False
        try:
            result = self.callback(demo, *args, **kwargs)
            did_return = True
            return result
        finally:
            if did_return and self.retry:
                demo.retry()
        
    def copy(self):
        """Initialize a new copy of Option.
        
        Returns:
            Option: An instance of Option with a deep copy of all attributes of self.
        """
        new_option = Option(
            name=str(self.name), 
            desc=str(self.desc),
            callback=self.callback,
            newline=bool(self.newline), 
            retry=bool(self.retry), 
            lock=bool(self.lock), 
            args=tuple(self.args), 
            kwargs=dict(self.kwargs))
        return new_option


class DemoOptions(object):
    """Designates options for input functions and forwards their registered callbacks dynamically.

    Attributes:
        demo (Demo): The Demo instance that a DemoOptions instance exists in.
        registry (dict): The options that have been registered. 
        cache (dict): A cache of the key ids and their options and keyword options that have been seen.
    """

    def __init__(self):
        self.demo = None
        self.registry = {}
        self.cache = {}

    def __call__(self, *opts, **kw_opts):
        retry = kw_opts.pop("retry", "Please try again.")
        key = kw_opts.pop("key", None)
        key_args = kw_opts.pop("key_args", ())
        key_kwargs = kw_opts.pop("key_kwargs", {})
        def options_decorator(input_func):
            self.set_options(key or input_func, *opts, **kw_opts)
            @functools.wraps(input_func)
            @catch_exc(DemoRetry)
            def inner(demo):
                response = input_func(demo)
                opts, kw_opts = demo.options.get_options(key or input_func)
                if response in opts or response in kw_opts:
                    option = kw_opts.get(response) or response
                    if option not in demo.options:
                        raise OptionNotFoundError(response)
                    elif demo.options.is_lock(option):
                        try:
                            return demo.options.call(option, key=key)
                        except TypeError as exc:
                            raise CallbackNotLockError(response)
                    else:
                        return demo.options.call(option)
                elif key:
                    return demo.options.call(key, response=response,
                        *key_args, **key_kwargs)
                else:
                    demo.retry(retry)
            return inner
        return options_decorator

    def register(self, option, desc="", newline=False, retry=False, lock=False,
                 args=(), kwargs={}):
        """Register a callback under an option.
        
        Args:
            option (str): The name of the option.
            desc (str, optional): A description of the option, if necessary.
            newline (bool): Whether a new line should be printed before the callback is executed.
            retry (bool): Whether an input function should be called again once the callback has returned.
            lock (bool): Whether the `key` of a trigerring input function should be received by the callback.
            args (tuple): The default arguments when the callback is called.
            kwargs (dict): The default keyword arguments when the callback is called.

        Returns:
            register_decorator: A decorator which takes a function, uses it to set the callback for the option, and returns the original function.

        Note:
            * An option can be an expected user response or an input function key.

            * If a callback is registered under an input function key, the callback must accept a `response` argument- the user's response to that input function.

            * If a callback is registered as a `lock`, it must accept a `key` argument- the key of the input function that triggered the callback.
        """
        self.registry[option] = Option(
            name=option, desc=desc, newline=newline, 
            retry=retry, lock=lock, args=args, kwargs=kwargs)
        def register_decorator(func):
            self.set_callback(option, func)
            return func
        return register_decorator

    def __contains__(self, option):
        """Check if an option is registered.
        
        Args:
            option (str): The name used to register a option.

        Returns:
            ``True`` if `option` exists in self.registry, ``False`` otherwise.
        """
        return option in self.registry
    
    def __getitem__(self, option):
        """Get the registered option.

        Args:
            option (str): The name used to register a option.

        Returns:
            The callback function that was registered under `option`.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        try:
            return self.registry[option]
        except KeyError:
            raise OptionNotFoundError(option)

    def call(self, option, *args, **kwargs):
        """Call the callback registered under an option.

        Args:
            option (str): The name used to register a option.
            *args: The arguments to pass to the callback.
            **kwargs: The keyword arguments to pass to the callback.

        Returns:
            The return value of the callback.

        Raises:
            DemoException: If self.demo is not set.
            OptionNotFoundError: If `option` does not exist in self.registry.
            CallbackNotFoundError: If a callback has not been registered under `option`.
        """
        if not self.demo:
            raise DemoException("Demo not set yet.")
        else:
            callback = self.get_callback(option)
            return callback(self.demo, *args, **kwargs)

    def get_callback(self, option):
        """Get the callback registered under an option.

        Args:
            option (str): The name used to register a option.

        Returns:
            The callback function that was registered under `option`.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry.
            CallbackNotFoundError: If a callback has not been registered under `option`.
        """
        if self[option].callback is None:
            raise CallbackNotFoundError(option)
        else:
            return self[option].call

    def set_callback(self, option, callback):
        """Set the callback registered under an option.

        Args:
            option (str): The name used to register a option.
            callback: The callback function to register under option.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        self[option].callback = callback                 

    def is_lock(self, option):
        """Check if an option was registered as a lock.

        Args:
            option (str): The name used to register a option.

        Returns:
            ``True`` if the callback was registered as a lock, ``False`` otherwise.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        return self[option].lock is True

    def toggle_lock(self, option):
        """Switch between whether an option is a lock.

        Args:
            option (str): The name used to register a option.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        self[option].lock = not self[option].lock 

    def will_retry(self, option):
        """Check if an option was registered to retry.

        Args:
            option (str): The name used to register a option.

        Returns:
            ``True`` if the callback was registered to retry, ``False`` otherwise.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        return self[option].retry is True

    def toggle_retry(self, option):
        """Switch between whether an option will retry.

        Args:
            option (str): The name used to register a option.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        self[option].retry = not self[option].retry 

    def has_newline(self, option):
        """Check if an option was registered to have a newline.

        Args:
            option (str): The name used to register a option.

        Returns:
            ``True`` if the callback was registered to have a newline, ``False`` otherwise.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        return self[option].newline is True

    def toggle_newline(self, option):
        """Switch between whether an option will have a newline.

        Args:
            option (str): The name used to register a option.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        self[option].newline = not self[option].newline 

    def get_desc(self, option):
        """Get the description of an option.

        Args:
            option (str): The name used to register a option.

        Returns:
            str: The `desc` was registered under `option`.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        return self[option].desc

    def set_desc(self, option, desc):
        """Set the description of an option.

        Args:
            option (str): The name used to register a option.
            desc (str): A description of the option.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        self[option].desc = str(desc)

    def get_args(self, option):
        """Get the default arguments for an option's callback.

        Args:
            option (str): The name used to register a option.

        Returns:
            tuple: The `args` that was registered under `option`.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        return self[option].args

    def set_args(self, option, *args):
        """Set the default arguments for an option's callback.

        Args:
            option (str): The name used to register a option.
            *args: The default arguments when the callback is called.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        self[option].args = tuple(args)

    def get_kwargs(self, option):
        """Get the default keyword arguments for an option's callback.

        Args:
            option (str): The name used to register a option.

        Returns:
            dict: The `kwargs` that was registered under `option`.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        return self[option].kwargs

    def set_kwargs(self, option, **kwargs):
        """Set the default keyword arguments for an option's callback.

        Args:
            option (str): The name used to register a option.
            **kwargs: The default keyword arguments when the callback is called.

        Raises:
            OptionNotFoundError: If `option` does not exist in self.registry. 
        """
        self[option].kwargs = dict(kwargs)

    @staticmethod
    def get_id(key):
        """Create a unique id for `key`.
        
        Args:
            key: A key for a set of options and keyword options.

        Returns:
            int: The id of `key`.
        """
        return id(key)

    def has_options(self, key):
        """Check if there are any options set with `key`.

        Args:
            key: A key for a set of options and keyword options.

        Returns:
            ``True`` if the id of `key` exists in self.cache, ``False`` otherwise.
        """
        return self.get_id(key) in self.cache

    def get_options(self, key):
        """Get the options that were set with `key`.

        Args:
            key: A key for a set of options and keyword options.

        Returns:
            list[list, dict]: The options and keyword options set under `key`.

        Raises:
            KeyNotFoundError: If the id of `key` does not exist in self.cache.
        """
        try:
            return self.cache[self.get_id(key)]
        except KeyError:
            raise KeyNotFoundError(key)

    def set_options(self, key, *opts, **kw_opts):
        """Change the options that were set with `key`.
        
        If `opts` or `kw_opts` are provided, the previously set options or keyword options will be overridden.

        Args:
            key: A key for a set of options and keyword options.
            *opts: Argument options for `key`.
            **kw_opts: Keyword options for `key`.
        """
        key_id = self.get_id(key)
        if key_id not in self.cache:
            self.cache[key_id] = [[], {}]
        if opts:
            self.cache[key_id][0] = list(opts)
        if kw_opts:
            self.cache[key_id][1] = dict(kw_opts)

    def insert(self, key, kw, opt, **kw_opts):
        """Insert an option into the options that were set with `key`.

        If `kw` is an int or a digit, it is treated as an argument option index to insert at. Otherwise, it is treated as a keyword option to update.

        Args:
            key: A key for a set of options and keyword options.
            kw: An index for argument options or a keyword option.
            opt (str): The option to insert.
            **kw_opts: More kw and opt pairs.

        Raises:
            KeyNotFoundError: If the id of `key` does not exist in self.cache.

        Note:
            `kw_opts` are are treated similarly as `kw` and `opt`.
        """
        options = self.get_options(key)
        for kw, opt in dict(kw_opts, **{kw:opt}).items():
            if isinstance(kw, str) and not kw.isdigit():
                options[1][kw] = opt
            else:
                options[0].insert(int(kw), opt)

    def copy(self):
        """Initialize a new copy of DemoOptions.
        
        Returns:
            DemoOptions: An instance of DemoOptions with a deep copy of self.cache and self.registry.
        """
        new_options = DemoOptions()
        for key_id, [opts, kw_opts] in self.cache.items():
            new_options.cache[key_id] = [list(opts), dict(kw_opts)]
        for name, option in self.registry.items():
            new_options.registry[name] = option.copy()
        return new_options

