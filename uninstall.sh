#!/bin/bash

rm -rf ${PWD}/srv1/.ssh
rm -rf ${PWD}/srv1/mnt/data
rm -rf ${PWD}/srv1/mnt/archive

rm -rf ${PWD}/srv2/.ssh
rm -rf ${PWD}/srv2/mnt/data
rm -rf ${PWD}/srv2/mnt/data_temp
rm -rf ${PWD}/srv2/mnt/archive

rm -rf ${PWD}/fin/mnt/data

rm -rf ${PWD}/pgadmin/azurecredentialcache
rm -rf ${PWD}/pgadmin/sessions

#rm -r ${PWD}/.venv

docker stop srv1
docker rm srv1
docker stop srv2
docker rm srv2
docker stop pga
docker rm pga
docker stop pgp
docker rm pgp
docker stop fin
docker rm fin
docker network rm postgresnet
docker image rm pgs
docker image rm pgp
#docker image rm dpage/pgadmin4

rm -rf ${PWD}/tools/data/telepules_megye.csv
rm -rf ${PWD}/tools/data/utonevek_nem.csv
rm -rf ${PWD}/tools/data/magyar_szavak.csv
