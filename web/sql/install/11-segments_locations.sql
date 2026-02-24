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
-- Name: segments_locations; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.segments_locations (
    id integer NOT NULL,
    tenprint_id uuid NOT NULL,
    fpc integer NOT NULL,
    x numeric NOT NULL,
    y numeric NOT NULL,
    width numeric NOT NULL,
    height numeric NOT NULL,
    orientation integer NOT NULL
);


ALTER TABLE public.segments_locations OWNER TO icnml;

--
-- Name: segments_locations_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.segments_locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.segments_locations_id_seq OWNER TO icnml;

--
-- Name: segments_locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.segments_locations_id_seq OWNED BY public.segments_locations.id;


--
-- Name: segments_locations id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.segments_locations ALTER COLUMN id SET DEFAULT nextval('public.segments_locations_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

