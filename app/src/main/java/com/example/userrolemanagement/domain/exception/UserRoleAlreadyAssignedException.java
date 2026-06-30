package com.example.userrolemanagement.domain.exception;

import java.util.UUID;

/**
 * Thrown when a role assignment already exists for a user/role pair.
 */
public class UserRoleAlreadyAssignedException extends RuntimeException {

    public UserRoleAlreadyAssignedException(UUID userId, UUID roleId) {
        super("Role " + roleId + " is already assigned to user " + userId);
    }
}
