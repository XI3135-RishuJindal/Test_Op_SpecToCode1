package com.pharmacy.adapter.out.persistence;

import com.pharmacy.application.port.out.PrescriptionRepository;
import com.pharmacy.domain.model.Prescription;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Outbound adapter — bridges the domain PrescriptionRepository port to JPA.
 */
@Component
public class PrescriptionRepositoryAdapter implements PrescriptionRepository {

    private final PrescriptionJpaRepository jpaRepository;

    public PrescriptionRepositoryAdapter(PrescriptionJpaRepository jpaRepository) {
        this.jpaRepository = jpaRepository;
    }

    @Override
    public Prescription save(Prescription prescription) {
        PrescriptionEntity entity = PrescriptionEntity.fromDomain(prescription);
        return jpaRepository.save(entity).toDomain();
    }

    @Override
    public Optional<Prescription> findById(UUID id) {
        return jpaRepository.findById(id).map(PrescriptionEntity::toDomain);
    }

    @Override
    public List<Prescription> findByPatientId(String patientId) {
        return jpaRepository.findByPatientId(patientId)
                .stream()
                .map(PrescriptionEntity::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public void deleteById(UUID id) {
        jpaRepository.deleteById(id);
    }
}
