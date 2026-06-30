package com.example.userrolemanagement.adapter.in.web;

import com.example.userrolemanagement.adapter.in.web.dto.RoleRequest;
import com.example.userrolemanagement.adapter.in.web.dto.RoleResponse;
import com.example.userrolemanagement.domain.port.in.RoleUseCase;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * REST adapter (inbound) for Role management endpoints.
 */
@RestController
@RequestMapping("/api/v1/roles")
@RequiredArgsConstructor
public class RoleController {

    private final RoleUseCase roleUseCase;

    /**
     * Create a new role.
     *
     * @param request role creation payload
     * @return 201 Created with the new role
     */
    @PostMapping
    public ResponseEntity<RoleResponse> createRole(@Valid @RequestBody RoleRequest request) {
        RoleResponse response = RoleResponse.from(
                roleUseCase.createRole(request.getName(), request.getDescription()));
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Retrieve all roles.
     *
     * @return 200 OK with list of roles
     */
    @GetMapping
    public ResponseEntity<List<RoleResponse>> getAllRoles() {
        List<RoleResponse> roles = roleUseCase.getAllRoles().stream()
                .map(RoleResponse::from)
                .collect(Collectors.toList());
        return ResponseEntity.ok(roles);
    }

    /**
     * Retrieve a role by ID.
     *
     * @param id role UUID
     * @return 200 OK with the role
     */
    @GetMapping("/{id}")
    public ResponseEntity<RoleResponse> getRoleById(@PathVariable UUID id) {
        return ResponseEntity.ok(RoleResponse.from(roleUseCase.getRoleById(id)));
    }

    /**
     * Update an existing role.
     *
     * @param id      role UUID
     * @param request update payload
     * @return 200 OK with the updated role
     */
    @PutMapping("/{id}")
    public ResponseEntity<RoleResponse> updateRole(
            @PathVariable UUID id,
            @Valid @RequestBody RoleRequest request) {
        RoleResponse response = RoleResponse.from(
                roleUseCase.updateRole(id, request.getName(), request.getDescription()));
        return ResponseEntity.ok(response);
    }

    /**
     * Delete a role.
     *
     * @param id role UUID
     * @return 204 No Content
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteRole(@PathVariable UUID id) {
        roleUseCase.deleteRole(id);
        return ResponseEntity.noContent().build();
    }
}
