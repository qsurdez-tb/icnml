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
-- Name: signin_requests; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.signin_requests (
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    email character varying NOT NULL,
    account_type integer NOT NULL,
    request_time timestamp with time zone DEFAULT now() NOT NULL,
    id integer NOT NULL,
    uuid uuid NOT NULL,
    validation_time timestamp with time zone,
    assertion_response character varying,
    status character varying DEFAULT 'pending'::character varying NOT NULL,
    username_id integer NOT NULL
);


ALTER TABLE public.signin_requests OWNER TO icnml;

--
-- Name: signin_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.signin_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.signin_requests_id_seq OWNER TO icnml;

--
-- Name: signin_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.signin_requests_id_seq OWNED BY public.signin_requests.id;


--
-- Name: signin_requests id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.signin_requests ALTER COLUMN id SET DEFAULT nextval('public.signin_requests_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

