#!/bin/bash

echo "creating database structure..."
docker exec -u postgres srv1 psql -p 5432 -U cms -d cms -q -f /mnt/sql/create_db_structure_cms.sql
echo "database structure created"
