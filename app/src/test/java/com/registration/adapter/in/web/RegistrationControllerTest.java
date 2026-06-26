package com.registration.adapter.in.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.registration.application.port.in.RegisterUserUseCase;
import com.registration.domain.exception.EmailAlreadyRegisteredException;
import com.registration.domain.model.Registration;
import com.registration.domain.model.RegistrationStatus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Slice tests for {@link RegistrationController}.
 */
@WebMvcTest(controllers = {RegistrationController.class, GlobalExceptionHandler.class})
@Import(com.registration.infrastructure.config.SecurityConfig.class)
@DisplayName("RegistrationController — web slice tests")
class RegistrationControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private RegisterUserUseCase registerUserUseCase;

    // ── Happy path ────────────────────────────────────────────────────────────

    @Test
    @DisplayName("POST /api/v1/registrations returns 201 Created on valid request")
    void register_validRequest_returns201() throws Exception {
        Registration stub = new Registration(
                UUID.randomUUID(),
                "alice@example.com",
                "alice",
                "hashed",
                RegistrationStatus.PENDING_VERIFICATION,
                "token-abc",
                Instant.now().plusSeconds(3600),
                Instant.now(),
                Instant.now());

        when(registerUserUseCase.registerUser(any())).thenReturn(stub);

        String body = """
                {
                  "email": "alice@example.com",
                  "username": "alice",
                  "password": "securePass1"
                }
                """;

        mockMvc.perform(post("/api/v1/registrations")
                       .contentType(MediaType.APPLICATION_JSON)
                       .content(body))
               .andExpect(status().isCreated())
               .andExpect(jsonPath("$.email").value("alice@example.com"))
               .andExpect(jsonPath("$.username").value("alice"))
               .andExpect(jsonPath("$.status").value("PENDING_VERIFICATION"));
    }

    // ── Validation errors ─────────────────────────────────────────────────────

    @Test
    @DisplayName("POST /api/v1/registrations returns 400 when email is blank")
    void register_blankEmail_returns400() throws Exception {
        String body = """
                {
                  "email": "",
                  "username": "alice",
                  "password": "securePass1"
                }
                """;

        mockMvc.perform(post("/api/v1/registrations")
                       .contentType(MediaType.APPLICATION_JSON)
                       .content(body))
               .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("POST /api/v1/registrations returns 400 when email format is invalid")
    void register_invalidEmail_returns400() throws Exception {
        String body = """
                {
                  "email": "not-an-email",
                  "username": "alice",
                  "password": "securePass1"
                }
                """;

        mockMvc.perform(post("/api/v1/registrations")
                       .contentType(MediaType.APPLICATION_JSON)
                       .content(body))
               .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("POST /api/v1/registrations returns 400 when password is too short")
    void register_shortPassword_returns400() throws Exception {
        String body = """
                {
                  "email": "alice@example.com",
                  "username": "alice",
                  "password": "short"
                }
                """;

        mockMvc.perform(post("/api/v1/registrations")
                       .contentType(MediaType.APPLICATION_JSON)
                       .content(body))
               .andExpect(status().isBadRequest());
    }

    // ── Business rule: duplicate email ────────────────────────────────────────

    @Test
    @DisplayName("POST /api/v1/registrations returns 409 when email is already registered")
    void register_duplicateEmail_returns409() throws Exception {
        when(registerUserUseCase.registerUser(any()))
                .thenThrow(new EmailAlreadyRegisteredException("alice@example.com"));

        String body = """
                {
                  "email": "alice@example.com",
                  "username": "alice",
                  "password": "securePass1"
                }
                """;

        mockMvc.perform(post("/api/v1/registrations")
                       .contentType(MediaType.APPLICATION_JSON)
                       .content(body))
               .andExpect(status().isConflict());
    }
}
