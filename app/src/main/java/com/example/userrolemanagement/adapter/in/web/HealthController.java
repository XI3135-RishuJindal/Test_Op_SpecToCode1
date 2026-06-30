package com.example.userrolemanagement.adapter.in.web;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Simple health-check endpoint.
 * Spring Boot Actuator is also configured, but this lightweight endpoint
 * provides a predictable path for load-balancer probes.
 */
@RestController
@RequestMapping("/health")
public class HealthController {

    /**
     * Returns service liveness status.
     *
     * @return 200 OK with {@code {"status": "UP"}}
     */
    @GetMapping
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
