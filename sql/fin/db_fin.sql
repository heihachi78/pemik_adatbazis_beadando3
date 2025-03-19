--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4 (Debian 17.4-1.pgdg120+2)
-- Dumped by pg_dump version 17.4 (Debian 17.4-1.pgdg120+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: fin_publicated_data; Type: TABLE DATA; Schema: public; Owner: fin
--

COPY public.fin_publicated_data (partner_case_number, account_number, first_name, last_name, birth_name, closed_at, current_amount, current_interest_amount, overpayment, last_payment_date, current_due_date, valid_to, case_id, bank_account_id, person_id, refreshed_at) FROM stdin;
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: fin
--

COPY public.payments (payment_id, amount, payment_date, bank_account_id, person_id, case_id, created_at, updated_at, deleted_at) FROM stdin;
\.


--
-- Data for Name: test; Type: TABLE DATA; Schema: public; Owner: fin
--

COPY public.test (test_id, n) FROM stdin;
\.


--
-- Name: payments_payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fin
--

SELECT pg_catalog.setval('public.payments_payment_id_seq', 1000000000, false);


--
-- Name: test_test_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fin
--

SELECT pg_catalog.setval('public.test_test_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

