#!/bin/bash

successes=0
errors=0

#trap '(1>&2 echo -e $"\e[2;31mFAIL \e[0;39m ret=$? ${BASH_SOURCE[0]}:${LINENO} ${FUNCNAME[*]} $BASH_COMMAND")' ERR

#trap 'echo ${BASH_SOURCE[*]}:${BASH_LINENO[*]} ${FUNCNAME[*]} cmd: $BASH_COMMAND' DEBUG

check()
{
	echo "Running: $@ : "
	if eval "$@"; then 
		echo -e "\033[2;32mOK \033[0;39m";
		let successes+=1;
	else
		local ret=$?
		echo -e "\033[2;31mError \033[0;39m $ret"
		let errors+=1; 
		return $ret
	fi
}

export-test()
{
	check './git-m --status | grep -q Total' # without status.yaml
	check './git-m --export'
	check './git-m | grep -q empty-tmp'
	check 'grep -q "^.:\$" status.yaml'

	check './git-m --csv | grep -q "standalone-empty-tmp,"'

	check 'test -s status.yaml'
	check './git-m --status | grep -q Total'
}

import-test()
{
	check '../git-m --import | grep -q ='
	check '../git-m --csv | grep -q ".*,.*"'
	check '../git-m --sha | grep -q ".*  .*"'
	check '../git-m --compare --csv | grep -q same'
	check 'grep -q "^.:\$" status.yaml'
}

compare-test()
{
	git init --initial-branch=main git-second-tmp > /dev/null
	(cd git-second-tmp; git commit --allow-empty -m empty; git checkout --detach; git branch -d main)

	../git-m --compare
	check '../git-m --compare --csv | grep -q "git-second-tmp.*undesired"'
	check "../git-m --compare --csv | grep -q 'standalone-empty-tmp.*\\(!\\|absent\\)'"
}

git_for_subdir-test()
{
	check '../git-m describe --always gitm-tmp'
	check '../git-m describe --always gitm-tmp/'
	check '../git-m log -n1 gitm-tmp/git-m | grep ^commit'
}

git_for_each-test()
{
	../git-m --export
	check '../git-m describe --always'
}

export-ssh-import-test()
{
	echo check one-liner replication over ssh

	export GIT_SSH_COMMAND="ssh -o BatchMode=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR"
	../git-m --export - | $GIT_SSH_COMMAND localhost \
		"mkdir -p $PWD/../tmp.ssh; cd \"\$_\";pwd;  ../git-m --import -"

	check diff --exclude={.git,git-second-tmp,status.yaml} -r . ../tmp.ssh
}

rm -rf tmp* gitm-tmp* standalone-empty-tmp status.yaml > /dev/null

# Sanity check
check ./git-m || exit

git clone -q git@github.com:makelinux/gitm.git gitm-tmp
\cp -a gitm-tmp gitm-tmp2
git init --initial-branch=main standalone-empty-tmp > /dev/null

export-test

check ./git-m --urls

mkdir tmp
cp status.yaml tmp
pushd tmp > /dev/null

import-test

compare-test

git_for_subdir-test

git_for_each-test

export-ssh-import-test

popd 2> /dev/null

echo Successes=$successes
echo Errors=$errors

(exit $errors)
