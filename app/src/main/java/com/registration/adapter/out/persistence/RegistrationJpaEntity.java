package com.registration.adapter.out.persistence;

import com.registration.domain.model.RegistrationStatus;
import jakarta.persistence.*;

import java.time.Instant;
import java.util.UUID;

/**
 * JPA entity for persisting a {@link com.registration.domain.model.Registration}.
 * Kept in the adapter layer — the domain model stays framework-free.
 */
@Entity
@Table(name = "registrations")
public class RegistrationJpaEntity {

    @Id
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    @Column(name = "email", nullable = false, unique = true, length = 255)
    private String email;

    @Column(name = "username", nullable = false, length = 50)
    private String username;

    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 30)
    private RegistrationStatus status;

    @Column(name = "verification_token")
    private String verificationToken;

    @Column(name = "verification_token_expires_at")
    private Instant verificationTokenExpiresAt;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    // ── JPA requires a no-arg constructor ────────────────────────────────────
    protected RegistrationJpaEntity() {}

    public RegistrationJpaEntity(
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

    // ── Getters ───────────────────────────────────────────────────────────────

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
