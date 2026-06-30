package com.pharmacy.adapter.out.persistence;

import com.pharmacy.domain.model.Prescription;
import com.pharmacy.domain.model.PrescriptionStatus;
import jakarta.persistence.*;

import java.time.LocalDate;
import java.util.UUID;

/**
 * JPA entity for Prescription persistence.
 */
@Entity
@Table(name = "prescriptions")
public class PrescriptionEntity {

    @Id
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    @Column(name = "patient_id", nullable = false)
    private String patientId;

    @Column(name = "medication_name", nullable = false)
    private String medicationName;

    @Column(name = "dosage", nullable = false)
    private String dosage;

    @Column(name = "quantity_prescribed", nullable = false)
    private int quantityPrescribed;

    @Column(name = "refills_remaining", nullable = false)
    private int refillsRemaining;

    @Column(name = "issued_date", nullable = false)
    private LocalDate issuedDate;

    @Column(name = "expiry_date", nullable = false)
    private LocalDate expiryDate;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    private PrescriptionStatus status;

    public PrescriptionEntity() {}

    // ── Mapping helpers ───────────────────────────────────────────────────────

    public static PrescriptionEntity fromDomain(Prescription domain) {
        PrescriptionEntity entity = new PrescriptionEntity();
        entity.id = domain.getId();
        entity.patientId = domain.getPatientId();
        entity.medicationName = domain.getMedicationName();
        entity.dosage = domain.getDosage();
        entity.quantityPrescribed = domain.getQuantityPrescribed();
        entity.refillsRemaining = domain.getRefillsRemaining();
        entity.issuedDate = domain.getIssuedDate();
        entity.expiryDate = domain.getExpiryDate();
        entity.status = domain.getStatus();
        return entity;
    }

    public Prescription toDomain() {
        return new Prescription(id, patientId, medicationName, dosage,
                quantityPrescribed, refillsRemaining,
                issuedDate, expiryDate, status);
    }

    // ── Getters / Setters ─────────────────────────────────────────────────────

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }
    public String getPatientId() { return patientId; }
    public void setPatientId(String patientId) { this.patientId = patientId; }
    public String getMedicationName() { return medicationName; }
    public void setMedicationName(String medicationName) { this.medicationName = medicationName; }
    public String getDosage() { return dosage; }
    public void setDosage(String dosage) { this.dosage = dosage; }
    public int getQuantityPrescribed() { return quantityPrescribed; }
    public void setQuantityPrescribed(int quantityPrescribed) { this.quantityPrescribed = quantityPrescribed; }
    public int getRefillsRemaining() { return refillsRemaining; }
    public void setRefillsRemaining(int refillsRemaining) { this.refillsRemaining = refillsRemaining; }
    public LocalDate getIssuedDate() { return issuedDate; }
    public void setIssuedDate(LocalDate issuedDate) { this.issuedDate = issuedDate; }
    public LocalDate getExpiryDate() { return expiryDate; }
    public void setExpiryDate(LocalDate expiryDate) { this.expiryDate = expiryDate; }
    public PrescriptionStatus getStatus() { return status; }
    public void setStatus(PrescriptionStatus status) { this.status = status; }
}
