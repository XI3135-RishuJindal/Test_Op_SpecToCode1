package com.example.userrolemanagement.adapter.in.web;

import com.example.userrolemanagement.adapter.in.web.dto.UserRoleRequest;
import com.example.userrolemanagement.adapter.in.web.dto.UserRoleResponse;
import com.example.userrolemanagement.domain.port.in.UserRoleUseCase;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * REST adapter (inbound) for UserRole assignment endpoints.
 */
@RestController
@RequestMapping("/api/v1/users/{userId}/roles")
@RequiredArgsConstructor
public class UserRoleController {

    private final UserRoleUseCase userRoleUseCase;

    /**
     * Assign a role to a user.
     *
     * @param userId  path variable — external user identifier
     * @param request assignment payload containing roleId
     * @return 201 Created with the assignment
     */
    @PostMapping
    public ResponseEntity<UserRoleResponse> assignRole(
            @PathVariable UUID userId,
            @Valid @RequestBody UserRoleRequest request) {
        UserRoleResponse response = UserRoleResponse.from(
                userRoleUseCase.assignRole(userId, request.getRoleId()));
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * List all roles assigned to a user.
     *
     * @param userId path variable — external user identifier
     * @return 200 OK with list of assignments
     */
    @GetMapping
    public ResponseEntity<List<UserRoleResponse>> getRolesForUser(@PathVariable UUID userId) {
        List<UserRoleResponse> roles = userRoleUseCase.getRolesForUser(userId).stream()
                .map(UserRoleResponse::from)
                .collect(Collectors.toList());
        return ResponseEntity.ok(roles);
    }

    /**
     * Revoke a role from a user.
     *
     * @param userId path variable — external user identifier
     * @param roleId path variable — role UUID
     * @return 204 No Content
     */
    @DeleteMapping("/{roleId}")
    public ResponseEntity<Void> revokeRole(
            @PathVariable UUID userId,
            @PathVariable UUID roleId) {
        userRoleUseCase.revokeRole(userId, roleId);
        return ResponseEntity.noContent().build();
    }

    /**
     * Validate whether a user holds a named role.
     * Intended for integration with the authentication service.
     *
     * @param userId   path variable — external user identifier
     * @param roleName query parameter — role name to check
     * @return 200 OK with boolean result
     */
    @GetMapping("/validate")
    public ResponseEntity<Boolean> validateUserRole(
            @PathVariable UUID userId,
            @RequestParam String roleName) {
        return ResponseEntity.ok(userRoleUseCase.validateUserRole(userId, roleName));
    }
}
