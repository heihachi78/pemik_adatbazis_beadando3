CREATE SUBSCRIPTION sub_fin_data 
CONNECTION 'host=pgp port=5432 user=cms dbname=cms passfile=/mnt/config/.pgpass connect_timeout=10 sslmode=prefer' 
PUBLICATION pub_fin_data 
WITH (
    connect = true, 
    enabled = true, 
    copy_data = true, 
    create_slot = true, 
    synchronous_commit = 'off', 
    binary = false, 
    streaming = 'False', 
    two_phase = false, 
    disable_on_error = false, 
    run_as_owner = false, 
    password_required = true, 
    origin = 'any');
