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
-- Name: files; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.files (
    id integer NOT NULL,
    creator integer,
    creation_time timestamp with time zone DEFAULT now() NOT NULL,
    folder integer,
    filename character varying NOT NULL,
    type integer,
    size bigint,
    uuid uuid,
    data character varying,
    width integer,
    height integer,
    format character varying,
    resolution integer,
    note character varying,
    quality integer
);


ALTER TABLE public.files OWNER TO icnml;

--
-- Name: files_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.files_id_seq OWNER TO icnml;

--
-- Name: files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.files_id_seq OWNED BY public.files.id;


--
-- Name: files id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.files ALTER COLUMN id SET DEFAULT nextval('public.files_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

