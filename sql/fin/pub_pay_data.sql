CREATE PUBLICATION pub_pay_data 
FOR TABLE ONLY public.payments (
	payment_id, 
	amount, 
	payment_date, 
	bank_account_id, 
	person_id, 
	case_id, 
	created_at, 
	updated_at, 
	deleted_at
)
WITH (publish = 'insert, update, delete, truncate', publish_via_partition_root = false);
