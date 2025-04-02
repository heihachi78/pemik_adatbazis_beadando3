CREATE OR REPLACE PROCEDURE public.generate_payments(
	)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
	case_record RECORD;
	calc_from DATE;
	calc_to DATE;
	interest NUMERIC;
	payment_amount NUMERIC;
	days_range INTEGER;
	c_bank_account_id INTEGER;
	c_person_id INTEGER;
	r_payment_id INTEGER;
	c_debt_amount_covered NUMERIC;
	c_interest_amount_covered NUMERIC;
	sum_interest_amount NUMERIC;
	sum_covered_interest_amount NUMERIC;
	remaining_interest_amount NUMERIC;
BEGIN
	FOR case_record IN
		select 
			c.case_id,
			c.amount,
			c.current_amount,
			c.due_date,
			d.calculated_from,
			d.calculated_to,
			d.interest_rate,
			c.current_interest_rate,
			c.current_due_date,
			c.current_interest_amount,
			d.debt_id
		from 
			cases c,
			debts d
		where 
			c.closed_at is null and 
			c.case_id = d.case_id and 
			d.open_debt = true
	LOOP
		calc_from := case_record.calculated_from;
		calc_to := case_record.calculated_to;
		days_range := least(calc_to - calc_from, 180);
		calc_to := calc_from + (RANDOM() * days_range)::INTEGER;
		interest := public.calculate_interest(case_record.current_amount, case_record.interest_rate, calc_from, calc_to);

		SELECT INTO c_bank_account_id, c_person_id p.bank_account_id , p.person_id
		FROM debtors s, account_holders p 
		WHERE s.case_id = case_record.case_id AND p.person_id = s.person_id
		ORDER BY RANDOM() LIMIT 1;

		if c_bank_account_id is null or c_person_id is null then continue; end if;

		update account_holders h set valid_from = calc_to, created_at = calc_to where h.person_id = c_person_id and h.bank_account_id = c_bank_account_id and h.valid_from > calc_to;

		update 
			debts
		set 
			calculated_to = calc_to,
			interest_rate = case_record.interest_rate,
			interest_amount = interest,
			updated_at = calc_to,
			created_at = calc_to,
			open_debt = false
		where
			debt_id = case_record.debt_id;

		select into sum_interest_amount sum(d.interest_amount) from debts d where d.case_id = case_record.case_id;
		select into sum_covered_interest_amount sum(interest_amount_covered) from payed_debts where debt_id in (select d.debt_id from debts d where d.case_id = case_record.case_id);
		remaining_interest_amount := sum_interest_amount - coalesce(sum_covered_interest_amount, 0.0);
		
		payment_amount := ((case_record.current_amount + remaining_interest_amount) * ((RANDOM() * 0.25) + 0.75));
		
		IF payment_amount < 25000 THEN
			payment_amount := (case_record.current_amount + remaining_interest_amount);
		END IF;

		INSERT INTO public.payments (
			amount, 
			payment_date, 
			bank_account_id, 
			person_id, 
			case_id,
			created_at)
		VALUES (
			payment_amount,
			calc_to,
			c_bank_account_id,
			c_person_id,
			case_record.case_id,
			calc_to
		) RETURNING payment_id INTO r_payment_id;

		IF payment_amount < remaining_interest_amount THEN
			c_interest_amount_covered := payment_amount;
			c_debt_amount_covered := 0.0;
		ELSE
			c_interest_amount_covered := remaining_interest_amount;
			c_debt_amount_covered := payment_amount - remaining_interest_amount;
		END IF;

		INSERT INTO public.payed_debts (
			debt_id,
			payment_id,
			debt_amount_covered,
			interest_amount_covered,
			created_at)
		VALUES (
			case_record.debt_id,
			r_payment_id,
			c_debt_amount_covered,
			c_interest_amount_covered,
			calc_to);

		UPDATE 
			cases c
		SET 
			current_interest_amount = remaining_interest_amount - c_interest_amount_covered,
			current_amount = current_amount - c_debt_amount_covered,
			closed_at = case when abs(current_amount - c_debt_amount_covered) < 1 then calc_to else null end,
			current_due_date = calc_to + 1,
			updated_at = calc_to
		WHERE 
			c.case_id = case_record.case_id;

	END LOOP;
END;
$BODY$;
ALTER PROCEDURE public.generate_payments()
    OWNER TO cms;
