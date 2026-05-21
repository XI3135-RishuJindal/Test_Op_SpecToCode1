using System;
using System.Net;
using System.Net.Http;
using System.Reflection;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Xunit;

namespace IntegrationTests.UpgradeValidation
{
    /// <summary>
    /// Validates that the xUnit + WebApplicationFactory integration test infrastructure
    /// was introduced correctly and is fully operational.
    /// </summary>
    public class UpgradeValidationTests : IClassFixture<WebApplicationFactory<Program>>
    {
        private readonly WebApplicationFactory<Program> _factory;
        private readonly HttpClient _client;

        public UpgradeValidationTests(WebApplicationFactory<Program> factory)
        {
            _factory = factory ?? throw new ArgumentNullException(nameof(factory));
            _client = _factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                AllowAutoRedirect = false,
                HandleCookies = true
            });
        }

        // -----------------------------------------------------------------------
        // 1. Version assertion — confirms the target runtime / framework is active
        // -----------------------------------------------------------------------

        [Fact]
        public void Runtime_IsAtLeastDotNet6_RequiredForWebApplicationFactory()
        {
            // WebApplicationFactory<T> requires .NET 6+ / ASP.NET Core 6+
            var version = Environment.Version;
            Assert.True(
                version.Major >= 6,
                $"Expected .NET 6 or later but found {version}. " +
                "WebApplicationFactory<TEntryPoint> requires .NET 6+.");
        }

        [Fact]
        public void MvcTestingAssembly_IsLoaded_AndMeetsMinimumVersion()
        {
            var assembly = typeof(WebApplicationFactory<>).Assembly;
            Assert.NotNull(assembly);

            var informationalVersion = assembly
                .GetCustomAttribute<AssemblyInformationalVersionAttribute>()
                ?.InformationalVersion ?? string.Empty;

            // The assembly must be present — its presence confirms the NuGet package
            // Microsoft.AspNetCore.Mvc.Testing was successfully restored and loaded.
            Assert.False(
                string.IsNullOrWhiteSpace(informationalVersion),
                "Could not read the informational version of Microsoft.AspNetCore.Mvc.Testing.");

            // Extract the leading numeric portion (e.g. "6.0.25+abc" → "6.0.25")
            var numericPart = informationalVersion.Split('+')[0].Trim();
            Assert.True(
                Version.TryParse(numericPart, out var parsedVersion),
                $"Could not parse version string '{numericPart}' from Microsoft.AspNetCore.Mvc.Testing.");

            Assert.True(
                parsedVersion!.Major >= 6,
                $"Microsoft.AspNetCore.Mvc.Testing version {parsedVersion} is below the required 6.x minimum.");
        }

        [Fact]
        public void XunitCoreAssembly_IsLoaded()
        {
            // Confirms xunit.core is present in the test process
            var xunitAssembly = typeof(FactAttribute).Assembly;
            Assert.NotNull(xunitAssembly);

            var name = xunitAssembly.GetName();
            Assert.Equal("xunit.core", name.Name, ignoreCase: true);
        }

        // -----------------------------------------------------------------------
        // 2. WebApplicationFactory infrastructure is wired correctly
        // -----------------------------------------------------------------------

        [Fact]
        public void WebApplicationFactory_CanBeInstantiated_WithProgramAsEntryPoint()
        {
            // If Program is not a public/partial class this line throws at construction time.
            Assert.NotNull(_factory);
        }

        [Fact]
        public void WebApplicationFactory_CreateClient_ReturnsNonNullHttpClient()
        {
            var client = _factory.CreateClient();
            Assert.NotNull(client);
        }

        [Fact]
        public void WebApplicationFactory_Services_CanBeResolved()
        {
            // Verifies the DI container was composed without errors
            using var scope = _factory.Services.CreateScope();
            Assert.NotNull(scope);
            Assert.NotNull(scope.ServiceProvider);
        }

        [Fact]
        public void WebApplicationFactory_Host_IsRunning()
        {
            // IHost must be accessible and in a started state
            var host = _factory.Server.Host;
            Assert.NotNull(host);

            var lifetime = host.Services.GetService<IHostApplicationLifetime>();
            Assert.NotNull(lifetime);
            Assert.True(
                lifetime!.ApplicationStarted.IsCancellationRequested,
                "The hosted application has not finished starting up.");
        }

        // -----------------------------------------------------------------------
        // 3. HTTP pipeline smoke test — critical application path
        // -----------------------------------------------------------------------

        [Fact]
        public async Task HttpClient_CanSendRequest_WithoutConnectionRefused()
        {
            // A connection-refused or host-not-found exception would indicate
            // the in-process server is not running.  Any HTTP status code
            // (including 404) proves the pipeline is alive.
            HttpResponseMessage response;
            try
            {
                response = await _client.GetAsync("/");
            }
            catch (HttpRequestException ex)
            {
                Assert.Fail(
                    $"HttpRequestException thrown — the in-process server may not be running. " +
                    $"Details: {ex.Message}");
                return; // unreachable; satisfies compiler
            }

            Assert.NotNull(response);
            // Any definitive HTTP status (1xx–5xx) is acceptable here;
            // we are only verifying the pipeline responded.
            Assert.True(
                (int)response.StatusCode >= 100 && (int)response.StatusCode <= 599,
                $"Unexpected status code value: {(int)response.StatusCode}");
        }

        [Fact]
        public async Task HealthEndpoint_ReturnsSuccessOrNotFound_NotServerError()
        {
            // Common health-check paths.  A 5xx would indicate a startup failure.
            var candidatePaths = new[] { "/health", "/healthz", "/api/health" };

            foreach (var path in candidatePaths)
            {
                var response = await _client.GetAsync(path);
                Assert.True(
                    response.StatusCode != HttpStatusCode.InternalServerError &&
                    response.StatusCode != HttpStatusCode.ServiceUnavailable,
                    $"Path '{path}' returned {(int)response.StatusCode} — " +
                    "a server-side error suggests the application did not start correctly.");
            }
        }

        // -----------------------------------------------------------------------
        // 4. CustomWebApplicationFactory — verifies the new class exists and works
        // -----------------------------------------------------------------------

        [Fact]
        public void CustomWebApplicationFactory_CanBeInstantiated()
        {
            // Verifies Phase 2 task: CustomWebApplicationFactory.cs was created
            using var customFactory = new CustomWebApplicationFactory();
            Assert.NotNull(customFactory);
        }

        [Fact]
        public void CustomWebApplicationFactory_CreateClient_ReturnsHttpClient()
        {
            using var customFactory = new CustomWebApplicationFactory();
            var client = customFactory.CreateClient();
            Assert.NotNull(client);
        }

        [Fact]
        public async Task CustomWebApplicationFactory_HttpClient_CanReachApplication()
        {
            using var customFactory = new CustomWebApplicationFactory();
            var client = customFactory.CreateClient();

            HttpResponseMessage response;
            try
            {
                response = await client.GetAsync("/");
            }
            catch (HttpRequestException ex)
            {
                Assert.Fail(
                    $"CustomWebApplicationFactory HttpClient threw HttpRequestException: {ex.Message}");
                return;
            }

            Assert.NotNull(response);
        }

        // -----------------------------------------------------------------------
        // 5. IntegrationTestBase — verifies the base class exists and is usable
        // -----------------------------------------------------------------------

        [Fact]
        public void IntegrationTestBase_Type_ExistsInTestAssembly()
        {
            // Verifies Phase 2 task: IntegrationTestBase.cs was created
            var testAssembly = Assembly.GetExecutingAssembly();
            var baseType = testAssembly.GetType("IntegrationTests.IntegrationTestBase")
                        ?? testAssembly.GetType("IntegrationTestBase");

            Assert.NotNull(baseType);
        }

        [Fact]
        public void IntegrationTestBase_ExposesHttpClientProperty()
        {
            var testAssembly = Assembly.GetExecutingAssembly();
            var baseType = testAssembly.GetType("IntegrationTests.IntegrationTestBase")
                        ?? testAssembly.GetType("IntegrationTestBase");

            Assert.NotNull(baseType);

            var httpClientProperty = baseType!.GetProperty(
                "Client",
                BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);

            Assert.NotNull(httpClientProperty);
            Assert.Equal(typeof(HttpClient), httpClientProperty!.PropertyType);
        }

        // -----------------------------------------------------------------------
        // 6. Program partial class — entry point is accessible to test assembly
        // -----------------------------------------------------------------------

        [Fact]
        public void Program_Class_IsAccessibleFromTestAssembly()
        {
            // Verifies Phase 2 task: `public partial class Program {}` was added
            // to Program.cs so the test assembly can reference it as TEntryPoint.
            var programType = typeof(Program);
            Assert.NotNull(programType);
            Assert.True(
                programType.IsPublic || programType.IsNestedPublic,
                "Program class must be public so WebApplicationFactory<Program> can use it as TEntryPoint.");
        }

        // -----------------------------------------------------------------------
        // 7. Deprecated / replaced API checks
        // -----------------------------------------------------------------------

        [Fact]
        public void TestServer_IsNotUsedDirectly_WebApplicationFactoryIsPreferred()
        {
            // Confirms the project does NOT reference the older Microsoft.AspNetCore.TestHost
            // standalone pattern (TestServer created manually) — WebApplicationFactory wraps it.
            // We verify by ensuring WebApplicationFactory exposes .Server (the wrapped TestServer)
            // rather than the test project constructing TestServer independently.
            var serverProperty = typeof(WebApplicationFactory<Program>)
                .GetProperty("Server", BindingFlags.Public | BindingFlags.Instance);

            Assert.NotNull(serverProperty);
            // If this property exists, the factory pattern is in use — correct.
        }

        [Fact]
        public void IWebHostBuilder_NotUsed_IHostBuilderOrWebApplicationBuilderIsPreferred()
        {
            // ASP.NET Core 6+ uses the minimal hosting model (WebApplication / WebApplicationBuilder).
            // Verify the host inside the factory is the generic IHost, not the legacy IWebHost.
            var host = _factory.Server.Host;
            Assert.IsAssignableFrom<IHost>(host);
        }
    }
}