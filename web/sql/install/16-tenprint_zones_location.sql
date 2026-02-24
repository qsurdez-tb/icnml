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
-- Name: tenprint_zones_location; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.tenprint_zones_location (
    pc integer NOT NULL,
    side character varying NOT NULL
);


ALTER TABLE public.tenprint_zones_location OWNER TO icnml;

--
-- Data for Name: tenprint_zones_location; Type: TABLE DATA; Schema: public; Owner: icnml
--

INSERT INTO public.tenprint_zones_location (pc, side) VALUES (1, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (2, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (3, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (4, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (5, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (6, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (7, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (8, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (9, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (10, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (11, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (12, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (13, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (14, 'front');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (22, 'back');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (24, 'back');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (25, 'back');
INSERT INTO public.tenprint_zones_location (pc, side) VALUES (27, 'back');


--
-- PostgreSQL database dump complete
--

