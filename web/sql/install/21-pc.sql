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
-- Name: pc; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.pc (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.pc OWNER TO icnml;

--
-- Name: fpc_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.fpc_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fpc_id_seq OWNER TO icnml;

--
-- Name: fpc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.fpc_id_seq OWNED BY public.pc.id;


--
-- Data for Name: pc; Type: TABLE DATA; Schema: public; Owner: icnml
--

INSERT INTO public.pc (id, name) VALUES (1, 'Right thumb');
INSERT INTO public.pc (id, name) VALUES (2, 'Right index');
INSERT INTO public.pc (id, name) VALUES (3, 'Right middle');
INSERT INTO public.pc (id, name) VALUES (4, 'Right ring');
INSERT INTO public.pc (id, name) VALUES (5, 'Right little');
INSERT INTO public.pc (id, name) VALUES (6, 'Left thumb');
INSERT INTO public.pc (id, name) VALUES (7, 'Left index');
INSERT INTO public.pc (id, name) VALUES (8, 'Left middle');
INSERT INTO public.pc (id, name) VALUES (9, 'Left ring');
INSERT INTO public.pc (id, name) VALUES (10, 'Left little');
INSERT INTO public.pc (id, name) VALUES (25, 'Right lower palm');
INSERT INTO public.pc (id, name) VALUES (27, 'Left lower palm');
INSERT INTO public.pc (id, name) VALUES (11, 'Right thumb slap');
INSERT INTO public.pc (id, name) VALUES (12, 'Left thumb slap');
INSERT INTO public.pc (id, name) VALUES (13, 'Right control slap');
INSERT INTO public.pc (id, name) VALUES (14, 'Left control slap');
INSERT INTO public.pc (id, name) VALUES (22, 'Right writer palm');
INSERT INTO public.pc (id, name) VALUES (24, 'Left writer palm');
INSERT INTO public.pc (id, name) VALUES (1000, 'All rolled');


--
-- Name: fpc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.fpc_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

