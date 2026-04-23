```java
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.web.client.RestTemplate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

@SpringBootTest
class ApplicationSmokeTest {

    private static final Logger logger = LoggerFactory.getLogger(ApplicationSmokeTest.class);

    private ObjectMapper objectMapper;
    private RestTemplate restTemplate;
    
    @BeforeEach
    void setUp() {
        objectMapper = new ObjectMapper();
        restTemplate = new RestTemplate();
    }

    @Test
    void contextLoads() {
        logger.info("Testing if the Spring Boot application context loads.");
        assertNotNull(restTemplate);
        assertNotNull(objectMapper);
    }

    @Test
    void testJsonSerialization() throws Exception {
        TestData testData = new TestData("testValue");
        String jsonString = objectMapper.writeValueAsString(testData);
        TestData result = objectMapper.readValue(jsonString, TestData.class);

        assertEquals(testData.getValue(), result.getValue());
    }

    @Test
    void testRestApiCall() {
        logger.info("Testing Rest API call for health check endpoint.");
        String response = restTemplate.getForObject("http://localhost:8080/actuator/health", String.class);
        assertNotNull(response);
        assertEquals("{\"status\":\"UP\"}", response);
    }

    static class TestData {
        @JsonProperty("value")
        private String value;

        public TestData() {}

        public TestData(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }

        public void setValue(String value) {
            this.value = value;
        }
    }
}
```