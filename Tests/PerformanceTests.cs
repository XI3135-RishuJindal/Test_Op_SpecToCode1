```csharp
using System.Net.Http;
using System.Threading.Tasks;
using Xunit;
using Microsoft.AspNetCore.Mvc.Testing;
using ApiGateway;
using System.Diagnostics;

public class PerformanceTests : IClassFixture<WebApplicationFactory<Startup>>
{
    private readonly HttpClient _client;

    public PerformanceTests(WebApplicationFactory<Startup> factory)
    {
        _client = factory.CreateClient();
    }

    [Theory]
    [InlineData("api/auth/token")]
    [InlineData("api/test")]
    public async Task API_Should_Respond_Within_ThreeSeconds(string url)
    {
        var stopwatch = Stopwatch.StartNew();
        
        // Perform concurrent requests up to max user limit
        var tasks = new List<Task<HttpResponseMessage>>();
        for (int i = 0; i < 10000; i++)
        {
            tasks.Add(_client.GetAsync(url));
        }

        // Wait for all requests to complete
        await Task.WhenAll(tasks);
        
        stopwatch.Stop();
        
        // Ensure each request completes within 3 seconds
        foreach (var task in tasks)
        {
            Assert.True(task.Result.IsSuccessStatusCode);
            Assert.True(stopwatch.Elapsed.TotalSeconds <= 3, "API response time exceeded 3 seconds");
        }
    }
}
```