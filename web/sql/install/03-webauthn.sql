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
-- Name: webauthn; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.webauthn (
    id integer NOT NULL,
    user_id integer NOT NULL,
    ukey character varying NOT NULL,
    credential_id character varying NOT NULL,
    pub_key character varying NOT NULL,
    sign_count integer NOT NULL,
    key_name character varying,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    last_usage timestamp with time zone,
    active boolean DEFAULT true NOT NULL,
    usage_counter integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.webauthn OWNER TO icnml;

--
-- Name: webauthn_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.webauthn_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.webauthn_id_seq OWNER TO icnml;

--
-- Name: webauthn_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.webauthn_id_seq OWNED BY public.webauthn.id;


--
-- Name: webauthn id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.webauthn ALTER COLUMN id SET DEFAULT nextval('public.webauthn_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

