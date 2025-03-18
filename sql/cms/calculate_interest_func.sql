CREATE OR REPLACE FUNCTION public.calculate_interest(
    debt NUMERIC,
    interest_rate NUMERIC,
    date_from DATE,
    date_to DATE
)
RETURNS NUMERIC AS $$
DECLARE
    days_difference INTEGER;
    annual_days INTEGER := 365;
    interest_amount NUMERIC;
BEGIN
    IF debt <= 0 THEN
        RAISE EXCEPTION 'Debt amount must be greater than zero';
    END IF;
    
    IF interest_rate < 0 THEN
        RAISE EXCEPTION 'Interest rate cannot be negative';
    END IF;
    
    IF date_from > date_to THEN
        RAISE EXCEPTION 'Start date must be before or equal to end date';
    END IF;
    
    days_difference := date_to - date_from;
    
    interest_amount := debt * interest_rate * (days_difference::NUMERIC / annual_days);
    
    RETURN ROUND(interest_amount, 3);
END;
$$ LANGUAGE plpgsql;
