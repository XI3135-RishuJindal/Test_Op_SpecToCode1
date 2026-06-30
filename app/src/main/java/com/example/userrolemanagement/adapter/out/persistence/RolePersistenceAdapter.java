package com.example.userrolemanagement.adapter.out.persistence;

import com.example.userrolemanagement.domain.model.Role;
import com.example.userrolemanagement.domain.port.out.RoleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Persistence adapter implementing the outbound {@link RoleRepository} port.
 * Delegates to the Spring Data JPA repository.
 */
@Component
@RequiredArgsConstructor
public class RolePersistenceAdapter implements RoleRepository {

    private final SpringRoleRepository springRoleRepository;

    @Override
    public Role save(Role role) {
        return springRoleRepository.save(role);
    }

    @Override
    public Optional<Role> findById(UUID id) {
        return springRoleRepository.findById(id);
    }

    @Override
    public Optional<Role> findByName(String name) {
        return springRoleRepository.findByName(name);
    }

    @Override
    public List<Role> findAll() {
        return springRoleRepository.findAll();
    }

    @Override
    public void deleteById(UUID id) {
        springRoleRepository.deleteById(id);
    }

    @Override
    public boolean existsById(UUID id) {
        return springRoleRepository.existsById(id);
    }
}
