package com.pharmacy.adapter.out.persistence;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

/**
 * Spring Data JPA repository for PrescriptionEntity.
 */
public interface PrescriptionJpaRepository extends JpaRepository<PrescriptionEntity, UUID> {

    List<PrescriptionEntity> findByPatientId(String patientId);
}
