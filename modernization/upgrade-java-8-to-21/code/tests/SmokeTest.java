import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.AfterAll;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestClientException;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class ApplicationSmokeTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private DataSource dataSource;
    
    @BeforeAll
    static void setupAll() {
        // Initialize any external resources if needed
        System.out.println("Setup for tests...");
    }
    
    @AfterAll
    static void tearDownAll() {
        // Cleanup resources
        System.out.println("Teardown after tests...");
    }

    @Test
    void contextLoads() {
        // This test ensures that the Spring Boot context loads without any issues
    }

    @Test
    void testRestApiHealthEndpoint() {
        try {
            ResponseEntity<String> response = restTemplate.getForEntity("/actuator/health", String.class);
            assertEquals(200, response.getStatusCodeValue());
            assertNotNull(response.getBody());
        } catch (RestClientException e) {
            throw new AssertionError("Failed to reach the /actuator/health endpoint", e);
        }
    }

    @Test
    void testDatabaseConnection() {
        try (Connection connection = dataSource.getConnection()) {
            assertNotNull(connection);
            assertEquals(false, connection.isClosed());
        } catch (SQLException e) {
            throw new AssertionError("Failed to establish a connection to the database", e);
        }
    }

    // Additional tests can be added to verify specific functionalities
}