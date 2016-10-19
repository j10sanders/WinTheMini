--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: entries; Type: TABLE; Schema: public; Owner: ubuntu; Tablespace: 
--

CREATE TABLE entries (
    id integer NOT NULL,
    title integer,
    content text,
    datetime timestamp with time zone,
    day_rank integer,
    author_id integer
);


ALTER TABLE public.entries OWNER TO ubuntu;

--
-- Name: entries_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE entries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.entries_id_seq OWNER TO ubuntu;

--
-- Name: entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE entries_id_seq OWNED BY entries.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: ubuntu; Tablespace: 
--

CREATE TABLE users (
    id integer NOT NULL,
    name character varying(128),
    email character varying(128),
    password character varying(128)
);


ALTER TABLE public.users OWNER TO ubuntu;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: ubuntu
--

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO ubuntu;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ubuntu
--

ALTER SEQUENCE users_id_seq OWNED BY users.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY entries ALTER COLUMN id SET DEFAULT nextval('entries_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- Data for Name: entries; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY entries (id, title, content, datetime, day_rank, author_id) FROM stdin;
2	50	test 1	2016-06-15 23:42:40.396112+00	1	1
1	144	meh	2016-06-15 23:41:48.111222+00	3	\N
3	68	1:08	2016-06-16 01:35:58.659701+00	2	1
\.


--
-- Name: entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('entries_id_seq', 3, true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY users (id, name, email, password) FROM stdin;
1	jonsandersss	jonsandersss@gmail.com	pbkdf2:sha1:1000$UsB69Ie5$93ca8cfb1b8de1b1f799d346a6af3b344604e620
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('users_id_seq', 1, true);


--
-- Name: entries_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu; Tablespace: 
--

ALTER TABLE ONLY entries
    ADD CONSTRAINT entries_pkey PRIMARY KEY (id);


--
-- Name: users_email_key; Type: CONSTRAINT; Schema: public; Owner: ubuntu; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: ubuntu; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: entries_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ubuntu
--

ALTER TABLE ONLY entries
    ADD CONSTRAINT entries_author_id_fkey FOREIGN KEY (author_id) REFERENCES users(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

