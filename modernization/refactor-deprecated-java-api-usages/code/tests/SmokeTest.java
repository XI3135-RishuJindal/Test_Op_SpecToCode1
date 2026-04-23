import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ApplicationIntegrationTest {

    @LocalServerPort
    private int port;

    private String baseUrl;
    private RestTemplate restTemplate;

    @BeforeEach
    void setUp() {
        baseUrl = "http://localhost:" + port;
        restTemplate = new RestTemplate();
    }

    @Test
    void contextLoads() {
        ResponseEntity<String> response = restTemplate.getForEntity(baseUrl + "/", String.class);
        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void testApiEndpoint() {
        ResponseEntity<String> response = restTemplate.getForEntity(baseUrl + "/api/hello", String.class);
        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(response.getBody()).contains("Hello, World");
    }

    @Test
    void testDatabaseConnection() {
        ResponseEntity<String> response = restTemplate.getForEntity(baseUrl + "/api/databaseCheck", String.class);
        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(response.getBody()).contains("Database connected");
    }

    @Test
    void testLog4jConfiguration() {
        ResponseEntity<String> response = restTemplate.getForEntity(baseUrl + "/api/logCheck", String.class);
        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(response.getBody()).contains("Logging configured");
    }
}