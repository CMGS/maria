#!/bin/bash

git_repo=$1
git_bare=$2

if [ ! -d $git_bare ]
then
	exit 1
fi

if [ -d $git_repo ]
then
	exit 2
fi

mkdir $git_repo
cd $git_repo 
git init 
touch test.c 
git add test.c
git commit -m "Add test.c"
git remote add origin git@127.0.0.1:$git_bare
git push origin master
