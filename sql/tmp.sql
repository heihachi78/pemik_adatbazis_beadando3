create table case_history as select * from cases where 1=2;

CREATE OR REPLACE FUNCTION log_case_updates()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN
INSERT INTO public.case_history(
	case_id, purchase_id, partner_case_number, due_date, current_due_date, amount, current_amount, interest_rate, current_interest_rate, current_interest_amount, calculated_purchase_value, closed_at, created_at, updated_at, deleted_at)
	VALUES (OLD.case_id, OLD.purchase_id, OLD.partner_case_number, OLD.due_date, OLD.current_due_date, OLD.amount, OLD.current_amount, OLD.interest_rate, OLD.current_interest_rate, OLD.current_interest_amount, OLD.calculated_purchase_value, OLD.closed_at, OLD.created_at, OLD.updated_at, OLD.deleted_at);
RETURN NEW;
END;
$$

CREATE TRIGGER log_case_updates_trg
    AFTER UPDATE ON cases
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION log_case_updates();



https://www.postgresql.org/docs/current/transaction-iso.html

