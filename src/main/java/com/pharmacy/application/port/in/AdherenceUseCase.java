package com.pharmacy.application.port.in;

import com.pharmacy.domain.model.AdherenceRecord;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * Inbound port — medication adherence use cases.
 */
public interface AdherenceUseCase {

    AdherenceRecord recordAdherence(RecordAdherenceCommand command);

    AdherenceRecord markAsTaken(UUID adherenceRecordId, LocalDateTime takenAt);

    List<AdherenceRecord> getAdherenceByPatient(String patientId);

    double calculateAdherenceRate(String patientId);
}
