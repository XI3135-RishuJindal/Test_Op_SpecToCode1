package com.registration.application.port.in;

import com.registration.domain.model.Registration;

/**
 * Inbound port — use case for registering a new user.
 */
public interface RegisterUserUseCase {

    /**
     * Registers a new user.
     *
     * @param command the registration command containing user details
     * @return the newly created {@link Registration} domain object
     * @throws com.registration.domain.exception.EmailAlreadyRegisteredException if the email is taken
     */
    Registration registerUser(RegisterUserCommand command);
}
