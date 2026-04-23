import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.web.client.RestTemplate;
import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@ExtendWith(SpringExtension.class)
public class ApplicationSmokeTest {

    @Autowired
    private RestTemplate restTemplate;

    private String baseUrl;

    @BeforeEach
    public void setUp() {
        baseUrl = "http://localhost:8080"; // Adjust according to your application's base URL
    }

    @Test
    public void contextLoads() {
        assertThat(restTemplate).isNotNull();
    }

    @Test
    public void testHealthEndpoint() {
        String response = restTemplate.getForObject(baseUrl + "/actuator/health", String.class);
        assertThat(response).contains("\"status\":\"UP\"");
    }

    @Test
    public void testApiEndpoint() {
        String response = restTemplate.getForObject(baseUrl + "/api/example", String.class);
        assertThat(response).isNotNull();
        assertThat(response).contains("expectedResponsePart"); // Adjust according to your API response
    }
}