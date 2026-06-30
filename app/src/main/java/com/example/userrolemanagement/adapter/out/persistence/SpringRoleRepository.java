package com.example.userrolemanagement.adapter.out.persistence;

import com.example.userrolemanagement.domain.model.Role;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

/**
 * Spring Data JPA repository for {@link Role}.
 * Internal to the persistence adapter — not exposed outside this package.
 */
@Repository
interface SpringRoleRepository extends JpaRepository<Role, UUID> {

    Optional<Role> findByName(String name);
}
