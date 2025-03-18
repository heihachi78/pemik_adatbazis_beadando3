#!/bin/bash

echo "creating database structure in cms..."
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/create_db_structure_cms.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/fin_publicated_data_job.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/calculate_interest_func.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/generate_payments_proc.sql
echo "database structure created"

echo "creating database structure in fin..."
docker exec -u postgres fin psql -p 5432 -U fin -d fin -q -f /mnt/sql/fin/create_db_structure_fin.sql
docker exec -u postgres fin psql -p 5432 -U fin -d fin -q -f /mnt/sql/fin/generate_payments_proc.sql
#docker exec -u postgres fin psql -p 5432 -U fin -d fin -q -f /mnt/sql/fin/generate_payments_job.sql
echo "database structure created"

docker exec -u postgres pgp psql -p 5432 -U cms -d cms -t -c "CREATE PUBLICATION pub_fin_data FOR TABLE ONLY public.fin_publicated_data (account_number, account_valid_from, account_valid_to, bank_account_id, first_name, last_name, birth_name, person_id, partner_case_number, amount, balance, purchased_at, case_id, created_at) WITH (publish = 'insert, update, delete, truncate', publish_via_partition_root = false);"
docker exec -u postgres fin psql -p 5432 -U fin -d fin -t -c "CREATE SUBSCRIPTION sub_fin_data CONNECTION 'host=pgp port=5432 user=cms dbname=cms connect_timeout=10 sslmode=prefer' PUBLICATION pub_fin_data WITH (connect = true, enabled = true, copy_data = true, create_slot = true, synchronous_commit = 'off', binary = false, streaming = 'False', two_phase = false, disable_on_error = false, run_as_owner = false, password_required = true, origin = 'any');"
