```java
package com.example.demo.integration;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.transaction.Transactional;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.web.client.RestTemplate;
import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@WebAppConfiguration
public class ApplicationIntegrationTest {

    @PersistenceContext
    private EntityManager entityManager;

    @Autowired
    private RestTemplate restTemplate;

    @Test
    public void contextLoads() {
        // Verifies that the Spring application context loads successfully
        assertThat(entityManager).isNotNull();
        assertThat(restTemplate).isNotNull();
    }

    @Test
    @Transactional
    public void testDatabaseInteraction() {
        // Simple transaction to ensure database connectivity
        entityManager.createQuery("SELECT 1").getResultList();
    }

    @Test
    public void testRestEndpoint() {
        // Perform a simple GET request to a known REST endpoint
        String response = restTemplate.getForObject("http://localhost:8080/api/sample-endpoint", String.class);
        assertThat(response).isEqualTo("Hello, World!");
    }
}
```