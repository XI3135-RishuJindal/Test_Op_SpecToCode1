package com.example.userrolemanagement.domain.exception;

import java.util.UUID;

/**
 * Thrown when a requested UserRole assignment does not exist.
 */
public class UserRoleNotFoundException extends RuntimeException {

    public UserRoleNotFoundException(UUID userId, UUID roleId) {
        super("No role assignment found for user " + userId + " and role " + roleId);
    }
}
