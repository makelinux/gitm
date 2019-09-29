# git-m - multiple git replication and management utility

There are great tools for multiple git repositories management: repo and git submodules.
But sometimes you can have dozens and hundreds of standalone git repositories which you
would like to manage.

Features:

 * Can be installed as git custom command:
	$ git m -h

 * Replicates standalone repositories which are not included in repo or submodules.

 * Perform git command from outer directory
   Example:

Git refuses to work from outer directory:

	$ git branch gitm/
	fatal: not a git repository (or any parent up to mount point /)

Gim-m changes directory to destination and performs requested command:

	$ git m branch gitm/
	 * master

This feature saves you from changing current directories between many repositories.

 * Perform git command on all repositories in directory tree:

	$ git m describe --always --all
	project .
	heads/master
	project A
	heads/master
	project B
	heads/master


Getting help:
 * git-m --help

TODO:
 * Accept list of files as input. For example pipe from: find . -name '.git' -printf "%h\n"
