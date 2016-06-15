--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'SQL_ASCII';
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
1	144	entry.content	2016-06-09 06:05:43.623752+00	1	\N
2	50	entry.content	2016-06-10 00:44:15.166132+00	5	1
3	50	entry.content	2016-06-10 00:52:18.737949+00	5	1
4	46	entry.content	2016-06-10 00:52:30.693419+00	4	1
5	20	entry.content	2016-06-10 05:44:13.179555+00	2	1
6	10	entry.content	2016-06-10 05:50:11.428018+00	1	2
7	30	entry.content	2016-06-10 05:50:19.652325+00	3	2
8	83	entry.content	2016-06-10 05:50:57.85177+00	7	3
9	111	entry.content	2016-06-10 05:51:09.214601+00	8	3
10	12	entry.content	2016-06-11 18:28:31.105282+00	2	2
12	90	entry.content	2016-06-11 21:02:59.666906+00	4	3
15	110	entry.content	2016-06-11 21:57:02.915695+00	5	3
32	40	entry.content	2016-06-11 23:38:26.637352+00	3	1
39	6	entry.content	2016-06-11 23:58:41.928349+00	1	2
40	45	entry.content	2016-06-14 05:16:13.204015+00	2	1
41	67	entry.content	2016-06-14 05:16:32.612425+00	3	3
42	23	entry.content	2016-06-14 05:16:54.866127+00	1	2
43	69	:)	2016-06-15 06:00:14.786821+00	1	1
\.


--
-- Name: entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('entries_id_seq', 43, true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: ubuntu
--

COPY users (id, name, email, password) FROM stdin;
1	jonsandersss	jonsandersss@gmail.com	pbkdf2:sha1:1000$CoWpFp7G$fa7490cd6ffd53bad7ff9d9938df33df7dfa7336
2	goodatthis	goodatthis@gmail.com	pbkdf2:sha1:1000$IGjri5E2$1e04e28a0434464133ef5389d88ef35d5027dcb0
3	badatthis	badatthis@gmail.com	pbkdf2:sha1:1000$vch3fvA5$11fc75549b6641d5125787b70f7390f7357b50af
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ubuntu
--

SELECT pg_catalog.setval('users_id_seq', 3, true);


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

