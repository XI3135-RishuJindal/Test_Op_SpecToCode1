package com.pharmacy.adapter.out.persistence;

import com.pharmacy.domain.model.AdherenceRecord;
import com.pharmacy.domain.model.AdherenceStatus;
import jakarta.persistence.*;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * JPA entity for AdherenceRecord persistence.
 */
@Entity
@Table(name = "adherence_records")
public class AdherenceRecordEntity {

    @Id
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    @Column(name = "patient_id", nullable = false)
    private String patientId;

    @Column(name = "prescription_id", nullable = false)
    private UUID prescriptionId;

    @Column(name = "scheduled_time", nullable = false)
    private LocalDateTime scheduledTime;

    @Column(name = "taken_time")
    private LocalDateTime takenTime;

    @Enumerated(EnumType.STRING)
    @Column(name = "adherence_status", nullable = false)
    private AdherenceStatus adherenceStatus;

    public AdherenceRecordEntity() {}

    public static AdherenceRecordEntity fromDomain(AdherenceRecord domain) {
        AdherenceRecordEntity entity = new AdherenceRecordEntity();
        entity.id = domain.getId();
        entity.patientId = domain.getPatientId();
        entity.prescriptionId = domain.getPrescriptionId();
        entity.scheduledTime = domain.getScheduledTime();
        entity.takenTime = domain.getTakenTime();
        entity.adherenceStatus = domain.getAdherenceStatus();
        return entity;
    }

    public AdherenceRecord toDomain() {
        return new AdherenceRecord(id, patientId, prescriptionId, scheduledTime, takenTime, adherenceStatus);
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
