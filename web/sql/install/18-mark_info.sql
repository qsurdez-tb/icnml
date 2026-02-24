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
-- Name: mark_info; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.mark_info (
    id integer NOT NULL,
    uuid uuid NOT NULL,
    pfsp character varying,
    detection_technic character varying,
    surface character varying
);


ALTER TABLE public.mark_info OWNER TO icnml;

--
-- Name: mark_info_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.mark_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mark_info_id_seq OWNER TO icnml;

--
-- Name: mark_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.mark_info_id_seq OWNED BY public.mark_info.id;


--
-- Name: mark_info id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.mark_info ALTER COLUMN id SET DEFAULT nextval('public.mark_info_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

