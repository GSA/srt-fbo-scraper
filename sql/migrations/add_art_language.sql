BEGIN;

CREATE TABLE art_language (
    id SERIAL NOT NULL, 
    solicitation_id INTEGER, 
    language JSONB NOT NULL, 
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE, 
    CONSTRAINT pk_art_language PRIMARY KEY (id), 
    CONSTRAINT fk_art_language_solicitation_solicitations FOREIGN KEY(solicitation_id) REFERENCES solicitations (id)
);

INSERT INTO alembic_version (version_num) VALUES ('2e38f559933b') RETURNING alembic_version.version_num;

COMMIT;