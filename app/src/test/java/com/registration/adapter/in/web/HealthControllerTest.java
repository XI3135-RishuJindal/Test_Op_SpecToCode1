package com.registration.adapter.in.web;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for the {@link HealthController}.
 *
 * <p>Verifies that the {@code GET /health} endpoint returns HTTP 200 with
 * {@code {"status":"UP"}} — the primary acceptance criterion from the spec.
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@DisplayName("HealthController — integration tests")
class HealthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("GET /health returns 200 OK")
    void health_returns200() throws Exception {
        mockMvc.perform(get("/health").accept(MediaType.APPLICATION_JSON))
               .andExpect(status().isOk());
    }

    @Test
    @DisplayName("GET /health returns JSON content type")
    void health_returnsJson() throws Exception {
        mockMvc.perform(get("/health").accept(MediaType.APPLICATION_JSON))
               .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON));
    }

    @Test
    @DisplayName("GET /health body contains status=UP")
    void health_bodyContainsStatusUp() throws Exception {
        mockMvc.perform(get("/health").accept(MediaType.APPLICATION_JSON))
               .andExpect(jsonPath("$.status").value("UP"));
    }
}
