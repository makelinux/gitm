#!/bin/sh

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

rm -rf tmp gitm-tmp* standalone-empty-tmp status.yaml > /dev/null

# Sanity check
check ./git-m || exit

git clone -q git@github.com:makelinux/gitm.git gitm-tmp
\cp -a gitm-tmp gitm-tmp2
git init standalone-empty-tmp > /dev/null

check './git-m --export | grep -q standalone-empty-tmp'
check 'grep -q "^.:\$" status.yaml'

check './git-m --csv | grep -q "standalone-empty-tmp,"'

check 'test -s status.yaml'

mkdir tmp
cp status.yaml tmp
pushd tmp > /dev/null

check '../git-m --import | grep -q same'
check '../git-m --csv | grep -q ".*,.*"'
check '../git-m --sha | grep -q ".*  .*"'
check '../git-m --compare | grep -q same'
check 'grep -q "^.:\$" status.yaml'

git init git-second-tmp > /dev/null
(cd git-second-tmp; git commit --allow-empty -m empty; git checkout --detach; git branch -d master)

../git-m --compare
check '../git-m --compare | grep -q "git-second-tmp.*undesired"'
check '../git-m --compare | grep -q "standalone-empty-tmp.*absent"'

echo test git_for_subdir:
check '../git-m describe --always gitm-tmp/'

echo test git_for_each:
rm status.yaml
../git-m --export
check '../git-m describe --always'

popd 2> /dev/null

(exit $errors)
