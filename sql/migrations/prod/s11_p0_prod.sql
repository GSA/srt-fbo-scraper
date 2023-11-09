BEGIN;

-- Running upgrade  -> 06c9149baecd

-- DROP TABLE solicitations_pre_dla_update_oct_2021;

ALTER TABLE "Agencies" ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE "Predictions" ALTER COLUMN "noticeType" DROP NOT NULL;

ALTER TABLE "Predictions" ALTER COLUMN "createdAt" SET NOT NULL;

ALTER TABLE "Predictions" DROP CONSTRAINT "uniqueSolNum";

ALTER TABLE "Predictions" ADD CONSTRAINT "uq_Predictions_solNum" UNIQUE ("solNum");

ALTER TABLE "Surveys" ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE "Users" ALTER COLUMN "updatedAt" DROP NOT NULL;

ALTER TABLE agency_alias ALTER COLUMN agency_id DROP NOT NULL;

ALTER TABLE notice_type ALTER COLUMN "createdAt" SET NOT NULL;

ALTER TABLE solicitations ALTER COLUMN "solNum" SET NOT NULL;

ALTER TABLE solicitations ALTER COLUMN "createdAt" SET NOT NULL;

ALTER TABLE solicitations DROP CONSTRAINT "solicitations_solNum_key";

ALTER TABLE solicitations ADD CONSTRAINT "uq_solicitations_solNum" UNIQUE ("solNum");

ALTER TABLE survey_responses ALTER COLUMN "createdAt" SET NOT NULL;

DROP INDEX "ix_feedback_solNum";

CREATE INDEX "ix_survey_responses_solNum" ON survey_responses ("solNum");

ALTER TABLE survey_responses_archive ALTER COLUMN "createdAt" SET NOT NULL;

COMMIT;

