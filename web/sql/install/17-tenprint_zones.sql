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
-- Name: tenprint_zones; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.tenprint_zones (
    id integer NOT NULL,
    pc integer NOT NULL,
    angle numeric(10,0),
    card integer NOT NULL,
    tl_x numeric,
    tl_y numeric,
    br_x numeric,
    br_y numeric
);


ALTER TABLE public.tenprint_zones OWNER TO icnml;

--
-- Name: tenprint_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.tenprint_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenprint_templates_id_seq OWNER TO icnml;

--
-- Name: tenprint_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.tenprint_templates_id_seq OWNED BY public.tenprint_zones.id;


--
-- Name: tenprint_zones id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.tenprint_zones ALTER COLUMN id SET DEFAULT nextval('public.tenprint_templates_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

