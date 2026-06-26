package com.registration.adapter.out.notification;

import com.registration.application.port.out.NotificationPort;
import com.registration.domain.model.Registration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Component;

/**
 * Outbound notification adapter — sends verification emails via SMTP.
 */
@Component
public class EmailNotificationAdapter implements NotificationPort {

    private static final Logger log = LoggerFactory.getLogger(EmailNotificationAdapter.class);

    private final JavaMailSender mailSender;
    private final String fromAddress;
    private final String baseUrl;

    public EmailNotificationAdapter(
            JavaMailSender mailSender,
            @Value("${app.mail.from}") String fromAddress,
            @Value("${app.base-url}") String baseUrl) {
        this.mailSender = mailSender;
        this.fromAddress = fromAddress;
        this.baseUrl = baseUrl;
    }

    @Override
    public void sendVerificationEmail(Registration registration) {
        String verificationLink = baseUrl
                + "/api/v1/registrations/verify?token="
                + registration.getVerificationToken();

        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(fromAddress);
        message.setTo(registration.getEmail());
        message.setSubject("Please verify your email address");
        message.setText(
                "Hi " + registration.getUsername() + ",\n\n"
                + "Thank you for registering. Please verify your email by clicking the link below:\n\n"
                + verificationLink + "\n\n"
                + "This link will expire in 24 hours.\n\n"
                + "If you did not register, please ignore this email.\n\n"
                + "Regards,\nThe Registration Service Team");

        try {
            mailSender.send(message);
            log.info("Verification email sent to {}", registration.getEmail());
        } catch (Exception e) {
            // Log and swallow — email failure should not roll back the registration
            log.error("Failed to send verification email to {}: {}", registration.getEmail(), e.getMessage(), e);
        }
    }
}
