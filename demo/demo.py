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
    """A basic framework for interactive demonstrations in command-line interface.
    
    Attributes:
        help_text (str): The help text of a `Demo`.
        help_options (dict): Formatting options for :func:`~Demo.print_help`.
        setup_prompt (str): The input prompt for :func:`~Demo.run_setup`.
        options (DemoOptions): Delegate for registering option callbacks and designating options to input functions.

    Warning:
        When inheriting options from a Demo superclass, either a new :class:`~demo.options.DemoOptions` instance should be created::

            class NewDemo(Demo):
                options = DemoOptions()
                ...

        Or a copy should be made by calling :func:`~demo.options.DemoOptions.copy`::

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

    def print_intro(self):
        """Print the welcome text once.

        After `print_intro` is called once, calling it again will no longer have any effect.
        """
        print("Welcome to {}!".format(self.__class__.__name__))
        print()
        self.print_intro = lambda: None

    @options.register("h", "Help.", retry=True, newline=True)
    def print_help(self, symbols=[" ", "●", "○", "▸", "▹"], width=60, indent=4,
                   border="~", title="=", subtitle="-", include=True):
        """Format and print the help text.
        
        The help text for all superclasses will be printed
        Attributes:
            symbols (list): A list of symbols for each level of indentation.
            max_width: The maximum width for a line printed.
            indent: The indentation of the text printed.
            border: The character used for the border of the help text.
            title: The character used for the border of the help title.
            subtitle: The character used for the border of the Demo subtitle.
            include: Whether to include the help text of all superclasses. 
        """
        symbols = list(enumerate(symbols))
        border *= width
        if include:
            classes = self.__class__.__mro__[-2::-1]
        else:
            classes = (self.__class__,)
        print(border)
        print("{line}\nHelp\n{line}\n".format(line=title*4))
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

    @options.register("o", "Options.", retry=True, lock=True, newline=True)
    def print_options(self, *opts, **key):
        """Print what responses are allowed for an input function.

        If `key` is provided, print_options will do the following:
            
            1. Retrieve options and descriptions from the function starting with `key` and ending in '_options', if defined.

            2. Check the cache in the options object for the options of the input function that uses `key`.

        Attributes:
            *opts (str): Which options to print.
            **key: An input function `key`.
        
        Note:
            * Other than those from the `key` function, option descriptions are taken from the `desc` argument registered to an option's callback.

            * Options are printed in the following order: 
                
              1. Options from defined `key` function
                
              2. Keyword options from options cache
                
              3. Argument options from options cache
                
              4. Argument options passed to `print_options`
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
            opt_list.append((opt, desc))
        opt_width = (max(len(opt) for opt, desc in opt_list)-3)//4*4+6
        for opt, desc in opt_list:
            print("{}: {}".format(opt.rjust(opt_width), desc))
        print()

    def __init__(self):
        self.options.demo = self

    @options.register("setup", retry=True)
    def setup_callback(self, response):
        """Handle user input to :func:`~demo.demo.Demo.run_setup`.

        Args:
            response (str): The user input.
        """
        print("Got: {}".format(response))
        print()

    @options("h", "o", "r", "q", key="setup")
    def run_setup(self):
        """Prompt the user for input for the setup process."""
        return input(self.setup_prompt)

    def setup_options(self):
        """Provide options for setup."""
        yield "*", "Any response."

    @catch_exc
    def run(self):
        """The main logic of a Demo program."""
        self.print_intro()
        self.print_options(key="setup")
        self.run_setup()

    @options.register("r", "Restart.")
    def restart(self, text=None):
        """Restart the main run loop.

        Args:
            text (str, optional): The text to print when restarting.
        """
        raise DemoRestart(text)

    @options.register("q", "Quit.")
    def quit(self, text=None):
        """Break out of the main run loop.

        Args:
            text (str, optional): The text to print when quitting.
        """
        raise DemoExit(text)

    def retry(self, text=None):
        """Go back to the last input function.

        Args:
            text (str, optional): The text to print when retrying.
        """
        raise DemoRetry(text)

