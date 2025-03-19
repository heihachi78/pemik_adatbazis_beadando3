DO $$
DECLARE
    jid integer;
    scid integer;
BEGIN

INSERT INTO pgagent.pga_job(
    jobjclid, jobname, jobdesc, jobhostagent, jobenabled
) VALUES (
    1::integer, 'process_new_payments_job'::text, ''::text, ''::text, true
) RETURNING jobid INTO jid;

INSERT INTO pgagent.pga_jobstep (
    jstjobid, jstname, jstenabled, jstkind,
    jstconnstr, jstdbname, jstonerror,
    jstcode, jstdesc
) VALUES (
    jid, 'process'::text, true, 's'::character(1),
    ''::text, 'cms'::name, 'f'::character(1),
    'call public.process_new_payments();'::text, ''::text
) ;

INSERT INTO pgagent.pga_schedule(
    jscjobid, jscname, jscdesc, jscenabled,
    jscstart,     jscminutes, jschours, jscweekdays, jscmonthdays, jscmonths
) VALUES (
    jid, 'process_new_payments_sch'::text, ''::text, true,
    '2025-03-19 16:05:00 +01:00'::timestamp with time zone, 
    -- Minutes
    '{t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f,t,f}'::bool[]::boolean[],
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