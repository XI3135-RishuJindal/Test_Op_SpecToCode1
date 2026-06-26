package com.registration.adapter.in.web;

import com.registration.domain.model.Registration;

import java.time.Instant;
import java.util.UUID;

/**
 * HTTP response body returned after a successful registration.
 */
public record RegistrationResponse(
        UUID id,
        String email,
        String username,
        String status,
        Instant createdAt
) {
    public static RegistrationResponse from(Registration registration) {
        return new RegistrationResponse(
                registration.getId(),
                registration.getEmail(),
                registration.getUsername(),
                registration.getStatus().name(),
                registration.getCreatedAt());
    }
}
