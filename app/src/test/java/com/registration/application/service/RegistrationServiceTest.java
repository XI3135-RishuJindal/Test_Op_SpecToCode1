package com.registration.application.service;

import com.registration.application.port.in.RegisterUserCommand;
import com.registration.application.port.out.NotificationPort;
import com.registration.application.port.out.RegistrationRepository;
import com.registration.domain.exception.EmailAlreadyRegisteredException;
import com.registration.domain.model.Registration;
import com.registration.domain.model.RegistrationStatus;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.Instant;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for {@link RegistrationService}.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("RegistrationService — unit tests")
class RegistrationServiceTest {

    @Mock
    private RegistrationRepository registrationRepository;

    @Mock
    private NotificationPort notificationPort;

    private PasswordEncoder passwordEncoder;
    private RegistrationService registrationService;

    @BeforeEach
    void setUp() {
        passwordEncoder = new BCryptPasswordEncoder();
        registrationService = new RegistrationService(
                registrationRepository,
                notificationPort,
                passwordEncoder,
                1440L);
    }

    // ── Happy path ────────────────────────────────────────────────────────────

    @Test
    @DisplayName("registerUser creates and persists a new registration")
    void registerUser_newEmail_createsRegistration() {
        RegisterUserCommand command = new RegisterUserCommand(
                "bob@example.com", "bob", "password123");

        when(registrationRepository.existsByEmail("bob@example.com")).thenReturn(false);
        when(registrationRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        Registration result = registrationService.registerUser(command);

        assertThat(result).isNotNull();
        assertThat(result.getEmail()).isEqualTo("bob@example.com");
        assertThat(result.getUsername()).isEqualTo("bob");
        assertThat(result.getStatus()).isEqualTo(RegistrationStatus.PENDING_VERIFICATION);
        assertThat(result.getVerificationToken()).isNotBlank();
        assertThat(result.getPasswordHash()).isNotEqualTo("password123"); // must be hashed
    }

    @Test
    @DisplayName("registerUser sends a verification email after saving")
    void registerUser_newEmail_sendsVerificationEmail() {
        RegisterUserCommand command = new RegisterUserCommand(
                "carol@example.com", "carol", "password123");

        when(registrationRepository.existsByEmail(anyString())).thenReturn(false);
        when(registrationRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        registrationService.registerUser(command);

        ArgumentCaptor<Registration> captor = ArgumentCaptor.forClass(Registration.class);
        verify(notificationPort, times(1)).sendVerificationEmail(captor.capture());
        assertThat(captor.getValue().getEmail()).isEqualTo("carol@example.com");
    }

    @Test
    @DisplayName("registerUser hashes the password before persisting")
    void registerUser_passwordIsHashed() {
        RegisterUserCommand command = new RegisterUserCommand(
                "dave@example.com", "dave", "mySecret99");

        when(registrationRepository.existsByEmail(anyString())).thenReturn(false);
        when(registrationRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        Registration result = registrationService.registerUser(command);

        assertThat(passwordEncoder.matches("mySecret99", result.getPasswordHash())).isTrue();
    }

    // ── Duplicate email ───────────────────────────────────────────────────────

    @Test
    @DisplayName("registerUser throws EmailAlreadyRegisteredException for duplicate email")
    void registerUser_duplicateEmail_throwsException() {
        RegisterUserCommand command = new RegisterUserCommand(
                "existing@example.com", "existing", "password123");

        when(registrationRepository.existsByEmail("existing@example.com")).thenReturn(true);

        assertThatThrownBy(() -> registrationService.registerUser(command))
                .isInstanceOf(EmailAlreadyRegisteredException.class)
                .hasMessageContaining("existing@example.com");

        verify(registrationRepository, never()).save(any());
        verify(notificationPort, never()).sendVerificationEmail(any());
    }
}
