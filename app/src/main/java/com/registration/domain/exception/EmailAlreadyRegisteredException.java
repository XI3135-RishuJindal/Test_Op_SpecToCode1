package com.registration.domain.exception;

/**
 * Thrown when a registration attempt is made with an email that already exists.
 */
public class EmailAlreadyRegisteredException extends RuntimeException {

    private final String email;

    public EmailAlreadyRegisteredException(String email) {
        super("Email is already registered: " + email);
        this.email = email;
    }

    public String getEmail() {
        return email;
    }
}
