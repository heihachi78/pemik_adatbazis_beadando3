BEGIN;

CREATE TABLE IF NOT EXISTS public.fin_publicated_data
(
    partner_case_number character varying(100) COLLATE pg_catalog."default",
    account_number character(26) COLLATE pg_catalog."default",
    first_name character varying(100) COLLATE pg_catalog."default",
    last_name character varying(100) COLLATE pg_catalog."default",
    birth_name character varying(150) COLLATE pg_catalog."default",
    closed_at timestamp with time zone,
    current_amount numeric(16, 3),
    current_interest_amount numeric(16, 3),
    overpayment numeric,
    last_payment_date date,
    current_due_date date,
    valid_to date,
    case_id integer,
    bank_account_id integer,
    person_id integer,
    refreshed_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT fin_publicated_data_pkey PRIMARY KEY (bank_account_id, person_id, case_id),
    CONSTRAINT fin_publicated_data_ukey UNIQUE (case_id, bank_account_id, person_id)
);

CREATE TABLE IF NOT EXISTS public.payments
(
    payment_id serial NOT NULL,
    amount integer NOT NULL,
    payment_date date NOT NULL,
    bank_account_id integer NOT NULL,
    person_id integer NOT NULL,
    case_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT payments_pkey PRIMARY KEY (payment_id)
);

CREATE TABLE IF NOT EXISTS public.test
(
    test_id serial NOT NULL,
    n integer NOT NULL,
    CONSTRAINT test_pkey PRIMARY KEY (test_id)
);

SELECT setval('public.payments_payment_id_seq', 1000000000, false);

ALTER SEQUENCE IF EXISTS public.payments_payment_id_seq
    START 1000000000
	MINVALUE 1000000000;

END;
