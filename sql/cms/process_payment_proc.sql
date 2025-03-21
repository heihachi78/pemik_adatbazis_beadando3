CREATE OR REPLACE PROCEDURE public.process_payment(
	IN p_payment_id integer)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
	payment_record RECORD;
	calc_from DATE;
	calc_to DATE;
	interest NUMERIC;
	sum_interest_amount NUMERIC;
	sum_covered_interest_amount NUMERIC;
	remaining_interest_amount NUMERIC;
	c_debt_amount_covered NUMERIC;
	c_interest_amount_covered NUMERIC;
BEGIN
	FOR payment_record IN
		select 
			p.payment_id, 
			p.amount, 
			p.bank_account_id, 
			p.person_id, 
			p.case_id, 
			d.debt_id, 
			d.calculated_from,
			d.calculated_to,
			p.payment_date, 
			c.current_amount,
			c.current_interest_rate
		from 
			payments p,
			cases c,
			bank_accounts b,
			debts d
		where 
			p.payment_id = p_payment_id and
			p.deleted_at is null and
			p.payment_id = p.payment_id and 
			c.case_id = p.case_id and
			c.deleted_at is null and
			c.closed_at is null and
			b.bank_account_id = p.bank_account_id and
			b.deleted_at is null and
			d.case_id = c.case_id and
			d.deleted_at is null and
			d.open_debt = true and
			p.payment_date > d.calculated_from
		order by 
			p.created_at asc,
			p.payment_date asc
	LOOP
		calc_from := payment_record.calculated_from;
		calc_to := payment_record.payment_date;
		interest := public.calculate_interest(payment_record.current_amount, payment_record.current_interest_rate, calc_from, calc_to);

		update 
			debts
		set 
			calculated_to = calc_to,
			interest_rate = payment_record.current_interest_rate,
			interest_amount = interest,
			updated_at = now(),
			created_at = calc_to,
			open_debt = false
		where
			debt_id = payment_record.debt_id;

		select into sum_interest_amount sum(d.interest_amount) from debts d where d.case_id = payment_record.case_id;
		select into sum_covered_interest_amount sum(interest_amount_covered) from payed_debts where debt_id in (select d.debt_id from debts d where d.case_id = payment_record.case_id);
		remaining_interest_amount := sum_interest_amount - coalesce(sum_covered_interest_amount, 0.0);

		IF payment_record.amount < remaining_interest_amount THEN
			c_interest_amount_covered := payment_record.amount;
			c_debt_amount_covered := 0.0;
		ELSE
			c_interest_amount_covered := remaining_interest_amount;
			c_debt_amount_covered := least(payment_record.amount - remaining_interest_amount, payment_record.current_amount);
		END IF;

		INSERT INTO public.payed_debts (
			debt_id,
			payment_id,
			debt_amount_covered,
			interest_amount_covered,
			overpayment,
			created_at)
		VALUES (
			payment_record.debt_id,
			p_payment_id,
			c_debt_amount_covered,
			c_interest_amount_covered,
			GREATEST(payment_record.amount - remaining_interest_amount - payment_record.current_amount, 0),
			now());

		UPDATE 
			cases c
		SET 
			current_interest_amount = remaining_interest_amount - c_interest_amount_covered,
			current_amount = current_amount - c_debt_amount_covered,
			closed_at = case when abs(current_amount - c_debt_amount_covered) < 1 then calc_to else null end,
			updated_at = calc_to,
			current_due_date = calc_to + 1
		WHERE 
			c.case_id = payment_record.case_id;

		CALL calculate_interest_for_case(payment_record.case_id);

END LOOP;
END;
$BODY$;
ALTER PROCEDURE public.process_payment(integer)
    OWNER TO cms;
