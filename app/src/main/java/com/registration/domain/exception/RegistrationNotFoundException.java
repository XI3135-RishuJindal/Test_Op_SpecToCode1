package com.registration.domain.exception;

/**
 * Thrown when a registration is not found by a given identifier.
 */
public class RegistrationNotFoundException extends RuntimeException {

    public RegistrationNotFoundException(String message) {
        super(message);
    }
}
