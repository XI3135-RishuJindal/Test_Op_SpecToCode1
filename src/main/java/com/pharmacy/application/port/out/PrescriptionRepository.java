package com.pharmacy.application.port.out;

import com.pharmacy.domain.model.Prescription;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Outbound port — persistence contract for prescriptions.
 * Implemented by the JPA adapter.
 */
public interface PrescriptionRepository {

    Prescription save(Prescription prescription);

    Optional<Prescription> findById(UUID id);

    List<Prescription> findByPatientId(String patientId);

    void deleteById(UUID id);
}
