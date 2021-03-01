#!/bin/bash

# Install script
# CLIC website software
#
# DO NOT RUN THIS AS SUDO
# This is a script to install the last version of the software to the
# production server. WARNING : this script is not meant to be run on
# development machines! Some commands may destruct unstaged git changes !
# This script does not launch the software.
#
# author: Alexandre CHAU

# Obtain complete path
DIR="$( cd "$(dirname "$0")" ; pwd -P )"
WEBDIR="${DIR}/clic-website"
echo "Installing website in $WEBDIR"

# Ensure we run the last version on master
cd $DIR
git stash
git checkout master
# Check if submodule is present, if yes clean git state
if [ -d $WEBDIR ]
then
    cd $WEBDIR
    git stash
    git checkout master
fi
# Download last version of all modules
cd $DIR
git pull --recurse-submodules
git submodule update --remote --merge
git commit -am "Automatic server update"
git push
# Install new update in clic-website submodule, clean
cd $WEBDIR
npm install
