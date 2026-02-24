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
-- Name: thumbnails; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.thumbnails (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    size integer NOT NULL,
    data character varying NOT NULL,
    format character varying NOT NULL
);


ALTER TABLE public.thumbnails OWNER TO icnml;

--
-- Name: thumbnails_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.thumbnails_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.thumbnails_id_seq OWNER TO icnml;

--
-- Name: thumbnails_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.thumbnails_id_seq OWNED BY public.thumbnails.id;


--
-- Name: thumbnails id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.thumbnails ALTER COLUMN id SET DEFAULT nextval('public.thumbnails_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

