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

--
-- Name: files_segments_v; Type: VIEW; Schema: public; Owner: icnml
--

CREATE VIEW public.files_segments_v AS
 SELECT files_segments.id,
    files_segments.tenprint,
    files_segments.pc,
    files_segments.uuid
   FROM public.files_segments;


ALTER TABLE public.files_segments_v OWNER TO icnml;

--
-- PostgreSQL database dump complete
--

