package com.registration.adapter.out.persistence;

import com.registration.domain.model.Registration;
import org.springframework.stereotype.Component;

/**
 * Maps between the domain {@link Registration} and the JPA entity.
 */
@Component
public class RegistrationMapper {

    public RegistrationJpaEntity toJpaEntity(Registration domain) {
        return new RegistrationJpaEntity(
                domain.getId(),
                domain.getEmail(),
                domain.getUsername(),
                domain.getPasswordHash(),
                domain.getStatus(),
                domain.getVerificationToken(),
                domain.getVerificationTokenExpiresAt(),
                domain.getCreatedAt(),
                domain.getUpdatedAt());
    }

    public Registration toDomain(RegistrationJpaEntity entity) {
        return new Registration(
                entity.getId(),
                entity.getEmail(),
                entity.getUsername(),
                entity.getPasswordHash(),
                entity.getStatus(),
                entity.getVerificationToken(),
                entity.getVerificationTokenExpiresAt(),
                entity.getCreatedAt(),
                entity.getUpdatedAt());
    }
}
