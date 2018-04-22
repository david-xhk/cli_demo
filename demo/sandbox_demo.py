# -*- coding: utf-8 -*-

"""This module contains SandboxDemo, a CodeDemo subclass that provides a shell for experimenting with the functions used in code commands."""

# For py2.7 compatibility
from __future__ import print_function
import sys
if sys.version_info < (3,3):
    input = raw_input

from .code_demo import CodeDemo


class SandboxDemo(CodeDemo):
    help_text = "SandboxDemo extends CodeDemo by providing a shell in which users can experiment with the context that has been set up by CodeDemo."

    options = CodeDemo.options.copy()

    options.insert("commands", 2, "s")

    @options.register("s", retry=True, lock=True, newline=False)
    def sandbox(self, key):
        """Sandbox mode."""
        print("Switched to sandbox mode.")
        print("Use quit() to leave sandbox mode.")
        print()
        while True:
            nestings = []
            keywords = ["def", "class", "for", "while"]
            nested_list = 0
            nested_tuple = 0
            nested_dict = 0
            prefix = ">>> "
            command = [input(prefix).expandtabs(4)]
            i = 0
            if command[i] == "quit()":
                break
            while True:
                decorating = command[i].lstrip().startswith("@")
                newline = command[i].rstrip().endswith("\\")
                while True:
                    expected_ws = len(nestings) * "    "
                    if command[i].startswith(expected_ws):
                        for keyword in keywords:
                            if command[i].lstrip().startswith(keyword):
                                nestings.append(keyword)
                                break
                        break
                    elif nestings:
                        nestings.pop()
                    else:
                        break
                nested_tuple += command[i].count("(")
                if nested_tuple:
                    nested_tuple -= command[i].count(")")
                nested_list += command[i].count("[")
                if nested_list:
                    nested_list -= command[i].count("]")
                nested_dict += command[i].count("{")
                if nested_dict:
                    nested_dict - command[i].count("}")
                nested = (nestings or nested_tuple 
                    or nested_list or nested_dict)
                if nested or newline:
                    prefix = "... "
                elif decorating:
                    prefix = ">>> "
                next_line = (
                    (newline or decorating or nested) 
                    and input(prefix).expandtabs(4))
                if not next_line:
                    break
                elif newline:
                    command[i] = command[i][:-1] + next_line
                else:
                    command.append(next_line)
                    i += 1
            if any(command):
                self.execute(["\n".join(command)], print_in=False)
        print("Leaving sandbox mode.")
        print()
        self.print_options(key=key)

