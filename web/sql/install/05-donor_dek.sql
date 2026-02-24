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
-- Name: donor_dek; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.donor_dek (
    id integer NOT NULL,
    donor_name character varying NOT NULL,
    salt character varying NOT NULL,
    iterations integer NOT NULL,
    algo character varying NOT NULL,
    hash character varying NOT NULL,
    dek character varying,
    dek_check character varying NOT NULL
);


ALTER TABLE public.donor_dek OWNER TO icnml;

--
-- Name: donor_dek_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.donor_dek_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.donor_dek_id_seq OWNER TO icnml;

--
-- Name: donor_dek_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.donor_dek_id_seq OWNED BY public.donor_dek.id;


--
-- Name: donor_dek id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.donor_dek ALTER COLUMN id SET DEFAULT nextval('public.donor_dek_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

