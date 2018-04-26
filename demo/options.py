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
        desc (str): The description of the option that should be printed in :func:`~demo.demo.Demo.print_options`.
        callback (function): The function that the :func:`~demo.options.Option.call` function should wrap.
        newline (bool): Whether an empty line should be printed before :attr:`~demo.options.Option.callback` is called in the :func:`~demo.options.Option.call` function.
        retry (bool): Whether an input function should be called again once :attr:`~demo.options.Option.callback` has returned.
        lock (bool): Whether the `key` of a trigerring input function should be received by :attr:`~demo.options.Option.callback`.
        args (tuple): The default arguments that should be used to call :attr:`~demo.options.Option.callback` in the :func:`~demo.options.Option.call` function.
        kwargs (dict): The default keyword arguments that should be used to call :attr:`~demo.options.Option.callback` in the :func:`~demo.options.Option.call` function.
    """
    __slots__ = ["name", "desc", "callback", "newline",
                 "retry", "lock", "args", "kwargs"]

    def __init__(self, **kwargs):
        for attr in ["name", "desc", "callback", "newline", 
                     "retry", "lock", "args", "kwargs"]:
            value = kwargs.get(attr, None)
            setattr(self, attr, value)

    def call(self, demo, *args, **kwargs):
        """Call the registered :attr:`~demo.options.Option.callback`.

        Args:
            demo (Demo): The :class:`~demo.demo.Demo` instance that should be passed to :attr:`~demo.options.Option.callback`.
            *args: The arguments that should be passed to :attr:`~demo.options.Option.callback`.
            **kwargs: The keyword arguments that should be passed to :attr:`~demo.options.Option.callback`.

        Note:
            * :attr:`~demo.options.Option.args` is used if `args` is empty.
            * :attr:`~demo.options.Option.kwargs` is used if `kwargs` is empty.
            * An empty line is printed before :attr:`~demo.options.Option.callback` is called if :attr:`~demo.options.Option.newline` is ``True``.
            * DemoRetry will be raised if :attr:`~demo.options.Option.retry` is ``True`` and :attr:`~demo.options.Option.callback` successfully returned.
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
        """Initialize a new copy of :class:`~demo.options.Option`.
        
        Returns:
            An instance of :class:`~demo.options.Option` with a deep copy of all attributes belonging to `self`.
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
        demo (Demo): The :class:`~demo.demo.Demo` instance that a :class:`~demo.options.DemoOptions` instance exists in.
        registry (dict): The options and their :class:`~demo.options.Option` objects that have been registered.
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

        An :class:`~demo.options.Option` object will be created based on the arguments and keyword arguments provided and then stored in :attr:`~demo.options.DemoOptions.registry`.
        
        Args:
            option (str): The name of the option.
            desc (str, optional): The description of the option that should be printed in :func:`~demo.demo.Demo.print_options`. Defaults to "".
            newline (bool, optional): Whether an empty line should be printed before the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object is called in its :func:`~demo.options.Option.call` function. Defaults to ``False``.
            retry (bool, optional): Whether an input function should be called again once the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object has returned. Defaults to ``False``.
            lock (bool, optional): Whether the `key` of a trigerring input function should be received by the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object. Defaults to ``False``.
            args (tuple, optional): The default arguments that should be used to call the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object in its :func:`~demo.options.Option.call` function. Defaults to ().
            kwargs (dict, optional): The default keyword arguments that should be used to call the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object in its :func:`~demo.options.Option.call` function. Defaults to {}.

        Returns:
            :func:`register_decorator`: A decorator which takes a function, sets the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object, and returns the original function.

        Note:
            * `option` can be an expected user response or an input function key.

            * If `option` is an input function key, the :attr:`~demo.options.Option.callback` that is set must accept a `response` argument- the user's response to that input function.

            * If `lock` is ``True``, the :attr:`~demo.options.Option.callback` that is set must accept a `key` argument- the key of the input function that triggered it.
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
        """Check if an :class:`~demo.options.Option` object is registered.
        
        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.

        Returns:
            ``True`` if `option` exists in :attr:`~demo.options.DemoOptions.registry`, ``False`` otherwise.
        """
        return (option in self.registry 
                and isinstance(self.registry[option], Option))
    
    def __getitem__(self, option):
        """Get the registered :class:`~demo.options.Option` object.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.

        Returns:
            The :class:`~demo.options.Option` object registered under `option`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        if option not in self:
            raise OptionNotFoundError(option)
        else:
            return self.registry[option]
            

    def call(self, option, *args, **kwargs):
        """Forward a call to the :func:`~demo.options.Option.call` function of the :class:`~demo.options.Option` object.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.
            *args: The arguments to use when calling :attr:`~demo.options.Option.callback`.
            **kwargs: The keyword arguments to use when calling :attr:`~demo.options.Option.callback`.

        Returns:
            The return value of :attr:`~demo.options.Option.callback`.

        Raises:
            DemoException: If :attr:`~demo.options.DemoOptions.demo` is not set.
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`.
            CallbackNotFoundError: If :attr:`~demo.options.Option.callback` has not been set in the :class:`~demo.options.Option` object.
        """
        if not self.demo:
            raise DemoException("Demo not set yet.")
        else:
            callback = self.get_callback(option)
            return callback(self.demo, *args, **kwargs)

    def get_callback(self, option):
        """Get the :func:`~demo.options.Option.call` function from the :class:`~demo.options.Option` object.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.

        Returns:
            The :func:`~demo.options.Option.call` function of the :class:`~demo.options.Option` object, which wraps the :attr:`~demo.options.Option.callback` that was set.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`.
            CallbackNotFoundError: If :attr:`~demo.options.Option.callback` has not been set in the :class:`~demo.options.Option` object.
        """
        option_obj = self[option]
        if option_obj.callback is None:
            raise CallbackNotFoundError(option)
        else:
            return option_obj.call

    def set_callback(self, option, callback):
        """Set the function that the :func:`~demo.options.Option.call` function of the :class:`~demo.options.Option` object should wrap.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.
            callback: The function that the :func:`~demo.options.Option.call` function of the :class:`~demo.options.Option` object should wrap.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].callback = callback                 

    def is_lock(self, option):
        """Check if the `key` of a trigerring input function will be received by the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.

        Returns:
            ``True`` if the :attr:`~demo.options.Option.newline` attribute of the :class:`~demo.options.Option` object is ``True``, ``False`` otherwise.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].lock is True

    def set_lock(self, option, lock):
        """Set whether the `key` of a trigerring input function should be received by the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.
            lock (bool): Whether the `key` of a trigerring input function should be received by the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].lock = bool(lock)

    def will_retry(self, option):
        """Check if an input function will be called again once the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object has returned.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.

        Returns:
            ``True`` if the :attr:`~demo.options.Option.retry` attribute of the :class:`~demo.options.Option` object is ``True``, ``False`` otherwise.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].retry is True

    def set_retry(self, option, retry):
        """Set whether an input function should be called again once the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object has returned.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.
            retry (bool): Whether an input function should be called again once the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object has returned.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].retry = bool(retry)

    def has_newline(self, option):
        """Check if an empty line will be printed before the :attr:`~demo.options.Option.callback` of the  :class:`~demo.options.Option` object is called.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.

        Returns:
            ``True`` if the :attr:`~demo.options.Option.newline` attribute of the :class:`~demo.options.Option` object is ``True``, ``False`` otherwise.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].newline is True

    def set_newline(self, option, newline):
        """Set whether an empty line should be printed before the :attr:`~demo.options.Option.callback` of the  :class:`~demo.options.Option` object is called.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.
            newline (bool): Whether an empty line should be printed before the :attr:`~demo.options.Option.callback` of the  :class:`~demo.options.Option` object is called.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].newline = bool(newline)

    def get_desc(self, option):
        """Get the description of the :class:`~demo.options.Option` object that will be printed in :func:`~demo.demo.Demo.print_options`.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.

        Returns:
            str: The :attr:`~demo.options.Option.desc` of the :class:`~demo.options.Option` object that was set.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].desc

    def set_desc(self, option, desc):
        """Set the description of the :class:`~demo.options.Option` object that should be printed in :func:`~demo.demo.Demo.print_options`.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.
            desc (str): The description of the :class:`~demo.options.Option` object that should be printed in :func:`~demo.demo.Demo.print_options`.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].desc = str(desc)

    def get_args(self, option):
        """Get the default arguments that will be used to call the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object in its :func:`~demo.options.Option.call` function.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.

        Returns:
            tuple: The :attr:`~demo.options.Option.args` of the :class:`~demo.options.Option` object that was set.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].args

    def set_args(self, option, *args):
        """Set the default arguments that should be used to call the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object in its :func:`~demo.options.Option.call` function.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.
            *args: The default arguments that should be used to call the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object in its :func:`~demo.options.Option.call` function.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        self[option].args = tuple(args)

    def get_kwargs(self, option):
        """Get the default keyword arguments that will be used to call the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object in its :func:`~demo.options.Option.call` function.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.

        Returns:
            dict: The :attr:`~demo.options.Option.kwargs` of the :class:`~demo.options.Option` object that was set.

        Raises:
            OptionNotFoundError: If `option` does not exist in :attr:`~demo.options.DemoOptions.registry`. 
        """
        return self[option].kwargs

    def set_kwargs(self, option, **kwargs):
        """Set the default keyword arguments that should be used to call the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object in its :func:`~demo.options.Option.call` function.

        Args:
            option (str): The :attr:`~demo.options.Option.name` used to register the :class:`~demo.options.Option` object.
            **kwargs: The default keyword arguments that should be used to call the :attr:`~demo.options.Option.callback` of the :class:`~demo.options.Option` object in its :func:`~demo.options.Option.call` function.

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
            ``True`` if the id of `key` exists in :attr:`~demo.options.DemoOptions.cache`, ``False`` otherwise.
        """
        return self.get_id(key) in self.cache

    def get_options(self, key):
        """Get the options that were set with `key`.

        Args:
            key: A key for a set of options and keyword options.

        Returns:
            list[list, dict]: The options and keyword options set under `key`.

        Raises:
            KeyNotFoundError: If the id of `key` does not exist in :attr:`~demo.options.DemoOptions.cache`.
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
            KeyNotFoundError: If the id of `key` does not exist in :attr:`~demo.options.DemoOptions.cache`.

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
        """Initialize a new copy of :class:`~demo.options.DemoOptions`.
        
        Returns:
            An instance of :class:`~demo.options.DemoOptions` with a deep copy of the :attr:`~demo.options.DemoOptions.cache` and :attr:`~demo.options.DemoOptions.registry` belonging to `self`.
        """
        new_options = DemoOptions()
        for key_id, [opts, kw_opts] in self.cache.items():
            new_options.cache[key_id] = [list(opts), dict(kw_opts)]
        for name, option in self.registry.items():
            new_options.registry[name] = option.copy()
        return new_options

