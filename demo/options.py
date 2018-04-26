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
            * :attr:`~demo.options.Option.args` is used if `args` is empty.
            * :attr:`~demo.options.Option.kwargs` is used if `kwargs` is empty.
            * An empty line is printed before the callback is called if :attr:`~demo.options.Option.newline` is ``True``.
            * DemoRetry will be raised if :attr:`~demo.options.Option.retry` is ``True`` and the callback successfully returned.
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
        registry (dict): The options and their Option objects that have been registered.
        cache (dict): A cache of input function key ids and the options and keyword options designated to them.
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

    def register(self, option, desc="", **kwargs):
        """Register an option.

        An Option object will be created based on the arguments and keyword arguments provided and then stored in :attr:`~demo.options.DemoOptions.registry`.
        
        Args:
            option (str): The name of the option.
            desc (str, optional): A description of the option. Defaults to "".
            newline (bool): Whether an empty line should be printed before calling :attr:`~demo.options.Option.callback`. Defaults to ``False``.
            retry (bool): Whether an input function should be called again once :attr:`~demo.options.Option.callback` has returned. Defaults to ``False``.
            lock (bool): Whether the `key` of a trigerring input function should be received by :attr:`~demo.options.Option.callback`. Defaults to ``False``.
            args (tuple): The default arguments to use when calling :attr:`~demo.options.Option.callback`. Defaults to ().
            kwargs (dict): The default keyword arguments to use when calling :attr:`~demo.options.Option.callback`. Defaults to {}.

        Returns:
            register_decorator: A decorator which takes a function, uses it to set the callback for the Option object, and returns the original function.

        Note:
            * `option` can be an expected user response or an input function key.

            * If `option` is an input function key, the :attr:`~demo.options.Option.callback` that is registered must accept a `response` argument- the user's response to that input function.

            * If `lock` is ``True``, the :attr:`~demo.options.Option.callback` that is registered must accept a `key` argument- the key of the input function that triggered it.
        """
        self.registry[option] = Option(name=option, desc=desc,
            newline=kwargs.get("newline", False), 
            retry=kwargs.get("retry", False),
            lock=kwargs.get("lock", False),
            args=kwargs.get("args", ()),
            kwargs=kwargs.get("kwargs", {}))
        def register_decorator(func):
            self.set_callback(option, func)
            return func
        return register_decorator

    def __contains__(self, option):
        """Check if an option is registered.
        
        Args:
            option (str): The name used to register the Option object.

        Returns:
            ``True`` if `option` exists in self.registry, ``False`` otherwise.
        """
        return option in self.registry
    
    def __getitem__(self, option):
        """Get the registered Option object.

        Args:
            option (str): The name used to register the Option object.

        Returns:
            Option: The Option object registered under `option`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        try:
            return self.registry[option]
        except KeyError:
            raise OptionNotFoundError(option)

    def call(self, option, *args, **kwargs):
        """Forward a call to the :func:`~demo.options.Option.call` function of the registered Option object.

        Args:
            option (str): The name used to register the Option object.
            *args: The arguments to use when calling :attr:`demo.options.Option.callback`.
            **kwargs: The keyword arguments to use when calling :attr:`demo.options.Option.callback`.

        Returns:
            The return value of :attr:`demo.options.Option.callback`.

        Raises:
            DemoException: If :attr:`~demo.options.DemoOptions.demo` is not set.
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`.
            CallbackNotFoundError: If :attr:`demo.options.Option.callback` has not been set in the Option object.
        """
        if not self.demo:
            raise DemoException("Demo not set yet.")
        else:
            callback = self.get_callback(option)
            return callback(self.demo, *args, **kwargs)

    def get_callback(self, option):
        """Get the :func:`~demo.options.Option.call` function from the registered Option object.

        Args:
            option (str): The name used to register the Option object.

        Returns:
            The :func:`~demo.options.Option.call` function of the Option object, which wraps the :attr:`demo.options.Option.callback` that was set.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`.
            CallbackNotFoundError: If :attr:`demo.options.Option.callback` has not been set in the Option object.
        """
        option_obj = self[option]
        if option_obj.callback is None:
            raise CallbackNotFoundError(option)
        else:
            return option_obj.call

    def set_callback(self, option, callback):
        """Set the callback of the registered Option object.

        Args:
            option (str): The name used to register the Option object.
            callback: The callback function to set.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].callback = callback                 

    def is_lock(self, option):
        """Check if the Option object was registered as a lock.

        Args:
            option (str): The name used to register the Option object.

        Returns:
            ``True`` if the Option object was registered as a lock, ``False`` otherwise.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].lock is True

    def set_lock(self, option, lock):
        """Set whether the Option object is a lock.

        Args:
            option (str): The name used to register the Option object.
            lock (bool): Whether the `key` of a trigerring input function should be received by :attr:`demo.options.Option.callback`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].lock = bool(lock)

    def will_retry(self, option):
        """Check if the Option object was registered to retry.

        Args:
            option (str): The name used to register the Option object.

        Returns:
            ``True`` if the Option object was registered to retry, ``False`` otherwise.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].retry is True

    def set_retry(self, option, retry):
        """Set whether an Option object will retry.

        Args:
            option (str): The name used to register the Option object.
            retry (bool): Whether an input function should be called again once :attr:`demo.options.Option.callback` has returned.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].retry = bool(retry)

    def has_newline(self, option):
        """Check if the Option object was registered to have a newline.

        Args:
            option (str): The name used to register the Option object.

        Returns:
            ``True`` if the Option object was registered to have a newline, ``False`` otherwise.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].newline is True

    def set_newline(self, option, newline):
        """Set whether the Option object will have a newline.

        Args:
            option (str): The name used to register the Option object.
            newline (bool): Whether an empty line should be printed before calling :attr:`demo.options.Option.callback`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].newline = bool(newline)

    def get_desc(self, option):
        """Get the description of the Option object.

        Args:
            option (str): The name used to register the Option object.

        Returns:
            str: The registered :attr:`~demo.options.Option.desc`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].desc

    def set_desc(self, option, desc):
        """Set the description of the Option object.

        Args:
            option (str): The name used to register the Option object.
            desc (str): A description of the option.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].desc = str(desc)

    def get_args(self, option):
        """Get the registered default arguments of the Option object.

        Args:
            option (str): The name used to register the Option object.

        Returns:
            tuple: The registered :attr:`~demo.options.Option.args`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].args

    def set_args(self, option, *args):
        """Set the default arguments of the Option object.

        Args:
            option (str): The name used to register the Option object.
            *args: The default arguments to use when calling :attr:`demo.options.Option.callback`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].args = tuple(args)

    def get_kwargs(self, option):
        """Get the registered default keyword arguments of the Option object.

        Args:
            option (str): The name used to register the Option object.

        Returns:
            dict: The registered :attr:`~demo.options.Option.kwargs`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].kwargs

    def set_kwargs(self, option, **kwargs):
        """Set the default keyword arguments of the Option object.

        Args:
            option (str): The name used to register the Option object.
            **kwargs: The default keyword arguments to use when calling :attr:`demo.options.Option.callback`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
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

