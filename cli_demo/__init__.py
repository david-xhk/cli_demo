# -*- coding: utf-8 -*-

"""This module contains a framework for interactive command line demonstrations.

Examples:
    Making a simple CodeDemo subclass:
        In spam.py:
            ::  

                from cli_demo import CodeDemo

                class SpamDemo(CodeDemo):
                    help_text = "An eggs and bacon bonanza."

                    setup_code = '''\
                    spam = 6
                    eggs = 42'''

                    commands = [
                        "spam  # is good for you",
                        "eggs  # is the meaning of life",
                        "eggs % spam  # go perfect together",
                        "response + ' was your response!'"
                    ]
    
    Running a Demo:
        In a command line interface:
            ::
        
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
                >>> spam = 6
                >>> eggs = 42

                Options:
                 0: spam  # is good for you
                 1: eggs  # is the meaning of life
                 2: eggs % spam  # go perfect together
                 3: response + 'was your response!'
                 a: Execute all of the above.
                 c: Setup code.
                 o: Options.
                 r: Restart.
                 q: Quit.

                Choose a command: a
                >>> spam  # is good for you
                6

                >>> eggs  # is the meaning of life
                42

                >>> eggs % spam  # go perfect together
                0

                >>> response + ' was your response!'
                'noodles was your response!'

                Choose a command: q
                Goodbye!

    Making a Demo script:
        1. In spam.py:
            ::

                ...
                ...

                if __name__ == "__main__":
                    demo = SpamDemo()
                    demo.run()

        2. In a command line interface:
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

