git-m - multiple git replication and management utility
=====

There are great tools for multiple git repositories management: repo and
git submodules. But sometimes you can have dozens and hundreds of
standalone git repositories which you would like to manage.


.. contents::
   :local:

Features
----

Can be installed as custom git command
~~~~

.. code-block::

    git m -h

To use git-m as custom git command copy it to PATH, for example to
/usr/local/bin.

Replicates tree of standalone repositories
~~~~

Standalone repository is r. which is not included in repo or submodules.

.. code-block::

    git m --export

Then copy status.yaml to another host or location and run

.. code-block::

    git m --import

Easy to use
~~~~

For most cases need just to add 'm' to correct git command as the second
word. See the next features for example.

Performs a git command from an outer directory
~~~~

Git refuses to work from outer directory:

.. code-block::

    $ git branch some_project
    fatal: not a git repository (or any parent up to mount point /)

Git-m changes directory to destination and performs requested command:

.. code-block::

    $ git m branch some_project
     * master

This feature saves you from changing current directories between
many repositories.

Performs a git command on all repositories in directory tree
~~~~

.. code-block::

    $ git m describe --always --all
    project .
    heads/master
    project A
    heads/master
    project B
    heads/master

Compares status of current tree of gits against saved
~~~~

See internal help for details.

Prints or exports status of tree of gits in various formats.
~~~~

- pretty text table with shortened strings
- csv
- sha
- json
- yaml

See internal help for details.

More features
~~~~

.. code-block::

  git-m --help

To do
----

* Accept list of files as input. For example pipe from: find . -name '.git' -printf "%h\n"
