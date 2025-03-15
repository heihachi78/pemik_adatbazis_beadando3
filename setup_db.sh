#!/bin/bash

echo "creating database structure in cms..."
docker exec -u postgres srv1 psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/create_db_structure_cms.sql
echo "database structure created"

echo "creating database structure in fin..."
docker exec -u postgres fin psql -p 5432 -U fin -d fin -q -f /mnt/sql/fin/create_db_structure_fin.sql
echo "database structure created"

docker exec -u postgres srv1 psql -p 5432 -U cms -d cms -t -c "CREATE PUBLICATION pub_test FOR TABLE ONLY public.test (n) WITH (publish = 'insert, update, delete, truncate', publish_via_partition_root = false);"
docker exec -u postgres fin psql -p 5432 -U fin -d fin -t -c "CREATE SUBSCRIPTION sub_test CONNECTION 'host=srv1 port=5432 user=cms dbname=cms connect_timeout=10 sslmode=prefer' PUBLICATION pub_test WITH (connect = true, enabled = true, copy_data = true, create_slot = true, synchronous_commit = 'off', binary = false, streaming = 'False', two_phase = false, disable_on_error = false, run_as_owner = false, password_required = true, origin = 'any');"
