package com.example.userrolemanagement.adapter.in.web.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.UUID;

/**
 * Request body for assigning a role to a user.
 */
@Data
public class UserRoleRequest {

    @NotNull(message = "roleId must not be null")
    private UUID roleId;
}
