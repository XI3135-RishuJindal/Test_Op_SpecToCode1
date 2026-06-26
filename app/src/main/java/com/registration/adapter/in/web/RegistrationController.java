package com.registration.adapter.in.web;

import com.registration.application.port.in.RegisterUserCommand;
import com.registration.application.port.in.RegisterUserUseCase;
import com.registration.domain.model.Registration;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST inbound adapter — exposes the registration use case over HTTP.
 */
@RestController
@RequestMapping("/api/v1/registrations")
public class RegistrationController {

    private final RegisterUserUseCase registerUserUseCase;

    public RegistrationController(RegisterUserUseCase registerUserUseCase) {
        this.registerUserUseCase = registerUserUseCase;
    }

    /**
     * POST /api/v1/registrations
     *
     * <p>Accepts a registration request, validates the payload, and delegates
     * to the use case.
     *
     * @param request the registration request body
     * @return 201 Created with the registration response, or 4xx on validation/business errors
     */
    @PostMapping
    public ResponseEntity<RegistrationResponse> register(
            @Valid @RequestBody RegistrationRequest request) {

        RegisterUserCommand command = new RegisterUserCommand(
                request.email(),
                request.username(),
                request.password());

        Registration registration = registerUserUseCase.registerUser(command);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(RegistrationResponse.from(registration));
    }
}
