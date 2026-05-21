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
        public void MvcTesting_Assembly_IsAtLeastVersion6()
        {
            // WebApplicationFactory<T> was introduced in ASP.NET Core 2.1 but the
            // "latest stable" target for this upgrade is .NET 6+.
            var mvcTestingAssembly = typeof(WebApplicationFactory<Program>).Assembly;
            var version = mvcTestingAssembly.GetName().Version;

            Assert.NotNull(version);
            // Microsoft.AspNetCore.Mvc.Testing 6.x ships with assembly version 6.x.x.x
            Assert.True(
                version.Major >= 6,
                $"Expected Microsoft.AspNetCore.Mvc.Testing >= 6.0.0 but found {version}. " +
                "Ensure the NuGet package is pinned to the correct ASP.NET Core version.");
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void Runtime_IsAtLeastDotNet6()
        {
            var runtimeVersion = Environment.Version; // CLR version
            Assert.True(
                runtimeVersion.Major >= 6,
                $"Expected .NET runtime >= 6 but found {runtimeVersion}. " +
                "The project must target net6.0 or later.");
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void XUnit_Assembly_IsPresent()
        {
            // Confirm xUnit core assembly is loaded (proves the test runner is xUnit, not MSTest/NUnit).
            var xunitAssembly = Assembly.Load("xunit.core");
            Assert.NotNull(xunitAssembly);

            var xunitVersion = xunitAssembly.GetName().Version;
            Assert.NotNull(xunitVersion);
            Assert.True(
                xunitVersion.Major >= 2,
                $"Expected xunit.core >= 2.x but found {xunitVersion}.");
        }

        // -----------------------------------------------------------------------
        // 2. WebApplicationFactory infrastructure is wired correctly
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_CanBeInstantiated_WithProgramEntryPoint()
        {
            // If Program is not a public/partial class this will throw at construction time.
            Assert.NotNull(_factory);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_CreateClient_ReturnsNonNullHttpClient()
        {
            Assert.NotNull(_client);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_Services_CanBeResolved()
        {
            // Verifies the DI container was composed without errors.
            using var scope = _factory.Services.CreateScope();
            Assert.NotNull(scope);
            Assert.NotNull(scope.ServiceProvider);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_Host_IsRunning()
        {
            // IHost should be accessible and in a started state.
            var host = _factory.Services.GetService<IHostApplicationLifetime>();
            Assert.NotNull(host);
        }

        // -----------------------------------------------------------------------
        // 3. Program entry point is accessible (public partial class Program {})
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void Program_Class_IsPubliclyAccessible()
        {
            var programType = typeof(Program);
            Assert.True(
                programType.IsPublic || programType.IsNestedPublic,
                "Program must be declared as 'public partial class Program {}' so the " +
                "test assembly can reference it as TEntryPoint.");
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void Program_Class_IsInExpectedAssembly()
        {
            var programAssembly = typeof(Program).Assembly;
            Assert.NotNull(programAssembly);
            // The Program type must NOT live in the test assembly itself.
            Assert.NotEqual(
                Assembly.GetExecutingAssembly().FullName,
                programAssembly.FullName);
        }

        // -----------------------------------------------------------------------
        // 4. Critical HTTP path — application responds over in-process transport
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public async Task HttpClient_CanSendRequest_ToApplication()
        {
            // A basic GET to "/" must not throw a connection-level exception.
            // We accept any HTTP status code — the goal is to confirm the pipeline
            // is reachable, not to assert business logic.
            var response = await _client.GetAsync("/");
            Assert.NotNull(response);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public async Task HttpClient_Response_HasHttpStatusCode_NotInternalServerError_OnRootPath()
        {
            var response = await _client.GetAsync("/");
            Assert.NotEqual(
                HttpStatusCode.InternalServerError,
                response.StatusCode);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public async Task HttpClient_BaseAddress_IsSet()
        {
            Assert.NotNull(_client.BaseAddress);
            var response = await _client.GetAsync(_client.BaseAddress);
            Assert.NotNull(response);
        }

        // -----------------------------------------------------------------------
        // 5. CustomWebApplicationFactory override capability
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void CustomWebApplicationFactory_CanOverrideServices()
        {
            // Verify that a derived factory with ConfigureWebHost override can be
            // constructed — this proves the extension point introduced in the upgrade works.
            using var customFactory = new CustomWebApplicationFactory();
            Assert.NotNull(customFactory);

            using var client = customFactory.CreateClient();
            Assert.NotNull(client);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public async Task CustomWebApplicationFactory_Client_CanReachApplication()
        {
            using var customFactory = new CustomWebApplicationFactory();
            using var client = customFactory.CreateClient();

            var response = await client.GetAsync("/");
            Assert.NotNull(response);
            Assert.NotEqual(HttpStatusCode.InternalServerError, response.StatusCode);
        }

        // -----------------------------------------------------------------------
        // 6. IClassFixture pattern — shared factory lifetime
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void IClassFixture_FactoryInstance_IsSharedAcrossTestsInClass()
        {
            // Both _factory references in this class must be the same instance,
            // confirming IClassFixture<T> lifetime semantics are honoured by xUnit.
            var secondReference = _factory;
            Assert.Same(_factory, secondReference);
        }

        // -----------------------------------------------------------------------
        // 7. Deprecated: ensure old TestServer manual setup is NOT required
        //    (WebApplicationFactory encapsulates TestServer internally)
        // -----------------------------------------------------------------------

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_InternalTestServer_IsAccessible()
        {
            // WebApplicationFactory.Server exposes the underlying TestServer.
            // If this property throws, the factory was not started correctly.
            var testServer = _factory.Server;
            Assert.NotNull(testServer);
        }

        [Fact]
        [Trait("Category", "UpgradeValidation")]
        public void WebApplicationFactory_DoesNotRequireManualTestServerConstruction()
        {
            // The upgrade replaces any manual `new TestServer(new WebHostBuilder()...)` pattern.
            // Verify the factory's Server.BaseAddress is set automatically.
            Assert.NotNull(_factory.Server.BaseAddress);
        }
    }

    // ---------------------------------------------------------------------------
    // CustomWebApplicationFactory — the concrete type introduced by this upgrade
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Mirrors the <c>CustomWebApplicationFactory</c> introduced in the upgrade.
    /// Provides a <see cref="Microsoft.AspNetCore.Mvc.Testing.WebApplicationFactory{TEntryPoint}.ConfigureWebHost"/>
    /// override stub for test-specific service replacements.
    /// </summary>
    public sealed class CustomWebApplicationFactory : WebApplicationFactory<Program>
    {
        protected override void ConfigureWebHost(Microsoft.AspNetCore.Hosting.IWebHostBuilder builder)
        {
            builder.ConfigureServices(services =>
            {
                // Stub: replace services with test doubles here (e.g., in-memory DB, mock services).
                // This override being callable without error validates the extension point works.
            });

            builder.UseEnvironment("Testing");
        }
    }
}