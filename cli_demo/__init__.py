# -*- coding: utf-8 -*-

"""This module contains a framework for interactive command line demonstrations.

Examples:
    Making a simple CodeDemo subclass:
    ::  
        
        # spam.py
        from cli_demo import CodeDemo
        
        def scramble(num):
            return "SCRAMBLE " * num

        class SpamDemo(CodeDemo):
            help_text = "An eggs and bacon bonanza."

            setup_code = '''\\
        eggs = 6
        spam = 42'''

            commands = [
                "eggs + spam  # yum yum",
                "bacon = spam % eggs",
                "eggs // bacon",
                "scramble(eggs)",
                "response + ' was your response!'"
            ]

    Running a Demo:
    ::

        >>> from spam import SpamDemo
        >>> demo = SpamDemo()
        >>> demo.run()
        Welcome to SpamDemo!

        Options:
         *: Any response.
         h: Help.
         o: Options.
         r: Restart.
         q: Quit.

        Select an option, or type something random: h

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ====
        Help
        ====

        SpamDemo
        --------

        An eggs and bacon bonanza.

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Select an option, or type something random: noodles

        Setup:
        >>> eggs = 6
        >>> spam = 42

        Options:
         0: "eggs + spam  # yum yum"
         1: "bacon = spam % eggs"
         2: "eggs // bacon"
         3: "scramble(eggs)"
         4: "response + ' was your response!'"
         a: Execute all of the above.
         c: Setup code.
         o: Options.
         r: Restart.
         q: Quit.

        Choose a command: a
        >>> eggs + spam  # yum yum
        48

        >>> bacon = spam % eggs
        >>> bacon
        0

        >>> eggs // bacon
        ZeroDivisionError: integer division or modulo by zero

        >>> scramble(eggs)
        'SCRAMBLE SCRAMBLE SCRAMBLE SCRAMBLE SCRAMBLE SCRAMBLE '

        >>> response + ' was your response!'
        'noodles was your response!'
        
        Choose a command: c

        Setup:
        >>> spam = 6
        >>> eggs = 42

        Choose a command: q
        Goodbye!
        

    Making a Demo script:
    ::

        # spam.py
        ...
        ...

        if __name__ == "__main__":
            demo = SpamDemo()
            demo.run()

    ::
    
        >>> python spam.py
        Welcome to SpamDemo!
        ...
        ...

    ::

        >>> python3 spam.py
        Welcome to SpamDemo!
        ...
        ...     
"""

__author__ = 'Han Keong'
__email__ = 'hk997@live.com'
__version__ = '0.0.1'

from .options import DemoOptions
from .demo import Demo
from .code import CodeDemo
from .sandbox import SandboxDemo

__all__ = ["DemoOptions", "Demo", "CodeDemo", "SandboxDemo"]

del options, demo, code, sandbox

