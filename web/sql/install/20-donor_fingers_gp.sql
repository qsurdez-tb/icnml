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
-- Name: donor_fingers_gp; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.donor_fingers_gp (
    id integer NOT NULL,
    donor_id integer NOT NULL,
    fpc integer NOT NULL,
    gp integer NOT NULL
);


ALTER TABLE public.donor_fingers_gp OWNER TO icnml;

--
-- Name: donor_fingers_gp_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.donor_fingers_gp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.donor_fingers_gp_id_seq OWNER TO icnml;

--
-- Name: donor_fingers_gp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.donor_fingers_gp_id_seq OWNED BY public.donor_fingers_gp.id;


--
-- Name: donor_fingers_gp id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.donor_fingers_gp ALTER COLUMN id SET DEFAULT nextval('public.donor_fingers_gp_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

