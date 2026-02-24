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
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: quality_type; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.quality_type (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.quality_type OWNER TO icnml;

--
-- Name: newtable_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.newtable_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.newtable_id_seq OWNER TO icnml;

--
-- Name: newtable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.newtable_id_seq OWNED BY public.quality_type.id;


--
-- Name: quality_type id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.quality_type ALTER COLUMN id SET DEFAULT nextval('public.newtable_id_seq'::regclass);


--
-- Data for Name: quality_type; Type: TABLE DATA; Schema: public; Owner: icnml
--

INSERT INTO public.quality_type VALUES (1, 'Prestine');
INSERT INTO public.quality_type VALUES (2, 'Medium');
INSERT INTO public.quality_type VALUES (3, 'Bad');


--
-- Name: newtable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.newtable_id_seq', 3, true);


--
-- PostgreSQL database dump complete
--

