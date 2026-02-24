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
-- Name: files_v; Type: VIEW; Schema: public; Owner: icnml
--

CREATE VIEW public.files_v AS
 SELECT files.id,
    files.creator,
    files.creation_time,
    files.folder,
    files.filename,
    files.type,
    files.size,
    files.resolution,
    files.width,
    files.height,
    files.uuid,
    files.format,
    files.note,
    files.quality
   FROM public.files;


ALTER TABLE public.files_v OWNER TO icnml;

--
-- PostgreSQL database dump complete
--

