DO $$
DECLARE
    jid integer;
    scid integer;
BEGIN
-- Creating a new job
INSERT INTO pgagent.pga_job(
    jobjclid, jobname, jobdesc, jobhostagent, jobenabled
) VALUES (
    4::integer, 'fin_publicated_data_job'::text, ''::text, ''::text, true
) RETURNING jobid INTO jid;

-- Steps
-- Inserting a step (jobid: NULL)
INSERT INTO pgagent.pga_jobstep (
    jstjobid, jstname, jstenabled, jstkind,
    jstconnstr, jstdbname, jstonerror,
    jstcode, jstdesc
) VALUES (
    jid, 'merge_data'::text, true, 's'::character(1),
    ''::text, 'cms'::name, 'f'::character(1),
'MERGE INTO fin_publicated_data f
USING (select b.account_number, h.valid_from, h.valid_to, b.bank_account_id, p.first_name, p.last_name, p.birth_name, p.person_id, c.partner_case_number, c.amount, c.case_id, now() as created_at, r.purchased_at, 0 as balance
from bank_accounts b, account_holders h, persons p, debtors d, cases c, purchases r
where b.bank_account_id = h.bank_account_id and h.person_id = p.person_id and p.person_id = d.person_id and d.case_id = c.case_id and c.purchase_id = r.purchase_id and 
b.deleted_at is null and h.deleted_at is null and p.deleted_at is null and d.deleted_at is null and c.deleted_at is null and r.deleted_at is null) AS t
ON f.person_id = t.person_id and f.case_id = t.case_id and f.bank_account_id = t.bank_account_id
WHEN MATCHED AND
    f.account_number != t.account_number OR 
    f.account_valid_from != t.valid_from OR 
    f.account_valid_to != t.valid_to OR 
    f.first_name != t.first_name OR 
    f.last_name != t.last_name OR 
    f.birth_name != t.birth_name OR 
    f.partner_case_number != t.partner_case_number OR
    f.amount != t.amount OR
    f.balance != t.balance OR
    f.purchased_at != t.purchased_at
 THEN
	UPDATE SET 
		account_number = t.account_number,
		account_valid_from = t.valid_from,
		account_valid_to = t.valid_to,
		first_name = t.first_name,
		last_name = t.last_name,
		birth_name = t.birth_name,
		partner_case_number = t.partner_case_number,
		amount = t.amount,
		balance = t.balance,
		purchased_at = t.purchased_at
WHEN NOT MATCHED THEN
INSERT (account_number, account_valid_from, account_valid_to, bank_account_id, first_name, last_name, birth_name, person_id, partner_case_number, amount, case_id, created_at, purchased_at, balance)
VALUES (t.account_number, t.valid_from, t.valid_to, t.bank_account_id, t.first_name, t.last_name, t.birth_name, t.person_id, t.partner_case_number, t.amount, t.case_id, now(), t.purchased_at, t.balance);'::text, ''::text
);

-- Schedules
-- Inserting a schedule
INSERT INTO pgagent.pga_schedule(
    jscjobid, jscname, jscdesc, jscenabled,
    jscstart,     jscminutes, jschours, jscweekdays, jscmonthdays, jscmonths
) VALUES (
    jid, 'fin_publicated_data_sch'::text, ''::text, true,
    '2025-03-16 17:20:00 +01:00'::timestamp with time zone, 
    -- Minutes
    '{t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f}'::bool[]::boolean[],
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