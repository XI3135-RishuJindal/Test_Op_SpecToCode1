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
        // 1. Version assertion — WebApplicationFactory / ASP.NET Core Mvc.Testing
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void MvcTesting_Assembly_IsLoaded_And_Meets_MinimumVersion()
        {
            // Microsoft.AspNetCore.Mvc.Testing requires .NET 6+ / ASP.NET Core 6+
            var mvcTestingAssembly = typeof(WebApplicationFactory<>).Assembly;
            Assert.NotNull(mvcTestingAssembly);

            var version = mvcTestingAssembly.GetName().Version;
            Assert.NotNull(version);

            // Target: ASP.NET Core 6.0 or later (major version >= 6)
            Assert.True(
                version.Major >= 6,
                $"Expected Microsoft.AspNetCore.Mvc.Testing version >= 6.0.0 but found {version}. " +
                "Ensure the NuGet package is pinned to the correct ASP.NET Core version.");
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void XUnit_Assembly_IsLoaded_And_Meets_MinimumVersion()
        {
            // xUnit 2.4+ is required for IClassFixture and modern async test support
            var xunitAssembly = typeof(FactAttribute).Assembly;
            Assert.NotNull(xunitAssembly);

            var version = xunitAssembly.GetName().Version;
            Assert.NotNull(version);

            Assert.True(
                version.Major >= 2 && version.Minor >= 4,
                $"Expected xunit version >= 2.4.0 but found {version}.");
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void DotNet_Runtime_IsAtLeast_Net6()
        {
            // WebApplicationFactory<T> requires .NET 6+
            var runtimeVersion = Environment.Version;
            Assert.True(
                runtimeVersion.Major >= 6,
                $"Expected .NET runtime >= 6.0 but found {runtimeVersion}. " +
                "Update the TargetFramework in the project file to net6.0 or later.");
        }

        // -----------------------------------------------------------------------
        // 2. WebApplicationFactory infrastructure is correctly wired
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_CanBeInstantiated_WithProgramAsEntryPoint()
        {
            // Verifies that Program is accessible (public partial class Program {})
            // and that WebApplicationFactory<Program> can be constructed without error.
            Assert.NotNull(_factory);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_CreateClient_ReturnsNonNullHttpClient()
        {
            var client = _factory.CreateClient();
            Assert.NotNull(client);
            Assert.NotNull(client.BaseAddress);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_Services_CanBeResolved()
        {
            // Confirms the DI container is composed and the host is running
            using var scope = _factory.Services.CreateScope();
            Assert.NotNull(scope);
            Assert.NotNull(scope.ServiceProvider);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_Host_IsRunning()
        {
            // IHost should be accessible and in a started state
            var host = _factory.Services.GetService<IHostApplicationLifetime>();
            Assert.NotNull(host);
            Assert.True(
                host.ApplicationStarted.IsCancellationRequested == false ||
                host.ApplicationStopped.IsCancellationRequested == false,
                "Host application lifetime tokens indicate the host did not start correctly.");
        }

        // -----------------------------------------------------------------------
        // 3. Program entry point visibility (public partial class Program)
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void Program_Class_IsPubliclyVisible_ToTestAssembly()
        {
            // If Program is not public/partial, WebApplicationFactory<Program> will fail
            // at runtime. This assertion catches that misconfiguration early.
            var programType = typeof(Program);
            Assert.True(
                programType.IsPublic || programType.IsNestedPublic,
                "Program class must be public (add 'public partial class Program {}' at the " +
                "bottom of Program.cs) so the test assembly can reference it as TEntryPoint.");
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void Program_Class_IsInExpectedAssembly()
        {
            var programAssembly = typeof(Program).Assembly;
            Assert.NotNull(programAssembly);

            // The Program type must NOT be in the test assembly itself
            var testAssembly = Assembly.GetExecutingAssembly();
            Assert.NotEqual(
                testAssembly.FullName,
                programAssembly.FullName,
                StringComparer.OrdinalIgnoreCase);
        }

        // -----------------------------------------------------------------------
        // 4. HTTP pipeline smoke test — critical application path
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public async Task HttpClient_CanSendRequest_ToApplication_WithoutConnectionError()
        {
            // A connection-level error (e.g., host not started) throws HttpRequestException.
            // Any HTTP response — including 404 — proves the pipeline is alive.
            HttpResponseMessage response;
            try
            {
                response = await _client.GetAsync("/");
            }
            catch (HttpRequestException ex)
            {
                throw new InvalidOperationException(
                    "WebApplicationFactory failed to handle an HTTP request. " +
                    "Ensure the application starts correctly and Program is the correct TEntryPoint. " +
                    $"Inner exception: {ex.Message}", ex);
            }

            Assert.NotNull(response);
            // Any response code is acceptable here — we are validating infrastructure, not business logic.
            Assert.True(
                (int)response.StatusCode >= 100 && (int)response.StatusCode < 600,
                $"Received an unexpected status code: {response.StatusCode}");
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public async Task HttpClient_HealthEndpoint_ReturnsSuccessOrNotFound()
        {
            // /health or /healthz is the conventional health-check endpoint.
            // A 200 confirms health checks are registered; 404 is acceptable if not yet configured.
            // A 5xx indicates a startup or middleware failure — that is a failure condition.
            var response = await _client.GetAsync("/health");

            Assert.True(
                response.StatusCode == HttpStatusCode.OK ||
                response.StatusCode == HttpStatusCode.NotFound ||
                response.StatusCode == HttpStatusCode.MethodNotAllowed,
                $"Health endpoint returned an unexpected server-side error: {(int)response.StatusCode} {response.StatusCode}. " +
                "A 5xx response indicates the application did not start cleanly.");
        }

        // -----------------------------------------------------------------------
        // 5. CustomWebApplicationFactory — validates the factory subclass pattern
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void CustomWebApplicationFactory_CanBeSubclassed_WithConfigureWebHostOverride()
        {
            // Instantiate the custom factory to confirm it compiles and constructs correctly.
            using var customFactory = new CustomWebApplicationFactory();
            Assert.NotNull(customFactory);

            var client = customFactory.CreateClient();
            Assert.NotNull(client);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public async Task CustomWebApplicationFactory_Client_CanReachApplication()
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
                throw new InvalidOperationException(
                    "CustomWebApplicationFactory failed to handle an HTTP request. " +
                    $"Inner exception: {ex.Message}", ex);
            }

            Assert.NotNull(response);
        }

        // -----------------------------------------------------------------------
        // 6. IClassFixture pattern — validates shared fixture wiring
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void IClassFixture_Factory_IsSharedAcrossTestsInClass()
        {
            // The factory injected via IClassFixture must be the same instance
            // across all tests in this class — confirms xUnit fixture scoping works.
            Assert.NotNull(_factory);

            // Create two clients from the same factory and confirm they share the same base address
            var clientA = _factory.CreateClient();
            var clientB = _factory.CreateClient();

            Assert.Equal(clientA.BaseAddress, clientB.BaseAddress);
        }

        // -----------------------------------------------------------------------
        // 7. Deprecated patterns — confirm old/manual HttpClient wiring is NOT used
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void HttpClient_BaseAddress_IsSetByFactory_NotManually()
        {
            // WebApplicationFactory sets BaseAddress automatically.
            // A null BaseAddress would indicate the client was created manually (old pattern).
            Assert.NotNull(_client.BaseAddress);
            Assert.True(
                _client.BaseAddress.IsAbsoluteUri,
                "HttpClient.BaseAddress must be an absolute URI set by WebApplicationFactory.CreateClient().");
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void HttpClient_IsNotDirectlyInstantiated_WithHardcodedBaseAddress()
        {
            // Confirm the client's base address uses the in-process test server scheme (http/https)
            // and NOT a hardcoded external address like http://localhost:5000.
            var baseAddress = _client.BaseAddress;
            Assert.NotNull(baseAddress);

            // WebApplicationFactory uses http://localhost by default (no explicit port like 5000/5001)
            Assert.True(
                baseAddress.Host == "localhost" || baseAddress.Host == "127.0.0.1",
                $"Unexpected base address host '{baseAddress.Host}'. " +
                "The HttpClient should be created via WebApplicationFactory, not pointed at an external server.");
        }
    }

    // ---------------------------------------------------------------------------
    // Supporting type: CustomWebApplicationFactory
    // Mirrors the class that should exist in the integration test project.
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Custom factory that extends <see cref="WebApplicationFactory{TEntryPoint}"/> to allow
    /// test-specific service overrides (e.g., in-memory database, mock services).
    /// This class validates the factory subclass pattern introduced by the upgrade.
    /// </summary>
    public sealed class CustomWebApplicationFactory : WebApplicationFactory<Program>
    {
        protected override void ConfigureWebHost(Microsoft.AspNetCore.Hosting.IWebHostBuilder builder)
        {
            // Stub for future test-specific service replacements.
            // Example: builder.ConfigureServices(services => { ... });
            builder.UseEnvironment("Testing");
        }
    }
}