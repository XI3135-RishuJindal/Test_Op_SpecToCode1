package com.example.userrolemanagement.domain.port.out;

import com.example.userrolemanagement.domain.model.UserRole;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Outbound port — persistence contract for {@link UserRole} assignments.
 */
public interface UserRoleRepository {

    UserRole save(UserRole userRole);

    List<UserRole> findByUserId(UUID userId);

    Optional<UserRole> findByUserIdAndRoleId(UUID userId, UUID roleId);

    void delete(UserRole userRole);

    boolean existsByUserIdAndRoleName(UUID userId, String roleName);
}
