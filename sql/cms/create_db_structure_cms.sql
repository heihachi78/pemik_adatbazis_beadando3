BEGIN;


CREATE TABLE IF NOT EXISTS public.cases
(
    case_id serial NOT NULL,
    purchase_id integer NOT NULL,
    partner_case_number character varying(100) COLLATE pg_catalog."default",
    due_date date NOT NULL,
    current_due_date date NOT NULL,
    amount numeric(16, 3) NOT NULL,
    current_amount numeric(16, 3) NOT NULL,
    interest_rate numeric(6, 3) NOT NULL,
    current_interest_rate numeric(6, 3) NOT NULL,
    current_interest_amount numeric(16, 3) NOT NULL,
    calculated_purchase_value numeric(16, 3),
    closed_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT case_pkey PRIMARY KEY (case_id)
);

CREATE TABLE IF NOT EXISTS public.cities
(
    city_id serial NOT NULL,
    name character varying(200) COLLATE pg_catalog."default" NOT NULL,
    region_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT cities_pkey PRIMARY KEY (city_id)
);

CREATE TABLE IF NOT EXISTS public.debtor_types
(
    debtor_type_id serial NOT NULL,
    name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT debtor_type_pkey PRIMARY KEY (debtor_type_id)
);

CREATE TABLE IF NOT EXISTS public.debtors
(
    debtor_id serial NOT NULL,
    case_id integer NOT NULL,
    person_id integer NOT NULL,
    debtor_type_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT debtor_pkey PRIMARY KEY (debtor_id),
    CONSTRAINT debtor_debtor_type_ukey UNIQUE (case_id, debtor_type_id, person_id)
);

CREATE TABLE IF NOT EXISTS public.genders
(
    gender_id serial NOT NULL,
    name character varying(10) NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT genders_pkey PRIMARY KEY (gender_id)
);

CREATE TABLE IF NOT EXISTS public.partners
(
    partner_id serial NOT NULL,
    name character varying(200) COLLATE pg_catalog."default" NOT NULL,
    sector_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT partners_pkey PRIMARY KEY (partner_id)
);

CREATE TABLE IF NOT EXISTS public.persons
(
    person_id serial NOT NULL,
    first_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    last_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    birth_place_city_id integer NOT NULL,
    birth_date date NOT NULL,
    birth_name character varying(150) COLLATE pg_catalog."default",
    mother_name character varying(150) COLLATE pg_catalog."default" NOT NULL,
    death_date date,
    gender_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT persons_pkey PRIMARY KEY (person_id)
);

CREATE TABLE IF NOT EXISTS public.purchases
(
    purchase_id serial NOT NULL,
    partner_id integer NOT NULL,
    batch_number character varying(50) COLLATE pg_catalog."default" NOT NULL,
    purchased_at date NOT NULL,
    batch_purchase_value integer NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT purchases_pkey PRIMARY KEY (purchase_id)
);

CREATE TABLE IF NOT EXISTS public.regions
(
    region_id serial NOT NULL,
    name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT regions_pkey PRIMARY KEY (region_id)
);

CREATE TABLE IF NOT EXISTS public.sectors
(
    sector_id serial NOT NULL,
    name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT sectors_pkey PRIMARY KEY (sector_id)
);

CREATE TABLE IF NOT EXISTS public.test
(
    test_id serial NOT NULL,
    n integer NOT NULL,
    CONSTRAINT test_pkey PRIMARY KEY (test_id)
);

CREATE TABLE IF NOT EXISTS public.bank_accounts
(
    bank_account_id serial NOT NULL,
    account_number character(26) NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT bank_accounts_pkey PRIMARY KEY (bank_account_id)
);

CREATE TABLE IF NOT EXISTS public.account_holders
(
    account_holder_id serial NOT NULL,
    person_id integer NOT NULL,
    bank_account_id integer NOT NULL,
    valid_from date NOT NULL,
    valid_to date,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT account_holders_pkey PRIMARY KEY (account_holder_id),
    CONSTRAINT person_bank_account_ukey UNIQUE (person_id, bank_account_id)
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

CREATE TABLE IF NOT EXISTS public.debts
(
    debt_id serial NOT NULL,
    case_id integer NOT NULL,
    calculated_from date NOT NULL,
    calculated_to date NOT NULL,
    debt_amount numeric(16, 3) NOT NULL,
    interest_rate numeric(6, 3) NOT NULL,
    interest_amount numeric(16, 3) NOT NULL,
    open_debt boolean NOT NULL DEFAULT false,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT debts_pkey PRIMARY KEY (debt_id)
);

CREATE TABLE IF NOT EXISTS public.payed_debts
(
    payed_debt_id serial NOT NULL,
    debt_id integer NOT NULL,
    payment_id integer NOT NULL,
    debt_amount_covered numeric(16, 3) NOT NULL,
    interest_amount_covered numeric(16, 3) NOT NULL,
    overpayment numeric(16, 3) NOT NULL DEFAULT 0,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    CONSTRAINT payed_debts_pkey PRIMARY KEY (payed_debt_id)
);

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

ALTER TABLE IF EXISTS public.cases
    ADD CONSTRAINT case_purchase_fkey FOREIGN KEY (purchase_id)
    REFERENCES public.purchases (purchase_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_case_purchase_fkey
    ON public.cases(purchase_id);


ALTER TABLE IF EXISTS public.cities
    ADD CONSTRAINT city_region_fkey FOREIGN KEY (region_id)
    REFERENCES public.regions (region_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_city_region_fkey
    ON public.cities(region_id);


ALTER TABLE IF EXISTS public.debtors
    ADD CONSTRAINT debtor_case_fkey FOREIGN KEY (case_id)
    REFERENCES public.cases (case_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_debtor_case_fkey
    ON public.debtors(case_id);


ALTER TABLE IF EXISTS public.debtors
    ADD CONSTRAINT debtor_debtor_type_fkey FOREIGN KEY (debtor_type_id)
    REFERENCES public.debtor_types (debtor_type_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_debtor_debtor_type_fkey
    ON public.debtors(debtor_type_id);


ALTER TABLE IF EXISTS public.debtors
    ADD CONSTRAINT debtor_person_fkey FOREIGN KEY (person_id)
    REFERENCES public.persons (person_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_debtor_person_fkey
    ON public.debtors(person_id);


ALTER TABLE IF EXISTS public.partners
    ADD CONSTRAINT parner_sector_fkey FOREIGN KEY (sector_id)
    REFERENCES public.sectors (sector_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_fk_parner_sector
    ON public.partners(sector_id);


ALTER TABLE IF EXISTS public.persons
    ADD CONSTRAINT person_birth_city_fkey FOREIGN KEY (birth_place_city_id)
    REFERENCES public.cities (city_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_person_birth_city_fkey
    ON public.persons(birth_place_city_id);


ALTER TABLE IF EXISTS public.persons
    ADD CONSTRAINT person_gender_fkey FOREIGN KEY (gender_id)
    REFERENCES public.genders (gender_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_person_gender_fkey
    ON public.persons(gender_id);


ALTER TABLE IF EXISTS public.purchases
    ADD CONSTRAINT purchase_partner_fkey FOREIGN KEY (partner_id)
    REFERENCES public.partners (partner_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_fk_purchase_partner
    ON public.purchases(partner_id);


ALTER TABLE IF EXISTS public.account_holders
    ADD CONSTRAINT person_fkey FOREIGN KEY (person_id)
    REFERENCES public.persons (person_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_person_fkey
    ON public.account_holders(person_id);


ALTER TABLE IF EXISTS public.account_holders
    ADD CONSTRAINT bank_account_fkey FOREIGN KEY (bank_account_id)
    REFERENCES public.bank_accounts (bank_account_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_bank_account_fkey
    ON public.account_holders(bank_account_id);


ALTER TABLE IF EXISTS public.payments
    ADD CONSTRAINT payment_person_fkey FOREIGN KEY (person_id)
    REFERENCES public.persons (person_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_payment_person_fkey
    ON public.payments(person_id);


ALTER TABLE IF EXISTS public.payments
    ADD CONSTRAINT payment_bank_account_fkey FOREIGN KEY (bank_account_id)
    REFERENCES public.bank_accounts (bank_account_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_payment_bank_account_fkey
    ON public.payments(bank_account_id);


ALTER TABLE IF EXISTS public.payments
    ADD CONSTRAINT payment_case_fkey FOREIGN KEY (case_id)
    REFERENCES public.cases (case_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_payment_case_fkey
    ON public.payments(case_id);


ALTER TABLE IF EXISTS public.debts
    ADD CONSTRAINT debt_case_fkey FOREIGN KEY (case_id)
    REFERENCES public.cases (case_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_debt_case_fkey
    ON public.debts(case_id);


ALTER TABLE IF EXISTS public.payed_debts
    ADD CONSTRAINT coverage_debt_fkey FOREIGN KEY (debt_id)
    REFERENCES public.debts (debt_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_debts_fkey
    ON public.payed_debts(debt_id);


ALTER TABLE IF EXISTS public.payed_debts
    ADD CONSTRAINT coverage_payment_fkey FOREIGN KEY (payment_id)
    REFERENCES public.payments (payment_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_payments_fkey
    ON public.payed_debts(payment_id);


ALTER TABLE IF EXISTS public.fin_publicated_data
    ADD CONSTRAINT fin_pub_data_case_fkey FOREIGN KEY (case_id)
    REFERENCES public.cases (case_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_case_fkey
    ON public.fin_publicated_data(case_id);


ALTER TABLE IF EXISTS public.fin_publicated_data
    ADD CONSTRAINT fin_pub_data_bank_account_fkey FOREIGN KEY (bank_account_id)
    REFERENCES public.bank_accounts (bank_account_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_fin_pub_data_bank_account_fkey
    ON public.fin_publicated_data(bank_account_id);


ALTER TABLE IF EXISTS public.fin_publicated_data
    ADD CONSTRAINT fin_pub_data_person_fkey FOREIGN KEY (person_id)
    REFERENCES public.persons (person_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_fin_pub_data_person_fkey
    ON public.fin_publicated_data(person_id);

CREATE OR REPLACE VIEW public.partner_statistics_v
 AS
 WITH purchase_summary AS (
         SELECT p.partner_id,
            sum(p.batch_purchase_value) AS total_purchase_value,
            count(DISTINCT p.batch_number) AS purchase_count,
            min(p.purchased_at) AS first_purchase,
            max(p.purchased_at) AS last_purchase
           FROM purchases p
          WHERE p.deleted_at IS NULL
          GROUP BY p.partner_id
        ), case_summary AS (
         SELECT p.partner_id,
            sum(c.calculated_purchase_value) AS total_calculated_value,
            sum(c.amount) AS total_amount,
            sum(c.current_amount) AS total_current_amount,
            sum(c.current_interest_amount) AS total_current_interest_amount,
            avg(c.amount) AS avg_amount,
            count(DISTINCT c.case_id) AS total_cases
           FROM purchases p
             JOIN cases c ON c.purchase_id = p.purchase_id
          WHERE p.deleted_at IS NULL AND c.deleted_at IS NULL
          GROUP BY p.partner_id
        ), debtor_summary AS (
         SELECT p.partner_id,
            count(DISTINCT d.person_id) AS total_debtors
           FROM purchases p
             JOIN cases c ON c.purchase_id = p.purchase_id
             JOIN debtors d ON d.case_id = c.case_id
          WHERE p.deleted_at IS NULL AND c.deleted_at IS NULL AND d.deleted_at IS NULL
          GROUP BY p.partner_id
        ), payments_summary AS (
         SELECT r_1.partner_id,
            sum(p.amount) AS sum_payment
           FROM payments p,
            cases c,
            purchases r_1
          WHERE p.case_id = c.case_id AND c.purchase_id = r_1.purchase_id AND p.deleted_at IS NULL AND c.deleted_at IS NULL AND r_1.deleted_at IS NULL
          GROUP BY r_1.partner_id
        ), coverage_summary AS (
         SELECT p.partner_id,
            sum(t.debt_amount_covered) AS debt_amount_covered,
            sum(t.interest_amount_covered) AS interest_amount_covered,
            sum(t.overpayment) AS overpayment
           FROM payed_debts t,
            debts d,
            cases c,
            purchases p
          WHERE d.debt_id = t.debt_id AND c.case_id = d.case_id AND p.purchase_id = c.purchase_id AND t.deleted_at IS NULL AND d.deleted_at IS NULL AND c.deleted_at IS NULL AND p.deleted_at IS NULL
          GROUP BY p.partner_id
        ), interest_summary AS (
         SELECT p.partner_id,
            sum(d.interest_amount) AS sum_interest
           FROM debts d,
            cases c,
            purchases p
          WHERE c.case_id = d.case_id AND p.purchase_id = c.purchase_id AND c.deleted_at IS NULL AND d.deleted_at IS NULL AND p.deleted_at IS NULL
          GROUP BY p.partner_id
        ), closed_case_summary AS (
         SELECT p.partner_id,
            count(DISTINCT c.case_id) AS open_cases
           FROM cases c,
            purchases p
          WHERE c.closed_at IS NULL AND p.purchase_id = c.purchase_id AND c.deleted_at IS NULL AND p.deleted_at IS NULL
          GROUP BY p.partner_id
        )
 SELECT r.name AS partner_neve,
    to_char(ps.total_purchase_value, '999 999 999 999D999'::text) AS vasarlasi_ertek,
    to_char(cs.total_amount, '999 999 999 999D999'::text) AS vasarolt_ugyek_osszerteke,
    ps.purchase_count AS vasarlasok_szama,
    cs.total_cases AS vasarolt_ugyek_szama,
    cc.open_cases AS nyitott_ugyek_szama,
    ds.total_debtors AS ugyfelek_szama,
    ps.first_purchase AS elso_vasarlas,
    ps.last_purchase AS utolso_vasarlas,
    to_char(cs.total_amount, '999 999 999 999D999'::text) AS teljes_toke_tartozas,
    to_char(ct.debt_amount_covered, '999 999 999 999D999'::text) AS leosztott_toke_tartozas,
    to_char(cs.total_amount - ct.debt_amount_covered, '999 999 999 999D999'::text) AS befizetetlen_toke_tartozas,
    to_char(cs.total_current_amount, '999 999 999 999D999'::text) AS nyilvantartott_befizetetlen_toke_tartozas,
    to_char(it.sum_interest, '999 999 999 999D999'::text) AS nyilvantartott_kamat,
    to_char(ct.interest_amount_covered, '999 999 999 999D999'::text) AS leosztott_kamat,
    to_char(it.sum_interest - ct.interest_amount_covered, '999 999 999 999D999'::text) AS befizetetlen_kamat,
    to_char(cs.total_current_interest_amount, '999 999 999 999D999'::text) AS nyilvantartott_befizetetlen_kamat_tartozas,
    to_char(ts.sum_payment, '999 999 999 999D999'::text) AS osszes_befizetes,
    to_char(ct.overpayment, '999 999 999 999D999'::text) AS tulfizetes,
    to_char(ct.debt_amount_covered + ct.interest_amount_covered, '999 999 999 999D999'::text) AS leosztas_osszesen
   FROM partners r
     LEFT JOIN purchase_summary ps ON r.partner_id = ps.partner_id
     LEFT JOIN case_summary cs ON r.partner_id = cs.partner_id
     LEFT JOIN debtor_summary ds ON r.partner_id = ds.partner_id
     LEFT JOIN payments_summary ts ON ts.partner_id = r.partner_id
     LEFT JOIN coverage_summary ct ON ct.partner_id = r.partner_id
     LEFT JOIN interest_summary it ON it.partner_id = r.partner_id
     LEFT JOIN closed_case_summary cc ON cc.partner_id = r.partner_id
  ORDER BY r.name;

ALTER TABLE public.partner_statistics_v
    OWNER TO cms;

CREATE OR REPLACE VIEW public.fin_publicated_data_v
 AS
 WITH overpayment_sum AS (
         SELECT d_1.case_id,
            sum(pd.overpayment) AS overpayment
           FROM payed_debts pd,
            debts d_1
          WHERE pd.debt_id = d_1.debt_id AND pd.deleted_at IS NULL AND d_1.deleted_at IS NULL
          GROUP BY d_1.case_id
        ), last_payment_date AS (
         SELECT p_1.case_id,
            max(p_1.payment_date) AS last_payment_date
           FROM payments p_1
          WHERE p_1.deleted_at IS NULL
          GROUP BY p_1.case_id
        )
 SELECT c.partner_case_number,
    a.account_number,
    p.first_name,
    p.last_name,
    p.birth_name,
    c.closed_at,
    c.current_amount,
    c.current_interest_amount,
    os.overpayment,
    lpd.last_payment_date,
    c.current_due_date,
    h.valid_to,
    c.case_id,
    a.bank_account_id,
    p.person_id
   FROM cases c,
    overpayment_sum os,
    last_payment_date lpd,
    account_holders h,
    persons p,
    debtors d,
    bank_accounts a
  WHERE c.deleted_at IS NULL AND (c.closed_at IS NULL OR c.closed_at IS NOT NULL AND os.overpayment > 0::numeric) AND os.case_id = c.case_id AND lpd.case_id = c.case_id AND h.person_id = p.person_id AND h.deleted_at IS NULL AND p.person_id = d.person_id AND d.deleted_at IS NULL AND d.case_id = c.case_id AND a.bank_account_id = h.bank_account_id AND a.deleted_at IS NULL AND h.valid_from < lpd.last_payment_date;

ALTER TABLE public.fin_publicated_data_v
    OWNER TO cms;

END;
