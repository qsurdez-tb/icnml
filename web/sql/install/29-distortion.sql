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
-- Name: distortion; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.distortion (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.distortion OWNER TO icnml;

--
-- Name: distortion_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.distortion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.distortion_id_seq OWNER TO icnml;

--
-- Name: distortion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.distortion_id_seq OWNED BY public.distortion.id;


--
-- Name: distortion id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.distortion ALTER COLUMN id SET DEFAULT nextval('public.distortion_id_seq'::regclass);


--
-- Data for Name: distortion; Type: TABLE DATA; Schema: public; Owner: icnml
--

INSERT INTO public.distortion VALUES (1, 'drag');
INSERT INTO public.distortion VALUES (2, 'twist');
INSERT INTO public.distortion VALUES (3, 'unknown');
INSERT INTO public.distortion VALUES (4, 'none');


--
-- Name: distortion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.distortion_id_seq', 4, true);


--
-- PostgreSQL database dump complete
--

