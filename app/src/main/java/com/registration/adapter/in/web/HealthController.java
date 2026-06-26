package com.registration.adapter.in.web;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Simple health-check endpoint.
 *
 * <p>Spring Boot Actuator already exposes {@code /actuator/health}, but this
 * lightweight endpoint provides a quick liveness probe at {@code /health}
 * without requiring Actuator on the classpath.
 */
@RestController
@RequestMapping("/health")
public class HealthController {

    /**
     * GET /health
     *
     * @return 200 OK with {@code {"status":"UP"}}
     */
    @GetMapping
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
