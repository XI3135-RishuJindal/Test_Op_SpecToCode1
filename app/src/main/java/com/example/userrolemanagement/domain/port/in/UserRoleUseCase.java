package com.example.userrolemanagement.domain.port.in;

import com.example.userrolemanagement.domain.model.UserRole;

import java.util.List;
import java.util.UUID;

/**
 * Inbound port — use-case interface for UserRole assignment operations.
 */
public interface UserRoleUseCase {

    /**
     * Assign a role to a user.
     *
     * @param userId external user identifier
     * @param roleId role UUID
     * @return the created {@link UserRole} assignment
     */
    UserRole assignRole(UUID userId, UUID roleId);

    /**
     * Retrieve all role assignments for a given user.
     *
     * @param userId external user identifier
     * @return list of {@link UserRole} assignments
     */
    List<UserRole> getRolesForUser(UUID userId);

    /**
     * Remove a role assignment from a user.
     *
     * @param userId external user identifier
     * @param roleId role UUID
     */
    void revokeRole(UUID userId, UUID roleId);

    /**
     * Validate whether a user holds a specific role.
     * Intended for integration with the authentication service.
     *
     * @param userId   external user identifier
     * @param roleName role name to check
     * @return {@code true} if the user has the role, {@code false} otherwise
     */
    boolean validateUserRole(UUID userId, String roleName);
}
