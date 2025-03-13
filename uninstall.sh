rm -rf ${PWD}/srv1/.ssh
rm -rf ${PWD}/srv1/mnt/data
rm -rf ${PWD}/srv1/mnt/archive

rm -rf ${PWD}/srv2/.ssh
rm -rf ${PWD}/srv2/mnt/data
rm -rf ${PWD}/srv2/mnt/data_temp
rm -rf ${PWD}/srv2/mnt/archive

rm -rf ${PWD}/pgadmin/azurecredentialcache
rm -rf ${PWD}/pgadmin/sessions

rm -r ${PWD}/.venv

docker stop srv1
docker rm srv1
docker stop srv2
docker rm srv2
docker stop pgadmin
docker rm pgadmin
docker network rm postgresnet
docker image rm pspemik
docker image rm dpage/pgadmin4
