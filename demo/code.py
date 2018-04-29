# -*- coding: utf-8 -*-

"""This module contains CodeDemo, a Demo subclass that supports code commands."""

# For py2.7 compatibility
from __future__ import print_function
import sys
if sys.version_info < (3,3):
    input = raw_input

import inspect
import pprint
from .demo import Demo
from .exceptions import catch_exc


class CodeDemo(Demo):
    """CodeDemo improves Demo by introducing a feature called `commands`, which allows the user to select from a set of code snippets and view the result of it being executed.
    
    Attributes:
        setup_code (str): Code to ``exec()`` for setting up a context in :meth:`~demo.code.CodeDemo.setup_callback`.
        command_prompt (str): The input prompt for :meth:`~demo.code.CodeDemo.get_commands`.
        commands (list[str]): The commands to ``exec()`` that the user can choose from in :meth:`~demo.code.CodeDemo.get_commands`.
        locals (dict): The local namespace for ``exec()`` statements. Populated in :meth:`~demo.code.CodeDemo.setup_callback`.
        globals (dict): The global namespace for ``exec()`` statements. Populated in :meth:`~demo.code.CodeDemo.setup_callback`.
    """
    
    help_text = """CodeDemo improves Demo by introducing a feature called `commands`, which allows the user to select from a set of code snippets and view the result of it being executed."""

    setup_code = """\
# Setup code here.
foo = 1 + 1
bar = 5 * 2
spam = 14"""

    command_prompt = "Choose a command: "

    commands = [
        "1  # Comments will be removed.",
        "response + \" was your response\"  # Variables are stored in memory",
        "foo + bar  # Operations will print their result.",
        "eggs = spam + 5  # Assignments will print the assigned value.",
        "spam / 0  # Errors will get printed too!"
        ]

    options = Demo.options.copy()

    @options.register("c", "Setup code.", retry=True, newline=True)
    def print_setup(self):
        print("Setup:")
        self.print_in(self.setup_code)
        print()

    @options.register("setup")
    def setup_callback(self, response):
        """Handle user input to :meth:`~demo.code.CodeDemo.run_setup`.

        :meth:`~demo.code.CodeDemo.setup_callback` is decorated with::

            @options.register("setup")
            def setup_callback(self, response):
                ...

        Args:
            response (str): The user input.

        Note:
            * When :meth:`~demo.code.CodeDemo.setup_callback` is called, the following occurs:
    
              1. :attr:`~demo.code.CodeDemo.locals` is updated with the global namespace from :mod:`__main__` and `response`.

              2. The ``__builtins__`` of :mod:`__main__` is copied into :attr:`~demo.code.CodeDemo.globals`.

              3. :attr:`~demo.code.CodeDemo.setup_code` is ``exec()``-ed in :attr:`~demo.code.CodeDemo.locals` and :attr:`~demo.code.CodeDemo.globals`.

            * The :attr:`~demo.code.CodeDemo.commands` selected by the user will be executed in this very namespace.

            * The :class:`~demo.demo.Demo` instance is available in this local namespace under the name `demo`, and the user response under `response`.
        """
        main = sys.modules["__main__"]
        self.globals = vars(main.__builtins__).copy()
        for name in ["__import__"]:
            del self.globals[name]
        self.locals = dict(
            inspect.getmembers(main, 
                predicate=lambda obj: not inspect.ismodule(obj)),
            demo=self, response=response)
        exec(compile(self.setup_code, "<string>", "exec"), {}, self.locals)
        print()
        self.print_setup()

    @options.register("commands", retry=True)
    def commands_callback(self, response):
        """Check if commands are correct and push them to `execute`."""
        commands = None
        if response == "a":
            commands = self.commands[:]
        elif response in map(str, range(len(self.commands))):
            commands = self.commands[int(response):int(response)+1]
        if commands:
            self.execute(commands)
        else:
            self.retry("Invalid index. Please try again.")
    
    @catch_exc
    def run(self):
        self.print_intro()
        self.print_options(key="setup")
        self.run_setup()
        self.print_options(key="commands")
        self.get_commands()

    @options("c", "o", "r", "q", key="commands")
    def get_commands(self):
        """Allow the user to select a command to his liking. 

        Several other options are provided as well in order to navigate around the demo. An invalid command or option will prompt the user to try again.
        """
        return input(self.command_prompt)

    def commands_options(self):
        for index, command in enumerate(self.commands):
            yield (str(index), "\n    ".join(command.splitlines()))
        yield ("a", "Execute all of the above.")

    def execute(self, commands, print_in=True):
        """For each command, print with `print_in` and exec in locals, then pretty-print the result via `print_out`."""
        for command in commands:
            if print_in:
                self.print_in(command)
            while "#" in command:
                hash_index = command.find("#")
                newline_index = command.find("\n", hash_index)
                if newline_index == -1:
                    command = command[:hash_index].rstrip()
                else:
                    command = (command[:hash_index].rstrip() 
                               + command[newline_index:])
            assigned_names = []
            for line in command.splitlines():
                if " = " in line:
                    names = line.split(" = ")[0]
                    if not (names.startswith("\t")
                            or names.startswith("    ")):
                        for name in names.split(","):
                            assigned_names.append(name.strip())
            try:
                if "\n" in command or " = " in command:
                    code = compile(command, "<string>", "exec")
                elif not command.startswith("print("):
                    code = "demo.print_out(" + command + ")"
                else:
                    code = command
                exec(code, self.globals, self.locals)
            except SyntaxError as exc:
                print("SyntaxError: invalid syntax (\"{}\", line {})".format(
                    command, exc.lineno))
            except Exception as exc:
                print("{}: {}".format(exc.__class__.__name__, exc))
            if assigned_names:
                self.execute(assigned_names)
            else:
                print()

    def print_in(self, text):
        for line in text.splitlines():
            if line.startswith("    "):
                print("... " + line)
            else:
                print(">>> " + line)

    def print_out(self, *args):
        if args:
            try:
                pprint.pprint(*args)
            except:
                print(*args)

