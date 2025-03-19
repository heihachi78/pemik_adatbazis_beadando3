CREATE OR REPLACE PROCEDURE public.calculate_interest(
	IN p_case_id integer)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
	case_record RECORD;
	calc_from DATE;
	calc_to DATE;
	interest NUMERIC;
	sum_interest_amount NUMERIC;
	sum_covered_interest_amount NUMERIC;
BEGIN
	FOR case_record IN
		select 
			c.case_id,
			c.amount,
			c.current_amount,
			c.due_date,
			d.calculated_from,
			c.current_interest_rate,
			c.current_due_date,
			d.debt_id
		from 
			cases c left join 
			debts d on (c.case_id = d.case_id and d.open_debt = true and d.deleted_at is null)
		where 
			c.closed_at is null and
			c.deleted_at is null and
			c.case_id = p_case_id
	LOOP
		calc_to := CURRENT_DATE;
		calc_from := case_record.current_due_date;
		if calc_from >= calc_to then continue; end if;
		interest := public.calculate_interest(case_record.current_amount, case_record.current_interest_rate, calc_from, calc_to);

		if case_record.debt_id is not null then
			update 
				debts
			set 
				calculated_to = calc_to,
				interest_rate = case_record.current_interest_rate,
				interest_amount = interest,
				updated_at = now()
			where
				debt_id = case_record.debt_id;
		else
			insert into debts (
			    case_id,
			    calculated_from,
			    calculated_to,
			    debt_amount,
			    interest_rate,
			    interest_amount,
			    open_debt,
			    created_at)
			values (
				case_record.case_id,
			    calc_from,
			    calc_to,
			    case_record.current_amount,
			    case_record.current_interest_rate,
			    interest,
			    true,
			    now());
		end if;

		select into sum_interest_amount sum(d.interest_amount) from debts d where d.case_id = case_record.case_id;
		select into sum_covered_interest_amount sum(interest_amount_covered) from payed_debts where debt_id in (select d.debt_id from debts d where d.case_id = case_record.case_id);

		UPDATE 
			cases c
		SET 
			updated_at = now(),
			current_interest_amount = coalesce(sum_interest_amount, 0.0) - coalesce(sum_covered_interest_amount, 0.0),
			current_due_date = calc_to + 1
		WHERE 
			c.case_id = case_record.case_id;

	END LOOP;
END;
$BODY$;
ALTER PROCEDURE public.calculate_interest(integer)
    OWNER TO cms;
