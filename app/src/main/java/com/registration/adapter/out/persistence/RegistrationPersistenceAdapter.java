package com.registration.adapter.out.persistence;

import com.registration.application.port.out.RegistrationRepository;
import com.registration.domain.model.Registration;
import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.UUID;

/**
 * Outbound persistence adapter — bridges the domain port to Spring Data JPA.
 */
@Component
public class RegistrationPersistenceAdapter implements RegistrationRepository {

    private final SpringDataRegistrationRepository springDataRepo;
    private final RegistrationMapper mapper;

    public RegistrationPersistenceAdapter(
            SpringDataRegistrationRepository springDataRepo,
            RegistrationMapper mapper) {
        this.springDataRepo = springDataRepo;
        this.mapper = mapper;
    }

    @Override
    public Registration save(Registration registration) {
        RegistrationJpaEntity entity = mapper.toJpaEntity(registration);
        RegistrationJpaEntity saved = springDataRepo.save(entity);
        return mapper.toDomain(saved);
    }

    @Override
    public Optional<Registration> findById(UUID id) {
        return springDataRepo.findById(id).map(mapper::toDomain);
    }

    @Override
    public Optional<Registration> findByEmail(String email) {
        return springDataRepo.findByEmail(email).map(mapper::toDomain);
    }

    @Override
    public boolean existsByEmail(String email) {
        return springDataRepo.existsByEmail(email);
    }
}
