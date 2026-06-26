package com.registration.domain.model;

import java.time.Instant;
import java.util.UUID;

/**
 * Core domain entity representing a user registration.
 * This is a plain Java object — no framework annotations here.
 */
public class Registration {

    private final UUID id;
    private final String email;
    private final String username;
    private final String passwordHash;
    private RegistrationStatus status;
    private String verificationToken;
    private Instant verificationTokenExpiresAt;
    private final Instant createdAt;
    private Instant updatedAt;

    public Registration(
            UUID id,
            String email,
            String username,
            String passwordHash,
            RegistrationStatus status,
            String verificationToken,
            Instant verificationTokenExpiresAt,
            Instant createdAt,
            Instant updatedAt) {
        this.id = id;
        this.email = email;
        this.username = username;
        this.passwordHash = passwordHash;
        this.status = status;
        this.verificationToken = verificationToken;
        this.verificationTokenExpiresAt = verificationTokenExpiresAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    /** Factory method for creating a brand-new registration. */
    public static Registration create(
            String email,
            String username,
            String passwordHash,
            String verificationToken,
            Instant tokenExpiresAt) {
        Instant now = Instant.now();
        return new Registration(
                UUID.randomUUID(),
                email,
                username,
                passwordHash,
                RegistrationStatus.PENDING_VERIFICATION,
                verificationToken,
                tokenExpiresAt,
                now,
                now);
    }

    public void markVerified() {
        this.status = RegistrationStatus.VERIFIED;
        this.verificationToken = null;
        this.verificationTokenExpiresAt = null;
        this.updatedAt = Instant.now();
    }

    // ── Getters ──────────────────────────────────────────────────────────────

    public UUID getId() { return id; }
    public String getEmail() { return email; }
    public String getUsername() { return username; }
    public String getPasswordHash() { return passwordHash; }
    public RegistrationStatus getStatus() { return status; }
    public String getVerificationToken() { return verificationToken; }
    public Instant getVerificationTokenExpiresAt() { return verificationTokenExpiresAt; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
}
