package com.example.userrolemanagement.domain.port.out;

import com.example.userrolemanagement.domain.model.Role;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Outbound port — persistence contract for {@link Role} entities.
 * The domain service depends on this interface; the JPA adapter implements it.
 */
public interface RoleRepository {

    Role save(Role role);

    Optional<Role> findById(UUID id);

    Optional<Role> findByName(String name);

    List<Role> findAll();

    void deleteById(UUID id);

    boolean existsById(UUID id);
}
