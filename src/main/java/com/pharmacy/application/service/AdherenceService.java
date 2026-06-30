package com.pharmacy.application.service;

import com.pharmacy.application.port.in.AdherenceUseCase;
import com.pharmacy.application.port.in.RecordAdherenceCommand;
import com.pharmacy.application.port.out.AdherenceRepository;
import com.pharmacy.domain.exception.AdherenceRecordNotFoundException;
import com.pharmacy.domain.model.AdherenceRecord;
import com.pharmacy.domain.model.AdherenceStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * Application service implementing medication adherence use cases.
 */
@Service
@Transactional
public class AdherenceService implements AdherenceUseCase {

    private final AdherenceRepository adherenceRepository;

    public AdherenceService(AdherenceRepository adherenceRepository) {
        this.adherenceRepository = adherenceRepository;
    }

    @Override
    public AdherenceRecord recordAdherence(RecordAdherenceCommand command) {
        AdherenceRecord record = new AdherenceRecord(
                UUID.randomUUID(),
                command.patientId(),
                command.prescriptionId(),
                command.scheduledTime(),
                null,
                AdherenceStatus.PENDING
        );
        return adherenceRepository.save(record);
    }

    @Override
    public AdherenceRecord markAsTaken(UUID adherenceRecordId, LocalDateTime takenAt) {
        AdherenceRecord record = adherenceRepository.findById(adherenceRecordId)
                .orElseThrow(() -> new AdherenceRecordNotFoundException(adherenceRecordId));
        record.markTaken(takenAt);
        return adherenceRepository.save(record);
    }

    @Override
    @Transactional(readOnly = true)
    public List<AdherenceRecord> getAdherenceByPatient(String patientId) {
        return adherenceRepository.findByPatientId(patientId);
    }

    @Override
    @Transactional(readOnly = true)
    public double calculateAdherenceRate(String patientId) {
        List<AdherenceRecord> records = adherenceRepository.findByPatientId(patientId);
        if (records.isEmpty()) {
            return 0.0;
        }
        long takenCount = records.stream()
                .filter(r -> r.getAdherenceStatus() == AdherenceStatus.TAKEN)
                .count();
        return (double) takenCount / records.size() * 100.0;
    }
}
