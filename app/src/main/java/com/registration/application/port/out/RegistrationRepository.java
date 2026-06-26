package com.registration.application.port.out;

import com.registration.domain.model.Registration;

import java.util.Optional;
import java.util.UUID;

/**
 * Outbound port — persistence operations for {@link Registration}.
 */
public interface RegistrationRepository {

    /**
     * Persists a new or updated registration.
     *
     * @param registration the registration to save
     * @return the saved registration
     */
    Registration save(Registration registration);

    /**
     * Finds a registration by its unique identifier.
     *
     * @param id the registration ID
     * @return an {@link Optional} containing the registration, or empty if not found
     */
    Optional<Registration> findById(UUID id);

    /**
     * Finds a registration by email address.
     *
     * @param email the email address
     * @return an {@link Optional} containing the registration, or empty if not found
     */
    Optional<Registration> findByEmail(String email);

    /**
     * Checks whether a registration with the given email already exists.
     *
     * @param email the email address
     * @return {@code true} if a registration exists, {@code false} otherwise
     */
    boolean existsByEmail(String email);
}
