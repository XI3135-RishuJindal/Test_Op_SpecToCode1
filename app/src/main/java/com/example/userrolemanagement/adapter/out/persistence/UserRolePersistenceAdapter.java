package com.example.userrolemanagement.adapter.out.persistence;

import com.example.userrolemanagement.domain.model.UserRole;
import com.example.userrolemanagement.domain.port.out.UserRoleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Persistence adapter implementing the outbound {@link UserRoleRepository} port.
 */
@Component
@RequiredArgsConstructor
public class UserRolePersistenceAdapter implements UserRoleRepository {

    private final SpringUserRoleRepository springUserRoleRepository;

    @Override
    public UserRole save(UserRole userRole) {
        return springUserRoleRepository.save(userRole);
    }

    @Override
    public List<UserRole> findByUserId(UUID userId) {
        return springUserRoleRepository.findByUserId(userId);
    }

    @Override
    public Optional<UserRole> findByUserIdAndRoleId(UUID userId, UUID roleId) {
        return springUserRoleRepository.findByUserIdAndRoleId(userId, roleId);
    }

    @Override
    public void delete(UserRole userRole) {
        springUserRoleRepository.delete(userRole);
    }

    @Override
    public boolean existsByUserIdAndRoleName(UUID userId, String roleName) {
        return springUserRoleRepository.existsByUserIdAndRoleName(userId, roleName);
    }
}
