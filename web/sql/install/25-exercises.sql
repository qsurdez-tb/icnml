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
-- Name: exercises; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.exercises (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    trainer_id integer NOT NULL,
    creationtime timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.exercises OWNER TO icnml;

--
-- Name: exercises_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.exercises_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exercises_id_seq OWNER TO icnml;

--
-- Name: exercises_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.exercises_id_seq OWNED BY public.exercises.id;


--
-- Name: exercises id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.exercises ALTER COLUMN id SET DEFAULT nextval('public.exercises_id_seq'::regclass);


--
-- Name: exercises_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.exercises_id_seq', 46, true);


--
-- PostgreSQL database dump complete
--

