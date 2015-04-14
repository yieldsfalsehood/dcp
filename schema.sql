-- A simple schema with data for testing.

-- Build the schema.
CREATE SCHEMA media;

CREATE TABLE media.distributors (
  id bigserial PRIMARY KEY,
  name text NOT NULL
);

CREATE TABLE media.movies (
  id bigserial PRIMARY KEY,
  distributor bigserial REFERENCES media.distributors,
  name text NOT NULL,
  code text
);

CREATE TABLE types (
  id bigserial PRIMARY KEY,
  name text NOT NULL
);

-- Copy in the data.
COPY media.distributors (id, name) FROM stdin;
1	new videos
2	old videos
3	cat videos
\.

SELECT pg_catalog.setval('media.distributors_id_seq', 3, true);

COPY media.movies (id, distributor, name, code) FROM stdin;
3	1	Something Techish	\N
4	1	A Dystopian Future	\N
1	1	The New Superheroes	\N
2	2	A Generic Western	12345ABC
5	2	A Black and White Romance	5
6	3	A Startled Cat	\N
7	3	A Cute Kitten	\N
\.

SELECT pg_catalog.setval('media.movies_id_seq', 7, true);

COPY types (id, name) FROM stdin;
1	social
2	movies
3	articles
\.

SELECT pg_catalog.setval('types_id_seq', 3, true);
