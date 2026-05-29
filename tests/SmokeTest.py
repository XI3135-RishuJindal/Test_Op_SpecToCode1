import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import org.junit.Before;
import org.junit.Test;

import java.net.HttpURLConnection;
import java.net.URL;

public class ServerRoutesTest {

    private ServerRoutes serverRoutes;

    @Before
    public void setUp() {
        serverRoutes = new ServerRoutes();
    }

    @Test
    public void testHealthEndpointReturns200() throws Exception {
        HttpURLConnection connection = mock(HttpURLConnection.class);
        URL url = new URL("http://localhost:8080/health");
        when(connection.getResponseCode()).thenReturn(200);
        
        assertEquals(200, serverRoutes.checkHealthEndpoint(url));
    }

    @Test
    public void testReadyEndpointReturns200() throws Exception {
        HttpURLConnection connection = mock(HttpURLConnection.class);
        URL url = new URL("http://localhost:8080/ready");
        when(connection.getResponseCode()).thenReturn(200);
        
        assertEquals(200, serverRoutes.checkReadyEndpoint(url));
    }

    @Test
    public void testHealthEndpointReturnsNon200OnCriticalFailure() throws Exception {
        HttpURLConnection connection = mock(HttpURLConnection.class);
        URL url = new URL("http://localhost:8080/health");
        when(connection.getResponseCode()).thenReturn(500); // Simulating failure
        
        assertNotEquals(200, serverRoutes.checkHealthEndpoint(url));
    }
    
    @Test
    public void testReadyEndpointReturnsNon200WhenNotReady() throws Exception {
        HttpURLConnection connection = mock(HttpURLConnection.class);
        URL url = new URL("http://localhost:8080/ready");
        when(connection.getResponseCode()).thenReturn(503); // Simulating not ready
        
        assertNotEquals(200, serverRoutes.checkReadyEndpoint(url));
    }
}
```

Note: Since the runtime or framework version and specific methods for checking the version or endpoints are unknown due to the provided input, the above is a general Java test suite using JUnit with Mockito framework assumptions for HTTP requests mocking.