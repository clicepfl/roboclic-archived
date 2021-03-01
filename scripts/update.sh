#!/bin/bash

# Update script
# CLIC website software
#
# DO NOT RUN THIS AS SUDO
# This script updates the server by calling ./install.sh, then ./run.sh
#
# author: Alexandre CHAU

# Crash script immediately on errors
set -e

# Obtain complete path
DIR="$( cd "$(dirname "$0")" ; pwd -P )"
WEBDIR="${DIR}/clic-website"
echo "Updating website in $WEBDIR"

# Call subroutines
cd $DIR
./install.sh

# Terminate old version, let systemd restart it
echo "Stopping old version, systemd should restart it in 3 sec..."
cd $WEBDIR
npm stop
