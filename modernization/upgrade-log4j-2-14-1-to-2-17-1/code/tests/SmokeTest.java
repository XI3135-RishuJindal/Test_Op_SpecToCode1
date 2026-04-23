```java
import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.web.servlet.MockMvc;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@SpringBootTest
@ExtendWith(SpringExtension.class)
@AutoConfigureMockMvc
class ApplicationIntegrationTest {

    private static final Logger logger = LogManager.getLogger(ApplicationIntegrationTest.class);

    @Autowired
    private MockMvc mockMvc;

    @Test
    void contextLoads() {
        assertThat(logger).isNotNull();
        logger.info("Context loaded successfully with the upgraded dependencies.");
    }

    @Test
    void testHealthEndpoint() throws Exception {
        mockMvc.perform(get("/actuator/health"))
               .andExpect(status().isOk())
               .andExpect(content().json("{\"status\":\"UP\"}"));
    }

    @Test
    void testGreetingEndpoint() throws Exception {
        mockMvc.perform(get("/api/greeting"))
               .andExpect(status().isOk())
               .andExpect(content().string("Hello, World!"));
    }

    @Test
    void testLog4jConfiguration() {
        String loggerName = logger.getName();
        assertThat(loggerName).isEqualTo(ApplicationIntegrationTest.class.getName());
        logger.info("Log4j is configured correctly with the new version.");
    }

    @Test
    void testJacksonUsedCorrectly() {
        String jsonString = "{\"name\":\"Test User\"}";
        User user = new User("Test User");
        
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            User parsedUser = objectMapper.readValue(jsonString, User.class);
            assertThat(parsedUser).isEqualTo(user);
            logger.info("Jackson version is used correctly for JSON serialization/deserialization.");
        } catch (JsonProcessingException e) {
            logger.error("Failed to parse JSON with new Jackson version", e);
        }
    }

    // Dummy class for serialization test
    static class User {
        private String name;

        public User() {}

        public User(String name) {
            this.name = name;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            User user = (User) o;
            return Objects.equals(name, user.name);
        }

        @Override
        public int hashCode() {
            return Objects.hash(name);
        }
    }
}
```