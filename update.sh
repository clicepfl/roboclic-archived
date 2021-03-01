#!/bin/bash

systemctl stop roboclic

DIR="$( cd "$(dirname "$0")" ; pwd -P )"

cd $DIR

git stash
git checkout master
git pull

systemctl start roboclic
