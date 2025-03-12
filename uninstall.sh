rm -rf ${PWD}/srv1/.ssh
rm -rf ${PWD}/srv1/mnt/data
rm -rf ${PWD}/srv1/mnt/archive

rm -rf ${PWD}/srv2/.ssh
rm -rf ${PWD}/srv2/mnt/data
rm -rf ${PWD}/srv2/mnt/data_temp
rm -rf ${PWD}/srv2/mnt/archive

docker stop srv1
docker rm srv1
docker stop srv2
docker rm srv2
docker network rm postgresnet
docker image rm pspemik