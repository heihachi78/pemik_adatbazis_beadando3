DO $$
DECLARE
    jid integer;
    scid integer;
BEGIN

INSERT INTO pgagent.pga_job(
    jobjclid, jobname, jobdesc, jobhostagent, jobenabled
) VALUES (
    4::integer, 'fin_publicated_data_job'::text, ''::text, ''::text, true
) RETURNING jobid INTO jid;

INSERT INTO pgagent.pga_jobstep (
    jstjobid, jstname, jstenabled, jstkind,
    jstconnstr, jstdbname, jstonerror,
    jstcode, jstdesc
) VALUES (
    jid, 'merge_data'::text, true, 's'::character(1),
    ''::text, 'cms'::name, 'f'::character(1),
'MERGE INTO fin_publicated_data f
USING (select * from fin_publicated_data_v) AS t
ON f.person_id = t.person_id and f.case_id = t.case_id and f.bank_account_id = t.bank_account_id
WHEN MATCHED AND
	(f.partner_case_number != t.partner_case_number OR 
	f.account_number != t.account_number OR 
    f.first_name != t.first_name OR 
    f.last_name != t.last_name OR 
    f.birth_name != t.birth_name OR 
	coalesce(f.closed_at, CURRENT_DATE) != coalesce(t.closed_at, CURRENT_DATE) OR 
	f.current_amount != t.current_amount OR 
	f.current_interest_amount != t.current_interest_amount OR 
	f.overpayment != t.overpayment OR 
	coalesce(f.last_payment_date, CURRENT_DATE) != coalesce(t.last_payment_date, CURRENT_DATE) OR 
	f.current_due_date != t.current_due_date OR 
	coalesce(f.valid_to, CURRENT_DATE) != coalesce(t.valid_to, CURRENT_DATE))
 THEN
	UPDATE SET 
		partner_case_number = t.partner_case_number,
		account_number = t.account_number,
	    first_name = t.first_name,
	    last_name = t.last_name, 
	    birth_name = t.birth_name,
		closed_at = t.closed_at, 
		current_amount = t.current_amount,
		current_interest_amount = t.current_interest_amount,
		overpayment = t.overpayment,
		last_payment_date = t.last_payment_date,
		current_due_date = t.current_due_date, 
		valid_to = t.valid_to,
		refreshed_at = now()
WHEN NOT MATCHED THEN
	INSERT (
		partner_case_number, 
		account_number, 
		first_name, 
		last_name, 
		birth_name, 
		closed_at, 
		current_amount, 
		current_interest_amount, 
		overpayment, 
		last_payment_date, 
		current_due_date, 
		valid_to, 
		case_id, 
		bank_account_id, 
		person_id, 
		refreshed_at)
	VALUES (
		t.partner_case_number, 
		t.account_number, 
		t.first_name, 
		t.last_name, 
		t.birth_name, 
		t.closed_at, 
		t.current_amount, 
		t.current_interest_amount, 
		t.overpayment, 
		t.last_payment_date, 
		t.current_due_date, 
		t.valid_to, 
		t.case_id, 
		t.bank_account_id, 
		t.person_id, 
		now());'::text, ''::text
);

INSERT INTO pgagent.pga_schedule(
    jscjobid, jscname, jscdesc, jscenabled,
    jscstart,     jscminutes, jschours, jscweekdays, jscmonthdays, jscmonths
) VALUES (
    jid, 'fin_publicated_data_sch'::text, ''::text, true,
    '2025-03-16 17:20:00 +01:00'::timestamp with time zone, 
    -- Minutes
    '{f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f}'::bool[]::boolean[],
    -- Hours
    '{t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t}'::bool[]::boolean[],
    -- Week days
    '{t,t,t,t,t,t,t}'::bool[]::boolean[],
    -- Month days
    '{t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t}'::bool[]::boolean[],
    -- Months
    '{t,t,t,t,t,t,t,t,t,t,t,t}'::bool[]::boolean[]
) RETURNING jscid INTO scid;
END
$$;