package com.example.userrolemanagement.adapter.in.web.dto;

import com.example.userrolemanagement.domain.model.UserRole;
import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.UUID;

/**
 * Response DTO for a UserRole assignment.
 */
@Data
@Builder
public class UserRoleResponse {

    private UUID id;
    private UUID userId;
    private RoleResponse role;
    private Instant assignedAt;

    public static UserRoleResponse from(UserRole userRole) {
        return UserRoleResponse.builder()
                .id(userRole.getId())
                .userId(userRole.getUserId())
                .role(RoleResponse.from(userRole.getRole()))
                .assignedAt(userRole.getAssignedAt())
                .build();
    }
}
