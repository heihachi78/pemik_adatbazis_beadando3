#!/bin/bash

#./setup_python.sh
./setup_docker.sh
./setup_db.sh
./setup_data.sh

echo "DO NOT CLOSE THIS TERMINAL WINDOW, THIS WILL KEEP ALIVE DOCKER BACKGROUND PROCESSES"
