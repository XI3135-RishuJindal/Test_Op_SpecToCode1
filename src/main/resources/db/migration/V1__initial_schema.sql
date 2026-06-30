-- V1: Initial schema for Pharmacy Microservice

CREATE TABLE IF NOT EXISTS prescriptions (
    id               UUID         NOT NULL PRIMARY KEY,
    patient_id       VARCHAR(255) NOT NULL,
    medication_name  VARCHAR(255) NOT NULL,
    dosage           VARCHAR(100) NOT NULL,
    quantity_prescribed INT       NOT NULL,
    refills_remaining   INT       NOT NULL DEFAULT 0,
    issued_date      DATE         NOT NULL,
    expiry_date      DATE         NOT NULL,
    status           VARCHAR(50)  NOT NULL
);

CREATE INDEX idx_prescriptions_patient_id ON prescriptions (patient_id);

CREATE TABLE IF NOT EXISTS adherence_records (
    id               UUID         NOT NULL PRIMARY KEY,
    patient_id       VARCHAR(255) NOT NULL,
    prescription_id  UUID         NOT NULL REFERENCES prescriptions(id),
    scheduled_time   TIMESTAMP    NOT NULL,
    taken_time       TIMESTAMP,
    adherence_status VARCHAR(50)  NOT NULL
);

CREATE INDEX idx_adherence_patient_id ON adherence_records (patient_id);
