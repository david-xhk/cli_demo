# -*- coding: utf-8 -*-

"""This module contains DemoOptions- the `options` delegate for Demo, and Option- a class that holds information about a registered option."""

# For py2.7 compatibility
from __future__ import print_function

import functools
import inspect
from .exceptions import (DemoException, DemoRetry, KeyNotFoundError,
                         OptionNotFoundError, CallbackNotFoundError,
                         CallbackLockError, CallbackResponseError, catch_exc)


class Option(object):
    """Holds information about a registered option.

    Attributes:
        name (str): The name of the option.
        desc (str): The description of the option that should be printed in :meth:`~cli_demo.demo.Demo.print_options`.
        callback (function): The function that :meth:`~cli_demo.options.Option.call` should wrap.
        newline (bool): Whether an empty line should be printed before :attr:`~cli_demo.options.Option.callback` is called in :meth:`~cli_demo.options.Option.call`.
        retry (bool): Whether an input function should be called again once :attr:`~cli_demo.options.Option.callback` has returned.
        lock (bool): Whether the `key` of a triggering input function should be received by :attr:`~cli_demo.options.Option.callback`.
        args (tuple): The default arguments that should be used to call :attr:`~cli_demo.options.Option.callback` in :meth:`~cli_demo.options.Option.call`.
        kwargs (dict): The default keyword arguments that should be used to call :attr:`~cli_demo.options.Option.callback` in :meth:`~cli_demo.options.Option.call`.
    """
    __slots__ = ["name", "desc", "callback", "newline",
                 "retry", "lock", "args", "kwargs"]

    def __init__(self, **kwargs):
        for attr in ["name", "desc", "callback", "newline", 
                     "retry", "lock", "args", "kwargs"]:
            value = kwargs.get(attr, None)
            setattr(self, attr, value)

    def call(self, demo, *args, **kwargs):
        """Call the registered :attr:`~cli_demo.options.Option.callback`.

        Args:
            demo: The :class:`~cli_demo.demo.Demo` instance that should be passed into :attr:`~cli_demo.options.Option.callback`.
            *args: The arguments that should be passed into :attr:`~cli_demo.options.Option.callback`.
            **kwargs: The keyword arguments that should be passed into :attr:`~cli_demo.options.Option.callback`.

        Note:
            * :attr:`~cli_demo.options.Option.args` is used if `args` is empty.
            * :attr:`~cli_demo.options.Option.kwargs` is used if `kwargs` is empty.
            * An empty line is printed before :attr:`~cli_demo.options.Option.callback` is called if :attr:`~cli_demo.options.Option.newline` is ``True``.
            * DemoRetry will be raised if :attr:`~cli_demo.options.Option.retry` is ``True`` and :attr:`~cli_demo.options.Option.callback` successfully returned.
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
        """Initialize a new copy of :class:`~cli_demo.options.Option`.
        
        Returns:
            An instance of :class:`~cli_demo.options.Option` with a deep copy of all attributes belonging to ``self``.
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
        demo: The parent :class:`~cli_demo.demo.Demo` instance.
        registry (dict): The options and their :class:`~cli_demo.options.Option` instances that have been registered.
        cache (dict): A cache of input function key ids and their options and keyword options that have been captured.
    """

    def __init__(self):
        self.demo = None
        self.registry = {}
        self.cache = {}

    def __call__(self, *opts, **kw_opts):
        """Designate a set of options to an input function.
        
        If a user input falls within the designated options, invoke the :attr:`~cli_demo.options.Option.callback` of the corresponding :class:`~cli_demo.options.Option` instance through its :meth:`~cli_demo.options.Option.call` method.

        Args:
            retry (str, optional): The text to print before the input function is called again when the user response is invalid. Defaults to ``"Please try again"``.
            key (str, optional): The key of the input function.
            args (tuple, optional): The arguments that should be passed into the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance registered under `key`. Defaults to ``()``.
            kwargs (dict, optional): The keyword arguments that should be passed into :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance registered under `key`. Defaults to ``{}``.
            *opts: The user responses that should be accepted.
            **kw_opts: The user responses that should be redirected.

        Note:
            If `key` is provided:

                * `key` will be used to store a record of `opts` and `kw_opts` in :attr:`~cli_demo.options.DemoOptions.cache`.
                
                * To reference the options stored in :attr:`~cli_demo.options.DemoOptions.cache` when calling :meth:`~cli_demo.demo.Demo.print_options`, you can pass in `key` as the `key` argument.

                * If a user input does not fall within the designated options, the response will be forwarded to the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance registered under `key` through its :meth:`~cli_demo.options.Option.call` method.

            If `key` is not provided:
                
                * The **input function** itself will be used to store a record of `opts` and `kw_opts` in :attr:`~cli_demo.options.DemoOptions.cache`.

                * To reference the options stored in :attr:`~cli_demo.options.DemoOptions.cache` when calling :meth:`~cli_demo.demo.Demo.print_options`, you need to pass in the input function itself as the `key` argument.

                * If a user input does not fall within the designated options, :class:`~cli_demo.exceptions.DemoRetry` will be raised and `retry` will be printed.

        Returns:
            ``options_decorator()``: A decorator which takes a function (expected to be an input function) and returns a wrapped function.
        
        The following exceptions will only be raised while the wrapped function is being called.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If an option does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`.
            :class:`~cli_demo.exceptions.CallbackNotFoundError`: If :attr:`~cli_demo.options.Option.callback` has not been set in an :class:`~cli_demo.options.Option` instance.
            :class:`~cli_demo.exceptions.CallbackLockError`: If the :attr:`~cli_demo.options.Option.lock` attribute of an :class:`~cli_demo.options.Option` instance is ``True`` but its :attr:`~cli_demo.options.Option.callback` does not accept a `key` argument.
            :class:`~cli_demo.exceptions.CallbackResponseError`: If `key` is provided but the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance registered under `key` does not accept a `response` argument.
            :class:`~cli_demo.exceptions.DemoRetry`: If the user response was invalid.
        """
        retry = kw_opts.pop("retry", "Please try again.")
        key = kw_opts.pop("key", None)
        args = kw_opts.pop("args", ())
        kwargs = kw_opts.pop("kwargs", {})
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
                            raise CallbackLockError(response)
                    else:
                        return demo.options.call(option)
                elif key:
                    try:
                        return demo.options.call(key, response=response,
                            *args, **kwargs)
                    except TypeError as exc:
                        raise CallbackResponseError(response)
                else:
                    demo.retry(retry)
            return inner
        return options_decorator

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
            ``True`` if the id of `key` exists in :attr:`~cli_demo.options.DemoOptions.cache`, ``False`` otherwise.
        """
        return self.get_id(key) in self.cache

    def get_options(self, key):
        """Get the options that were set with `key`.

        Args:
            key: A key for a set of options and keyword options.

        Returns:
            list[list, dict]: The options and keyword options set under `key`.

        Raises:
            :class:`~cli_demo.exceptions.KeyNotFoundError`: If the id of `key` does not exist in :attr:`~cli_demo.options.DemoOptions.cache`.
        """
        try:
            return self.cache[self.get_id(key)]
        except KeyError:
            raise KeyNotFoundError(key)

    def set_options(self, key, *opts, **kw_opts):
        """Change the options that were set with `key`.
        
        If `opts` or `kw_opts` are provided, override the options or keyword options that were recorded previously.

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

        Insert `opt` into the argument options at index `kw` if it is an int or a digit. Otherwise, update the keyword options with `kw` and `opt`.

        Args:
            key: A key for a set of options and keyword options.
            kw: An index for argument options or a keyword option.
            opt (str): The option to insert.
            **kw_opts: More kw and opt pairs.

        Raises:
            :class:`~cli_demo.exceptions.KeyNotFoundError`: If the id of `key` does not exist in :attr:`~cli_demo.options.DemoOptions.cache`.

        Note:
            `kw_opts` are are treated similarly as `kw` and `opt`.
        """
        options = self.get_options(key)
        for kw, opt in dict(kw_opts, **{kw:opt}).items():
            if isinstance(kw, str) and not kw.isdigit():
                options[1][kw] = opt
            else:
                options[0].insert(int(kw), opt)
    
    def register(self, option, desc="", **kwargs):
        """Register an option.

        Create an :class:`~cli_demo.options.Option` instance based on the arguments and keyword arguments provided and then store in :attr:`~cli_demo.options.DemoOptions.registry`.

        Returns:
            ``register_decorator()``: A decorator which takes a function, sets the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance using :meth:`~cli_demo.options.DemoOption.set_callback`, and returns the original function.

        Args:
            option (str): The name of the option.
            desc (str, optional): The description of the option that should be printed in :meth:`~cli_demo.demo.Demo.print_options`. If not provided, it will be set to the name of :attr:`~cli_demo.options.Option.callback`.
            newline (bool, optional): Whether an empty line should be printed before :attr:`~cli_demo.options.Option.callback` is called. Defaults to ``False``.
            retry (bool, optional): Whether an input function should be called again once :attr:`~cli_demo.options.Option.callback` has returned. Defaults to ``False``.
            lock (bool, optional): Whether the `key` of a triggering input function should be received by :attr:`~cli_demo.options.Option.callback`. Defaults to ``False``.
            args (tuple, optional): The default arguments that should be used to call :attr:`~cli_demo.options.Option.callback`. Defaults to ``()``.
            kwargs (dict, optional): The default keyword arguments that should be used to call :attr:`~cli_demo.options.Option.callback`. Defaults to ``{}``.

        Note:
            * `option` can be an expected user response or an input function key.

            * If `option` is an input function key:

              * The :attr:`~cli_demo.options.Option.callback` that is set must accept a `response` argument- the user's response to that input function.

              * Any response to that input function which does not fall within its designated options will be forwarded to the :attr:`~cli_demo.options.Option.callback` through the :meth:`~cli_demo.options.Option.call` method of the :class:`~cli_demo.options.Option` instance for further processing.

            * If `lock` is ``True``, the :attr:`~cli_demo.options.Option.callback` that is set must accept a `key` argument- the key of the input function that triggered it.
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
        """Check if an :class:`~cli_demo.options.Option` instance is registered.
        
        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.

        Returns:
            ``True`` if `option` exists in :attr:`~cli_demo.options.DemoOptions.registry` and its value is an instance of :class:`~cli_demo.options.Option`, ``False`` otherwise.
        """
        return (option in self.registry 
                and isinstance(self.registry[option], Option))
    
    def __getitem__(self, option):
        """Get the registered :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.

        Returns:
            The :class:`~cli_demo.options.Option` instance registered under `option`.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`.
        """
        if option not in self:
            raise OptionNotFoundError(option)
        else:
            return self.registry[option]
            

    def call(self, option, *args, **kwargs):
        """Invoke the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance through its :meth:`~cli_demo.options.Option.call` method.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.
            *args: The arguments to use when calling :attr:`~cli_demo.options.Option.callback`.
            **kwargs: The keyword arguments to use when calling :attr:`~cli_demo.options.Option.callback`.

        Returns:
            The return value of the :attr:`~cli_demo.options.Option.callback`.

        Raises:
            :class:`~cli_demo.exceptions.DemoException`: If :attr:`~cli_demo.options.DemoOptions.demo` is not set.
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`.
            :class:`~cli_demo.exceptions.CallbackNotFoundError`: If :attr:`~cli_demo.options.Option.callback` has not been set in the :class:`~cli_demo.options.Option` instance.
        """
        if not self.demo:
            raise DemoException("Demo not set yet.")
        else:
            callback = self.get_callback(option)
            return callback(self.demo, *args, **kwargs)

    def get_callback(self, option):
        """Get the :meth:`~cli_demo.options.Option.call` method of the :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.

        Returns:
            The :meth:`~cli_demo.options.Option.call` method of the :class:`~cli_demo.options.Option` instance, which wraps its :attr:`~cli_demo.options.Option.callback`.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`.
            :class:`~cli_demo.exceptions.CallbackNotFoundError`: If :attr:`~cli_demo.options.Option.callback` has not been set in the :class:`~cli_demo.options.Option` instance.
        """
        opt = self[option]
        if opt.callback is None:
            raise CallbackNotFoundError(option)
        else:
            return opt.call

    def set_callback(self, option, callback):
        """Set the function that the :meth:`~cli_demo.options.Option.call` method of the :class:`~cli_demo.options.Option` instance should wrap.
        
        If the :attr:`~cli_demo.options.Option.desc` of the :class:`~cli_demo.options.Option` instance is blank, use the name of `callback` to set it. 

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.
            callback: The function that :meth:`~cli_demo.options.Option.call` should wrap.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance :class:`~cli_demo.options.Option`.
        """
        self[option].callback = callback
        if not self.get_desc(option):
            self.set_desc(option, "{}.".format(
                callback.__name__.replace("_", " ").capitalize()))

    def is_lock(self, option):
        """Check if the `key` of a triggering input function will be received by the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.

        Returns:
            ``True`` if the :attr:`~cli_demo.options.Option.lock` attribute of the :class:`~cli_demo.options.Option` instance is ``True``, ``False`` otherwise.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        return self[option].lock is True

    def set_lock(self, option, lock):
        """Set whether the `key` of a triggering input function should be received by the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.
            lock (bool): Whether the `key` of a triggering input function should be received by :attr:`~cli_demo.options.Option.callback`.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        self[option].lock = bool(lock)

    def will_retry(self, option):
        """Check if an input function will be called again once the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance has returned.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.

        Returns:
            ``True`` if the :attr:`~cli_demo.options.Option.retry` attribute of the :class:`~cli_demo.options.Option` instance is ``True``, ``False`` otherwise.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        return self[option].retry is True

    def set_retry(self, option, retry):
        """Set whether an input function should be called again once the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance has returned.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.
            retry (bool): Whether an input function should be called again once :attr:`~cli_demo.options.Option.callback` has returned.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        self[option].retry = bool(retry)

    def has_newline(self, option):
        """Check if an empty line will be printed before the :attr:`~cli_demo.options.Option.callback` of the  :class:`~cli_demo.options.Option` instance is called.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.

        Returns:
            ``True`` if the :attr:`~cli_demo.options.Option.newline` attribute of the :class:`~cli_demo.options.Option` instance is ``True``, ``False`` otherwise.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        return self[option].newline is True

    def set_newline(self, option, newline):
        """Set whether an empty line should be printed before the :attr:`~cli_demo.options.Option.callback` of the  :class:`~cli_demo.options.Option` instance is called.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.
            newline (bool): Whether an empty line should be printed before :attr:`~cli_demo.options.Option.callback` is called.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        self[option].newline = bool(newline)

    def get_desc(self, option):
        """Get the description of the :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.

        Returns:
            str: The :attr:`~cli_demo.options.Option.desc` attribute of the :class:`~cli_demo.options.Option` instance.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        return self[option].desc

    def set_desc(self, option, desc):
        """Set the description of the :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.
            desc (str): The description that should be printed in :meth:`~cli_demo.demo.Demo.print_options`.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        self[option].desc = str(desc)

    def get_args(self, option):
        """Get the default arguments that will be used to call the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.

        Returns:
            tuple: The :attr:`~cli_demo.options.Option.args` attribute of the :class:`~cli_demo.options.Option` instance.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        return self[option].args

    def set_args(self, option, *args):
        """Set the default arguments that should be used to call the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.
            *args: The default arguments that should be used to call :attr:`~cli_demo.options.Option.callback` in :meth:`~cli_demo.options.Option.call`.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        self[option].args = tuple(args)

    def get_kwargs(self, option):
        """Get the default keyword arguments that will be used to call the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.

        Returns:
            dict: The :attr:`~cli_demo.options.Option.kwargs` attribute of the :class:`~cli_demo.options.Option` instance.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        return self[option].kwargs

    def set_kwargs(self, option, **kwargs):
        """Set the default keyword arguments that should be used to call the :attr:`~cli_demo.options.Option.callback` of the :class:`~cli_demo.options.Option` instance.

        Args:
            option (str): The :attr:`~cli_demo.options.Option.name` used to register the :class:`~cli_demo.options.Option` instance.
            **kwargs: The default keyword arguments that should be used to call :attr:`~cli_demo.options.Option.callback` in :meth:`~cli_demo.options.Option.call`.

        Raises:
            :class:`~cli_demo.exceptions.OptionNotFoundError`: If `option` does not exist in :attr:`~cli_demo.options.DemoOptions.registry`, or if its value is not an instance of :class:`~cli_demo.options.Option`. 
        """
        self[option].kwargs = dict(kwargs)

    def copy(self):
        """Initialize a new copy of :class:`~cli_demo.options.DemoOptions`.
        
        Returns:
            An instance of :class:`~cli_demo.options.DemoOptions` with a deep copy of the :attr:`~cli_demo.options.DemoOptions.cache` and :attr:`~cli_demo.options.DemoOptions.registry` belonging to ``self``.
        """
        new_options = DemoOptions()
        for key_id, [opts, kw_opts] in self.cache.items():
            new_options.cache[key_id] = [list(opts), dict(kw_opts)]
        for name, option in self.registry.items():
            new_options.registry[name] = option.copy()
        return new_options

