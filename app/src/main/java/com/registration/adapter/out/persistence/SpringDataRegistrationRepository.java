package com.registration.adapter.out.persistence;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

/**
 * Spring Data JPA repository for {@link RegistrationJpaEntity}.
 */
public interface SpringDataRegistrationRepository
        extends JpaRepository<RegistrationJpaEntity, UUID> {

    Optional<RegistrationJpaEntity> findByEmail(String email);

    boolean existsByEmail(String email);
}
