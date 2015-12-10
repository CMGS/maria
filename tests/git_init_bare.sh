#!/bin/bash

git_bare=$1

if [ -d $git_bare ]
then
	exit 1
fi

mkdir $git_bare
cd $git_bare
git init --bare
