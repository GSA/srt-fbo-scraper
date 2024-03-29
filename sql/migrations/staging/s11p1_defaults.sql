ALTER TABLE "Agencies" ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE "Predictions" ADD COLUMN "eitLikelihood" JSONB;

ALTER TABLE "Predictions" ADD COLUMN active BOOLEAN DEFAULT true;

ALTER TABLE "Predictions" ALTER COLUMN title SET NOT NULL;

ALTER TABLE "Predictions" ALTER COLUMN "solNum" SET NOT NULL;

ALTER TABLE "Predictions" ALTER COLUMN "noticeType" SET NOT NULL;

ALTER TABLE "Predictions" ALTER COLUMN "createdAt" SET NOT NULL;

ALTER TABLE "Predictions" ALTER COLUMN history SET DEFAULT '[]'::jsonb;

ALTER TABLE "Predictions" ADD UNIQUE ("solNum");

ALTER TABLE "Predictions" DROP COLUMN feedback;

ALTER TABLE "Predictions" DROP COLUMN category_list;

ALTER TABLE "Surveys" ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE "Users" ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE agency_alias ALTER COLUMN agency_id SET NOT NULL;

ALTER TABLE agency_alias ALTER COLUMN "createdAt" SET NOT NULL;

ALTER TABLE agency_alias ALTER COLUMN "createdAt" SET DEFAULT now();

ALTER TABLE agency_alias ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE notice_type ADD COLUMN "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now();

ALTER TABLE notice_type ADD COLUMN "updatedAt" TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE survey_responses ALTER COLUMN "createdAt" SET NOT NULL;

CREATE INDEX "ix_survey_responses_solNum" ON survey_responses ("solNum");

ALTER TABLE survey_responses_archive ALTER COLUMN "createdAt" SET NOT NULL;

ALTER TABLE survey_responses_archive ALTER COLUMN "createdAt" SET DEFAULT now();

ALTER TABLE survey_responses_archive ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE survey_responses_archive ALTER COLUMN response SET DEFAULT '[]'::jsonb;

ALTER TABLE solicitations ALTER COLUMN "createdAt" SET DEFAULT now();

ALTER TABLE solicitations ADD UNIQUE ("solNum");

ALTER TABLE solicitations ALTER COLUMN history SET DEFAULT '[]'::jsonb;

UPDATE solicitations SET history = '[]'::jsonb WHERE history IS NULL;

ALTER TABLE solicitations ALTER COLUMN action SET DEFAULT '[]'::jsonb;

ALTER TABLE solicitations ALTER COLUMN predictions SET DEFAULT '{"value": "red", "history": []}'::jsonb;

ALTER TABLE solicitations ALTER COLUMN compliant SET DEFAULT 0;

ALTER TABLE solicitations ALTER COLUMN active SET DEFAULT true;

ALTER TABLE solicitations ALTER COLUMN na_flag SET DEFAULT false;

ALTER TABLE solicitations ALTER COLUMN title type character varying;

ALTER TABLE solicitations ALTER COLUMN url type character varying;

ALTER TABLE solicitations ALTER COLUMN agency type character varying;

ALTER TABLE solicitations ALTER COLUMN "noticeType" type character varying;

ALTER TABLE solicitations ALTER COLUMN office type character varying;

ALTER TABLE solicitations ALTER COLUMN "actionStatus" type character varying;

ALTER TABLE solicitations ALTER COLUMN "reviewRec" type character varying;

ALTER TABLE solicitations ALTER COLUMN "searchText" type character varying;

ALTER TABLE attachment ALTER COLUMN "createdAt" SET NOT NULL;

ALTER TABLE attachment ALTER COLUMN "createdAt" SET DEFAULT now();

ALTER TABLE notice ALTER COLUMN "createdAt" SET NOT NULL;

ALTER TABLE notice ALTER COLUMN "createdAt" SET DEFAULT now();

ALTER TABLE notice_type ALTER COLUMN "createdAt" SET DEFAULT now();



