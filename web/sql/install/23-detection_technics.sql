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
-- Name: detection_technics; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.detection_technics (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.detection_technics OWNER TO icnml;

--
-- Name: detection_technics_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.detection_technics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.detection_technics_id_seq OWNER TO icnml;

--
-- Name: detection_technics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.detection_technics_id_seq OWNED BY public.detection_technics.id;


--
-- Name: detection_technics id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.detection_technics ALTER COLUMN id SET DEFAULT nextval('public.detection_technics_id_seq'::regclass);


--
-- Data for Name: detection_technics; Type: TABLE DATA; Schema: public; Owner: icnml
--

INSERT INTO public.detection_technics VALUES (1, 'Black Powder');
INSERT INTO public.detection_technics VALUES (2, 'Ninhydrine');
INSERT INTO public.detection_technics VALUES (3, '1,2-Indanedione');
INSERT INTO public.detection_technics VALUES (4, 'Cyanoacrylate fuming (CA)');
INSERT INTO public.detection_technics VALUES (5, 'Black Powder Suspension (BPS)');
INSERT INTO public.detection_technics VALUES (6, 'Optical');
INSERT INTO public.detection_technics VALUES (7, 'Blueing');
INSERT INTO public.detection_technics VALUES (8, 'Ardrox');
INSERT INTO public.detection_technics VALUES (9, 'Basic Red 14 (BR14)');
INSERT INTO public.detection_technics VALUES (10, 'Basic Red 28 (BR28)');
INSERT INTO public.detection_technics VALUES (11, 'Basic Yellow 40 (BY40)');
INSERT INTO public.detection_technics VALUES (12, 'Rhodamine 6G (R6G) / Basic Red 1 (BR1)');
INSERT INTO public.detection_technics VALUES (13, 'Diaminobenzidine (DAB)');
INSERT INTO public.detection_technics VALUES (14, '1,8-diaza-9-fluorenone (DFO)');
INSERT INTO public.detection_technics VALUES (15, 'Genipin');
INSERT INTO public.detection_technics VALUES (16, 'Amido Black');
INSERT INTO public.detection_technics VALUES (17, 'Oil Red O (ORO)');
INSERT INTO public.detection_technics VALUES (18, '4-dimethylaminocinnamaldehyde (p-DMAC)');
INSERT INTO public.detection_technics VALUES (19, 'Physical Developer (PD)');
INSERT INTO public.detection_technics VALUES (20, 'Single Metal Deposition (SMD)');
INSERT INTO public.detection_technics VALUES (21, 'Multi Metal Deposition (MMD)');
INSERT INTO public.detection_technics VALUES (22, 'DABCO');
INSERT INTO public.detection_technics VALUES (23, 'SPR');
INSERT INTO public.detection_technics VALUES (24, 'Sticky Side Powder (SSP)');
INSERT INTO public.detection_technics VALUES (25, 'Sudan Black');
INSERT INTO public.detection_technics VALUES (26, 'Gentian Violet (GV)');
INSERT INTO public.detection_technics VALUES (27, 'Leuco Crystal Violet (LCV)');
INSERT INTO public.detection_technics VALUES (28, 'RAM (Rhodamine6G, MBD, Ardrox)');
INSERT INTO public.detection_technics VALUES (29, 'Wetwop');
INSERT INTO public.detection_technics VALUES (30, 'Safranine O / Basic Red 2 (BR2)');
INSERT INTO public.detection_technics VALUES (31, 'Liqui-drox');
INSERT INTO public.detection_technics VALUES (32, 'MBD');
INSERT INTO public.detection_technics VALUES (33, 'Nile Red');
INSERT INTO public.detection_technics VALUES (34, 'Thenoyl europium chelate (TEC)');
INSERT INTO public.detection_technics VALUES (35, 'MRM 10 (Rhodamine 6G, BY40, MBD)');
INSERT INTO public.detection_technics VALUES (36, 'RAY (Rhodamine 6G, BY40, Ardrox)');
INSERT INTO public.detection_technics VALUES (37, 'Lumicyanoacrylate (LCA)');
INSERT INTO public.detection_technics VALUES (38, 'Vacuum Metal Deposition (VMD)');
INSERT INTO public.detection_technics VALUES (39, 'Optical detection - white light');
INSERT INTO public.detection_technics VALUES (40, 'Optical detection - UV');
INSERT INTO public.detection_technics VALUES (41, 'Optical detection - IR');
INSERT INTO public.detection_technics VALUES (42, 'Amino Black 1 (AB1)');
INSERT INTO public.detection_technics VALUES (43, 'Acid yellow 7 (AY7)');
INSERT INTO public.detection_technics VALUES (44, 'Acid violet 17 (AV17)');
INSERT INTO public.detection_technics VALUES (45, 'Other dye stain');
INSERT INTO public.detection_technics VALUES (46, 'White Powder Suspension (WPS)');
INSERT INTO public.detection_technics VALUES (47, 'Small particle Reagent (SPR)');
INSERT INTO public.detection_technics VALUES (48, 'Magnetic Powder');
INSERT INTO public.detection_technics VALUES (49, 'Aluminium Powder');


--
-- Name: detection_technics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: icnml
--

SELECT pg_catalog.setval('public.detection_technics_id_seq', 50, true);


--
-- PostgreSQL database dump complete
--

