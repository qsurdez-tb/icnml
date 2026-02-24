--
-- PostgreSQL database dump
--


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: account_type; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.account_type (
    id integer NOT NULL,
    name character varying NOT NULL,
    can_singin boolean DEFAULT false NOT NULL
);


ALTER TABLE public.account_type OWNER TO icnml;

--
-- Name: accounts_types_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.accounts_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.accounts_types_id_seq OWNER TO icnml;

--
-- Name: accounts_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.accounts_types_id_seq OWNED BY public.account_type.id;


--
-- Name: account_type id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.account_type ALTER COLUMN id SET DEFAULT nextval('public.accounts_types_id_seq'::regclass);


--
-- Data for Name: account_type; Type: TABLE DATA; Schema: public; Owner: icnml
--

INSERT INTO public.account_type (id, name, can_singin) VALUES (1, 'Administrator', false);
INSERT INTO public.account_type (id, name, can_singin) VALUES (2, 'Donor', false);
INSERT INTO public.account_type (id, name, can_singin) VALUES (3, 'Submitter', true);
INSERT INTO public.account_type (id, name, can_singin) VALUES (4, 'Trainer', true);
INSERT INTO public.account_type (id, name, can_singin) VALUES (5, 'AFIS', true);
INSERT INTO public.account_type (id, name, can_singin) VALUES (6, 'Selection', true);


--
-- Name: accounts_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.accounts_types_id_seq', 6, true);


--
-- Name: account_type account_type_pk; Type: CONSTRAINT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.account_type
    ADD CONSTRAINT account_type_pk PRIMARY KEY (id);


--
-- Name: account_type_id_idx; Type: INDEX; Schema: public; Owner: icnml
--

CREATE INDEX account_type_id_idx ON public.account_type USING btree (id);


--
-- PostgreSQL database dump complete
--

