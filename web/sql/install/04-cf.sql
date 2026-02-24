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
-- Name: cf; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.cf (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    data character varying NOT NULL,
    email character varying NOT NULL
);


ALTER TABLE public.cf OWNER TO icnml;

--
-- Name: cf_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.cf_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cf_id_seq OWNER TO icnml;

--
-- Name: cf_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.cf_id_seq OWNED BY public.cf.id;


--
-- Name: cf id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.cf ALTER COLUMN id SET DEFAULT nextval('public.cf_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

