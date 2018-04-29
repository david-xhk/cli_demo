***************
 Documentation
***************

.. automodule:: cli_demo

======
 Demo
======

.. autoclass:: cli_demo.demo.Demo

Program logic of a Demo instance
--------------------------------
.. automethod:: cli_demo.demo.Demo.run

Setup process of a Demo instance
--------------------------------
.. automethod:: cli_demo.demo.Demo.run_setup

.. automethod:: cli_demo.demo.Demo.setup_callback

.. automethod:: cli_demo.demo.Demo.setup_options

Print functions of a Demo instance
----------------------------------
.. automethod:: cli_demo.demo.Demo.print_intro

.. automethod:: cli_demo.demo.Demo.print_options

.. automethod:: cli_demo.demo.Demo.print_help

Control flow tools of a Demo instance
-------------------------------------
.. automethod:: cli_demo.demo.Demo.restart

.. automethod:: cli_demo.demo.Demo.quit

.. automethod:: cli_demo.demo.Demo.retry

==========
 CodeDemo
==========

.. autoclass:: cli_demo.code.CodeDemo
    :show-inheritance:

Program logic of a CodeDemo instance
------------------------------------
.. automethod:: cli_demo.code.CodeDemo.run

Setup process of a CodeDemo instance
------------------------------------
.. automethod:: cli_demo.code.CodeDemo.setup_callback

Commands process of a CodeDemo instance
---------------------------------------
.. automethod:: cli_demo.code.CodeDemo.get_commands

.. automethod:: cli_demo.code.CodeDemo.commands_callback

.. automethod:: cli_demo.code.CodeDemo.commands_options

.. automethod:: cli_demo.code.CodeDemo.execute

Print functions of a CodeDemo instance
--------------------------------------
.. automethod:: cli_demo.code.CodeDemo.print_setup

.. automethod:: cli_demo.code.CodeDemo.print_in

.. automethod:: cli_demo.code.CodeDemo.print_out

=============
 SandboxDemo
=============

.. autoclass:: cli_demo.sandbox.SandboxDemo
    :show-inheritance:

Commands process of a SandboxDemo instance
------------------------------------------
.. automethod:: cli_demo.sandbox.SandboxDemo.get_commands

.. automethod:: cli_demo.sandbox.SandboxDemo.sandbox

=============
 DemoOptions
=============

.. autoclass:: cli_demo.options.DemoOptions

Designating options for an input function
-----------------------------------------
.. automethod:: cli_demo.options.DemoOptions.__call__

Getting the options for an input function
-----------------------------------------
.. automethod:: cli_demo.options.DemoOptions.get_options

.. automethod:: cli_demo.options.DemoOptions.has_options

.. automethod:: cli_demo.options.DemoOptions.get_id

Setting the options for an input function
-----------------------------------------
.. automethod:: cli_demo.options.DemoOptions.set_options

.. automethod:: cli_demo.options.DemoOptions.insert

Registering an Option instance
------------------------------
.. automethod:: cli_demo.options.DemoOptions.register

.. autoclass:: cli_demo.options.Option

Invoking the callback of an Option instance
-------------------------------------------
.. autoclass:: cli_demo.options.DemoOptions.call

.. autoclass:: cli_demo.options.Option.call

Getting attributes of an Option instance
----------------------------------------
.. automethod:: cli_demo.options.DemoOptions.__contains__

.. automethod:: cli_demo.options.DemoOptions.__getitem__

.. automethod:: cli_demo.options.DemoOptions.get_callback

.. automethod:: cli_demo.options.DemoOptions.is_lock

.. automethod:: cli_demo.options.DemoOptions.will_retry

.. automethod:: cli_demo.options.DemoOptions.has_newline

.. automethod:: cli_demo.options.DemoOptions.get_desc

.. automethod:: cli_demo.options.DemoOptions.get_args

.. automethod:: cli_demo.options.DemoOptions.get_kwargs

Setting attributes of an Option instance
----------------------------------------
.. automethod:: cli_demo.options.DemoOptions.set_callback

.. automethod:: cli_demo.options.DemoOptions.set_lock

.. automethod:: cli_demo.options.DemoOptions.set_retry

.. automethod:: cli_demo.options.DemoOptions.set_newline

.. automethod:: cli_demo.options.DemoOptions.set_desc

.. automethod:: cli_demo.options.DemoOptions.set_args

.. automethod:: cli_demo.options.DemoOptions.set_kwargs

Inheriting options from a Demo base class
-----------------------------------------
.. automethod:: cli_demo.options.DemoOptions.copy

.. automethod:: cli_demo.options.Option.copy

============
 exceptions
============

.. automodule:: cli_demo.exceptions
    :members:
    :member-order: bysource
    :show-inheritance:
    :special-members: __init__

