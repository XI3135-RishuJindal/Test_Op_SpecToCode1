package com.pharmacy.adapter.out.persistence;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

/**
 * Spring Data JPA repository for AdherenceRecordEntity.
 */
public interface AdherenceRecordJpaRepository extends JpaRepository<AdherenceRecordEntity, UUID> {

    List<AdherenceRecordEntity> findByPatientId(String patientId);
}
