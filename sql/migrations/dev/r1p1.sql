BEGIN;

-- Running upgrade  -> 3df0b576624f

ALTER TABLE survey_responses ADD CONSTRAINT survey_responses_pkey PRIMARY KEY (id);

CREATE SEQUENCE survey_responses_id_seq;

ALTER TABLE survey_responses ALTER COLUMN id SET DEFAULT nextval('survey_responses_id_seq');

ALTER TABLE "Predictions" ADD COLUMN active BOOLEAN;

-- ALTER TABLE notice ADD CONSTRAINT fk_notice_notice_type_id_notice_type FOREIGN KEY(notice_type_id) REFERENCES notice_type (id);

INSERT INTO alembic_version (version_num) VALUES ('3df0b576624f') RETURNING alembic_version.version_num;

COMMIT;

