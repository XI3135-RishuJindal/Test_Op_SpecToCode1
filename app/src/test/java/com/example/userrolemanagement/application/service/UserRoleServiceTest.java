package com.example.userrolemanagement.application.service;

import com.example.userrolemanagement.domain.exception.RoleNotFoundException;
import com.example.userrolemanagement.domain.exception.UserRoleAlreadyAssignedException;
import com.example.userrolemanagement.domain.exception.UserRoleNotFoundException;
import com.example.userrolemanagement.domain.model.Role;
import com.example.userrolemanagement.domain.model.UserRole;
import com.example.userrolemanagement.domain.port.out.RoleRepository;
import com.example.userrolemanagement.domain.port.out.UserRoleRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for {@link UserRoleService}.
 */
@ExtendWith(MockitoExtension.class)
class UserRoleServiceTest {

    @Mock
    private UserRoleRepository userRoleRepository;

    @Mock
    private RoleRepository roleRepository;

    @InjectMocks
    private UserRoleService userRoleService;

    private Role sampleRole;
    private UUID userId;

    @BeforeEach
    void setUp() {
        userId = UUID.randomUUID();
        sampleRole = Role.builder()
                .id(UUID.randomUUID())
                .name("EDITOR")
                .description("Editor role")
                .build();
    }

    @Test
    @DisplayName("assignRole — creates and returns assignment")
    void assignRole_createsAssignment() {
        when(roleRepository.findById(sampleRole.getId())).thenReturn(Optional.of(sampleRole));
        when(userRoleRepository.findByUserIdAndRoleId(userId, sampleRole.getId()))
                .thenReturn(Optional.empty());
        UserRole saved = UserRole.builder()
                .id(UUID.randomUUID())
                .userId(userId)
                .role(sampleRole)
                .build();
        when(userRoleRepository.save(any(UserRole.class))).thenReturn(saved);

        UserRole result = userRoleService.assignRole(userId, sampleRole.getId());

        assertThat(result.getUserId()).isEqualTo(userId);
        assertThat(result.getRole()).isEqualTo(sampleRole);
    }

    @Test
    @DisplayName("assignRole — throws RoleNotFoundException when role missing")
    void assignRole_roleNotFound_throwsException() {
        UUID unknownRoleId = UUID.randomUUID();
        when(roleRepository.findById(unknownRoleId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> userRoleService.assignRole(userId, unknownRoleId))
                .isInstanceOf(RoleNotFoundException.class);
    }

    @Test
    @DisplayName("assignRole — throws UserRoleAlreadyAssignedException on duplicate")
    void assignRole_duplicate_throwsException() {
        when(roleRepository.findById(sampleRole.getId())).thenReturn(Optional.of(sampleRole));
        UserRole existing = UserRole.builder().id(UUID.randomUUID()).userId(userId).role(sampleRole).build();
        when(userRoleRepository.findByUserIdAndRoleId(userId, sampleRole.getId()))
                .thenReturn(Optional.of(existing));

        assertThatThrownBy(() -> userRoleService.assignRole(userId, sampleRole.getId()))
                .isInstanceOf(UserRoleAlreadyAssignedException.class);
    }

    @Test
    @DisplayName("getRolesForUser — returns list of assignments")
    void getRolesForUser_returnsList() {
        UserRole assignment = UserRole.builder().id(UUID.randomUUID()).userId(userId).role(sampleRole).build();
        when(userRoleRepository.findByUserId(userId)).thenReturn(List.of(assignment));

        List<UserRole> result = userRoleService.getRolesForUser(userId);

        assertThat(result).hasSize(1);
    }

    @Test
    @DisplayName("revokeRole — deletes assignment")
    void revokeRole_deletesAssignment() {
        UserRole assignment = UserRole.builder().id(UUID.randomUUID()).userId(userId).role(sampleRole).build();
        when(userRoleRepository.findByUserIdAndRoleId(userId, sampleRole.getId()))
                .thenReturn(Optional.of(assignment));

        userRoleService.revokeRole(userId, sampleRole.getId());

        verify(userRoleRepository).delete(assignment);
    }

    @Test
    @DisplayName("revokeRole — throws UserRoleNotFoundException when assignment missing")
    void revokeRole_notFound_throwsException() {
        when(userRoleRepository.findByUserIdAndRoleId(userId, sampleRole.getId()))
                .thenReturn(Optional.empty());

        assertThatThrownBy(() -> userRoleService.revokeRole(userId, sampleRole.getId()))
                .isInstanceOf(UserRoleNotFoundException.class);
    }

    @Test
    @DisplayName("validateUserRole — delegates to repository")
    void validateUserRole_delegatesToRepository() {
        when(userRoleRepository.existsByUserIdAndRoleName(userId, "EDITOR")).thenReturn(true);

        boolean result = userRoleService.validateUserRole(userId, "EDITOR");

        assertThat(result).isTrue();
    }
}
