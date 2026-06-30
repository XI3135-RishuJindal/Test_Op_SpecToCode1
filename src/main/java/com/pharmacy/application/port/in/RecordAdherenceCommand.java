package com.pharmacy.application.port.in;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Command object for recording a scheduled adherence event.
 */
public record RecordAdherenceCommand(
        @NotBlank String patientId,
        @NotNull UUID prescriptionId,
        @NotNull LocalDateTime scheduledTime
) {}
