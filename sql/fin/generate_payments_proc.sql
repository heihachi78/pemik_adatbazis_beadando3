CREATE OR REPLACE PROCEDURE public.generate_payments(
	)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    cms_record RECORD;
	days_range INTEGER;
	r_payment_date DATE;
	r_payment_amount NUMERIC;
	last_case_id INTEGER := 0;
BEGIN
    FOR cms_record IN 
        SELECT 
			f.partner_case_number, 
			f.account_number, 
			f.first_name, 
			f.last_name, 
			f.birth_name, 
			f.closed_at, 
			f.current_amount, 
			f.current_interest_amount, 
			f.overpayment, 
			f.last_payment_date, 
			f.current_due_date, 
			f.valid_to, 
			f.case_id, 
			f.bank_account_id, 
			f.person_id, 
			f.refreshed_at 
		FROM 
			public.fin_publicated_data f
		WHERE
			not exists (select 1 from payments p where p.created_at > f.refreshed_at and p.case_id = f.case_id) and
			f.closed_at is null and
			f.overpayment = 0
		ORDER BY
			f.case_id
    LOOP
		if RANDOM() < 0.4 then continue; end if;
		if last_case_id = cms_record.case_id then continue; end if;
		days_range := least((cms_record.current_due_date - cms_record.last_payment_date) - 2, 60);
		if days_range < 3 or then continue; end if;
		r_payment_date := cms_record.last_payment_date + 2 + (RANDOM() * days_range)::INTEGER;
		if r_payment_date > CURRENT_DATE then continue; end if;
		if r_payment_date <= cms_record.last_payment_date then continue; end if;
		days_range := r_payment_date - cms_record.last_payment_date;
		if days_range < 1 then continue; end if;
		r_payment_amount := (cms_record.current_amount + (cms_record.current_interest_amount * ((r_payment_date - cms_record.last_payment_date) / (cms_record.current_due_date - cms_record.last_payment_date)))) * ((RANDOM() * 0.5) + 0.5);
		if cms_record.current_amount < 5000 then
			r_payment_amount := cms_record.current_amount + (cms_record.current_interest_amount * ((r_payment_date - cms_record.last_payment_date + 1) / (cms_record.current_due_date - cms_record.last_payment_date)));
		end if;
		INSERT INTO public.payments(
			amount, 
			payment_date, 
			bank_account_id, 
			person_id, 
			case_id, 
			created_at, 
			updated_at, 
			deleted_at)
		VALUES (
			r_payment_amount, 
			r_payment_date, 
			cms_record.bank_account_id, 
			cms_record.person_id, 
			cms_record.case_id, 
			now(), 
			null, 
			null
		);
		last_case_id := cms_record.case_id;
    END LOOP;
    
END;
$BODY$;
