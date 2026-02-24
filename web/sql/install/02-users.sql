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
-- Name: users; Type: TABLE; Schema: public; Owner: icnml
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    password character varying,
    email character varying,
    totp character varying,
    active boolean DEFAULT true,
    type integer NOT NULL
);


ALTER TABLE public.users OWNER TO icnml;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: icnml
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO icnml;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: icnml
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: users users_un; Type: CONSTRAINT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_un UNIQUE (username);


--
-- Name: users_username_idx; Type: INDEX; Schema: public; Owner: icnml
--

CREATE INDEX users_username_idx ON public.users USING btree (username);


--
-- Name: users users_fk; Type: FK CONSTRAINT; Schema: public; Owner: icnml
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_fk FOREIGN KEY (type) REFERENCES public.account_type(id);


--
-- PostgreSQL database dump complete
--

