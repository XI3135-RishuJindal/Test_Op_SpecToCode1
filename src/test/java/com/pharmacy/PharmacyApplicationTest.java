package com.pharmacy;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

/**
 * Smoke test — verifies the Spring application context loads successfully.
 */
@SpringBootTest
@ActiveProfiles("test")
class PharmacyApplicationTest {

    @Test
    void contextLoads() {
        // If the context fails to load, this test will fail with a descriptive error.
    }
}
