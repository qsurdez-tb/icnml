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
-- Name: submissions; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.submissions (
    id integer NOT NULL,
    email_aes character varying NOT NULL,
    email_hash character varying NOT NULL,
    nickname character varying,
    donor_id integer,
    status character varying NOT NULL,
    created_time timestamp with time zone DEFAULT now() NOT NULL,
    update_time timestamp with time zone DEFAULT now() NOT NULL,
    submitter_id integer NOT NULL,
    uuid uuid NOT NULL,
    consent_form boolean DEFAULT false NOT NULL
);


ALTER TABLE public.submissions OWNER TO icnml;

--
-- Name: submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.submissions_id_seq OWNER TO icnml;

--
-- Name: submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.submissions_id_seq OWNED BY public.submissions.id;


--
-- Name: submissions id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.submissions ALTER COLUMN id SET DEFAULT nextval('public.submissions_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

