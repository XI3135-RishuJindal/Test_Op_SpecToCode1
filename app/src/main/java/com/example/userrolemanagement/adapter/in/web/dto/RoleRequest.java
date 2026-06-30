package com.example.userrolemanagement.adapter.in.web.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * Request body for creating or updating a Role.
 */
@Data
public class RoleRequest {

    @NotBlank(message = "Role name must not be blank")
    @Size(max = 100, message = "Role name must not exceed 100 characters")
    private String name;

    @Size(max = 500, message = "Description must not exceed 500 characters")
    private String description;
}
