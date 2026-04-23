import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import jakarta.persistence.EntityManager;
import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@ActiveProfiles("test")
public class ApplicationSmokeTest {

    @Autowired
    private ApplicationContext context;

    @Autowired
    private EntityManager entityManager;

    @Test
    void contextLoads() {
        assertThat(context).isNotNull();
    }

    @Test
    void entityManagerLoads() {
        assertThat(entityManager).isNotNull();
    }

    @Test
    void springBootVersion() {
        String version = context.getEnvironment().getProperty("spring.boot.version");
        assertThat(version.startsWith("3.3")).isTrue();
    }

    @Test
    void javaVersionCheck() {
        String javaVersion = System.getProperty("java.version");
        assertThat(javaVersion.startsWith("21")).isTrue();
    }
    
    @Test
    void persistenceContextCheck() {
        assertThat(context.containsBean("entityManagerFactory")).isTrue();
    }
}