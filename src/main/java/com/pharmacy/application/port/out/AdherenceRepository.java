package com.pharmacy.application.port.out;

import com.pharmacy.domain.model.AdherenceRecord;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Outbound port — persistence contract for adherence records.
 */
public interface AdherenceRepository {

    AdherenceRecord save(AdherenceRecord record);

    Optional<AdherenceRecord> findById(UUID id);

    List<AdherenceRecord> findByPatientId(String patientId);
}
