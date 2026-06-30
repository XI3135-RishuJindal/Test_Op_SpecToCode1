package com.pharmacy.application.port.in;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

import java.time.LocalDate;

/**
 * Command object for creating a new prescription.
 */
public record CreatePrescriptionCommand(
        @NotBlank String patientId,
        @NotBlank String medicationName,
        @NotBlank String dosage,
        @Positive int quantityPrescribed,
        @Positive int refillsAllowed,
        @NotNull LocalDate issuedDate,
        @NotNull LocalDate expiryDate
) {}
