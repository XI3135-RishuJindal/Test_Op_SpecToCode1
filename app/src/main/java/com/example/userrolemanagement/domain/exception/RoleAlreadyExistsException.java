package com.example.userrolemanagement.domain.exception;

/**
 * Thrown when attempting to create a role whose name already exists.
 */
public class RoleAlreadyExistsException extends RuntimeException {

    public RoleAlreadyExistsException(String name) {
        super("Role already exists with name: " + name);
    }
}
