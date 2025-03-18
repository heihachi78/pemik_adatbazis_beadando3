CREATE OR REPLACE PROCEDURE public.calculate_interest() AS $$
DECLARE
	case_record RECORD;
	calc_from DATE;
	calc_to DATE;
	end_date DATE := CURRENT_DATE;
	interest NUMERIC;
	curr_balance NUMERIC;
	remaining_amount NUMERIC;
BEGIN
	FOR case_record IN
		select
			c.case_id,
			c.amount, 
			c.due_date,
			c.interest_rate,
			c.amount - sum(t.debt_amount_covered) as amount_not_covered, 
			coalesce(sum(d.interest_value) - sum(t.interest_amount_covered), 0) as interest_not_covered, 
			max(d.calculated_from) as last_calculated_from,
			max(d.calculated_to) as last_calculated_to,
			max(d.debt_id) as last_debt_record,
			max(t.debt_id) as last_coverage_record
		from cases c 
			left join debts d on c.case_id = d.case_id 
			left join debt_coverages t on d.debt_id = t.debt_id
		where
			c.closed_at is null and c.deleted_at is null and d.deleted_at is null and t.deleted_at is null
		group by 
			c.case_id,
			c.amount
	LOOP
		IF case_record.last_coverage_record = case_record.last_debt_record THEN
			calc_from := coalesce(case_record.last_calculated_to + 1, case_record.due_date);
		ELSE
			calc_from := coalesce(case_record.last_calculated_from, case_record.due_date);
		END IF;
		
		calc_to := end_date;
		curr_balance := coalesce(case_record.amount_not_covered, case_record.amount);
		IF curr_balance > 1 THEN
			IF calc_from > calc_to THEN CONTINUE; END IF;
			interest := public.calculate_interest(curr_balance, case_record.interest_rate, calc_from, calc_to);
	        remaining_amount := curr_balance + interest + case_record.interest_not_covered;

			IF case_record.last_debt_record IS NULL OR (case_record.last_coverage_record = case_record.last_debt_record) THEN 

				INSERT INTO public.debts (
		    		case_id,
		    		calculated_from,
		    		calculated_to,
		    		debt_amount,
		    		interest_rate,
		    		interest_value,
					unsecured_interest_value,
					created_at
				)
				VALUES (
					case_record.case_id,
		    		calc_from,
		    		calc_to,
		    		curr_balance,
		    		case_record.interest_rate,
		    		interest,
					case_record.interest_not_covered,
					now()
				);
			ELSE
				UPDATE 
					debts 
				SET 
					calculated_from = calc_from, 
					calculated_to = calc_to, 
					debt_amount = curr_balance,
					interest_rate = case_record.interest_rate,
					interest_value = interest,
					updated_at = NOW()
				WHERE 
					debt_id = case_record.last_debt_record AND 
					case_id = case_record.case_id;
			END IF;

		END IF;
	END LOOP;
END;
$$ LANGUAGE plpgsql;
