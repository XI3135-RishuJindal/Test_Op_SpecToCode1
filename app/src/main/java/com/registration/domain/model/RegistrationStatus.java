package com.registration.domain.model;

/**
 * Lifecycle states of a user registration.
 */
public enum RegistrationStatus {
    /** Email verification has been sent but not yet confirmed. */
    PENDING_VERIFICATION,
    /** User has confirmed their email address. */
    VERIFIED
}
