*******
 About
*******

:mod:`cli_demo` provides a framework for interactive demonstrations in a command line interface.

==========
 Features
==========

.. contents:: 
    :local:

-----------------------
 Registering an option
-----------------------

There are various ways to :func:`~cli_demo.options.DemoOptions.register` an option:

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
:class:`~cli_demo.code.CodeDemo` information here.

-------------
 SandboxDemo
-------------
:class:`~cli_demo.sandbox.SandboxDemo` information here.

=========
 Credits
=========

cli_demo was written by Han Keong <hk997@live.com>.

