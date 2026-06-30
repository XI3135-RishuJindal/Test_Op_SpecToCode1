package com.pharmacy.adapter.in.web;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration slice test for the health check endpoint.
 * Uses @WebMvcTest to load only the web layer — no database required.
 */
@WebMvcTest(HealthController.class)
@DisplayName("HealthController")
class HealthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("GET /api/v1/health returns 200 with status UP")
    void health_returns200WithStatusUp() throws Exception {
        mockMvc.perform(get("/api/v1/health"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith("application/json"))
                .andExpect(jsonPath("$.status", is("UP")))
                .andExpect(jsonPath("$.service", is("pharmacy-microservice")))
                .andExpect(jsonPath("$.timestamp", notNullValue()));
    }
}
