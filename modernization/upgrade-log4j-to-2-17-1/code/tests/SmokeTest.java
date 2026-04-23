```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.web.client.RestTemplate;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SpringExtension.class)
@SpringBootTest
class ApplicationSmokeTest {

    @Autowired
    private ApplicationContext applicationContext;

    @Autowired
    private RestTemplate restTemplate;

    @Test
    void contextLoads() {
        assertThat(applicationContext).isNotNull();
    }

    @Test
    void restTemplateLoads() {
        assertThat(restTemplate).isNotNull();
    }

    @Test
    void log4jConfigurationTest() {
        org.apache.logging.log4j.Logger logger = org.apache.logging.log4j.LogManager.getLogger(ApplicationSmokeTest.class);
        assertThat(logger).isNotNull();
        logger.info("Log4j is configured correctly.");
    }

    @Test
    void endpointTest() {
        String apiUrl = "http://localhost:8080/api/healthcheck";
        String response = restTemplate.getForObject(apiUrl, String.class);
        assertThat(response).contains("OK");
    }
}
```