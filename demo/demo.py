#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains Demo, the basic framework for interactive command line demonstrations."""

# For py2.7 compatibility
from __future__ import print_function
import sys
if sys.version_info < (3,3):
    input = raw_input

import inspect
from .options import DemoOptions
from .exceptions import DemoRetry, DemoExit, DemoRestart, catch_exc


class Demo(object):
    """Demo provides a basic framework for interactive demonstrations in the command-line interface.

Several key features are introduced:
    `restart`, `retry`, and `exit`: the main control flow tools.
    `run`, the main logic of a demo program.
    `print_help`, a function that prints the help text.
    `options`, a class object that you can use to:
        Decorate an input function with the responses allowed.
        Register a callback for some input response.
    `print_options`, a function that prints what responses are allowed."""
    
    help_text = """
Demo provides a basic framework for interactive demonstrations in the command-line interface.

Several key features are introduced:
    `restart`, `retry`, and `exit`: the main control flow tools.
    `run`, the main logic of a demo program.
    `print_help`, a function that prints the help text.
    `options`, a class object that you can use to:
        Decorate an input function with the responses allowed.
        Register a callback for some input response.
    `print_options`, a function that prints what responses are allowed."""

    symbols = [" ", "●", "○", "▸", "▹"]

    max_width = 60

    indent = 4

    setup_prompt = "Select an option, or type something random: "

    options = DemoOptions()
    """options, a class object for managing user input."""
    """Decorate an input function with allowed responses.

    If a response is correct (i.e. part of the options provided), the callback registered to that response will be called, and its return value returned. 

    Otherwise, the input function will be called again to get another response from the user.

    An error will be raised if an option provided does not have a callback registered, 

    Alternatively, other responses can be redirected to another callback using the `key` keyword.

    Providing keyword options allow specific responses to be redirected to another callback.
    
    Examples:
        @options("h", "o", "r", "q")
        def foo(self):
            # Only accept the given responses.
            ...

        @options("y", "n", reply="Enter 'y' or 'n'")
        def bar(self):
            # Only accept the given responses, with a reply prompt.
            ...

        @options("h", "o", "r", "q", key="setup")
        def baz(self):
            # Accept the given responses, or redirect response to callback registered at "setup".
            ...

        @options(h="c")
        def quz(self):
            # Redirect 'h' response to callback registered at "c".
            ...

        @options(s="stop")
        def quuz(self):
            # Redirect 's' response to callback registered at "stop".
            ...
    """
    """Register a callback for some input response.

    A callback registered under a supposed `key` should accept a `response` argument.
    
    Setting `lock` to True causes the `key` of a triggering input function to be received. (default is False).

    Setting `newline` to True causes a new line to be printed before the callback is executed. (default is True)

    Setting `retry` to True causes the input function to be called again once the callback has returned. (default is False)

    Examples:
        @options.register("setup"):
        def setup_demo(self, response):
            # Receive response from input functions using "setup" key.
            ...

        @options.register("o", lock=True):
        def print_options(self, key):
            # Receive the key of the input function which triggers it (in order to print the options of that input function, for instance).
            ...

        @options.register("h", newline=True):
        def print_help(self):
            # Leave a line before executing in order to create a gap between the user input and the contents printed.
            ...

        @options.register("e", retry=True):
        def echo_response(self, response):
            # When an input function triggers this function, call the input function again once done with execution.
            ...
    """
    """Inheriting options from a Demo superclass.
    
    When inheriting options from a Demo superclass, always make a copy instead of referencing it directly. 
    
    Alternatively, a new options object can be created.

    This is to avoid mangling options between superclass and subclasses.

    Examples:
        class DemoSubclass(Demo):
            options = Demo.options.copy()
            ...
        
        class NewDemo(Demo):
            options = DemoOptions()
            ...
    """

    @options.register("r", newline=False)
    def restart(self, text=None):
        """Restart."""
        raise DemoRestart(text)

    @options.register("q", newline=False)
    def quit(self, text=None):
        """Quit."""
        raise DemoExit(text)

    def retry(self, text=None):
        raise DemoRetry(text)

    def print_intro(self):
        print("Welcome to {}!".format(self.__class__.__name__))
        print()
        self.print_intro = lambda: None

    @classmethod
    def get_dashes(cls, dash="=", num=None):
        if not num:
            num = cls.max_width
        return dash * num

    @classmethod
    def format_help(cls):
        return """{line}\n{title}\n{line}\n\n{text}\n\n""".format(
            line=cls.get_dashes("-", len(cls.__name__)),
            title=cls.__name__, text=cls.help_text.strip())

    @options.register("h", retry=True)
    def print_help(self):
        """Help."""
        """Format and print the help text.

        The indentation of the text printed is controlled by the class attribute `indent`.
        
        The length of each line in help_text is limited to a length of the class attribute, `max_width`. Overflow is iteratively printed on a new line.
        
        help_text is formatted by the following:
Unindented lines are printed as-is.
    Indented lines are a sub point.
        And
            up to
                four levels of indentation are supported.

        Sections can be separated with whitespace.
        """
        symbols = list(enumerate(self.symbols))
        dashes = self.get_dashes()
        width = self.max_width
        indent = self.indent
        print("Help:")
        print(dashes)
        for cls in self.__class__.__mro__[-2::-1]:
            for line in cls.format_help().splitlines():
                if not line.lstrip():
                    print()
                    continue
                for i, mark in reversed(symbols):
                    if not line.startswith("    " * i):
                        continue
                    ws = " " * (indent*i)
                    lines = [(ws[:-2] + mark + " "
                        if i else "") + line.lstrip()]
                    j = 0
                    while True:
                        line = lines[j]
                        total = 0
                        escapes = 0
                        for char in line:
                            if (char.isalnum() 
                                    or not repr(char).startswith("'\\x")):
                                total += 1
                            else:
                                escapes += 1
                        total += escapes / 3
                        if total <= width:
                            break
                        k = line.rfind(" ", 0, width + (escapes or 1))
                        if k == -1:
                            k = width + escapes
                        lines[j], overflow = line[:k], lines[k+1:]
                        lines.append(ws + overflow)
                        j += 1
                    for line in lines:
                        print(line)
                    break
        print(dashes)
        print()

    @options.register("o", retry=True, lock=True)
    def print_options(self, *opts, **kwargs):
        """Options."""
        """Print what responses are allowed for an input function.

        If a `key` is provided, print_options will do the following:
            Retrieve options and descriptions from the function starting with `key` and ending in '_options', if defined.

            Check the cache in the options object for the options of the input function that uses `key`.
        
        The description for an option will be the docstring of its registered callback.

        Options are printed in the following order: 
            Options from defined `key` function
            Keyword options from options cache
            Argument options from options cache
            Argument options passed to `print_options`
        """
        print("Options:")
        opt_list = []
        opts = [(opt, opt) for opt in opts]
        key = kwargs.pop("key", None)
        if key:
            func_name = key + "_options"
            if hasattr(self, func_name):
                for opt in getattr(self, func_name)():
                    opt_list.append(opt)
            if key in self.options:
                key_opts, kw_opts = self.options[key]
                opts = (list(kw_opts.items())
                        + [(opt, opt) for opt in key_opts]
                        + opts)
        for opt, name in opts:
            if self.options.has_callback(name):
                desc = self.options.get_callback(name).__doc__
            else:
                desc = ""
            opt_list.append((opt, desc))
        opt_width = (max(len(opt) for opt, desc in opt_list)-3)//4*4+6
        for opt, desc in opt_list:
            print("{}: {}".format(opt.rjust(opt_width), desc))
        print()

    def __init__(self):
        self.options.demo = self

    @options.register("setup", retry=True, newline=False)
    def setup_callback(self, response):
        print("Got: {}".format(response))
        print()

    @options("h", "o", "r", "q", key="setup")
    def run_setup(self):
        return input(self.setup_prompt)

    def setup_options(self):
        yield "*", "Any response."

    @catch_exc
    def run(self):
        self.print_intro()
        self.print_options(key="setup")
        self.run_setup()

