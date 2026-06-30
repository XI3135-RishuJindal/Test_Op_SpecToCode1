package com.pharmacy.adapter.out.persistence;

import com.pharmacy.application.port.out.AdherenceRepository;
import com.pharmacy.domain.model.AdherenceRecord;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Outbound adapter — bridges the domain AdherenceRepository port to JPA.
 */
@Component
public class AdherenceRepositoryAdapter implements AdherenceRepository {

    private final AdherenceRecordJpaRepository jpaRepository;

    public AdherenceRepositoryAdapter(AdherenceRecordJpaRepository jpaRepository) {
        this.jpaRepository = jpaRepository;
    }

    @Override
    public AdherenceRecord save(AdherenceRecord record) {
        AdherenceRecordEntity entity = AdherenceRecordEntity.fromDomain(record);
        return jpaRepository.save(entity).toDomain();
    }

    @Override
    public Optional<AdherenceRecord> findById(UUID id) {
        return jpaRepository.findById(id).map(AdherenceRecordEntity::toDomain);
    }

    @Override
    public List<AdherenceRecord> findByPatientId(String patientId) {
        return jpaRepository.findByPatientId(patientId)
                .stream()
                .map(AdherenceRecordEntity::toDomain)
                .collect(Collectors.toList());
    }
}
