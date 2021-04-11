#!/bin/bash

# DO NOT LAUNCH as sudo, otherwise the wrong key will be fetched

DIR="$( cd "$(dirname "$0")" ; pwd -P )"

cd $DIR

git stash
git checkout master
git pull

pip3 install python-telegram-bot
systemctl restart roboclic
