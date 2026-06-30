package com.pharmacy.application.service;

import com.pharmacy.application.port.in.CreatePrescriptionCommand;
import com.pharmacy.application.port.in.PrescriptionUseCase;
import com.pharmacy.application.port.out.PrescriptionRepository;
import com.pharmacy.domain.exception.PrescriptionNotFoundException;
import com.pharmacy.domain.model.Prescription;
import com.pharmacy.domain.model.PrescriptionStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

/**
 * Application service implementing prescription use cases.
 * Orchestrates domain logic and delegates persistence to the outbound port.
 */
@Service
@Transactional
public class PrescriptionService implements PrescriptionUseCase {

    private final PrescriptionRepository prescriptionRepository;

    public PrescriptionService(PrescriptionRepository prescriptionRepository) {
        this.prescriptionRepository = prescriptionRepository;
    }

    @Override
    public Prescription createPrescription(CreatePrescriptionCommand command) {
        Prescription prescription = new Prescription(
                UUID.randomUUID(),
                command.patientId(),
                command.medicationName(),
                command.dosage(),
                command.quantityPrescribed(),
                command.refillsAllowed(),
                command.issuedDate(),
                command.expiryDate(),
                PrescriptionStatus.ACTIVE
        );
        return prescriptionRepository.save(prescription);
    }

    @Override
    @Transactional(readOnly = true)
    public Prescription getPrescription(UUID id) {
        return prescriptionRepository.findById(id)
                .orElseThrow(() -> new PrescriptionNotFoundException(id));
    }

    @Override
    @Transactional(readOnly = true)
    public List<Prescription> getPrescriptionsByPatient(String patientId) {
        return prescriptionRepository.findByPatientId(patientId);
    }

    @Override
    public Prescription refillPrescription(UUID id) {
        Prescription prescription = getPrescription(id);
        prescription.refill();
        return prescriptionRepository.save(prescription);
    }

    @Override
    public void cancelPrescription(UUID id) {
        Prescription prescription = getPrescription(id);
        prescription.setStatus(PrescriptionStatus.CANCELLED);
        prescriptionRepository.save(prescription);
    }
}
