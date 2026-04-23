import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.ResponseEntity;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class ApplicationSmokeTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    public void contextLoads() {
        // Application context loading is verified by the test itself.
    }

    @Test
    public void apiEndpointShouldReturnSuccess() {
        ResponseEntity<String> response = restTemplate.getForEntity("/api/status", String.class);
        assertThat(response.getStatusCodeValue()).isEqualTo(200);
        assertThat(response.getBody()).contains("UP");
    }

    @Test
    public void verifyLog4jUpgrade() {
        // This is a placeholder test to ensure Log4j was upgraded.
        // Specific tests would typically be more detailed and require library-specific verifications.
        String log4jVersion = org.apache.logging.log4j.util.PropertiesUtil.getProperties().getStringProperty("log4j2.version");
        assertThat(log4jVersion).isNotNull().isEqualTo("2.20.0");
    }
    
    @Test
    public void verifyJpaMigration() {
        // Validate a basic JPA repository operation to ensure migration to jakarta.persistence
        ResponseEntity<String> response = restTemplate.getForEntity("/api/entities/1", String.class);
        assertThat(response.getStatusCodeValue()).isEqualTo(200);
        assertThat(response.getBody()).contains("entityName");
    }
}