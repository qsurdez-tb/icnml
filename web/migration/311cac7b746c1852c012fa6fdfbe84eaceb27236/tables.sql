-- public.cnm_data definition

-- Drop table

-- DROP TABLE public.cnm_data;

CREATE TABLE public.cnm_data (
	id int4 NOT NULL DEFAULT nextval('cnm_annotation_id_seq'::regclass),
	uuid uuid NOT NULL,
	folder_uuid uuid NOT NULL,
	"data" varchar NULL,
	type_id int4 NULL
);

-- Permissions

ALTER TABLE public.cnm_data OWNER TO icnml;
GRANT ALL ON TABLE public.cnm_data TO icnml;

-- public.cnm_folder definition

-- Drop table

-- DROP TABLE public.cnm_folder;

CREATE TABLE public.cnm_folder (
	id serial NOT NULL,
	uuid uuid NOT NULL,
	pc int4 NOT NULL,
	donor_id int4 NOT NULL
);

-- Permissions

ALTER TABLE public.cnm_folder OWNER TO icnml;
GRANT ALL ON TABLE public.cnm_folder TO icnml;

-- public.donor_segments_v source

CREATE OR REPLACE VIEW public.donor_segments_v
AS SELECT submissions.donor_id,
    files_segments.tenprint,
    files_segments.pc,
    files_segments.uuid
   FROM submissions
     JOIN files ON files.folder = submissions.id
     JOIN files_segments ON files_segments.tenprint = files.uuid;

-- Permissions

ALTER TABLE public.donor_segments_v OWNER TO icnml;
GRANT ALL ON TABLE public.donor_segments_v TO icnml;

-- public.cnm_data_type definition

-- Drop table

-- DROP TABLE public.cnm_data_type;

CREATE TABLE public.cnm_data_type (
	id serial NOT NULL,
	"name" varchar NOT NULL
);

-- Permissions

ALTER TABLE public.cnm_data_type OWNER TO icnml;
GRANT ALL ON TABLE public.cnm_data_type TO icnml;

INSERT INTO public.cnm_data_type ("name") VALUES
	 ('annotation'),
	 ('cnm');

-- public.fingers_same definition

-- Drop table

-- DROP TABLE public.fingers_same;

CREATE TABLE public.fingers_same (
	id serial NOT NULL,
	base_finger int4 NOT NULL,
	target int4 NOT NULL
);

-- Permissions

ALTER TABLE public.fingers_same OWNER TO icnml;
GRANT ALL ON TABLE public.fingers_same TO icnml;

INSERT INTO public.fingers_same (base_finger,target) VALUES
	 (1,11),
	 (2,13),
	 (3,13),
	 (4,13),
	 (5,13),
	 (6,12),
	 (7,14),
	 (8,14),
	 (9,14),
	 (10,14);
INSERT INTO public.fingers_same (base_finger,target) VALUES
	 (1,1),
	 (2,2),
	 (3,3),
	 (4,4),
	 (5,5),
	 (6,6),
	 (7,7),
	 (8,8),
	 (9,9),
	 (10,10);
INSERT INTO public.fingers_same (base_finger,target) VALUES
	 (22,22),
	 (24,24),
	 (25,25),
	 (27,27);
    
-- public.cnm_assignment definition

-- Drop table

-- DROP TABLE public.cnm_assignment;

CREATE TABLE public.cnm_assignment (
	id serial NOT NULL,
	folder_uuid uuid NOT NULL,
	user_id int4 NOT NULL,
	assignment_type int4 NULL
);

-- Permissions

ALTER TABLE public.cnm_assignment OWNER TO icnml;
GRANT ALL ON TABLE public.cnm_assignment TO icnml;


-- public.cnm_assignment_type definition

-- Drop table

-- DROP TABLE public.cnm_assignment_type;

CREATE TABLE public.cnm_assignment_type (
	id serial NOT NULL,
	"name" varchar NOT NULL
);

-- Permissions

ALTER TABLE public.cnm_assignment_type OWNER TO icnml;
GRANT ALL ON TABLE public.cnm_assignment_type TO icnml;

INSERT INTO public.cnm_assignment_type ("name") VALUES
	 ('reference'),
	 ('mark');
    
