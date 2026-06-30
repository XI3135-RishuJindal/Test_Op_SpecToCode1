package com.example.userrolemanagement.domain.exception;

import java.util.UUID;

/**
 * Thrown when a requested {@link com.example.userrolemanagement.domain.model.Role} does not exist.
 */
public class RoleNotFoundException extends RuntimeException {

    public RoleNotFoundException(UUID id) {
        super("Role not found with id: " + id);
    }

    public RoleNotFoundException(String name) {
        super("Role not found with name: " + name);
    }
}
