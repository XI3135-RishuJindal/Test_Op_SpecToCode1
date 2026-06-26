-- Flyway migration: initial schema for the registration service

CREATE TABLE IF NOT EXISTS registrations (
    id                              UUID            NOT NULL,
    email                           VARCHAR(255)    NOT NULL,
    username                        VARCHAR(50)     NOT NULL,
    password_hash                   TEXT            NOT NULL,
    status                          VARCHAR(30)     NOT NULL DEFAULT 'PENDING_VERIFICATION',
    verification_token              VARCHAR(255),
    verification_token_expires_at   TIMESTAMPTZ,
    created_at                      TIMESTAMPTZ     NOT NULL,
    updated_at                      TIMESTAMPTZ     NOT NULL,

    CONSTRAINT pk_registrations PRIMARY KEY (id),
    CONSTRAINT uq_registrations_email UNIQUE (email)
);

CREATE INDEX IF NOT EXISTS idx_registrations_email ON registrations (email);
