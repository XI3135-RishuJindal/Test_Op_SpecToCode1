```java
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.context.ApplicationContext;
import org.springframework.core.env.Environment;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.web.client.RestTemplate;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@ActiveProfiles("test")
class ApplicationSmokeTest {

    @LocalServerPort
    private int port;

    @Autowired
    private ApplicationContext context;

    @Autowired
    private Environment environment;

    private RestTemplate restTemplate;
    private String baseUrl;

    @BeforeAll
    void setUp() {
        restTemplate = new RestTemplate();
        baseUrl = "http://localhost:" + port;
    }

    @Test
    void contextLoads() {
        assertNotNull(context, "Application context should have loaded.");
    }

    @Test
    void testSpringBootVersion() {
        assertTrue(environment.getProperty("spring.boot.version").startsWith("3.3"), "Spring Boot version should be 3.3.x");
    }

    @Test
    void testJavaVersion() {
        String javaVersion = System.getProperty("java.version");
        assertTrue(javaVersion.startsWith("21"), "Java version should be 21.x");
    }

    @Test
    void testHomeEndpoint() {
        String response = restTemplate.getForObject(baseUrl + "/", String.class);
        assertEquals("Welcome to our application!", response, "Home endpoint should return expected welcome message.");
    }

    @Test
    void testHealthEndpoint() {
        String healthResponse = restTemplate.getForObject(baseUrl + "/actuator/health", String.class);
        assertNotNull(healthResponse, "Health endpoint should return a response.");
        assertTrue(healthResponse.contains("\"status\":\"UP\""), "Health status should be UP");
    }

    @AfterAll
    void tearDown() {
        // Optionally, clean up resources if necessary
    }
}
```