package com.example.userrolemanagement.adapter.in.web;

import com.example.userrolemanagement.adapter.in.web.dto.RoleRequest;
import com.example.userrolemanagement.adapter.in.web.dto.UserRoleRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for the UserRole assignment REST endpoints.
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class UserRoleControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    // ── Helpers ──────────────────────────────────────────────────────────────

    private String createRole(String name) throws Exception {
        RoleRequest req = new RoleRequest();
        req.setName(name);
        req.setDescription(name + " description");
        String body = mockMvc.perform(post("/api/v1/roles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();
        return objectMapper.readTree(body).get("id").asText();
    }

    // ── Tests ─────────────────────────────────────────────────────────────────

    @Test
    @DisplayName("POST /api/v1/users/{userId}/roles — assigns role and returns 201")
    void assignRole_returns201() throws Exception {
        UUID userId = UUID.randomUUID();
        String roleId = createRole("ASSIGN_TEST_ROLE");

        UserRoleRequest req = new UserRoleRequest();
        req.setRoleId(UUID.fromString(roleId));

        mockMvc.perform(post("/api/v1/users/{userId}/roles", userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.userId").value(userId.toString()))
                .andExpect(jsonPath("$.role.id").value(roleId));
    }

    @Test
    @DisplayName("POST /api/v1/users/{userId}/roles — duplicate assignment returns 409")
    void assignRole_duplicate_returns409() throws Exception {
        UUID userId = UUID.randomUUID();
        String roleId = createRole("DUPLICATE_ASSIGN_ROLE");

        UserRoleRequest req = new UserRoleRequest();
        req.setRoleId(UUID.fromString(roleId));

        mockMvc.perform(post("/api/v1/users/{userId}/roles", userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated());

        mockMvc.perform(post("/api/v1/users/{userId}/roles", userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isConflict());
    }

    @Test
    @DisplayName("GET /api/v1/users/{userId}/roles — returns user's roles")
    void getRolesForUser_returnsList() throws Exception {
        UUID userId = UUID.randomUUID();
        String roleId = createRole("LIST_ROLE");

        UserRoleRequest req = new UserRoleRequest();
        req.setRoleId(UUID.fromString(roleId));

        mockMvc.perform(post("/api/v1/users/{userId}/roles", userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/api/v1/users/{userId}/roles", userId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].role.id").value(roleId));
    }

    @Test
    @DisplayName("DELETE /api/v1/users/{userId}/roles/{roleId} — revokes role and returns 204")
    void revokeRole_returns204() throws Exception {
        UUID userId = UUID.randomUUID();
        String roleId = createRole("REVOKE_ROLE");

        UserRoleRequest req = new UserRoleRequest();
        req.setRoleId(UUID.fromString(roleId));

        mockMvc.perform(post("/api/v1/users/{userId}/roles", userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated());

        mockMvc.perform(delete("/api/v1/users/{userId}/roles/{roleId}", userId, roleId))
                .andExpect(status().isNoContent());
    }

    @Test
    @DisplayName("GET /api/v1/users/{userId}/roles/validate — returns true when role assigned")
    void validateUserRole_returnsTrue() throws Exception {
        UUID userId = UUID.randomUUID();
        String roleId = createRole("VALIDATE_ROLE");

        UserRoleRequest req = new UserRoleRequest();
        req.setRoleId(UUID.fromString(roleId));

        mockMvc.perform(post("/api/v1/users/{userId}/roles", userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/api/v1/users/{userId}/roles/validate", userId)
                        .param("roleName", "VALIDATE_ROLE"))
                .andExpect(status().isOk())
                .andExpect(content().string("true"));
    }

    @Test
    @DisplayName("GET /api/v1/users/{userId}/roles/validate — returns false when role not assigned")
    void validateUserRole_returnsFalse() throws Exception {
        UUID userId = UUID.randomUUID();

        mockMvc.perform(get("/api/v1/users/{userId}/roles/validate", userId)
                        .param("roleName", "NONEXISTENT_ROLE"))
                .andExpect(status().isOk())
                .andExpect(content().string("false"));
    }
}
