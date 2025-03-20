#!/bin/bash

unzip ${PWD}/tools/data/magyar_szavak.zip -d ${PWD}/tools/data/
unzip ${PWD}/tools/data/telepules_megye.zip -d ${PWD}/tools/data/
unzip ${PWD}/tools/data/utonevek_nem.zip -d ${PWD}/tools/data/

source .venv/bin/activate
#python3 tools/generate_initial_data.py
#docker exec -u postgres srv1 pg_dump -a -d cms -n public -f /mnt/sql/cms/db_cms.sql
#docker exec -u postgres fin pg_dump -a -d fin -n public -f /mnt/sql/fin/db_fin.sql

docker exec -u postgres srv1 psql -X -d cms -f /mnt/sql/cms/db_cms.sql
docker exec -u postgres fin psql -X -d fin -f /mnt/sql/fin/db_fin.sql
