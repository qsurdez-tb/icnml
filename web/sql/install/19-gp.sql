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
-- Name: gp; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.gp (
    id integer NOT NULL,
    name character varying NOT NULL,
    div_name character varying NOT NULL
);


ALTER TABLE public.gp OWNER TO icnml;

--
-- Name: gp_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.gp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gp_id_seq OWNER TO icnml;

--
-- Name: gp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.gp_id_seq OWNED BY public.gp.id;


--
-- Name: gp id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.gp ALTER COLUMN id SET DEFAULT nextval('public.gp_id_seq'::regclass);


--
-- Data for Name: gp; Type: TABLE DATA; Schema: public; Owner: icnml
--

INSERT INTO public.gp VALUES (1, 'unknown', 'unknown');
INSERT INTO public.gp VALUES (2, 'left loop', 'll');
INSERT INTO public.gp VALUES (3, 'right loop', 'rl');
INSERT INTO public.gp VALUES (4, 'whorl', 'whorl');
INSERT INTO public.gp VALUES (5, 'arch', 'arch');
INSERT INTO public.gp VALUES (6, 'central pocket loop', 'cpl');
INSERT INTO public.gp VALUES (7, 'double loop', 'dl');
INSERT INTO public.gp VALUES (8, 'missing/amputated', 'ma');
INSERT INTO public.gp VALUES (9, 'scarred/mutilated', 'sm');


--
-- Name: gp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.gp_id_seq', 8, true);


--
-- PostgreSQL database dump complete
--

