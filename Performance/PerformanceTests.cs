```csharp
using System.Diagnostics;
using System.Net.Http;
using System.Threading.Tasks;
using Xunit;

public class PerformanceTests
{
    private const string ApiBaseUrl = "http://localhost:5000/api";
    private readonly HttpClient _client;

    public PerformanceTests()
    {
        _client = new HttpClient();
    }

    [Fact]
    public async Task TestAuditLoggingPerformance()
    {
        var tasks = new Task[10000];
        var stopwatch = new Stopwatch();

        stopwatch.Start();

        for (int i = 0; i < tasks.Length; i++)
        {
            tasks[i] = SimulateUserLoginAsync(i.ToString());
        }

        await Task.WhenAll(tasks);

        stopwatch.Stop();

        // Confirm total duration is within 3 seconds
        Assert.True(stopwatch.Elapsed.TotalSeconds < 3, $"Audit logging took too long: {stopwatch.Elapsed.TotalSeconds} seconds");
    }

    private async Task SimulateUserLoginAsync(string username)
    {
        var loginPayload = new
        {
            Username = username,
            Password = "password" // Assuming a default password for test users
        };

        var response = await _client.PostAsJsonAsync($"{ApiBaseUrl}/auth/token", loginPayload);

        response.EnsureSuccessStatusCode();
    }
}
```