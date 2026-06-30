package com.example.userrolemanagement.adapter.in.web;

import com.example.userrolemanagement.adapter.in.web.dto.RoleRequest;
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

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for the Role REST endpoints.
 * Each test runs in a transaction that is rolled back after the test.
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class RoleControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    // ── Helpers ──────────────────────────────────────────────────────────────

    private RoleRequest buildRequest(String name, String description) {
        RoleRequest req = new RoleRequest();
        req.setName(name);
        req.setDescription(description);
        return req;
    }

    private String toJson(Object obj) throws Exception {
        return objectMapper.writeValueAsString(obj);
    }

    // ── Tests ─────────────────────────────────────────────────────────────────

    @Test
    @DisplayName("POST /api/v1/roles — creates a role and returns 201")
    void createRole_returns201() throws Exception {
        mockMvc.perform(post("/api/v1/roles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(buildRequest("ADMIN", "Administrator role"))))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").isNotEmpty())
                .andExpect(jsonPath("$.name").value("ADMIN"))
                .andExpect(jsonPath("$.description").value("Administrator role"));
    }

    @Test
    @DisplayName("POST /api/v1/roles — blank name returns 400")
    void createRole_blankName_returns400() throws Exception {
        mockMvc.perform(post("/api/v1/roles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(buildRequest("", "desc"))))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("POST /api/v1/roles — duplicate name returns 409")
    void createRole_duplicateName_returns409() throws Exception {
        mockMvc.perform(post("/api/v1/roles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(buildRequest("EDITOR", "Editor role"))))
                .andExpect(status().isCreated());

        mockMvc.perform(post("/api/v1/roles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(buildRequest("EDITOR", "Duplicate"))))
                .andExpect(status().isConflict());
    }

    @Test
    @DisplayName("GET /api/v1/roles — returns list of roles")
    void getAllRoles_returnsList() throws Exception {
        // Create two roles first
        mockMvc.perform(post("/api/v1/roles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(buildRequest("VIEWER", "Viewer role"))))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/api/v1/roles"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(greaterThanOrEqualTo(1))));
    }

    @Test
    @DisplayName("GET /api/v1/roles/{id} — returns role by ID")
    void getRoleById_returnsRole() throws Exception {
        String body = mockMvc.perform(post("/api/v1/roles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(buildRequest("MODERATOR", "Moderator role"))))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();

        String id = objectMapper.readTree(body).get("id").asText();

        mockMvc.perform(get("/api/v1/roles/{id}", id))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("MODERATOR"));
    }

    @Test
    @DisplayName("GET /api/v1/roles/{id} — unknown ID returns 404")
    void getRoleById_unknownId_returns404() throws Exception {
        mockMvc.perform(get("/api/v1/roles/{id}", "00000000-0000-0000-0000-000000000000"))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("PUT /api/v1/roles/{id} — updates role and returns 200")
    void updateRole_returns200() throws Exception {
        String body = mockMvc.perform(post("/api/v1/roles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(buildRequest("SUPPORT", "Support role"))))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();

        String id = objectMapper.readTree(body).get("id").asText();

        mockMvc.perform(put("/api/v1/roles/{id}", id)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(buildRequest("SUPPORT_V2", "Updated support role"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("SUPPORT_V2"));
    }

    @Test
    @DisplayName("DELETE /api/v1/roles/{id} — deletes role and returns 204")
    void deleteRole_returns204() throws Exception {
        String body = mockMvc.perform(post("/api/v1/roles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(buildRequest("TEMP_ROLE", "Temporary"))))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();

        String id = objectMapper.readTree(body).get("id").asText();

        mockMvc.perform(delete("/api/v1/roles/{id}", id))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/v1/roles/{id}", id))
                .andExpect(status().isNotFound());
    }
}
