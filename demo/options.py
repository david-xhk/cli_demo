# -*- coding: utf-8 -*-

"""This module contains DemoOptions, the `options` delegate for Demo."""

# For py2.7 compatibility
from __future__ import print_function

import functools
import inspect
import types
from .exceptions import (DemoException, DemoRetry, OptionsNotFoundError,
                         CallbackError, CallbackNotLockError, catch_exc)


class DemoOptions(object):
    """Designate options for input functions and forward their registered callbacks dynamically.

    Attributes:
        demo (Demo): The Demo instance that a DemoOptions instance exists in.
        cache (dict): A cache of key ids and options and keyword options seen.
        callbacks (dict): A registry of callbacks registered under options.
    """

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
                        raise CallbackError(response)
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
            option (str): The option to register a callback under.
            desc (str, optional): A description of the option, if necessary.
            newline (bool): Whether a new line should be printed before the callback is executed.
            retry (bool): Whether an input function should be called again once the callback has returned.
            lock (bool): Whether the `key` of a trigerring input function should be received by the callback.
            args (tuple): The default arguments when the callback is called.
            kwargs (dict): The default keyword arguments when the callback is called.

        Note:
            * An option can be an expected user response or an input function key.

            * If a callback is registered under an input function key, the callback must accept a `response` argument- the user's response to that input function.

            * If a callback is registered as a `lock`, it must accept a `key` argument- the key of the input function that triggered the callback.

        Returns:
            register_decorator: A decorator which takes a function and creates a callback based on the arguments provided to `register`. The callback is stored in self.callbacks, and the original function is returned.
        
        Examples:
            Registering with an expected user response::
            
                @options.register("r", "Restart."):
                def restart(self):
                    ...  # Restart demo

            Registering with an input function key::

                @options.register("setup"):
                def setup_callback(self, response):
                    ...  # Process response.

            Setting newline to True:

            ::

                @options.register("h", "Help." newline=True):
                def print_help(self):
                    print("This is the help text.")
                    ...  # Print the help text
            
            ::

                >>> Enter an input: h

                This is the help text.  # A gap is inserted beforehand.
                ...

            Setting retry to True:

            ::
    
                @options.register("echo", retry=True):
                def echo_response(self, response):
                    print("Got:", response)
            
            ::

                >>> Enter an input: hello
                Got: hello
                >>> Enter an input:  # The input function is called again.

            Setting lock to True::

                @options.register("o", lock=True):
                def print_options(self, key):
                    if key == "setup":
                        ...  # Print setup options
                    elif key == "echo":
                        ...  # Print echo options
        """
        def register_decorator(func):
            @functools.wraps(func)
            def callback(demo, *args, **kwargs):
                if not args:
                    args = callback.args
                if not kwargs:
                    kwargs = callback.kwargs
                if newline:
                    print()
                did_return = False
                try:
                    result = func(demo, *args, **kwargs)
                    did_return = True
                    return result
                finally:
                    if did_return and retry:
                        demo.retry()
            callback.lock = lock
            callback.desc = desc
            callback.args = args
            callback.kwargs = kwargs
            self.callbacks[option] = callback
            return func
        return register_decorator

    def call(self, option, *args, **kwargs):
        """Call the callback registered under an option.

        Args:
            option (str): The option used to register a callback.
            *args: The arguments to pass to the callback.
            **kwargs: The keyword arguments to pass to the callback.

        Returns:
            The return value of the callback.

        Raises:
            DemoException: If self.demo is not set.
            CallbackError: If `option` does not exist in self.callbacks. 
        """
        if not self.demo:
            raise DemoException("Demo not set yet.")
        else:
            return self[option](
                self.demo, *args, **kwargs)

    def __init__(self):
        self.demo = None
        self.cache = {}
        self.callbacks = {}

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
        """Check if there are any options set under `key`.

        Args:
            key: A key for a set of options and keyword options.

        Returns:
            ``True`` if the id of `key` exists in self.cache, ``False`` otherwise.
        """
        return self.get_id(key) in self.cache

    def get_options(self, key):
        """Get the options set under `key`.

        Args:
            key: A key for a set of options and keyword options.

        Returns:
            list[list, dict]: The options and keyword options set under `key`.

        Raises:
            OptionsNotFoundError: If the id of `key` does not exist in self.cache.
        """
        try:
            return self.cache[self.get_id(key)]
        except KeyError:
            raise OptionsNotFoundError(key)

    def set_options(self, key, *opts, **kw_opts):
        """Set options under `key`.
        
        If `opts` or `kw_opts` are provided, override the previously set options or keyword options.
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
        """Insert options under `key`.

        If `kw` is an int or a digit, it is treated as an argument option index to insert at. Otherwise, it is treated as a keyword option to update.

        Args:
            key: A key for a set of options and keyword options.
            kw: An index for argument options or a keyword option.
            opt (str): The option to insert.
            **kw_opts: More kw and opt pairs.

        Note:
            `kw_opts` are are treated similarly as `kw` and `opt`.

        Raises:
            OptionsNotFoundError: If the id of `key` does not exist in self.cache.
        """
        key_id = self.get_id(key)
        for kw, opt in dict(kw_opts, **{kw:opt}).items():
            if isinstance(kw, str) and not kw.isdigit():
                self.cache[key_id][1][kw] = opt
            else:
                self.cache[key_id][0].insert(int(kw), opt)

    def __contains__(self, option):
        """Check if an option is registered.
        
        Args:
            option (str): The option used to register a callback.

        Returns:
            ``True`` if `option` exists in self.callbacks, ``False`` otherwise.
        """
        return option in self.callbacks
    
    def __getitem__(self, option):
        """Get the callback registered under an option.

        Args:
            option (str): The option used to register a callback.

        Returns:
            The callback function that was registered under `option`.

        Raises:
            CallbackError: If `option` does not exist in self.callbacks. 
        """
        try:
            return self.callbacks[option]
        except KeyError:
            raise CallbackError(option)

    def is_lock(self, option):
        """Check if an option was registered as a lock.

        Args:
            option (str): The option used to register a callback.

        Returns:
            ``True if the callback was registered as a lock, ``False`` otherwise.

        Raises:
            CallbackError: If `option` does not exist in self.callbacks. 
        """
        return self[option].lock is True

    def get_desc(self, option):
        """Get the description of an option.

        Args:
            option (str): The option used to register a callback.

        Returns:
            str: The `desc` was registered under `option`.

        Raises:
            CallbackError: If `option` does not exist in self.callbacks. 
        """
        return self[option].desc

    def set_desc(self, option, desc=""):
        """Set the description of an option.

        Args:
            option (str): The option used to register a callback.
            desc (str): A description of the option.

        Raises:
            CallbackError: If `option` does not exist in self.callbacks. 
        """
        self[option].desc = desc

    def get_args(self, option):
        """Get the default arguments for an option's callback.

        Args:
            option (str): The option used to register a callback.

        Returns:
            tuple: The `args` that was registered under `option`.

        Raises:
            CallbackError: If `option` does not exist in self.callbacks. 
        """
        return self[option].args

    def set_args(self, option, *args):
        """Set the default arguments for an option's callback.

        Args:
            option (str): The option used to register a callback.
            *args: The default arguments when the callback is called.

        Raises:
            CallbackError: If `option` does not exist in self.callbacks. 
        """
        self[option].args = args

    def get_kwargs(self, option):
        """Get the default keyword arguments for an option's callback.

        Args:
            option (str): The option used to register a callback.

        Returns:
            dict: The `kwargs` that was registered under `option`.

        Raises:
            CallbackError: If `option` does not exist in self.callbacks. 
        """
        return self[option].kwargs

    def set_kwargs(self, option, **kwargs):
        """Set the default keyword arguments for an option's callback.

        Args:
            option (str): The option used to register a callback.
            **kwargs: The default keyword arguments when the callback is called.

        Raises:
            CallbackError: If `option` does not exist in self.callbacks. 
        """
        self[option].kwargs = kwargs

    def copy(self):
        """Initialize a new copy of DemoOptions.
        
        When inheriting options from a Demo superclass, either a new DemoOptions instance should be created, or a copy should be made by calling this method. This is to avoid mangling options between superclass and subclasses.

        Examples:
            Creating a new instance of DemoOptions::

                class NewDemo(Demo):
                    options = DemoOptions()
                    ...

            Making a copy of the superclass options::

                class DemoSubclass(Demo):
                    options = Demo.options.copy()
                    ...

        Returns:
            DemoOptions: An instance of DemoOptions with a copy of self.cache and self.callbacks.
        """
        new_options = DemoOptions()
        for key_id, [opts, kw_opts] in self.cache.items():
            new_options.cache[key_id] = [list(opts), dict(kw_opts)]
        for option, callback in self.callbacks.items():
            new_options.callbacks[option] = types.FunctionType(
                callback.__code__, callback.__globals__, callback.__name__,
                callback.__defaults__, callback.__closure__)
            new_options.callbacks[option].lock = bool(callback.lock)
            new_options.callbacks[option].desc = str(callback.desc)
            new_options.callbacks[option].args = tuple(callback.args)
            new_options.callbacks[option].kwargs = dict(callback.kwargs)
        return new_options

