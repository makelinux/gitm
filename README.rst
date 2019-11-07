git-m - multiple git replication and management utility
=====

There are great tools for multiple gits (git repositories) management: repo and git submodules.
But sometimes you can have dozens or hundreds of standalone gits which you would like to manage without
manual initialization of repo or git submodules.

The mission of git-m is to simplify work with multiple gits.

.. contents::
   :local:

Features
****

Can be installed as custom git command 'm'
----

To use git-m as custom git command copy it to PATH, for example to /usr/local/bin.

.. code-block::

    git m -h

Discovers and replicates tree of standalone gits
----

Standalone git [repository] is r. which is not included in repo or submodules.

.. code-block::

    git m --export

Then copy status.yaml to another host or location and run

.. code-block::

    git m --import

Expands and works around limitations of original git commands
----

To use git-m with original git command just use arguments of git as arguments of git-m.
If git-m is installed as custom command just add "m" between "git" and original command.

Performs a git command from an outer directory
~~~~

Git refuses to work from outer directory:

.. code-block::

    $ git log some_project/some_file
    fatal: not a git repository (or any parent up to mount point /)

You can use option -C

.. code-block::
    $ git -C some_project log some_file

More easy just to use git-m. It changes directory to destination directory and performs requested command:

.. code-block::

    $ git m log some_project/some_file

This feature saves you from splitting patches and changing current directories between many repositories.

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
----

Please see internal help for details.

Discovers status of tree of gits in various handy formats.
----

- pretty text table with shortened strings
- csv
- sha
- json
- yaml

See internal help for details.

More features
----

.. code-block::

  git-m --help

To do
****

* Accept list of files as input. For example pipe from: find . -name '.git' -printf "%h\n"
