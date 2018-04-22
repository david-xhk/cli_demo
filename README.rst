*****
About
*****

binary_tree provides a Node object and some useful tools like constructors and tree traversals for a binary tree data structure.

========
Features
========

* Construct a binary tree using 

  * String
  * In-order and pre-order traversal
  * In-order and post-order traversal

* Check if a binary tree

  * Has a certain path sum
  * Is symmetrical

* Traverse a binary tree by 
    
  * Pre-order
  * In-order
  * Post-order
  * Level-order

* Get from a binary tree

  * All root-to-leaf paths
  * The maximum depth

=====
Usage
=====

---------
Importing
---------

To use the functions provided by :mod:`binary_tree`, you can do the following import::

    import binary_tree as tree

If you would like to use :class:`~binary_tree.Node` on its own, you may also write::
    
    from binary_tree import Node

-------------
Making a node 
-------------

To create an instance, pass a value into :class:`~binary_tree.Node`. ::
    
    node = Node(1)

Nodes have a :attr:`~binary_tree.Node.left` and a :attr:`~binary_tree.Node.right` attribute, which are expected to be instances of :class:`~binary_tree.Node`. They can be set on initialization. ::

    another_node = Node(2)
    parent_node = Node(3, node, another_node)

---------------
Checking a node
---------------

When you need to test for :class:`~binary_tree.Node` instances, you can make use of :func:`~binary_tree.is_node`. ::

    if tree.is_node(parent_node.left):
        print(str(parent_node) + "has left child!")

You can also use :func:`~binary_tree.is_leaf` to check for leaf nodes. ::

    if tree.is_leaf(parent_node.right):
        print(str(parent_node.right) + "is a leaf node!")

------------------------
Setting up a binary tree 
------------------------

To generate a binary tree, you can pass in a string of values to the :meth:`~binary_tree.Node.from_string` constructor. ::

    tree_string = "1,2,3,4,,5,6"
    root = Node.from_string(tree_string)

.. note::
    
    Node.from_string() will grow the tree structure in **level-order**.

Another way is by passing the in-order and pre-order traversal into :meth:`~binary_tree.Node.from_orders` to retrieve the original tree structure.  ::

    in_order = [4,2,1,5,3,6]
    pre_order = [1,2,4,3,5,6]
    root = Node.from_orders("in-pre", in_order, pre_order)

Alternatively, you can use the in-order and post-order traversal. ::

    in_order = [4,2,1,5,3,6]
    post_order = [4,2,5,6,3,1]
    root = Node.from_orders("in-post", in_order, post_order)

.. note::
    
    There should not be duplicates present in `in_order` and `pre_order` or `post_order`.

------------------------
Processing a binary tree
------------------------

With a tree set up, :func:`~binary_tree.has_path_sum` and :func:`~binary_tree.is_symmetrical` can be used to analyse the nature of the tree. ::

    if tree.has_path_sum(root, 10):
        print(str(root) + "has path with sum 10!")

    if tree.is_symmetrical(root):
        print(str(root) + "is symmetrical!")

You can also traverse down the tree, yielding each node along the way. There are four different kinds provided: :func:`pre-order <binary_tree.traverse_pre_order>`, :func:`in-order <binary_tree.traverse_in_order>`, :func:`post-order <binary_tree.traverse_post_order>`, and :func:`level-order <binary_tree.traverse_level_order>`. ::

    print("This is a pre-order traversal.")
    for node in tree.traverse_pre_order(root):
        print(node)

    print("This is an in-order traversal.")
    for node in tree.traverse_in_order(root):
        print(node)

    print("This is a post-order traversal.")
    for node in tree.traverse_post_order(root):
        print(node)

    print("This is a level-order traversal")
    for level in tree.traverse_level_order(root):
        for node in level:
            print(node)

A single dispatch function, :func:`~binary_tree.traverse`, is also available. ::
    
    traversals = []
    for kind in ("pre", "in", "post", "level"):
        traversal = list(tree.traverse(root, kind))
        traversals.append(traversal)

On top of traversals, you can get the paths between the root and each leaf node using :func:`~binary_tree.get_all_paths`. An example is in :func:`~binary_tree.has_path_sum`:

.. code-block:: python
    :emphasize-lines: 2
    
    def has_path_sum(node, value):
        for path in tree.get_all_paths(node):
            total = 0
            for node in path:
                total += node.value
            if total == value:
                return True
        else:
            return False

Lastly, you can use :func:`~binary_tree.get_max_depth` to get the total number of levels in the tree. ::
    
    depth = tree.get_max_depth(root)

=======
Credits
=======

binary_tree was written by Han Keong <hk997@live.com>.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

