#!/bin/bash

# Run script
# CLIC website software
#
# DO NOT RUN THIS AS SUDO
# This script kills any previous instance of the server and restarts it
#
# author: Alexandre CHAU

# Obtain complete path
DIR="$( cd "$(dirname "$0")" ; pwd -P )"
WEBDIR="${DIR}/clic-website"
echo "Run website in $WEBDIR"

# Kill previous instance
cd $WEBDIR
npm stop
# Remove logs
rm ~/.npm/_logs/*.log

# Set NODE_ENV environment variable to "production"
export NODE_ENV="production"

# Start server
npm start