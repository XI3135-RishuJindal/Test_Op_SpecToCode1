package com.example.userrolemanagement.application.service;

import com.example.userrolemanagement.domain.exception.RoleNotFoundException;
import com.example.userrolemanagement.domain.exception.UserRoleAlreadyAssignedException;
import com.example.userrolemanagement.domain.exception.UserRoleNotFoundException;
import com.example.userrolemanagement.domain.model.Role;
import com.example.userrolemanagement.domain.model.UserRole;
import com.example.userrolemanagement.domain.port.in.UserRoleUseCase;
import com.example.userrolemanagement.domain.port.out.RoleRepository;
import com.example.userrolemanagement.domain.port.out.UserRoleRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

/**
 * Application service implementing {@link UserRoleUseCase}.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class UserRoleService implements UserRoleUseCase {

    private final UserRoleRepository userRoleRepository;
    private final RoleRepository roleRepository;

    @Override
    public UserRole assignRole(UUID userId, UUID roleId) {
        log.info("Assigning role={} to user={}", roleId, userId);
        Role role = roleRepository.findById(roleId)
                .orElseThrow(() -> new RoleNotFoundException(roleId));

        userRoleRepository.findByUserIdAndRoleId(userId, roleId).ifPresent(existing -> {
            throw new UserRoleAlreadyAssignedException(userId, roleId);
        });

        UserRole userRole = UserRole.builder()
                .userId(userId)
                .role(role)
                .build();
        return userRoleRepository.save(userRole);
    }

    @Override
    @Transactional(readOnly = true)
    public List<UserRole> getRolesForUser(UUID userId) {
        return userRoleRepository.findByUserId(userId);
    }

    @Override
    public void revokeRole(UUID userId, UUID roleId) {
        log.info("Revoking role={} from user={}", roleId, userId);
        UserRole userRole = userRoleRepository.findByUserIdAndRoleId(userId, roleId)
                .orElseThrow(() -> new UserRoleNotFoundException(userId, roleId));
        userRoleRepository.delete(userRole);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean validateUserRole(UUID userId, String roleName) {
        return userRoleRepository.existsByUserIdAndRoleName(userId, roleName);
    }
}
