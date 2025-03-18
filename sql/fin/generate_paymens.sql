CREATE OR REPLACE PROCEDURE public.generate_payments() AS $$
DECLARE
    payment_record RECORD;
    total_amount NUMERIC;
    remaining_amount NUMERIC;
    payment_amount INTEGER;
    payment_count INTEGER := 0;
	min_payment INTEGER := 5000;
    random_date DATE;
    start_date DATE;
    end_date DATE := CURRENT_DATE;
    days_range INTEGER;
BEGIN
    FOR payment_record IN 
        SELECT bank_account_id, person_id, case_id, amount, account_valid_from, account_valid_to FROM public.fin_publicated_data
    LOOP
		random_date := payment_record.account_valid_from;
        total_amount := payment_record.amount;
        remaining_amount := total_amount;
        
        WHILE remaining_amount > 0 LOOP
			start_date := random_date;
        	days_range := end_date - start_date;
            IF remaining_amount > min_payment THEN
                payment_amount := FLOOR(RANDOM() * remaining_amount);
            ELSE
                payment_amount := remaining_amount;
            END IF;
            
            IF payment_amount > remaining_amount OR payment_amount < min_payment THEN
                payment_amount := remaining_amount;
            END IF;
            
            random_date := start_date + (RANDOM() * days_range)::INTEGER;
            
            INSERT INTO public.payments(
                amount, 
                payment_date, 
                bank_account_id, 
                person_id, 
                case_id)
            VALUES (
                payment_amount, 
                random_date, 
                payment_record.bank_account_id, 
                payment_record.person_id, 
                payment_record.case_id
            );
            
            remaining_amount := remaining_amount - payment_amount;
            
            IF remaining_amount < 1 THEN
                EXIT;
            END IF;
            
        END LOOP;
    END LOOP;
    
END;
$$ LANGUAGE plpgsql;
