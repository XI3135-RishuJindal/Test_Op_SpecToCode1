```csharp
using System;
using System.Net.Http;
using System.Threading.Tasks;
using NBomber.CSharp;

namespace LoadTest
{
    public class NLPPerformanceTest
    {
        public static void Run()
        {
            var httpClient = new HttpClient
            {
                BaseAddress = new Uri("http://localhost:5000") // Adjust the base address as per your setup
            };

            var step = Step.Create("post_nlp_request", clientFactory: HttpClientFactory.Create(), async context =>
            {
                var content = new StringContent("{\"message\":\"Extract requirements from this text input for the system.\"}", System.Text.Encoding.UTF8, "application/json");
                var response = await httpClient.PostAsync("/api/test", content);
                
                response.EnsureSuccessStatusCode();
                
                return Response.Ok(sizeBytes: response.Content.Headers.ContentLength ?? 0);
            });

            var scenario = ScenarioBuilder.CreateScenario("NLP_Performance_Test", step)
                .WithWarmUpDuration(TimeSpan.FromSeconds(10))
                .WithLoadSimulations(
                    Simulation.InjectPerSec(rate: 100, during: TimeSpan.FromMinutes(1))
                );

            NBomberRunner
                .RegisterScenarios(scenario)
                .Run();
        }
    }
}
```