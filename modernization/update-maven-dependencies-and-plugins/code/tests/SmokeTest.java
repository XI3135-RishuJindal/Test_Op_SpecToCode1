import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.web.client.RestTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ApplicationSmokeTest {

    @LocalServerPort
    private int port;

    @Value("${server.servlet.context-path}")
    private String contextPath;

    private final RestTemplate restTemplate = new RestTemplate();

    @Test
    void contextLoads() {
        // Test to ensure the Spring Boot context loads successfully
    }

    @Test
    void applicationStartsSuccessfully() {
        String baseUrl = "http://localhost:" + port + contextPath + "/";
        ResponseEntity<String> response = restTemplate.getForEntity(baseUrl, String.class);
        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
    }
    
    @Test
    void testHealthEndpoint() {
        String healthUrl = "http://localhost:" + port + contextPath + "/actuator/health";
        ResponseEntity<String> response = restTemplate.getForEntity(healthUrl, String.class);
        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(response.getBody()).contains("\"status\":\"UP\"");
    }

    @Test
    void testLogConfiguration() {
        // Basic test to ensure Log4j2 is configured and doesn't throw errors
        org.apache.logging.log4j.Logger logger = org.apache.logging.log4j.LogManager.getLogger(ApplicationSmokeTest.class);
        logger.info("Log4j2 configuration test message");
        assertThat(logger).isNotNull();
    }

    @Test
    void testJsonDeserialization() {
        // Test Jackson Databind functionality
        String json = "{\"key\":\"value\"}";
        com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
        try {
            java.util.Map<String, String> map = mapper.readValue(json, java.util.Map.class);
            assertThat(map).containsEntry("key", "value");
        } catch (Exception e) {
            assertThat(false).isTrue(); // force fail
        }
    }

}