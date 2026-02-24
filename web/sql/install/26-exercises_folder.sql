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
-- Name: exercises_folder; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.exercises_folder (
    id integer NOT NULL,
    mark uuid NOT NULL,
    folder uuid NOT NULL
);


ALTER TABLE public.exercises_folder OWNER TO icnml;

--
-- Name: exercises_folder_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.exercises_folder_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exercises_folder_id_seq OWNER TO icnml;

--
-- Name: exercises_folder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.exercises_folder_id_seq OWNED BY public.exercises_folder.id;


--
-- Name: exercises_folder id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.exercises_folder ALTER COLUMN id SET DEFAULT nextval('public.exercises_folder_id_seq'::regclass);


--
-- Name: exercises_folder_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.exercises_folder_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

