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
-- Name: files_type; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.files_type (
    id integer NOT NULL,
    name character varying NOT NULL,
    "desc" character varying
);


ALTER TABLE public.files_type OWNER TO icnml;

--
-- Name: files_type_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.files_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.files_type_id_seq OWNER TO icnml;

--
-- Name: files_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.files_type_id_seq OWNED BY public.files_type.id;


--
-- Name: files_type id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.files_type ALTER COLUMN id SET DEFAULT nextval('public.files_type_id_seq'::regclass);


--
-- Data for Name: files_type; Type: TABLE DATA; Schema: public; Owner: icnml
--

INSERT INTO public.files_type (id, name, "desc") VALUES (0, 'consent_form', 'Consent form');
INSERT INTO public.files_type (id, name, "desc") VALUES (1, 'tenprint_card_front', 'Tenprint card front');
INSERT INTO public.files_type (id, name, "desc") VALUES (2, 'tenprint_card_back', 'Tenprint card back');
INSERT INTO public.files_type (id, name, "desc") VALUES (3, 'mark_target', 'Mark target');
INSERT INTO public.files_type (id, name, "desc") VALUES (4, 'mark_incidental', 'Mark incidental');
INSERT INTO public.files_type (id, name, "desc") VALUES (5, 'tenprint_nist', 'TP NIST file');


--
-- Name: files_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.files_type_id_seq', 4, true);


--
-- PostgreSQL database dump complete
--

