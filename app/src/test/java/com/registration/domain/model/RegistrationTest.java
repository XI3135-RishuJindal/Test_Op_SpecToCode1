package com.registration.domain.model;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.Instant;

import static org.assertj.core.api.Assertions.*;

/**
 * Unit tests for the {@link Registration} domain model.
 */
@DisplayName("Registration — domain model tests")
class RegistrationTest {

    @Test
    @DisplayName("create() produces a PENDING_VERIFICATION registration")
    void create_producesCorrectInitialState() {
        Instant expiresAt = Instant.now().plusSeconds(3600);

        Registration reg = Registration.create(
                "eve@example.com",
                "eve",
                "hashedPassword",
                "token-xyz",
                expiresAt);

        assertThat(reg.getId()).isNotNull();
        assertThat(reg.getEmail()).isEqualTo("eve@example.com");
        assertThat(reg.getUsername()).isEqualTo("eve");
        assertThat(reg.getPasswordHash()).isEqualTo("hashedPassword");
        assertThat(reg.getStatus()).isEqualTo(RegistrationStatus.PENDING_VERIFICATION);
        assertThat(reg.getVerificationToken()).isEqualTo("token-xyz");
        assertThat(reg.getVerificationTokenExpiresAt()).isEqualTo(expiresAt);
        assertThat(reg.getCreatedAt()).isNotNull();
        assertThat(reg.getUpdatedAt()).isNotNull();
    }

    @Test
    @DisplayName("markVerified() transitions status to VERIFIED")
    void markVerified_changesStatusToVerified() {
        Registration reg = Registration.create(
                "frank@example.com", "frank", "hash", "tok", Instant.now().plusSeconds(60));

        reg.markVerified();

        assertThat(reg.getStatus()).isEqualTo(RegistrationStatus.VERIFIED);
    }

    @Test
    @DisplayName("markVerified() clears the verification token")
    void markVerified_clearsToken() {
        Registration reg = Registration.create(
                "grace@example.com", "grace", "hash", "tok", Instant.now().plusSeconds(60));

        reg.markVerified();

        assertThat(reg.getVerificationToken()).isNull();
        assertThat(reg.getVerificationTokenExpiresAt()).isNull();
    }
}
