package com.example.userrolemanagement.application.service;

import com.example.userrolemanagement.domain.exception.RoleAlreadyExistsException;
import com.example.userrolemanagement.domain.exception.RoleNotFoundException;
import com.example.userrolemanagement.domain.model.Role;
import com.example.userrolemanagement.domain.port.out.RoleRepository;
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
 * Unit tests for {@link RoleService}.
 * Uses Mockito to isolate the service from the persistence layer.
 */
@ExtendWith(MockitoExtension.class)
class RoleServiceTest {

    @Mock
    private RoleRepository roleRepository;

    @InjectMocks
    private RoleService roleService;

    private Role sampleRole;

    @BeforeEach
    void setUp() {
        sampleRole = Role.builder()
                .id(UUID.randomUUID())
                .name("ADMIN")
                .description("Administrator")
                .build();
    }

    @Test
    @DisplayName("createRole — saves and returns new role")
    void createRole_savesAndReturns() {
        when(roleRepository.findByName("ADMIN")).thenReturn(Optional.empty());
        when(roleRepository.save(any(Role.class))).thenReturn(sampleRole);

        Role result = roleService.createRole("ADMIN", "Administrator");

        assertThat(result.getName()).isEqualTo("ADMIN");
        verify(roleRepository).save(any(Role.class));
    }

    @Test
    @DisplayName("createRole — throws RoleAlreadyExistsException when name taken")
    void createRole_duplicateName_throwsException() {
        when(roleRepository.findByName("ADMIN")).thenReturn(Optional.of(sampleRole));

        assertThatThrownBy(() -> roleService.createRole("ADMIN", "desc"))
                .isInstanceOf(RoleAlreadyExistsException.class);

        verify(roleRepository, never()).save(any());
    }

    @Test
    @DisplayName("getAllRoles — returns list from repository")
    void getAllRoles_returnsList() {
        when(roleRepository.findAll()).thenReturn(List.of(sampleRole));

        List<Role> roles = roleService.getAllRoles();

        assertThat(roles).hasSize(1).contains(sampleRole);
    }

    @Test
    @DisplayName("getRoleById — returns role when found")
    void getRoleById_found() {
        when(roleRepository.findById(sampleRole.getId())).thenReturn(Optional.of(sampleRole));

        Role result = roleService.getRoleById(sampleRole.getId());

        assertThat(result).isEqualTo(sampleRole);
    }

    @Test
    @DisplayName("getRoleById — throws RoleNotFoundException when not found")
    void getRoleById_notFound_throwsException() {
        UUID id = UUID.randomUUID();
        when(roleRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> roleService.getRoleById(id))
                .isInstanceOf(RoleNotFoundException.class);
    }

    @Test
    @DisplayName("updateRole — updates and returns role")
    void updateRole_updatesAndReturns() {
        when(roleRepository.findById(sampleRole.getId())).thenReturn(Optional.of(sampleRole));
        when(roleRepository.findByName("SUPER_ADMIN")).thenReturn(Optional.empty());
        when(roleRepository.save(any(Role.class))).thenAnswer(inv -> inv.getArgument(0));

        Role result = roleService.updateRole(sampleRole.getId(), "SUPER_ADMIN", "Super admin");

        assertThat(result.getName()).isEqualTo("SUPER_ADMIN");
    }

    @Test
    @DisplayName("deleteRole — deletes when role exists")
    void deleteRole_deletesWhenExists() {
        when(roleRepository.existsById(sampleRole.getId())).thenReturn(true);

        roleService.deleteRole(sampleRole.getId());

        verify(roleRepository).deleteById(sampleRole.getId());
    }

    @Test
    @DisplayName("deleteRole — throws RoleNotFoundException when not found")
    void deleteRole_notFound_throwsException() {
        UUID id = UUID.randomUUID();
        when(roleRepository.existsById(id)).thenReturn(false);

        assertThatThrownBy(() -> roleService.deleteRole(id))
                .isInstanceOf(RoleNotFoundException.class);

        verify(roleRepository, never()).deleteById(any());
    }
}
