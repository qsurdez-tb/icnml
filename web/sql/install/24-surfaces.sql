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

SET default_table_access_method = heap;

--
-- Name: surfaces; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.surfaces (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.surfaces OWNER TO icnml;

--
-- Name: surfaces_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.surfaces_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.surfaces_id_seq OWNER TO icnml;

--
-- Name: surfaces_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.surfaces_id_seq OWNED BY public.surfaces.id;


--
-- Name: surfaces id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.surfaces ALTER COLUMN id SET DEFAULT nextval('public.surfaces_id_seq'::regclass);


--
-- Data for Name: surfaces; Type: TABLE DATA; Schema: public; Owner: icnml
--

INSERT INTO public.surfaces VALUES (1, 'Paper');
INSERT INTO public.surfaces VALUES (2, 'Plastic');
INSERT INTO public.surfaces VALUES (3, 'Glass');
INSERT INTO public.surfaces VALUES (4, 'Bag');
INSERT INTO public.surfaces VALUES (5, 'Bottle');
INSERT INTO public.surfaces VALUES (6, 'Sticky side');
INSERT INTO public.surfaces VALUES (7, 'Non-adhesive side');
INSERT INTO public.surfaces VALUES (8, 'Tape');
INSERT INTO public.surfaces VALUES (9, 'Fabric / Cloth');
INSERT INTO public.surfaces VALUES (10, 'Metal');
INSERT INTO public.surfaces VALUES (11, 'Cartridge');
INSERT INTO public.surfaces VALUES (12, 'Wood');
INSERT INTO public.surfaces VALUES (13, 'Porcelain');


--
-- Name: surfaces_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.surfaces_id_seq', 13, true);


--
-- PostgreSQL database dump complete
--

