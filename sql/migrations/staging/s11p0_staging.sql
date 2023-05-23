BEGIN;

-- Running upgrade  -> b0cbeeb30c9b

CREATE SEQUENCE "Predictions_id_seq";

CREATE TABLE "Predictions" (
    id INTEGER DEFAULT nextval('"Predictions_id_seq"'::regclass) NOT NULL, 
    title VARCHAR NOT NULL, 
    url VARCHAR, 
    agency VARCHAR, 
    "numDocs" INTEGER, 
    "solNum" VARCHAR NOT NULL, 
    "noticeType" VARCHAR NOT NULL, 
    date TIMESTAMP WITHOUT TIME ZONE, 
    office VARCHAR, 
    na_flag BOOLEAN, 
    "eitLikelihood" JSONB, 
    undetermined BOOLEAN, 
    action JSONB, 
    "actionStatus" VARCHAR, 
    "actionDate" TIMESTAMP WITHOUT TIME ZONE, 
    history JSONB, 
    "contactInfo" JSONB, 
    "parseStatus" JSONB, 
    predictions JSONB, 
    "reviewRec" VARCHAR, 
    "searchText" VARCHAR, 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    active BOOLEAN DEFAULT true, 
    PRIMARY KEY (id), 
    UNIQUE ("solNum")
);

CREATE SEQUENCE "Surveys_id_seq";

CREATE TABLE "Surveys" (
    id INTEGER DEFAULT nextval('"Surveys_id_seq"'::regclass) NOT NULL, 
    question TEXT, 
    choices JSONB, 
    section VARCHAR(2000), 
    type VARCHAR(2000), 
    answer TEXT, 
    note TEXT, 
    "choicesNote" JSONB, 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE SEQUENCE agency_alias_id_seq;

CREATE TABLE agency_alias (
    id INTEGER DEFAULT nextval('agency_alias_id_seq'::regclass) NOT NULL, 
    agency_id INTEGER NOT NULL, 
    alias VARCHAR, 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE SEQUENCE model_id_seq;

CREATE TABLE model (
    id INTEGER DEFAULT nextval('model_id_seq'::regclass) NOT NULL, 
    results JSONB, 
    params JSONB, 
    score FLOAT(53), 
    create_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id)
);

CREATE SEQUENCE notice_type_id_seq;

CREATE TABLE notice_type (
    id INTEGER DEFAULT nextval('notice_type_id_seq'::regclass) NOT NULL, 
    notice_type VARCHAR(50), 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_notice_type_notice_type ON notice_type (notice_type);

CREATE TABLE survey_backup (
    id SERIAL, 
    question TEXT, 
    choices JSONB, 
    section VARCHAR(2000), 
    type VARCHAR(2000), 
    answer TEXT, 
    note TEXT, 
    "choicesNote" JSONB, 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE SEQUENCE survey_responses_id_seq;

CREATE TABLE survey_responses (
    id INTEGER DEFAULT nextval('survey_responses_id_seq'::regclass) NOT NULL, 
    "solNum" VARCHAR, 
    contemporary_notice_id INTEGER, 
    response JSONB DEFAULT '[]'::jsonb, 
    "maxId" VARCHAR(256), 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE INDEX "ix_survey_responses_solNum" ON survey_responses ("solNum");

CREATE SEQUENCE survey_responses_archive_id_seq;

CREATE TABLE survey_responses_archive (
    id INTEGER DEFAULT nextval('survey_responses_archive_id_seq'::regclass) NOT NULL, 
    "solNum" VARCHAR, 
    contemporary_notice_id INTEGER, 
    response JSONB DEFAULT '[]'::jsonb, 
    "maxId" VARCHAR(256), 
    original_created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE TABLE winston_logs (
    timestamp TIMESTAMP WITH TIME ZONE, 
    level VARCHAR(255), 
    message TEXT, 
    meta JSONB
);

CREATE SEQUENCE attachment_id_seq;

CREATE TABLE attachment (
    id INTEGER DEFAULT nextval('attachment_id_seq'::regclass) NOT NULL, 
    notice_id INTEGER, 
    notice_type_id INTEGER, 
    machine_readable BOOLEAN, 
    attachment_text TEXT, 
    prediction INTEGER, 
    decision_boundary FLOAT(53), 
    validation INTEGER, 
    attachment_url TEXT, 
    trained BOOLEAN, 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    filename TEXT NOT NULL, 
    solicitation_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(notice_type_id) REFERENCES notice_type (id), 
    FOREIGN KEY(solicitation_id) REFERENCES solicitations (id)
);

CREATE SEQUENCE notice_id_seq;

CREATE TABLE notice (
    id INTEGER DEFAULT nextval('notice_id_seq'::regclass) NOT NULL, 
    notice_type_id INTEGER, 
    solicitation_number VARCHAR(150), 
    agency VARCHAR(150), 
    date TIMESTAMP WITHOUT TIME ZONE, 
    notice_data JSONB, 
    compliant INTEGER, 
    feedback JSONB, 
    history JSONB, 
    action JSONB, 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    na_flag BOOLEAN, 
    PRIMARY KEY (id), 
    FOREIGN KEY(notice_type_id) REFERENCES notice_type (id)
);

CREATE INDEX ix_notice_solicitation_number ON notice (solicitation_number);

ALTER TABLE "Agencies" ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE "Users" ADD COLUMN "maxId" VARCHAR(256);

ALTER TABLE "Users" ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE solicitations ADD UNIQUE ("solNum");

ALTER TABLE solicitations ADD UNIQUE ("solNum");

ALTER TABLE solicitations ALTER COLUMN history SET DEFAULT '[]'::jsonb;

ALTER TABLE solicitations ALTER COLUMN action SET DEFAULT '[]'::jsonb;

ALTER TABLE solicitations ALTER COLUMN predictions SET DEFAULT '{"value": "red", "history": []}'::jsonb;

ALTER TABLE solicitations ALTER COLUMN compliant SET DEFAULT 0;

ALTER TABLE solicitations ALTER COLUMN active SET DEFAULT true;

ALTER TABLE solicitations ALTER COLUMN na_flag SET DEFAULT false;

ALTER TABLE solicitations ALTER COLUMN "updatedAt" DROP NOT NULL;

COMMIT;

