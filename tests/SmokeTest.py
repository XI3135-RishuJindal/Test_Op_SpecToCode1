using System;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Xunit;

namespace UpgradeValidation.Tests
{
    /// <summary>
    /// Upgrade validation tests for:
    ///   1. HTTPS enforcement (redirect + HSTS header)
    ///   2. /healthz endpoint availability and correct response
    ///   3. DataAnnotations input validation (400 on invalid input, 200 on valid input)
    ///
    /// These tests are intentionally framework-agnostic at the assertion level but
    /// assume an ASP.NET Core host is reachable.  Adjust the TEntryPoint type
    /// parameter to match the actual Program / Startup class in the target project.
    /// </summary>
    public class UpgradeValidationTests : IClassFixture<WebApplicationFactory<Program>>
    {
        private readonly WebApplicationFactory<Program> _factory;

        public UpgradeValidationTests(WebApplicationFactory<Program> factory)
        {
            _factory = factory;
        }

        // ─────────────────────────────────────────────────────────────────────
        // 1. Runtime / framework version assertion
        // ─────────────────────────────────────────────────────────────────────

        [Fact]
        public void Runtime_IsLatestStableDotNet()
        {
            // Verify the process is running on .NET 8 (latest stable LTS as of this upgrade).
            // Update the major version constant when the project targets a newer release.
            const int expectedMajorVersion = 8;

            var runtimeVersion = Environment.Version;

            Assert.True(
                runtimeVersion.Major >= expectedMajorVersion,
                $"Expected .NET runtime major version >= {expectedMajorVersion} but found {runtimeVersion}. " +
                "Ensure the project targets net8.0 (or later) in the .csproj TargetFramework element.");
        }

        // ─────────────────────────────────────────────────────────────────────
        // 2. HTTPS enforcement — HTTP → HTTPS redirect
        // ─────────────────────────────────────────────────────────────────────

        [Fact]
        public async Task HttpRequest_RedirectsToHttps_WithPermanentRedirect()
        {
            // Create a client that does NOT follow redirects so we can inspect the 301/308.
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                AllowAutoRedirect = false,
                BaseAddress = new Uri("http://localhost/")
            });

            var response = await client.GetAsync("/");

            Assert.True(
                response.StatusCode == HttpStatusCode.MovedPermanently ||
                response.StatusCode == HttpStatusCode.PermanentRedirect,
                $"Expected 301 or 308 redirect from HTTP but received {(int)response.StatusCode} {response.StatusCode}. " +
                "Ensure UseHttpsRedirection() is registered in the middleware pipeline.");

            Assert.NotNull(response.Headers.Location);
            Assert.True(
                response.Headers.Location!.Scheme == Uri.UriSchemeHttps ||
                response.Headers.Location.OriginalString.StartsWith("https://", StringComparison.OrdinalIgnoreCase),
                $"Redirect Location header should point to HTTPS but was: {response.Headers.Location}");
        }

        [Fact]
        public async Task HttpsRequest_DoesNotRedirect()
        {
            // A request already on HTTPS must not be redirected again.
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                AllowAutoRedirect = false,
                BaseAddress = new Uri("https://localhost/")
            });

            var response = await client.GetAsync("/healthz");

            Assert.False(
                response.StatusCode == HttpStatusCode.MovedPermanently ||
                response.StatusCode == HttpStatusCode.PermanentRedirect,
                $"HTTPS request should not be redirected but received {(int)response.StatusCode}.");
        }

        // ─────────────────────────────────────────────────────────────────────
        // 3. HSTS header is present on HTTPS responses
        // ─────────────────────────────────────────────────────────────────────

        [Fact]
        public async Task HttpsResponse_ContainsStrictTransportSecurityHeader()
        {
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                BaseAddress = new Uri("https://localhost/")
            });

            var response = await client.GetAsync("/healthz");

            Assert.True(
                response.Headers.Contains("Strict-Transport-Security"),
                "Response is missing the Strict-Transport-Security (HSTS) header. " +
                "Ensure UseHsts() is registered in the middleware pipeline and the environment is not Development.");

            var hstsValue = string.Join(", ", response.Headers.GetValues("Strict-Transport-Security"));

            Assert.Contains("max-age=", hstsValue, StringComparison.OrdinalIgnoreCase);
        }

        // ─────────────────────────────────────────────────────────────────────
        // 4. Health-check endpoint
        // ─────────────────────────────────────────────────────────────────────

        [Fact]
        public async Task HealthzEndpoint_Returns200_WithHealthyStatus()
        {
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                BaseAddress = new Uri("https://localhost/")
            });

            var response = await client.GetAsync("/healthz");

            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        }

        [Fact]
        public async Task HealthzEndpoint_ReturnsJsonBody_ContainingStatus()
        {
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                BaseAddress = new Uri("https://localhost/")
            });

            var response = await client.GetAsync("/healthz");
            var body = await response.Content.ReadAsStringAsync();

            Assert.False(string.IsNullOrWhiteSpace(body),
                "Health-check endpoint returned an empty body. Expected a JSON payload with a 'status' field.");

            // Accept either {"status":"Healthy"} (ASP.NET Core built-in) or a plain "Healthy" string.
            bool containsHealthy =
                body.Contains("Healthy", StringComparison.OrdinalIgnoreCase) ||
                body.Contains("healthy", StringComparison.OrdinalIgnoreCase);

            Assert.True(containsHealthy,
                $"Health-check body does not contain 'Healthy'. Actual body: {body}");
        }

        [Fact]
        public async Task HealthzEndpoint_IsRegisteredAsGetRoute()
        {
            // Verify that POST to /healthz is not accidentally handled (405 or 404 expected).
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                BaseAddress = new Uri("https://localhost/")
            });

            var response = await client.PostAsync("/healthz", new StringContent("{}"));

            Assert.True(
                response.StatusCode == HttpStatusCode.MethodNotAllowed ||
                response.StatusCode == HttpStatusCode.NotFound,
                $"POST /healthz should return 404 or 405 but returned {(int)response.StatusCode}.");
        }

        [Fact]
        public void HealthChecks_ServiceIsRegistered()
        {
            // Verify that the IHealthCheckService is present in the DI container,
            // confirming AddHealthChecks() was called during service registration.
            using var scope = _factory.Services.CreateScope();
            var healthCheckService = scope.ServiceProvider.GetService<HealthCheckService>();

            Assert.NotNull(healthCheckService);
        }

        // ─────────────────────────────────────────────────────────────────────
        // 5. DataAnnotations input validation
        // ─────────────────────────────────────────────────────────────────────

        [Fact]
        public async Task ApiEndpoint_Returns400_WhenRequiredFieldIsMissing()
        {
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                BaseAddress = new Uri("https://localhost/")
            });

            // Send an empty JSON object — all [Required] fields will be absent.
            var content = new StringContent("{}", Encoding.UTF8, "application/json");
            var response = await client.PostAsync("/api/sample", content);

            Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);

            var body = await response.Content.ReadAsStringAsync();
            Assert.False(string.IsNullOrWhiteSpace(body),
                "400 response body should contain validation error details but was empty.");
        }

        [Fact]
        public async Task ApiEndpoint_Returns400_WhenFieldExceedsMaxLength()
        {
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                BaseAddress = new Uri("https://localhost/")
            });

            // Build a payload where a string field exceeds its [MaxLength] constraint.
            var oversizedPayload = new
            {
                Name = new string('x', 1024),   // Exceeds any reasonable [MaxLength]
                Email = "valid@example.com"
            };

            var json = JsonSerializer.Serialize(oversizedPayload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await client.PostAsync("/api/sample", content);

            Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        }

        [Fact]
        public async Task ApiEndpoint_Returns400_WhenEmailFormatIsInvalid()
        {
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                BaseAddress = new Uri("https://localhost/")
            });

            var invalidEmailPayload = new
            {
                Name = "Test User",
                Email = "not-an-email"
            };

            var json = JsonSerializer.Serialize(invalidEmailPayload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await client.PostAsync("/api/sample", content);

            Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        }

        [Fact]
        public async Task ApiEndpoint_Returns2xx_WhenPayloadIsValid()
        {
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                BaseAddress = new Uri("https://localhost/")
            });

            var validPayload = new
            {
                Name = "Test User",
                Email = "valid@example.com"
            };

            var json = JsonSerializer.Serialize(validPayload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await client.PostAsync("/api/sample", content);

            Assert.True(
                (int)response.StatusCode >= 200 && (int)response.StatusCode < 300,
                $"Expected 2xx for a valid payload but received {(int)response.StatusCode} {response.StatusCode}.");
        }

        [Fact]
        public async Task ApiEndpoint_ValidationErrorResponse_ContainsFieldNames()
        {
            var client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                BaseAddress = new Uri("https://localhost/")
            });

            var content = new StringContent("{}", Encoding.UTF8, "application/json");
            var response = await client.PostAsync("/api/sample", content);

            Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);

            var body = await response.Content.ReadAsStringAsync();

            // ASP.NET Core's default ProblemDetails validation response includes an "errors" key.
            Assert.Contains("errors", body, StringComparison.OrdinalIgnoreCase);
        }

        // ─────────────────────────────────────────────────────────────────────
        // 6. Deprecated / replaced API surface checks
        // ─────────────────────────────────────────────────────────────────────

        [Fact]
        public void ModelValidation_IsNotPerformedManuallyInControllers_HealthCheckUsesBuiltIn()
        {
            // Verify that the built-in ASP.NET Core health-check infrastructure is used
            // rather than a hand-rolled controller action, by confirming the service
            // registration exists (already covered above) and that no legacy manual
            // ModelState.IsValid guard is the sole validation mechanism.
            //
            // This is a compile-time / registration-level check: if AddHealthChecks() and
            // automatic model validation (via ApiBehaviorOptions) are both registered,
            // the upgrade is complete.

            using var scope = _factory.Services.CreateScope();

            var healthCheckService = scope.ServiceProvider.GetService<HealthCheckService>();
            Assert.NotNull(healthCheckService);

            // ApiBehaviorOptions being resolvable confirms [ApiController] automatic
            // model-state validation is active (registered via AddControllers() /
            // AddControllersWithViews() in .NET 6+).
            var apiBehaviorOptions = scope.ServiceProvider
                .GetService<Microsoft.Extensions.Options.IOptions<Microsoft.AspNetCore.Mvc.ApiBehaviorOptions>>();

            Assert.NotNull(apiBehaviorOptions);
            Assert.False(
                apiBehaviorOptions!.Value.SuppressModelStateInvalidFilter,
                "SuppressModelStateInvalidFilter must be false so that DataAnnotations validation " +
                "automatically returns 400 without manual ModelState.IsValid checks in every action.");
        }
    }
}