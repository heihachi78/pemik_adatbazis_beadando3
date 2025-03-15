#!/bin/bash

./setup_python.sh
./setup_docker.sh
./setup_db.sh

unzip ${PWD}/tools/data/magyar_szavak.zip -d ${PWD}/tools/data/
unzip ${PWD}/tools/data/telepules_megye.zip -d ${PWD}/tools/data/
unzip ${PWD}/tools/data/utonevek_nem.zip -d ${PWD}/tools/data/
