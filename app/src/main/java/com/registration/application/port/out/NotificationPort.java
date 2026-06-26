package com.registration.application.port.out;

import com.registration.domain.model.Registration;

/**
 * Outbound port — notification operations for sending verification emails.
 */
public interface NotificationPort {

    /**
     * Sends an email verification message to the newly registered user.
     *
     * @param registration the registration whose owner should receive the email
     */
    void sendVerificationEmail(Registration registration);
}
