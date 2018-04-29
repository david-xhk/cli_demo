*******
 About
*******

<<<<<<< HEAD
:mod:`cli_demo` provides a framework for interactive demonstrations in a command line interface.
=======
:mod:`demo` provides a framework for interactive demonstrations in a command line interface.
>>>>>>> 4ad383388e7e1ba7bf9b253439e011ef33d646b9

==========
 Features
==========

.. contents:: 
    :local:

-----------------------
 Registering an option
-----------------------

<<<<<<< HEAD
There are various ways to :func:`~cli_demo.options.DemoOptions.register` an option:
=======
There are various ways to :func:`~demo.options.DemoOptions.register` an option:
>>>>>>> 4ad383388e7e1ba7bf9b253439e011ef33d646b9

* Registering with an expected user response
::

    @options.register("r", "Restart."):
    def restart(self):
        ...  # Restart demo

* Registering with an input function key
::

    @options.register("setup"):
    def setup_callback(self, response):
        ...  # Process response.

* Setting newline to True
::

    @options.register("h", "Help." newline=True):
    def print_help(self):
        print("This is the help text.")
        ...  # Print the help text

::

    >>> Enter an input: h

    This is the help text.  # A gap is inserted beforehand.
    ...

* Setting retry to True
::

    @options.register("echo", retry=True):
    def echo_response(self, response):
        print("Got:", response)

::

    >>> Enter an input: hello
    Got: hello
    >>> Enter an input:  # The input function is called again.

* Setting lock to True
::

    @options.register("o", lock=True):
    def print_options(self, key):
        if key == "setup":
            ...  # Print setup options
        elif key == "echo":
            ...  # Print echo options

----------
 CodeDemo
----------
<<<<<<< HEAD
:class:`~cli_demo.code.CodeDemo` information here.
=======
:class:`~demo.code.CodeDemo` information here.
>>>>>>> 4ad383388e7e1ba7bf9b253439e011ef33d646b9

-------------
 SandboxDemo
-------------
<<<<<<< HEAD
:class:`~cli_demo.sandbox.SandboxDemo` information here.
=======
:class:`~demo.sandbox.SandboxDemo` information here.
>>>>>>> 4ad383388e7e1ba7bf9b253439e011ef33d646b9

=========
 Credits
=========

<<<<<<< HEAD
cli_demo was written by Han Keong <hk997@live.com>.
=======
demo was written by Han Keong <hk997@live.com>.
>>>>>>> 4ad383388e7e1ba7bf9b253439e011ef33d646b9

