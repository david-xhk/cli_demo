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
    """A basic framework for interactive demonstrations in a command line interface.
    
    Attributes:
        help_text (str): The help text used in :meth:`~cli_demo.demo.Demo.print_help`.
        setup_prompt (str): The input prompt for :meth:`~cli_demo.demo.Demo.run_setup`.
        options: A :class:`~cli_demo.options.DemoOptions` instance for :meth:`registering <cli_demo.options.DemoOptions.register>` option callbacks and :meth:`designating <cli_demo.options.DemoOptions.__call__>` options to input functions.

    Warning:
        When inheriting :attr:`~cli_demo.demo.Demo.options` from a :class:`~cli_demo.demo.Demo` superclass, either a new :class:`~cli_demo.options.DemoOptions` instance should be created::

            class NewDemo(Demo):
                options = DemoOptions()
                ...

        Or a copy should be made by calling :meth:`~cli_demo.options.DemoOptions.copy`::

            class DemoSubclass(Demo):
                options = Demo.options.copy()
                ...

        This is to avoid mangling options between superclass and subclasses.
    """

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

    setup_prompt = "Select an option, or type something random: "

    options = DemoOptions()

    def __init__(self):
        self.options.demo = self
    
    @catch_exc
    def run(self):
        """The main logic of a :class:`~cli_demo.demo.Demo` program.
        
        First, call :meth:`~cli_demo.demo.Demo.print_intro`, then print the options for :meth:`~cli_demo.demo.Demo.run_setup` using :meth:`~cli_demo.demo.Demo.print_options` before calling :meth:`~cli_demo.demo.Demo.run_setup`.
        
        Note:
            :meth:`~cli_demo.demo.Demo.run` is decorated with::

                @catch_exc
                def run(self):
                    ...
        """
        self.print_intro()
        self.print_options(key="setup")
        self.run_setup()

    def print_intro(self):
        """Print the welcome text once.
        
        Note:
            After :meth:`~cli_demo.demo.Demo.print_intro` is called for the first time, calling it again will no longer have any effect.
        """
        print("Welcome to {}!".format(self.__class__.__name__))
        print()
        self.print_intro = lambda: None

    @options.register("o", "Options.", retry=True, lock=True, newline=True)
    def print_options(self, *opts, **key):
        """Print what responses are allowed for an input function.

        Args:
            *opts (str): Which options to print.
            **key (str): An input function key.
        
        Note:
            * If an input function `key` is provided, :meth:`~cli_demo.demo.Demo.print_options` will do the following:
            
              1. Retrieve options and descriptions (in a tuple) from ``key_options()``- a function that starts with `key` and ends in '_options'- if it is defined.

              2. Get options from :func:`~cli_demo.options.DemoOptions.get_options` using the input function `key`.

            * Options are printed in the following order: 
                
              1. Options from ``key_options()``
                
              2. Keyword options from :func:`~cli_demo.options.DemoOptions.get_options`
                
              3. Argument options from :func:`~cli_demo.options.DemoOptions.get_options`
                
              4. Argument options passed into :meth:`~cli_demo.demo.Demo.print_options`

            * Besides the options from ``key_options()``, option descriptions are taken from the :attr:`~cli_demo.options.Option.desc` of the :class:`~cli_demo.options.Option` instance registered under it. If an option is not :meth:`registered <cli_demo.options.DemoOptions.__contains__>`, then ``""`` is used for the description.

            * :meth:`~cli_demo.demo.Demo.print_options` is decorated with::

                @options.register("o", "Options", retry=True, lock=True, newline=True)
                def print_options(self, *opts, **key):
                    ...
        """
        print("Options:")
        opt_list = []
        kw_opts = [(opt, opt) for opt in opts]
        key = key.pop("key", None)
        if key:
            func_name = key + "_options"
            if hasattr(self, func_name):
                for opt, desc in getattr(self, func_name)():
                    opt_list.append((opt, desc))
            if self.options.has_options(key):
                kw_opts = (
                    list(self.options.get_options(key)[1].items())
                    + [(opt, opt) for opt in self.options.get_options(key)[0]]
                    + kw_opts)
        for name, opt in kw_opts:
            if opt in self.options:
                desc = self.options.get_desc(opt)
            else:
                desc = ""
            opt_list.append((name, desc))
        name_width = (max(len(name) for name, desc in opt_list)-3)//4*4+6
        for name, desc in opt_list:
            print("{}: {}".format(name.rjust(opt_width), name_width))
        print()

    @options.register("h", "Help.", retry=True, newline=True)
    def print_help(self, **kwargs):
        """Format and print :attr:`~cli_demo.demo.Demo.help_text`.

        Args:
            symbols (list): A list of symbols for each level of indentation. Defaults to ``[" ", "●", "○", "▸", "▹"]``.
            width (int): The maximum width for a line printed. Defaults to ``60``.
            indent (int): The number of spaces per indent for the text printed. Defaults to ``4``.
            border (str): The character used for the border for :attr:`~cli_demo.demo.Demo.help_text`. Defaults to ``"~"``.
            title (str): The character used for the border for the "Help" title. Defaults to ``"="``.
            subtitle (str): The character used for the border for the name of each :class:`~cli_demo.demo.Demo` subclass. Defaults to ``"-"``.
            include (bool): Whether to include the :attr:`~cli_demo.demo.Demo.help_text` of all superclasses that are subclasses of :class:`~cli_demo.demo.Demo`. Defaults to ``False``.

        Note:
            :meth:`~cli_demo.demo.Demo.print_help` is decorated with::

                @options.register("h", "Help.", retry=True, newline=True)
                def print_help(self, **kwargs):
                    ...
        """
        symbols = list(enumerate(kwargs.get(
            "symbols", [" ", "●", "○", "▸", "▹"])))
        width = kwargs.get("width", 60)
        indent = kwargs.get("indent", 4)
        border = kwargs.get("border", "~") * width
        title = "{line}\nHelp\n{line}\n".format(
            line=kwargs.get("title", "=")*4)
        subtitle = kwargs.get("subtitle", "-")
        if kwargs.get("include", False):
            classes = [cls for cls in reversed(self.__class__.__mro__)
                       if issubclass(cls, Demo)]
        else:
            classes = [self.__class__]
        print(border)
        print(title)
        for cls in classes:
            text = """{title}\n{line}\n\n{text}\n\n""".format(
                title=cls.__name__,
                line=subtitle*len(cls.__name__),
                text=cls.help_text.strip())
            for line in text.splitlines():
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
                        lines[j], overflow = line[:k], line[k+1:]
                        lines.append(ws + overflow)
                        j += 1
                    for line in lines:
                        print(line)
                    break
        print(border)
        print()

    @options("h", "o", "r", "q", key="setup")
    def run_setup(self):
        """Prompt the user for input for the setup process.
        
        Note:
            :meth:`~cli_demo.demo.Demo.run_setup` is decorated with::

                @options("h", "o", "r", "q", key="setup")
                def run_setup(self):
                    ...
        """
        return input(self.setup_prompt)
    
    @options.register("setup", retry=True)
    def setup_callback(self, response):
        """Handle user input to :meth:`~cli_demo.demo.Demo.run_setup`.

        Args:
            response (str): The user input to :meth:`~cli_demo.demo.Demo.run_setup`.

        Note:
            :meth:`~cli_demo.demo.Demo.setup_callback` is decorated with::

                @options.register("setup", retry=True)
                def setup_callback(self, response):
                    ...
        """
        print("Got: {}".format(response))
        print()

    def setup_options(self):
        """Provide options for :meth:`~cli_demo.demo.Demo.run_setup`.
        
        Note:
            The default option is ``"*"`` with description ``"Any response."``.
        """
        yield "*", "Any response."

    @options.register("r")
    def restart(self, text=None):
        """Restart the main :meth:`~cli_demo.demo.Demo.run` loop.
        
        Args:
            text (str, optional): The text to print when restarting.

        Raises:
            :class:`~cli_demo.exceptions.DemoRestart`

        Note:
            :meth:`~cli_demo.demo.Demo.restart` is decorated with::

                @options.register("r")
                def restart(self, text=None):
                    ...
        """
        raise DemoRestart(text)

    @options.register("q")
    def quit(self, text=None):
        """Break out of the main :meth:`~cli_demo.demo.Demo.run` loop.

        Args:
            text (str, optional): The text to print when quitting.

        Raises:
            :class:`~cli_demo.exceptions.DemoQuit`

        Note:
            :meth:`~cli_demo.demo.Demo.quit` is decorated with::

                @options.register("q")
                def quit(self, text=None):
                    ...
        """
        raise DemoExit(text)

    def retry(self, text=None):
        """Go back to the last input function.

        Args:
            text (str, optional): The text to print when retrying.

        Raises:
            :class:`~cli_demo.exceptions.DemoRetry`
        """
        raise DemoRetry(text)

