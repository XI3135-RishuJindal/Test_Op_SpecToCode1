package com.pharmacy.domain.model;

import java.time.LocalDate;
import java.util.UUID;

/**
 * Core domain entity representing a prescription.
 * Pure domain object — no framework dependencies.
 */
public class Prescription {

    private UUID id;
    private String patientId;
    private String medicationName;
    private String dosage;
    private int quantityPrescribed;
    private int refillsRemaining;
    private LocalDate issuedDate;
    private LocalDate expiryDate;
    private PrescriptionStatus status;

    public Prescription() {}

    public Prescription(
            UUID id,
            String patientId,
            String medicationName,
            String dosage,
            int quantityPrescribed,
            int refillsRemaining,
            LocalDate issuedDate,
            LocalDate expiryDate,
            PrescriptionStatus status) {
        this.id = id;
        this.patientId = patientId;
        this.medicationName = medicationName;
        this.dosage = dosage;
        this.quantityPrescribed = quantityPrescribed;
        this.refillsRemaining = refillsRemaining;
        this.issuedDate = issuedDate;
        this.expiryDate = expiryDate;
        this.status = status;
    }

    // ── Domain behaviour ──────────────────────────────────────────────────────

    public boolean isExpired() {
        return LocalDate.now().isAfter(expiryDate);
    }

    public boolean canRefill() {
        return refillsRemaining > 0 && !isExpired() && status == PrescriptionStatus.ACTIVE;
    }

    public void refill() {
        if (!canRefill()) {
            throw new IllegalStateException("Prescription cannot be refilled.");
        }
        this.refillsRemaining--;
    }

    public void cancel() {
        this.status = PrescriptionStatus.CANCELLED;
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
