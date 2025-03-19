CREATE PUBLICATION pub_fin_data 
FOR TABLE ONLY public.fin_publicated_data (
    partner_case_number, 
    account_number, 
    first_name, 
    last_name, 
    birth_name, 
    closed_at, 
    current_amount, 
    current_interest_amount, 
    overpayment, 
    last_payment_date, 
    current_due_date, 
    valid_to, 
    case_id, 
    bank_account_id, 
    person_id, 
    refreshed_at)
WITH (publish = 'insert, update, delete, truncate', publish_via_partition_root = false);
