package com.pharmacy.domain.model;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Domain entity tracking whether a patient took their medication on schedule.
 */
public class AdherenceRecord {

    private UUID id;
    private String patientId;
    private UUID prescriptionId;
    private LocalDateTime scheduledTime;
    private LocalDateTime takenTime;
    private AdherenceStatus adherenceStatus;

    public AdherenceRecord() {}

    public AdherenceRecord(
            UUID id,
            String patientId,
            UUID prescriptionId,
            LocalDateTime scheduledTime,
            LocalDateTime takenTime,
            AdherenceStatus adherenceStatus) {
        this.id = id;
        this.patientId = patientId;
        this.prescriptionId = prescriptionId;
        this.scheduledTime = scheduledTime;
        this.takenTime = takenTime;
        this.adherenceStatus = adherenceStatus;
    }

    // ── Domain behaviour ──────────────────────────────────────────────────────

    public boolean isMissed() {
        return adherenceStatus == AdherenceStatus.MISSED;
    }

    public void markTaken(LocalDateTime takenAt) {
        this.takenTime = takenAt;
        this.adherenceStatus = AdherenceStatus.TAKEN;
    }

    // ── Getters / Setters ─────────────────────────────────────────────────────

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getPatientId() { return patientId; }
    public void setPatientId(String patientId) { this.patientId = patientId; }

    public UUID getPrescriptionId() { return prescriptionId; }
    public void setPrescriptionId(UUID prescriptionId) { this.prescriptionId = prescriptionId; }

    public LocalDateTime getScheduledTime() { return scheduledTime; }
    public void setScheduledTime(LocalDateTime scheduledTime) { this.scheduledTime = scheduledTime; }

    public LocalDateTime getTakenTime() { return takenTime; }
    public void setTakenTime(LocalDateTime takenTime) { this.takenTime = takenTime; }

    public AdherenceStatus getAdherenceStatus() { return adherenceStatus; }
    public void setAdherenceStatus(AdherenceStatus adherenceStatus) { this.adherenceStatus = adherenceStatus; }
}
