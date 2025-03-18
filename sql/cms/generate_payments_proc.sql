CREATE OR REPLACE PROCEDURE public.generate_payments() AS $$
DECLARE
	case_record RECORD;
	calculated_from DATE;
	calculated_to DATE;
	end_date DATE := CURRENT_DATE;
	days_range INTEGER;
	interest NUMERIC;
	current_balance NUMERIC;
	payment_amount INTEGER;
	bank_account_id INTEGER;
	person_id INTEGER;
	remaining_amount NUMERIC;
	r_debt_id INTEGER;
	r_payment_id INTEGER;
	debt_amount_covered NUMERIC;
	interest_amount_covered NUMERIC;
BEGIN
	FOR case_record IN
		select
			c.case_id,
			c.amount, 
			c.due_date,
			c.interest_rate,
			c.amount - sum(t.debt_amount_covered) as amount_not_covered, 
			coalesce(sum(d.interest_value) - sum(t.interest_amount_covered), 0) as interest_not_covered, 
			max(d.calculated_to) as last_calculation
		from cases c 
			left join debts d on c.case_id = d.case_id 
			left join debt_coverages t on d.debt_id = t.debt_id
		where
			c.closed_at is null
		group by 
			c.case_id,
			c.amount
	LOOP
		calculated_from := coalesce(case_record.last_calculation + 1, case_record.due_date);
		days_range := end_date - calculated_from;
		calculated_to := calculated_from + (RANDOM() * days_range)::INTEGER;
		current_balance := coalesce(case_record.amount_not_covered, case_record.amount);
		IF current_balance > 1 THEN
			IF calculated_from >= calculated_to THEN CONTINUE; END IF;
			interest := public.calculate_interest(current_balance, case_record.interest_rate, calculated_from, calculated_to);
	        remaining_amount := current_balance + interest + case_record.interest_not_covered;

			SELECT INTO bank_account_id, person_id p.bank_account_id , p.person_id
			FROM debtors s, account_holders p 
			WHERE s.case_id = case_record.case_id AND p.person_id = s.person_id AND p.valid_from <= calculated_to
			ORDER BY RANDOM() LIMIT 1;

			IF bank_account_id IS NULL THEN
				CONTINUE;
			END IF;

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
	    		calculated_from,
	    		calculated_to,
	    		current_balance,
	    		case_record.interest_rate,
	    		interest,
				case_record.interest_not_covered,
				calculated_to
			) RETURNING debt_id into r_debt_id;

			IF remaining_amount > case_record.amount * 0.2 THEN
				payment_amount := FLOOR(((RANDOM() * 0.8) + 0.2) * remaining_amount);
			ELSE
				payment_amount := remaining_amount;
			END IF;
	
			IF payment_amount > (interest + case_record.interest_not_covered) THEN
				interest_amount_covered := (interest + case_record.interest_not_covered);
				debt_amount_covered := least(payment_amount - (interest + case_record.interest_not_covered), current_balance);
			ELSE
				interest_amount_covered := payment_amount;
				debt_amount_covered := 0;
			END IF;

			INSERT INTO public.payments (
				amount, 
				payment_date, 
				bank_account_id, 
				person_id, 
				case_id,
				created_at
			)
			VALUES (
				payment_amount,
				calculated_to,
				bank_account_id,
				person_id,
				case_record.case_id,
				calculated_to
			) RETURNING payment_id INTO r_payment_id;
	
			INSERT INTO public.debt_coverages (
			    debt_id,
			    payment_id,
			    debt_amount_covered,
			    interest_amount_covered,
				created_at
			)
			VALUES (
			    r_debt_id,
			    r_payment_id,
			    debt_amount_covered,
			    interest_amount_covered,
				calculated_to
			);

			IF (remaining_amount - payment_amount) < 1 THEN
				UPDATE cases SET closed_at = calculated_to WHERE case_id = case_record.case_id;
			END IF;
		END IF;
	END LOOP;
END;
$$ LANGUAGE plpgsql;
