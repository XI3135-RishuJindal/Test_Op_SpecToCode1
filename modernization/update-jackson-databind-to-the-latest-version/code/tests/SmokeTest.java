```java
package com.example.smoketest;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class SmokeTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    public void contextLoads() {
        assertNotNull(port);
        assertNotEquals(0, port);
    }

    @Test
    public void testJacksonSerialization() throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        TestEntity entity = new TestEntity(1, "TestName");
        String jsonString = objectMapper.writeValueAsString(entity);
        TestEntity deserializedEntity = objectMapper.readValue(jsonString, TestEntity.class);

        assertEquals(entity.getId(), deserializedEntity.getId());
        assertEquals(entity.getName(), deserializedEntity.getName());
    }

    @Test
    public void apiHealthCheck() {
        String url = String.format("http://localhost:%d/actuator/health", port);
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertTrue(response.getBody().contains("\"status\":\"UP\""));
    }

    @Test
    public void sampleApiTest() {
        String url = String.format("http://localhost:%d/api/sample", port);
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertTrue(response.getBody().contains("Hello, World!"));
    }

    static class TestEntity {
        private int id;
        private String name;

        public TestEntity() {
        }

        public TestEntity(int id, String name) {
            this.id = id;
            this.name = name;
        }

        public int getId() {
            return id;
        }

        public String getName() {
            return name;
        }

        public void setId(int id) {
            this.id = id;
        }

        public void setName(String name) {
            this.name = name;
        }
    }
}
```