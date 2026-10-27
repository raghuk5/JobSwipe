--
-- PostgreSQL database dump
--

\restrict gBdQzb1fO52PNkZWZdp8cVyCFjqqQ4iUbha3KMj9zEM5bdTbgov8eUNyn9rgcsH

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: accounts_user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_user (id, password, last_login, is_superuser, first_name, last_name, is_staff, is_active, date_joined, email, full_name, role) FROM stdin;
3	pbkdf2_sha256$1000000$yPFc0BNnDQfhT5K1wPNXud$Dgj53GInEiopdbbzkXxdqfTqNugJACPDx05DQgDHGgE=	2026-10-27 11:45:52.379297+05:30	f			f	t	2026-10-20 16:24:17.870138+05:30	raghunathank481@gmail.com	John	employer
2	pbkdf2_sha256$1000000$OgeqWyhq9lrVRv4PZ7pJgD$E/PSXRsTqcYAh2yGYPr1AApmWb3zwO95uxj56iLfxiU=	2026-10-27 13:08:00.136388+05:30	f			f	t	2026-10-20 00:02:17.684435+05:30	knraghu555@gmail.com	Raghunathan	candidate
1	pbkdf2_sha256$1000000$sxsTBtitrEx09gO4aZlCoM$zU7Vhs//6RKAxVBKLyc2b/MfkZXKaGKtMXmVP7Ouvbo=	2026-10-21 17:42:09.730627+05:30	t			t	t	2026-10-19 23:56:50.937113+05:30	raghunathank154@gmail.com		candidate
\.


--
-- Data for Name: accounts_jobpreference; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_jobpreference (id, user_id, preferred_roles, preferred_locations, minimum_salary, maximum_salary, work_mode, employment_type, experience_level, willing_to_relocate, updated_at) FROM stdin;
2	1			\N	\N	any	any	any	f	2026-10-20 12:02:06.151091+05:30
1	2		Pan India	\N	\N	any	any	fresher	t	2026-10-20 13:17:18.318185+05:30
\.


--
-- Data for Name: accounts_profile; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_profile (id, user_id, qualification, skills, experience_years, resume, created_at, updated_at) FROM stdin;
2	1			0.0		2026-10-20 12:02:06.119519+05:30	2026-10-20 12:02:06.119543+05:30
1	2	B.Tech ECE	Python , Django , SQL , REST APIs	0.0	resumes/Raghunathan_K_resume_1.pdf	2026-10-20 11:59:33.120042+05:30	2026-10-20 13:16:38.776118+05:30
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: accounts_user_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	accounts	user
7	accounts	jobpreference
8	accounts	profile
9	jobs	job
10	jobs	company
11	jobs	jobswipe
12	jobs	jobbookmark
13	jobs	companymembership
14	jobs	conversation
15	jobs	message
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add user	6	add_user
22	Can change user	6	change_user
23	Can delete user	6	delete_user
24	Can view user	6	view_user
25	Can add job preference	7	add_jobpreference
26	Can change job preference	7	change_jobpreference
27	Can delete job preference	7	delete_jobpreference
28	Can view job preference	7	view_jobpreference
29	Can add profile	8	add_profile
30	Can change profile	8	change_profile
31	Can delete profile	8	delete_profile
32	Can view profile	8	view_profile
33	Can add job	9	add_job
34	Can change job	9	change_job
35	Can delete job	9	delete_job
36	Can view job	9	view_job
37	Can add company	10	add_company
38	Can change company	10	change_company
39	Can delete company	10	delete_company
40	Can view company	10	view_company
41	Can add job swipe	11	add_jobswipe
42	Can change job swipe	11	change_jobswipe
43	Can delete job swipe	11	delete_jobswipe
44	Can view job swipe	11	view_jobswipe
45	Can add job bookmark	12	add_jobbookmark
46	Can change job bookmark	12	change_jobbookmark
47	Can delete job bookmark	12	delete_jobbookmark
48	Can view job bookmark	12	view_jobbookmark
49	Can add company membership	13	add_companymembership
50	Can change company membership	13	change_companymembership
51	Can delete company membership	13	delete_companymembership
52	Can view company membership	13	view_companymembership
53	Can add conversation	14	add_conversation
54	Can change conversation	14	change_conversation
55	Can delete conversation	14	delete_conversation
56	Can view conversation	14	view_conversation
57	Can add message	15	add_message
58	Can change message	15	change_message
59	Can delete message	15	delete_message
60	Can view message	15	view_message
\.


--
-- Data for Name: accounts_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2026-10-20 13:06:19.172751+05:30	1	Thaagam Foundation	1	[{"added": {}}]	10	1
2	2026-10-20 13:09:09.833009+05:30	1	Python Developer — Thaagam Foundation	1	[{"added": {}}]	9	1
3	2026-10-20 13:11:01.680867+05:30	2	Software Engineer — Thaagam Foundation	1	[{"added": {}}]	9	1
4	2026-10-20 15:25:24.71908+05:30	2	BluePeak Technologies	1	[{"added": {}}]	10	1
5	2026-10-20 15:26:29.288218+05:30	3	CodeNest Solutions	1	[{"added": {}}]	10	1
6	2026-10-20 15:27:12.177933+05:30	4	Databridge Analytics	1	[{"added": {}}]	10	1
7	2026-10-20 15:27:51.671067+05:30	5	Cloudorbit Systems	1	[{"added": {}}]	10	1
8	2026-10-20 15:28:39.285462+05:30	6	NextWave Digital	1	[{"added": {}}]	10	1
9	2026-10-20 15:31:08.888828+05:30	3	Junior Python Developer — BluePeak Technologies	1	[{"added": {}}]	9	1
10	2026-10-20 15:40:18.180453+05:30	4	Graduate Software Engineer — CodeNest Solutions	1	[{"added": {}}]	9	1
11	2026-10-20 15:42:16.475646+05:30	5	Junior Data Analyst — Databridge Analytics	1	[{"added": {}}]	9	1
12	2026-10-20 15:44:08.289252+05:30	6	Technical Support Engineer — Cloudorbit Systems	1	[{"added": {}}]	9	1
13	2026-10-20 16:26:18.212118+05:30	1	raghunathank481@gmail.com — Techno Solutions (owner)	2	[]	13	1
14	2026-10-20 16:26:56.891682+05:30	7	Techno Solutions	2	[{"changed": {"fields": ["Is verified"]}}]	10	1
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2026-10-19 23:53:34.701698+05:30
2	contenttypes	0002_remove_content_type_name	2026-10-19 23:53:34.724315+05:30
3	auth	0001_initial	2026-10-19 23:53:34.822389+05:30
4	auth	0002_alter_permission_name_max_length	2026-10-19 23:53:34.835554+05:30
5	auth	0003_alter_user_email_max_length	2026-10-19 23:53:34.84437+05:30
6	auth	0004_alter_user_username_opts	2026-10-19 23:53:34.852234+05:30
7	auth	0005_alter_user_last_login_null	2026-10-19 23:53:34.863817+05:30
8	auth	0006_require_contenttypes_0002	2026-10-19 23:53:34.866371+05:30
9	auth	0007_alter_validators_add_error_messages	2026-10-19 23:53:34.87566+05:30
10	auth	0008_alter_user_username_max_length	2026-10-19 23:53:34.883708+05:30
11	auth	0009_alter_user_last_name_max_length	2026-10-19 23:53:34.894218+05:30
12	auth	0010_alter_group_name_max_length	2026-10-19 23:53:34.915227+05:30
13	auth	0011_update_proxy_permissions	2026-10-19 23:53:34.926005+05:30
14	auth	0012_alter_user_first_name_max_length	2026-10-19 23:53:34.933689+05:30
15	accounts	0001_initial	2026-10-19 23:53:35.041804+05:30
16	admin	0001_initial	2026-10-19 23:53:35.109577+05:30
17	admin	0002_logentry_remove_auto_add	2026-10-19 23:53:35.127967+05:30
18	admin	0003_logentry_add_action_flag_choices	2026-10-19 23:53:35.141329+05:30
19	sessions	0001_initial	2026-10-19 23:53:35.166841+05:30
20	jobs	0001_initial	2026-10-20 13:02:39.537565+05:30
21	jobs	0002_jobswipe	2026-10-20 13:49:47.928445+05:30
22	jobs	0003_jobbookmark	2026-10-20 14:38:42.911689+05:30
23	accounts	0002_user_role	2026-10-20 16:18:31.113377+05:30
24	jobs	0004_employer_review_chat	2026-10-20 16:18:31.473037+05:30
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
q6u1gs085p9exzqymixyixb7q8z876dp	.eJxVjDsOwjAQRO_iGlkb_0NJnzNE3uwaB5AtxUmFuDuJlAKaKea9mbcY47bmcWu8jDOJq9Di8tthnJ5cDkCPWO5VTrWsy4zyUORJmxwq8et2un8HOba8rxFYWyQG4xX1EbvOY5gcEDsfewDLqYOgrVLJomXjTOi139MlssaD-HwB3-E3GQ:1xLZee:FNiTbjWXO2Aiu8aVvArmrwWibB7eKM8z4lDOE_IoBck	2026-11-10 10:53:24.120902+05:30
fkym4esuzfvs2uvatlxirwolv39f1o8h	.eJxVjDsOwjAQRO_iGlkb_0NJnzNE3uwaB5AtxUmFuDuJlAKaKea9mbcY47bmcWu8jDOJq9Di8tthnJ5cDkCPWO5VTrWsy4zyUORJmxwq8et2un8HOba8rxFYWyQG4xX1EbvOY5gcEDsfewDLqYOgrVLJomXjTOi139MlssaD-HwB3-E3GQ:1xLaTQ:RvaCzsURJYEqY2dhzTYyW8Evo0hECmhs_0xF3PxyW3Q	2026-11-10 11:45:52.387452+05:30
mhggxlehh4t60ed5ze4b9xfqadtmrc0f	.eJxVjDsOwjAQBe_iGln-rT-U9JzB8tobHEC2FCcV4u4QKQW0b2bei8W0rTVug5Y4F3Zmip1-N0z5QW0H5Z7arfPc27rMyHeFH3Tway_0vBzu30FNo35rMgiFHDqVQjDaCg06hJBQFKGNByCcSrDOZFSZpLcG0OIkHXpCkIa9P9qnN7Q:1xLbku:27Wegmznoi4KU_WXa8j9HAtSZvxeyjRny92yg7IB7Ow	2026-11-10 13:08:00.147321+05:30
2clcsxdefo7nnwepgruyitiuq8zt5nla	.eJxVjDsOwjAQBe_iGln-rT-U9JzB8tobHEC2FCcV4u4QKQW0b2bei8W0rTVug5Y4F3Zmip1-N0z5QW0H5Z7arfPc27rMyHeFH3Tway_0vBzu30FNo35rMgiFHDqVQjDaCg06hJBQFKGNByCcSrDOZFSZpLcG0OIkHXpCkIa9P9qnN7Q:1xJ8g7:PGmIpoaHeQ5Cpoi-HB2SLO1ambpNuLXGwk6I9cdV7_U	2026-11-03 17:40:51.797675+05:30
e2gtiqzkdgitsdpj9hbosu0nm86fcomi	.eJxVjDsOwjAQBe_iGln-rT-U9JzB8tobHEC2FCcV4u4QKQW0b2bei8W0rTVug5Y4F3Zmip1-N0z5QW0H5Z7arfPc27rMyHeFH3Tway_0vBzu30FNo35rMgiFHDqVQjDaCg06hJBQFKGNByCcSrDOZFSZpLcG0OIkHXpCkIa9P9qnN7Q:1xJ8g8:NbZM5yEQMdkpReh__orZaFq0a89NhVpPDrq2z6PVVNQ	2026-11-03 17:40:52.956302+05:30
41d95yc9t95b047ll716pzftzmw0qalf	.eJxVjDsOwjAQBe_iGln-rT-U9JzB8tobHEC2FCcV4u4QKQW0b2bei8W0rTVug5Y4F3Zmip1-N0z5QW0H5Z7arfPc27rMyHeFH3Tway_0vBzu30FNo35rMgiFHDqVQjDaCg06hJBQFKGNByCcSrDOZFSZpLcG0OIkHXpCkIa9P9qnN7Q:1xJ9tn:JGkD0-SKkEvx1Spwn1E3tNa075yg4WBDceFci0l6KC4	2026-11-03 18:59:03.016485+05:30
aua4fm3yq3dv1h59p2upuwnhdghptdrz	.eJxVjDsOwjAQRO_iGlkb_0NJnzNE3uwaB5AtxUmFuDuJlAKaKea9mbcY47bmcWu8jDOJq9Di8tthnJ5cDkCPWO5VTrWsy4zyUORJmxwq8et2un8HOba8rxFYWyQG4xX1EbvOY5gcEDsfewDLqYOgrVLJomXjTOi139MlssaD-HwB3-E3GQ:1xJoFC:z8DsyNr94mKv4WfLGBDnLhGQ3yN5hBCMPG5NmUPU7l8	2026-11-05 14:03:50.125358+05:30
1w4ippel5pqyt08kj3doxpowvn9c5n7b	.eJxVjDsOwjAQRO_iGlkb_0NJnzNE3uwaB5AtxUmFuDuJlAKaKea9mbcY47bmcWu8jDOJq9Di8tthnJ5cDkCPWO5VTrWsy4zyUORJmxwq8et2un8HOba8rxFYWyQG4xX1EbvOY5gcEDsfewDLqYOgrVLJomXjTOi139MlssaD-HwB3-E3GQ:1xJoFL:twNsE6SMQfbmd5bPfXTj_c_7UgYyRKT5bwhE-ijwcpw	2026-11-05 14:03:59.148142+05:30
5tulx1hwwf59ue06dz4a0nyexxwbmbda	.eJxVjDsOwjAQRO_iGlkb_0NJnzNE3uwaB5AtxUmFuDuJlAKaKea9mbcY47bmcWu8jDOJq9Di8tthnJ5cDkCPWO5VTrWsy4zyUORJmxwq8et2un8HOba8rxFYWyQG4xX1EbvOY5gcEDsfewDLqYOgrVLJomXjTOi139MlssaD-HwB3-E3GQ:1xJoFN:L_TMngkE55peAcK_j_vX5SMtyP66Zve01oy78Z-dPdc	2026-11-05 14:04:01.242949+05:30
2dl42ls4gybnilkllt08g582118m9rru	.eJxVjDsOwjAQRO_iGlkb_0NJnzNE3uwaB5AtxUmFuDuJlAKaKea9mbcY47bmcWu8jDOJq9Di8tthnJ5cDkCPWO5VTrWsy4zyUORJmxwq8et2un8HOba8rxFYWyQG4xX1EbvOY5gcEDsfewDLqYOgrVLJomXjTOi139MlssaD-HwB3-E3GQ:1xJoFQ:ZQoGtU9pUqNBVC_PnoALb27dFe6eV9BT3wT67XmdRMU	2026-11-05 14:04:04.267455+05:30
\.


--
-- Data for Name: jobs_company; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs_company (id, name, website, description, headquarters, logo_url, is_verified, created_at, updated_at) FROM stdin;
1	Thaagam Foundation	http://www.thaagam.org		Chennai		t	2026-10-20 13:06:19.168916+05:30	2026-10-20 13:06:19.168943+05:30
2	BluePeak Technologies	https://example.com	Fictional company created for JobSwipe development and testing.	Chennai, Tamil Nadu		f	2026-10-20 15:25:24.7145+05:30	2026-10-20 15:25:24.714527+05:30
3	CodeNest Solutions	https://example1.com	Fictional company created for JobSwipe development and testing	Bengaluru, Karnataka		t	2026-10-20 15:26:29.282318+05:30	2026-10-20 15:26:29.282348+05:30
4	Databridge Analytics	https://example2.com	Fictional company created for JobSwipe development and testing	Hyderabad, Telangana		f	2026-10-20 15:27:12.176658+05:30	2026-10-20 15:27:12.176684+05:30
5	Cloudorbit Systems	https://example3.com	Fictional company created for JobSwipe development and testing	Pune , Maharashtra		f	2026-10-20 15:27:51.668738+05:30	2026-10-20 15:27:51.668768+05:30
6	NextWave Digital	https://example4.com	Fictional company created for JobSwipe development and testing	Coimbatore, Tamil Nadu		f	2026-10-20 15:28:39.283951+05:30	2026-10-20 15:28:39.283978+05:30
7	Techno Solutions	http://www.technosolutions.com		Chennai , India		t	2026-10-20 16:24:20.704289+05:30	2026-10-20 16:26:56.884777+05:30
\.


--
-- Data for Name: jobs_companymembership; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs_companymembership (id, role, is_active, created_at, company_id, user_id) FROM stdin;
1	owner	t	2026-10-20 16:24:20.706595+05:30	7	3
\.


--
-- Data for Name: jobs_job; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs_job (id, title, description, responsibilities, required_skills, location, work_mode, employment_type, experience_level, minimum_salary, maximum_salary, application_url, posted_at, closing_date, is_active, created_at, updated_at, company_id) FROM stdin;
1	Python Developer	---		Python\r\nDjango\r\nSQL\r\nDesign web applications\r\nGood Communication skills	Chennai	onsite	full_time	fresher	\N	\N	http://www.thaagam.org	2026-10-20	\N	t	2026-10-20 13:09:09.786595+05:30	2026-10-20 13:09:09.786644+05:30	1
2	Software Engineer	---		Proficiency in Java, Python \r\nCI/CD pipelines\r\nSDLC Cycle\r\nGood communication skills	Chennai	onsite	full_time	fresher	\N	\N	http://www.thaagam.org	2026-10-20	\N	t	2026-10-20 13:11:01.675799+05:30	2026-10-20 13:11:01.675824+05:30	1
3	Junior Python Developer	Develop and maintain web applications using Python and Django. Work with the development team to build APIs, debug issues, and write clean, maintainable code.	Develop Django views and REST APIs.\r\nWrite SQL queries and integrate PostgreSQL.\r\nDebug errors and participate in code reviews.	Python, Django, SQL, PostgreSQL, Git, REST API	Chennai	onsite	full_time	fresher	300000	500000	https://example.com/apply/python-developer	2026-10-20	\N	t	2026-10-20 15:31:08.880833+05:30	2026-10-20 15:31:08.880854+05:30	2
4	Graduate Software Engineer	Join a software engineering team building business applications. Assist with implementation, testing, debugging, and documentation while learning established development practices.	- Implement and test software features.\r\n- Fix defects and document code.\r\n- Collaborate with senior developers.	Python, Java, Data Structures, OOP, Git	Bengaluru	onsite	full_time	fresher	\N	\N	https://example.com/apply/graduate-engineer	2026-10-20	\N	t	2026-10-20 15:40:18.174912+05:30	2026-10-20 15:40:18.174934+05:30	3
5	Junior Data Analyst	Analyze datasets, prepare reports, and help business teams identify trends. Use SQL and spreadsheets to clean, validate, and summarize data.	Write SQL queries and validate data.\r\nPrepare reports and dashboards.\r\nCommunicate findings to stakeholders.	SQL, Excel, Python, Data Analysis, Power BI	Hyderabad	hybrid	full_time	fresher	\N	\N	https://example.com/apply/junior-data-analyst	2026-10-20	\N	t	2026-10-20 15:42:16.463476+05:30	2026-10-20 15:42:16.463498+05:30	4
6	Technical Support Engineer	---		Troubleshooting, SQL, Linux, Networking, Communication	Coimbatore	onsite	full_time	fresher	\N	\N	https://example.com/apply/technical-support	2026-10-20	\N	t	2026-10-20 15:44:08.281308+05:30	2026-10-20 15:44:08.281331+05:30	5
7	SQL Developer	---		Python , SQL , Database Management	Chennai	onsite	full_time	fresher	\N	\N	http://www.technosolutions.com	2026-10-20	\N	t	2026-10-20 16:31:11.596491+05:30	2026-10-20 16:31:11.596514+05:30	7
8	Associate Software Engineeer	---	Working on SDLC Cycles\r\nproficiency in Python , Java	Python , SQL , Communication Skills	Remote	onsite	full_time	fresher	300000	400000	https://example.com/apply/python-developer	2026-10-27	2026-10-31	t	2026-10-27 10:56:19.548102+05:30	2026-10-27 10:56:19.548129+05:30	7
\.


--
-- Data for Name: jobs_jobswipe; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs_jobswipe (id, direction, created_at, updated_at, job_id, user_id, interest_status, reviewed_at, reviewed_by_id) FROM stdin;
1	interested	2026-10-20 14:26:41.920396+05:30	2026-10-20 14:26:41.920423+05:30	1	2	not_applicable	\N	\N
2	skipped	2026-10-20 14:27:57.351315+05:30	2026-10-20 14:27:57.351341+05:30	2	2	not_applicable	\N	\N
3	interested	2026-10-20 16:32:46.481269+05:30	2026-10-20 16:34:40.640705+05:30	7	1	accepted	2026-10-20 16:34:40.640501+05:30	3
4	interested	2026-10-20 17:41:06.281145+05:30	2026-10-20 17:41:06.310517+05:30	4	2	pending	\N	\N
5	interested	2026-10-20 18:57:41.953762+05:30	2026-10-20 19:06:28.941647+05:30	7	2	accepted	2026-10-20 19:06:28.941404+05:30	3
6	interested	2026-10-22 14:10:58.867957+05:30	2026-10-22 14:10:58.976939+05:30	6	2	pending	\N	\N
7	interested	2026-10-27 10:56:47.468156+05:30	2026-10-27 10:57:20.029988+05:30	8	2	accepted	2026-10-27 10:57:20.029773+05:30	3
\.


--
-- Data for Name: jobs_conversation; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs_conversation (id, created_at, updated_at, swipe_id) FROM stdin;
1	2026-10-20 16:34:40.655121+05:30	2026-10-20 18:58:15.98485+05:30	3
2	2026-10-20 19:06:28.963324+05:30	2026-10-20 19:07:31.007765+05:30	5
3	2026-10-27 10:57:20.041995+05:30	2026-10-27 11:52:13.685454+05:30	7
\.


--
-- Data for Name: jobs_jobbookmark; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs_jobbookmark (id, created_at, job_id, user_id) FROM stdin;
\.


--
-- Data for Name: jobs_message; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs_message (id, body, created_at, read_at, conversation_id, sender_id) FROM stdin;
1	hii raghu	2026-10-20 16:35:01.208925+05:30	\N	1	3
2	can we move further?	2026-10-20 16:35:35.487681+05:30	\N	1	3
3	whats your expections?	2026-10-20 18:55:30.805995+05:30	\N	1	3
4	hello	2026-10-20 18:58:15.978008+05:30	\N	1	3
5	hii	2026-10-20 19:06:49.196501+05:30	2026-10-20 19:07:05.248761+05:30	2	3
6	can we talk about requirements?	2026-10-20 19:07:30.987727+05:30	2026-10-20 19:07:49.477005+05:30	2	2
7	hii	2026-10-27 10:57:41.5335+05:30	2026-10-27 10:58:27.7669+05:30	3	3
9	Based on role?	2026-10-27 11:46:51.184833+05:30	\N	3	3
8	what are the requirements?	2026-10-27 11:46:32.162613+05:30	2026-10-27 11:51:57.714792+05:30	3	2
10	hii	2026-10-27 11:51:45.636449+05:30	2026-10-27 11:51:57.714792+05:30	3	2
11	hello	2026-10-27 11:52:06.21856+05:30	\N	3	2
12	hii	2026-10-27 11:52:13.683613+05:30	\N	3	3
\.


--
-- Name: accounts_jobpreference_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_jobpreference_id_seq', 2, true);


--
-- Name: accounts_profile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_profile_id_seq', 2, true);


--
-- Name: accounts_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_groups_id_seq', 1, false);


--
-- Name: accounts_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_id_seq', 3, true);


--
-- Name: accounts_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_user_permissions_id_seq', 1, false);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 60, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 14, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 15, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 24, true);


--
-- Name: jobs_company_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.jobs_company_id_seq', 7, true);


--
-- Name: jobs_companymembership_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.jobs_companymembership_id_seq', 1, true);


--
-- Name: jobs_conversation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.jobs_conversation_id_seq', 3, true);


--
-- Name: jobs_job_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.jobs_job_id_seq', 8, true);


--
-- Name: jobs_jobbookmark_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.jobs_jobbookmark_id_seq', 1, false);


--
-- Name: jobs_jobswipe_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.jobs_jobswipe_id_seq', 7, true);


--
-- Name: jobs_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.jobs_message_id_seq', 12, true);


--
-- PostgreSQL database dump complete
--

\unrestrict gBdQzb1fO52PNkZWZdp8cVyCFjqqQ4iUbha3KMj9zEM5bdTbgov8eUNyn9rgcsH

