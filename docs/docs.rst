***************
 Documentation
***************

.. automodule:: cli_demo

======
 Demo
======

.. autoclass:: cli_demo.demo.Demo

Program logic
-------------
.. automethod:: cli_demo.demo.Demo.run

Setup process
-------------
.. automethod:: cli_demo.demo.Demo.run_setup

.. automethod:: cli_demo.demo.Demo.setup_callback

.. automethod:: cli_demo.demo.Demo.setup_options

Print functions
---------------
.. automethod:: cli_demo.demo.Demo.print_intro

.. automethod:: cli_demo.demo.Demo.print_options

.. automethod:: cli_demo.demo.Demo.print_help

Control flow tools
------------------
.. automethod:: cli_demo.demo.Demo.restart

.. automethod:: cli_demo.demo.Demo.quit

.. automethod:: cli_demo.demo.Demo.retry

==========
 CodeDemo
==========

.. autoclass:: cli_demo.code.CodeDemo

Program logic
-------------
.. automethod:: cli_demo.code.CodeDemo.run

Setup process
-------------
.. automethod:: cli_demo.code.CodeDemo.setup_callback

Commands process
----------------
.. automethod:: cli_demo.code.CodeDemo.get_commands

.. automethod:: cli_demo.code.CodeDemo.commands_callback

.. automethod:: cli_demo.code.CodeDemo.commands_options

.. automethod:: cli_demo.code.CodeDemo.execute

Print functions
---------------
.. automethod:: cli_demo.code.CodeDemo.print_setup

.. automethod:: cli_demo.code.CodeDemo.print_in

.. automethod:: cli_demo.code.CodeDemo.print_out

=============
 SandboxDemo
=============

.. autoclass:: cli_demo.sandbox.SandboxDemo
    :members:
    :member-order: bysource
    :show-inheritance:

=========
 options
=========

.. automodule:: cli_demo.options

Designating options for an input function
-----------------------------------------
.. automethod:: cli_demo.options.DemoOptions.__call__

Registering a callback
----------------------
.. automethod:: cli_demo.options.DemoOptions.register

.. autoclass:: cli_demo.options.Option

Calling a callback
------------------
.. autoclass:: cli_demo.options.DemoOptions.call

.. autoclass:: cli_demo.options.Option.call

Inheriting a DemoOptions instance
---------------------------------
.. automethod:: cli_demo.options.DemoOptions.copy

.. automethod:: cli_demo.options.Option.copy

Getting Option attributes
-------------------------
.. automethod:: cli_demo.options.DemoOptions.__contains__

.. automethod:: cli_demo.options.DemoOptions.__getitem__

.. automethod:: cli_demo.options.DemoOptions.get_callback

.. automethod:: cli_demo.options.DemoOptions.is_lock

.. automethod:: cli_demo.options.DemoOptions.will_retry

.. automethod:: cli_demo.options.DemoOptions.has_newline

.. automethod:: cli_demo.options.DemoOptions.get_desc

.. automethod:: cli_demo.options.DemoOptions.get_args

.. automethod:: cli_demo.options.DemoOptions.get_kwargs

Setting Option attributes
-------------------------
.. automethod:: cli_demo.options.DemoOptions.set_callback

.. automethod:: cli_demo.options.DemoOptions.set_lock

.. automethod:: cli_demo.options.DemoOptions.set_retry

.. automethod:: cli_demo.options.DemoOptions.set_newline

.. automethod:: cli_demo.options.DemoOptions.set_desc

.. automethod:: cli_demo.options.DemoOptions.set_args

.. automethod:: cli_demo.options.DemoOptions.set_kwargs

Getting the options for an input function
-----------------------------------------
.. automethod:: cli_demo.options.DemoOptions.get_options

Setting the options for an input function
-----------------------------------------
.. automethod:: cli_demo.options.DemoOptions.set_options

.. automethod:: cli_demo.options.DemoOptions.insert

============
 exceptions
============

.. automodule:: cli_demo.exceptions
    :members:
    :member-order: bysource
    :show-inheritance:
    :special-members: __init__

