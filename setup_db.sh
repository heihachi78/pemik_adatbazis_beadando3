#!/bin/bash

echo "creating database structure in cms..."
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/create_db_structure_cms.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/fin_publicated_data_job.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/calculate_interest_func.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/generate_payments_proc.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/calculate_interest_all_proc.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/calculate_interest_for_case_proc.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/process_payment_proc.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/process_new_payments_proc.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/process_new_payments_job.sql
echo "database structure created"

echo "creating database structure in fin..."
docker exec -u postgres fin psql -p 5432 -U fin -d fin -q -f /mnt/sql/fin/create_db_structure_fin.sql
docker exec -u postgres fin psql -p 5432 -U fin -d fin -q -f /mnt/sql/fin/generate_payments_proc.sql
docker exec -u postgres fin psql -p 5432 -U fin -d fin -q -f /mnt/sql/fin/generate_payments_job.sql
echo "database structure created"

echo "creating publications and subscriptions..."
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/pub_fin_data.sql
docker exec -u postgres fin psql -p 5432 -U fin -d fin -q -f /mnt/sql/fin/pub_pay_data.sql

docker exec -u postgres fin psql -p 5432 -U fin -d fin -q -f /mnt/sql/fin/sub_fin_data.sql
docker exec -u postgres pgp psql -p 5432 -U cms -d cms -q -f /mnt/sql/cms/sub_pay_data.sql
echo "pubs and subs are created"
