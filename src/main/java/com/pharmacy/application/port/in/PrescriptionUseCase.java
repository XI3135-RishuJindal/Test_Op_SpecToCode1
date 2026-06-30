package com.pharmacy.application.port.in;

import com.pharmacy.domain.model.Prescription;

import java.util.List;
import java.util.UUID;

/**
 * Inbound port — prescription use cases.
 * Implemented by the application service; called by REST adapters.
 */
public interface PrescriptionUseCase {

    Prescription createPrescription(CreatePrescriptionCommand command);

    Prescription getPrescription(UUID id);

    List<Prescription> getPrescriptionsByPatient(String patientId);

    Prescription refillPrescription(UUID id);

    void cancelPrescription(UUID id);
}
