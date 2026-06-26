package com.registration.application.service;

import com.registration.application.port.in.RegisterUserCommand;
import com.registration.application.port.in.RegisterUserUseCase;
import com.registration.application.port.out.NotificationPort;
import com.registration.application.port.out.RegistrationRepository;
import com.registration.domain.exception.EmailAlreadyRegisteredException;
import com.registration.domain.model.Registration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.UUID;

/**
 * Application service implementing the {@link RegisterUserUseCase}.
 *
 * <p>Orchestrates domain logic, persistence, and notification without
 * containing any infrastructure concerns itself.
 */
@Service
@Transactional
public class RegistrationService implements RegisterUserUseCase {

    private static final Logger log = LoggerFactory.getLogger(RegistrationService.class);

    private final RegistrationRepository registrationRepository;
    private final NotificationPort notificationPort;
    private final PasswordEncoder passwordEncoder;
    private final long tokenExpiryMinutes;

    public RegistrationService(
            RegistrationRepository registrationRepository,
            NotificationPort notificationPort,
            PasswordEncoder passwordEncoder,
            @org.springframework.beans.factory.annotation.Value("${app.verification.token-expiry-minutes:1440}")
            long tokenExpiryMinutes) {
        this.registrationRepository = registrationRepository;
        this.notificationPort = notificationPort;
        this.passwordEncoder = passwordEncoder;
        this.tokenExpiryMinutes = tokenExpiryMinutes;
    }

    @Override
    public Registration registerUser(RegisterUserCommand command) {
        log.info("Processing registration for email: {}", command.email());

        if (registrationRepository.existsByEmail(command.email())) {
            log.warn("Registration rejected — email already registered: {}", command.email());
            throw new EmailAlreadyRegisteredException(command.email());
        }

        String passwordHash = passwordEncoder.encode(command.password());
        String verificationToken = UUID.randomUUID().toString();
        Instant tokenExpiresAt = Instant.now().plus(tokenExpiryMinutes, ChronoUnit.MINUTES);

        Registration registration = Registration.create(
                command.email(),
                command.username(),
                passwordHash,
                verificationToken,
                tokenExpiresAt);

        Registration saved = registrationRepository.save(registration);
        log.info("Registration created with id={} for email={}", saved.getId(), saved.getEmail());

        notificationPort.sendVerificationEmail(saved);

        return saved;
    }
}
