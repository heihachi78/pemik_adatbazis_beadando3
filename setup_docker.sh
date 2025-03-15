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

docker network create postgresnet

docker image rm pgs
docker image rm pgp
docker build -t pgs ${PWD}/DockerPostgres
docker build -t pgp ${PWD}/DockerPgPool

docker run \
    --net postgresnet \
    --name srv1 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=pass \
    -e POSTGRES_DB=postgres \
    -e PGDATA="/mnt/data" \
    -e PGPASSFILE="/mnt/config/.pgpass" \
    -p 5431:5432 \
    -v ${PWD}/srv1/mnt/config:/mnt/config \
    -v ${PWD}/srv1/mnt/data:/mnt/data \
    -v ${PWD}/srv1/mnt/archive:/mnt/archive \
    -v ${PWD}/srv1/.ssh:/.ssh \
    -v ${PWD}/srv2/.ssh:/mnt/ssh/ \
    -v ${PWD}/sql/:/mnt/sql/ \
    -d pgs \
    -c "config_file=/mnt/config/postgresql.conf"

docker exec -u postgres srv1 bash -c "cd ~ && cp /mnt/config/.pgpass . && chmod 0600 .pgpass && chmod 0600 /mnt/config/.pgpass"

while true; do
    row_count=$(docker exec -u postgres srv1 psql -p 5432 -U postgres -d postgres -t -c "select 1" 2>/dev/null | xargs)
    if [ -n "$row_count" ]
    then
        if [ "$row_count" -gt 0 ]; then
          break
        fi
    else
        echo "waiting for srv1 to start..."
        sleep 1
    fi
done

docker exec -u postgres srv1 createuser -s repmgr
docker exec -u postgres srv1 createdb repmgr -O repmgr
docker exec -u postgres srv1 psql -p 5432 -U postgres -d postgres -t -c "alter user repmgr with password 'pass';"
docker exec -u postgres srv1 createuser -s cms
docker exec -u postgres srv1 createdb cms -O cms
docker exec -u postgres srv1 psql -p 5432 -U postgres -d postgres -t -c "alter user cms with password 'pass';"
docker exec -u postgres srv1 psql -p 5432 -U postgres -d postgres -t -c "alter user repmgr with replication;"
docker exec -u postgres srv1 ssh-keygen -q -t rsa -b 4096 -N '' -f /.ssh/id_rsa
docker exec -u postgres srv1 bash -c "cat /.ssh/id_rsa.pub >> /.ssh/authorized_keys"
docker exec -u postgres srv1 repmgr -f /mnt/config/repmgr.conf primary register
docker exec -u postgres srv1 psql -p 5432 -U postgres -d postgres -t -c "create extension pgagent;"

docker run \
    --net postgresnet \
    --name srv2 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=pass \
    -e POSTGRES_DB=postgres \
    -e PGDATA="/mnt/data_temp" \
    -e PGPASSFILE="/mnt/config/.pgpass" \
    -p 5432:5432 \
    -v ${PWD}/srv2/mnt/config:/mnt/config \
    -v ${PWD}/srv2/mnt/data_temp:/mnt/data_temp \
    -v ${PWD}/srv2/mnt/data:/mnt/data \
    -v ${PWD}/srv2/mnt/archive:/mnt/archive \
    -v ${PWD}/srv2/.ssh:/.ssh \
    -v ${PWD}/srv1/.ssh:/mnt/ssh/ \
    -d pgs \
    -c "config_file=/mnt/config/postgresql.conf"

docker exec -u postgres srv2 bash -c "cd ~ && cp /mnt/config/.pgpass . && chmod 0600 .pgpass && chmod 0600 /mnt/config/.pgpass"

while true; do
    row_count=$(docker exec srv2 psql -p 5432 -U postgres -d postgres -t -c "select 1" 2>/dev/null | xargs)
    if [ -n "$row_count" ]
    then
        if [ "$row_count" -gt 0 ]; then
          break
        fi
    else
        echo "waiting for srv2 to start..."
        sleep 1
    fi
done

docker exec -u postgres srv2 ssh-keygen -q -t rsa -b 4096 -N '' -f /.ssh/id_rsa
docker exec -u postgres srv2 bash -c "cat /.ssh/id_rsa.pub >> /.ssh/authorized_keys"
docker exec -u postgres srv1 bash -c "cat /mnt/ssh/id_rsa.pub >> /.ssh/authorized_keys"
docker exec -u postgres srv2 bash -c "cat /mnt/ssh/id_rsa.pub >> /.ssh/authorized_keys"
docker exec -u postgres srv2 repmgr -f /mnt/config/repmgr.conf -h srv1 -U repmgr -d repmgr standby clone -F -c
docker exec -u postgres srv2 /usr/lib/postgresql/17/bin/pg_ctl -D /mnt/data_temp stop

docker rm srv2
rm -rf ${PWD}/srv2/mnt/data_temp

docker run \
    --net postgresnet \
    --name srv2 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=pass \
    -e POSTGRES_DB=postgres \
    -e PGDATA="/mnt/data" \
    -e PGPASSFILE="/mnt/config/.pgpass" \
    -p 5432:5432 \
    -v ${PWD}/srv2/mnt/config:/mnt/config \
    -v ${PWD}/srv2/mnt/data:/mnt/data \
    -v ${PWD}/srv2/mnt/archive:/mnt/archive \
    -v ${PWD}/srv2/.ssh:/.ssh \
    -v ${PWD}/srv1/.ssh:/mnt/ssh/ \
    -d pgs \
    -c "config_file=/mnt/config/postgresql.conf"

docker exec -u postgres srv2 bash -c "cd ~ && cp /mnt/config/.pgpass . && chmod 0600 .pgpass && chmod 0600 /mnt/config/.pgpass"

while true; do
    row_count=$(docker exec srv2 psql -p 5432 -U postgres -d postgres -t -c "select 1" 2>/dev/null | xargs)
    if [ -n "$row_count" ]
    then
        if [ "$row_count" -gt 0 ]; then
          break
        fi
    else
        echo "waiting for srv2 to start..."
        sleep 1
    fi
done

docker exec -u postgres srv2 repmgr -f /mnt/config/repmgr.conf standby register --upstream-node-id=1
docker exec -u postgres srv1 psql -p 5432 -U postgres -d postgres -q -c "ALTER SYSTEM SET synchronous_standby_names = 'srv2';"
docker exec -u postgres srv1 psql -p 5432 -U postgres -d postgres -q -c "SELECT pg_reload_conf();"

docker exec -u postgres srv1 repmgr daemon start -f /mnt/config/repmgr.conf
docker exec -u postgres srv2 repmgr daemon start -f /mnt/config/repmgr.conf

docker run \
    --net postgresnet \
    --name pga \
    -p 8080:80 \
    -e PGADMIN_DEFAULT_EMAIL=beadando@pemik.hu \
    -e PGADMIN_DEFAULT_PASSWORD=pass \
    -v ${PWD}/pgadmin:/var/lib/pgadmin \
    -d dpage/pgadmin4

docker run \
    --net postgresnet \
    --name pgp \
    -p 5433:5432 \
    -v ${PWD}/pgpool/mnt/config/:/mnt/config \
    -d pgp

docker run \
    --net postgresnet \
    --name fin \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=pass \
    -e POSTGRES_DB=postgres \
    -e PGDATA="/mnt/data" \
    -e PGPASSFILE="/mnt/config/.pgpass" \
    -p 5434:5432 \
    -v ${PWD}/fin/mnt/config:/mnt/config \
    -v ${PWD}/fin/mnt/data:/mnt/data \
    -v ${PWD}/sql/:/mnt/sql/ \
    -d pgs \
    -c "config_file=/mnt/config/postgresql.conf"

docker exec -u postgres fin bash -c "cd ~ && cp /mnt/config/.pgpass . && chmod 0600 .pgpass && chmod 0600 /mnt/config/.pgpass"

OK=0
while [ $OK -lt 3 ]; do
    row_count=$(docker exec fin psql -p 5432 -U postgres -d postgres -t -c "select 1" 2>/dev/null | xargs)
    if [ -n "$row_count" ]
    then
        if [ "$row_count" -gt 0 ]; then
          ((OK++))
        fi
    else
        echo "waiting for fin to start..."
        sleep 1
    fi
done

docker exec -u postgres fin createuser -s fin
docker exec -u postgres fin createdb fin -O fin
docker exec -u postgres fin psql -p 5432 -U postgres -d postgres -t -c "alter user fin with password 'pass';"
docker exec -u postgres fin psql -p 5432 -U postgres -d postgres -t -c "create extension pgagent;"

SRV1_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' srv1)
SRV2_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' srv2)
FIN_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fin)
ADMIN_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' pga)
PGPOOL_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' pgp)

echo "IP ADDRESSES"
echo "srv1 : $SRV1_IP"
echo "srv2 : $SRV2_IP"
echo "fin : $FIN_IP"
echo "pgadmin : $ADMIN_IP"
echo "pgpool : $PGPOOL_IP"

echo "PORTS MAPPING"
echo "srv1 : 5432:5431"
echo "srv2 : 5432:5432"
echo "fin : 5432:5434"
echo "pgadmin : 80:8080"
echo "pgpool : 5432:5433"

echo "PASSWORDS"
echo "repmgr/pass"
echo "postgres/pass"
echo "cms/pass"
echo "fin/pass"
echo "beadando@pemik.hu/pass"
