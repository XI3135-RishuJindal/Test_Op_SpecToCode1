```java
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.web.client.RestTemplate;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class ApplicationSmokeTest {

    @LocalServerPort
    private int port;

    private static RestTemplate restTemplate;

    @BeforeAll
    public static void init() {
        restTemplate = new RestTemplate();
    }

    @Test
    public void contextLoads() {
    }

    @Test
    public void shouldReturnDefaultMessage() throws Exception {
        String baseUrl = "http://localhost:" + port + "/api/health";
        ResponseEntity<String> responseEntity = restTemplate.getForEntity(baseUrl, String.class);
        assertThat(responseEntity.getStatusCodeValue()).isEqualTo(200);
        assertThat(responseEntity.getBody()).contains("UP");
    }

    @Test
    public void jacksonUpgradeTest() throws Exception {
        String baseUrl = "http://localhost:" + port + "/api/test-json";
        ResponseEntity<String> responseEntity = restTemplate.postForEntity(baseUrl, "{\"key\":\"value\"}", String.class);
        assertThat(responseEntity.getStatusCodeValue()).isEqualTo(200);
        assertThat(responseEntity.getBody()).contains("key", "value");
    }

    @Test
    public void log4jUpgradeTest() throws Exception {
        String baseUrl = "http://localhost:" + port + "/api/test-logging";
        ResponseEntity<String> responseEntity = restTemplate.postForEntity(baseUrl, "Log test", String.class);
        assertThat(responseEntity.getStatusCodeValue()).isEqualTo(200);
        assertThat(responseEntity.getBody()).contains("Log test");
    }
}
```