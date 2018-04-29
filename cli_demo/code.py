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
    """CodeDemo improves Demo by introducing a feature called :attr:`~cli_demo.code.CodeDemo.commands`, which allows the user to select from a set of code snippets and view the result of it being passed into :meth:`~cli_demo.code.CodeDemo.execute`.
    
    Attributes:
        setup_code (str): The code to run in :meth:`~cli_demo.code.CodeDemo.setup_callback`.
        command_prompt (str): The input prompt for :meth:`~cli_demo.code.CodeDemo.get_commands`.
        commands (list[str]): The code snippets for the user to choose from in :meth:`~cli_demo.code.CodeDemo.get_commands`.
        locals (dict): The local namespace populated in :meth:`~cli_demo.code.CodeDemo.setup_callback`.
        globals (dict): The global namespace populated in :meth:`~cli_demo.code.CodeDemo.setup_callback`.
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

    @catch_exc
    def run(self):
        """The main logic of a :class:`~cli_demo.code.CodeDemo` program.
        
        First, :meth:`~cli_demo.demo.Demo.print_intro` is called, then the options for :meth:`~cli_demo.demo.Demo.run_setup` is printed via :meth:`~cli_demo.demo.Demo.print_options` before :meth:`~cli_demo.demo.Demo.run_setup` itself is called, followed by the same process for :meth:`~cli_demo.code.CodeDemo.get_commands`.

        :meth:`~cli_demo.demo.Demo.run` is decorated with::

            @catch_exc
            def run(self):
                ...
        """
        self.print_intro()
        self.print_options(key="setup")
        self.run_setup()
        self.print_options(key="commands")
        self.get_commands()

    @options.register("c", "Setup code.", retry=True, newline=True)
    def print_setup(self):
        """Print :attr:`~cli_demo.code.CodeDemo.setup_code`."""
        print("Setup:")
        self.print_in(self.setup_code)
        print()

    @options.register("setup")
    def setup_callback(self, response):
        """Handle user input to :meth:`~cli_demo.demo.Demo.run_setup`.
        
        Set :attr:`~cli_demo.code.CodeDemo.locals` to the global namespace of :mod:`__main__` before updating with `response`. Then, copy the ``__builtins__`` of :mod:`__main__` into :attr:`~cli_demo.code.CodeDemo.globals`. Finally, ``exec`` :attr:`~cli_demo.code.CodeDemo.setup_code` in :attr:`~cli_demo.code.CodeDemo.locals` and :attr:`~cli_demo.code.CodeDemo.globals` before printing it via :meth:`~cli_demo.code.CodeDemo.print_setup`.

        :meth:`~cli_demo.code.CodeDemo.setup_callback` is decorated with::

            @options.register("setup")
            def setup_callback(self, response):
                ...

        Args:
            response (str): The user input to :meth:`~cli_demo.demo.Demo.run_setup`.

        Note:
            The :class:`~cli_demo.code.CodeDemo` instance is available in :attr:`~cli_demo.code.CodeDemo.locals` under the name `demo`, and the user response under `response`.
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

    @options("c", "o", "r", "q", key="commands")
    def get_commands(self):
        """Prompt the user to select a command from :attr:`~cli_demo.code.CodeDemo.commands`.

        :meth:`~cli_demo.code.CodeDemo.get_commands` is decorated with::

            @options("c", "o", "r", "q", key="commands")
            def get_commands(self):
                ...
        """
        return input(self.command_prompt)

    @options.register("commands", retry=True)
    def commands_callback(self, response):
        """Handle user input to :meth:`~cli_demo.code.CodeDemo.get_commands`.
        
        :meth:`~cli_demo.code.CodeDemo.execute` the respective code snippet or all :attr:`~cli_demo.code.CodeDemo.commands` if `response` is a valid index or ``"a"``. Otherwise, :meth:`~cli_demo.demo.Demo.retry` with the error message: ``"Invalid index. Please try again."``.

        :meth:`~cli_demo.code.CodeDemo.commands_callback` is decorated with::

            @options.register("commands", retry=True)
            def commands_callback(self, response):
                ...

        Args:
            response (str): The user input to :meth:`~cli_demo.code.CodeDemo.get_commands`.
        """
        commands = None
        if response == "a":
            commands = self.commands[:]
        elif response in map(str, range(len(self.commands))):
            commands = self.commands[int(response):int(response)+1]
        if commands:
            self.execute(commands)
        else:
            self.retry("Invalid index. Please try again.")

    def commands_options(self):
        """Provide options for :meth:`~cli_demo.code.CodeDemo.get_commands`.

        The descriptions and options are the code snippets and their enumerations. An additional option is ``"a"``, which is ``"Execute all of the above."``.
        """
        for index, command in enumerate(self.commands):
            yield (str(index), "\n    ".join(command.splitlines()))
        yield ("a", "Execute all of the above.")

    def execute(self, commands, print_in=True):
        """``exec`` each command in :attr:`~cli_demo.code.CodeDemo.locals` and :attr:`~cli_demo.code.CodeDemo.globals`.

        :meth:`~cli_demo.code.CodeDemo.print_in` the command if necessary, then strip any comments, and then compile the command if there are multiple lines or assignments before ``exec``-ing it. :meth:`~cli_demo.code.CodeDemo.print_out` the result or catch and print any errors. If there are any assignments in the command, :meth:`~cli_demo.code.CodeDemo.execute` their assigned names.

        Args:
            commands (list): The code snippets to ``exec``.
            print_in (bool): Whether to :meth:`~cli_demo.code.CodeDemo.print_in` a command before ``exec``-ing it.
        """
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
        """Print each line in `text` starting with ">>>" or "..."."""
        for line in text.splitlines():
            if line.startswith("    "):
                print("... " + line)
            else:
                print(">>> " + line)

    def print_out(self, *args):
        """Pretty-print or print `args`."""
        if args:
            try:
                pprint.pprint(*args)
            except:
                print(*args)

