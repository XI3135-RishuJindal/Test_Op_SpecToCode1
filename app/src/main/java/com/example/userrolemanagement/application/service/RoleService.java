package com.example.userrolemanagement.application.service;

import com.example.userrolemanagement.domain.exception.RoleAlreadyExistsException;
import com.example.userrolemanagement.domain.exception.RoleNotFoundException;
import com.example.userrolemanagement.domain.model.Role;
import com.example.userrolemanagement.domain.port.in.RoleUseCase;
import com.example.userrolemanagement.domain.port.out.RoleRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

/**
 * Application service implementing {@link RoleUseCase}.
 * Orchestrates domain logic and delegates persistence to the outbound port.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class RoleService implements RoleUseCase {

    private final RoleRepository roleRepository;

    @Override
    public Role createRole(String name, String description) {
        log.info("Creating role with name={}", name);
        roleRepository.findByName(name).ifPresent(existing -> {
            throw new RoleAlreadyExistsException(name);
        });
        Role role = Role.builder()
                .name(name)
                .description(description)
                .build();
        return roleRepository.save(role);
    }

    @Override
    @Transactional(readOnly = true)
    public List<Role> getAllRoles() {
        return roleRepository.findAll();
    }

    @Override
    @Transactional(readOnly = true)
    public Role getRoleById(UUID id) {
        return roleRepository.findById(id)
                .orElseThrow(() -> new RoleNotFoundException(id));
    }

    @Override
    public Role updateRole(UUID id, String name, String description) {
        log.info("Updating role id={}", id);
        Role role = roleRepository.findById(id)
                .orElseThrow(() -> new RoleNotFoundException(id));

        // Check name uniqueness only if the name is actually changing
        if (!role.getName().equals(name)) {
            roleRepository.findByName(name).ifPresent(existing -> {
                throw new RoleAlreadyExistsException(name);
            });
        }

        role.setName(name);
        role.setDescription(description);
        return roleRepository.save(role);
    }

    @Override
    public void deleteRole(UUID id) {
        log.info("Deleting role id={}", id);
        if (!roleRepository.existsById(id)) {
            throw new RoleNotFoundException(id);
        }
        roleRepository.deleteById(id);
    }
}
