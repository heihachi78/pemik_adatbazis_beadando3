DO $$
DECLARE
    jid integer;
    scid integer;
BEGIN

INSERT INTO pgagent.pga_job(
    jobjclid, jobname, jobdesc, jobhostagent, jobenabled
) VALUES (
    5::integer, 'generate_payments'::text, ''::text, ''::text, true
) RETURNING jobid INTO jid;

INSERT INTO pgagent.pga_jobstep (
    jstjobid, jstname, jstenabled, jstkind,
    jstconnstr, jstdbname, jstonerror,
    jstcode, jstdesc
) VALUES (
    jid, 'generate_data'::text, true, 's'::character(1),
    ''::text, 'fin'::name, 'f'::character(1),
    'call public.generate_payments();'::text, ''::text
) ;

INSERT INTO pgagent.pga_schedule(
    jscjobid, jscname, jscdesc, jscenabled,
    jscstart,     jscminutes, jschours, jscweekdays, jscmonthdays, jscmonths
) VALUES (
    jid, 'generate_payments_sch'::text, ''::text, true,
    '2025-03-17 17:25:00 +01:00'::timestamp with time zone, 
    -- Minutes
    '{f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t,f,f,t}'::bool[]::boolean[],
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
