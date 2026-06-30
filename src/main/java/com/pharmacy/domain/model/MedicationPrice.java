package com.pharmacy.domain.model;

import java.math.BigDecimal;
import java.util.UUID;

/**
 * Domain entity representing a medication price at a specific pharmacy.
 */
public class MedicationPrice {

    private UUID id;
    private String medicationName;
    private String pharmacyName;
    private String pharmacyLocation;
    private BigDecimal price;
    private String currency;

    public MedicationPrice() {}

    public MedicationPrice(
            UUID id,
            String medicationName,
            String pharmacyName,
            String pharmacyLocation,
            BigDecimal price,
            String currency) {
        this.id = id;
        this.medicationName = medicationName;
        this.pharmacyName = pharmacyName;
        this.pharmacyLocation = pharmacyLocation;
        this.price = price;
        this.currency = currency;
    }

    // ── Getters / Setters ─────────────────────────────────────────────────────

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getMedicationName() { return medicationName; }
    public void setMedicationName(String medicationName) { this.medicationName = medicationName; }

    public String getPharmacyName() { return pharmacyName; }
    public void setPharmacyName(String pharmacyName) { this.pharmacyName = pharmacyName; }

    public String getPharmacyLocation() { return pharmacyLocation; }
    public void setPharmacyLocation(String pharmacyLocation) { this.pharmacyLocation = pharmacyLocation; }

    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }

    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }
}
