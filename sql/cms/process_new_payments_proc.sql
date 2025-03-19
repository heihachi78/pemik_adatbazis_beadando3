CREATE OR REPLACE PROCEDURE public.process_new_payments()
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
	payment_record RECORD;
BEGIN
	FOR payment_record IN
		select 
			p.payment_id
		from 
			payments p
		where
			not exists (select 1 from payed_debts d where d.payment_id = p.payment_id)
		order by 
			p.created_at asc,
			p.payment_date asc,
			p.payment_id asc
	LOOP
		call process_payment(payment_record.payment_id);
	END LOOP;
END;
$BODY$;