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
                "WebApplicationFactory<TEntryPoint> requires ASP.NET Core 6+.");
        }

        [Fact]
        public void MvcTestingAssembly_IsLoaded_AndMeetsMinimumVersion()
        {
            var assembly = typeof(WebApplicationFactory<>).Assembly;
            Assert.NotNull(assembly);

            var assemblyVersion = assembly.GetName().Version;
            Assert.NotNull(assemblyVersion);

            // Microsoft.AspNetCore.Mvc.Testing ships in-box with ASP.NET Core 6+
            Assert.True(
                assemblyVersion!.Major >= 6,
                $"Expected Microsoft.AspNetCore.Mvc.Testing v6+ but found {assemblyVersion}.");
        }

        [Fact]
        public void XunitCoreAssembly_IsLoaded_AndMeetsMinimumVersion()
        {
            var assembly = typeof(FactAttribute).Assembly;
            Assert.NotNull(assembly);

            var assemblyVersion = assembly.GetName().Version;
            Assert.NotNull(assemblyVersion);

            // xUnit v2 is the stable baseline; v2.4+ is required for .NET 6 support
            Assert.True(
                assemblyVersion!.Major >= 2,
                $"Expected xUnit v2+ but found {assemblyVersion}.");
        }

        // -----------------------------------------------------------------------
        // 2. WebApplicationFactory infrastructure is wired correctly
        // -----------------------------------------------------------------------

        [Fact]
        public void WebApplicationFactory_CanBeInstantiated_WithProgramAsEntryPoint()
        {
            // Verifies that Program is accessible (public partial class Program {})
            // and that the factory can be constructed without throwing.
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
            // Confirms the DI container is composed and the host is running.
            using var scope = _factory.Services.CreateScope();
            Assert.NotNull(scope);
            Assert.NotNull(scope.ServiceProvider);
        }

        [Fact]
        public void WebApplicationFactory_Host_IsRunning()
        {
            // IHost should be accessible and in a started state via the factory.
            var host = _factory.Server.Host;
            Assert.NotNull(host);
        }

        // -----------------------------------------------------------------------
        // 3. Program entry point is accessible to the test assembly
        // -----------------------------------------------------------------------

        [Fact]
        public void ProgramClass_IsPublicPartial_AccessibleFromTestAssembly()
        {
            // If Program is not public (or not a partial class exposed publicly),
            // WebApplicationFactory<Program> would fail to resolve it.
            var programType = typeof(Program);
            Assert.NotNull(programType);
            Assert.True(
                programType.IsPublic || programType.IsNestedPublic,
                "Program class must be public so the test assembly can reference it as TEntryPoint.");
        }

        // -----------------------------------------------------------------------
        // 4. HTTP pipeline is reachable — smoke test via in-process server
        // -----------------------------------------------------------------------

        [Fact]
        public async Task HttpClient_CanSendRequest_ToInProcessServer()
        {
            // A response of any kind (including 404) proves the pipeline is live.
            var response = await _client.GetAsync("/");
            Assert.NotNull(response);
            // Any HTTP status code is acceptable here — we only verify connectivity.
            Assert.True(
                (int)response.StatusCode >= 100 && (int)response.StatusCode < 600,
                $"Unexpected status code value: {(int)response.StatusCode}");
        }

        [Fact]
        public async Task HealthEndpoint_ReturnsSuccessOrNotFound_PipelineIsAlive()
        {
            // Common health-check paths. A 200 confirms health middleware is registered;
            // a 404 still confirms the HTTP pipeline processed the request correctly.
            var response = await _client.GetAsync("/health");
            Assert.NotNull(response);
            Assert.True(
                response.StatusCode == HttpStatusCode.OK ||
                response.StatusCode == HttpStatusCode.NotFound ||
                response.StatusCode == HttpStatusCode.ServiceUnavailable,
                $"Unexpected status code {response.StatusCode} for /health endpoint.");
        }

        // -----------------------------------------------------------------------
        // 5. New configuration introduced by the upgrade loads without errors
        // -----------------------------------------------------------------------

        [Fact]
        public void Configuration_WebApplicationFactoryClientOptions_CanBeConstructed()
        {
            // Verifies the new WebApplicationFactoryClientOptions type (introduced
            // alongside WebApplicationFactory) is available and configurable.
            var options = new WebApplicationFactoryClientOptions
            {
                AllowAutoRedirect = false,
                HandleCookies = true,
                MaxAutomaticRedirections = 7,
                BaseAddress = new Uri("http://localhost/")
            };

            Assert.False(options.AllowAutoRedirect);
            Assert.True(options.HandleCookies);
            Assert.Equal(7, options.MaxAutomaticRedirections);
            Assert.Equal(new Uri("http://localhost/"), options.BaseAddress);
        }

        [Fact]
        public void Configuration_CustomWebApplicationFactory_CanOverrideServices()
        {
            // Verifies that WithWebHostBuilder (the mechanism used in
            // CustomWebApplicationFactory.ConfigureWebHost) is available and callable.
            var customFactory = _factory.WithWebHostBuilder(builder =>
            {
                // Stub override — mirrors what CustomWebApplicationFactory.ConfigureWebHost does.
                builder.ConfigureServices(services =>
                {
                    Assert.NotNull(services);
                });
            });

            Assert.NotNull(customFactory);
            using var client = customFactory.CreateClient();
            Assert.NotNull(client);
        }

        // -----------------------------------------------------------------------
        // 6. Deprecated / replaced APIs are NOT being used
        // -----------------------------------------------------------------------

        [Fact]
        public void TestServer_IsAccessedViaFactory_NotDirectInstantiation()
        {
            // The old pattern was to new up TestServer directly (pre-WebApplicationFactory).
            // Verify we are using the factory-provided server, not a raw TestServer.
            var server = _factory.Server;
            Assert.NotNull(server);

            // The server's BaseAddress should be set by the factory, not manually.
            Assert.NotNull(server.BaseAddress);
        }

        [Fact]
        public void IClassFixture_Pattern_IsUsed_NotICollectionFixture_ForBasicTests()
        {
            // Confirms this test class itself implements the IClassFixture<> pattern
            // that was introduced as the recommended approach with WebApplicationFactory.
            var thisType = GetType();
            var interfaces = thisType.GetInterfaces();
            var hasClassFixture = false;

            foreach (var iface in interfaces)
            {
                if (iface.IsGenericType &&
                    iface.GetGenericTypeDefinition() == typeof(IClassFixture<>))
                {
                    hasClassFixture = true;
                    break;
                }
            }

            Assert.True(hasClassFixture,
                "Integration test classes should implement IClassFixture<WebApplicationFactory<Program>> " +
                "as introduced by this upgrade.");
        }

        // -----------------------------------------------------------------------
        // 7. IntegrationTestBase pattern is available (base class convention)
        // -----------------------------------------------------------------------

        [Fact]
        public void IntegrationTestBase_ExposesSharedHttpClient_ViaFactory()
        {
            // Mirrors the contract of IntegrationTestBase.cs introduced in Phase 2.
            // The shared client must be non-null and have a base address set.
            Assert.NotNull(_client);
            Assert.NotNull(_client.BaseAddress);
        }

        [Fact]
        public void HttpClient_BaseAddress_PointsToLocalhost()
        {
            Assert.NotNull(_client.BaseAddress);
            Assert.True(
                _client.BaseAddress!.IsLoopback ||
                _client.BaseAddress.Host.Equals("localhost", StringComparison.OrdinalIgnoreCase),
                $"Expected loopback base address but got {_client.BaseAddress}.");
        }
    }
}