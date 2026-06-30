package com.example.userrolemanagement.domain.port.in;

import com.example.userrolemanagement.domain.model.Role;

import java.util.List;
import java.util.UUID;

/**
 * Inbound port — use-case interface for Role operations.
 * Adapters (REST controllers) depend on this interface, not on the service implementation.
 */
public interface RoleUseCase {

    /**
     * Create a new role.
     *
     * @param name        unique role name
     * @param description optional human-readable description
     * @return the persisted {@link Role}
     */
    Role createRole(String name, String description);

    /**
     * Retrieve all roles.
     *
     * @return list of all {@link Role} entities
     */
    List<Role> getAllRoles();

    /**
     * Retrieve a single role by its identifier.
     *
     * @param id role UUID
     * @return the matching {@link Role}
     */
    Role getRoleById(UUID id);

    /**
     * Update the name and/or description of an existing role.
     *
     * @param id          role UUID
     * @param name        new name
     * @param description new description
     * @return the updated {@link Role}
     */
    Role updateRole(UUID id, String name, String description);

    /**
     * Delete a role by its identifier.
     *
     * @param id role UUID
     */
    void deleteRole(UUID id);
}
