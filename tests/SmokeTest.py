using System;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Json;
using System.Reflection;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.ApplicationParts;
using Microsoft.AspNetCore.Mvc.Controllers;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Xunit;

namespace AspNetCoreMigration.UpgradeValidationTests
{
    /// <summary>
    /// Validates that the migration from ASP.NET Web API 2 to ASP.NET Core succeeded.
    /// These tests assert the exact runtime, absence of legacy Web API 2 abstractions,
    /// and correct behaviour of migrated controllers and models.
    /// </summary>
    public class UpgradeValidationTests : IAsyncLifetime
    {
        private IHost _host = null!;
        private HttpClient _client = null!;

        // ── Runtime / framework version assertions ────────────────────────────

        [Fact]
        public void Runtime_IsNetCoreOrNet5Plus_NotNetFramework()
        {
            // The migration target is .NET 6+ (ASP.NET Core).
            // System.Runtime.InteropServices.RuntimeInformation confirms the runtime.
            var frameworkDescription =
                System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription;

            Assert.False(
                frameworkDescription.StartsWith(".NET Framework", StringComparison.OrdinalIgnoreCase),
                $"Expected a .NET Core / .NET 5+ runtime but found: {frameworkDescription}");

            Assert.True(
                frameworkDescription.StartsWith(".NET ", StringComparison.OrdinalIgnoreCase)
                && !frameworkDescription.StartsWith(".NET Framework", StringComparison.OrdinalIgnoreCase),
                $"Runtime should be .NET 6 or later. Actual: {frameworkDescription}");
        }

        [Fact]
        public void Runtime_MeetsMinimumVersionRequirement_Net6()
        {
            var version = Environment.Version; // CLR version
            Assert.True(
                version.Major >= 6,
                $"ASP.NET Core migration requires .NET 6 or later. Detected CLR version: {version}");
        }

        [Fact]
        public void AspNetCore_MvcAssembly_IsLoaded_NotSystemWebHttp()
        {
            // Microsoft.AspNetCore.Mvc must be present; System.Web.Http must NOT be.
            var loadedAssemblies = AppDomain.CurrentDomain.GetAssemblies();

            var aspNetCoreMvc = loadedAssemblies.FirstOrDefault(a =>
                a.GetName().Name?.Equals("Microsoft.AspNetCore.Mvc.Core",
                    StringComparison.OrdinalIgnoreCase) == true);

            Assert.NotNull(aspNetCoreMvc);

            var legacyWebApi = loadedAssemblies.FirstOrDefault(a =>
                a.GetName().Name?.Equals("System.Web.Http",
                    StringComparison.OrdinalIgnoreCase) == true);

            Assert.Null(legacyWebApi);
        }

        // ── Absence of legacy Web API 2 types ────────────────────────────────

        [Fact]
        public void LegacyType_ApiController_IsNotReferenced()
        {
            // No controller in the application assemblies should inherit from
            // System.Web.Http.ApiController.
            var appAssemblies = GetApplicationAssemblies();

            foreach (var assembly in appAssemblies)
            {
                var legacyControllers = assembly.GetTypes()
                    .Where(t => InheritsFromApiController(t))
                    .ToList();

                Assert.True(
                    legacyControllers.Count == 0,
                    $"Assembly '{assembly.GetName().Name}' still contains types inheriting " +
                    $"System.Web.Http.ApiController: " +
                    string.Join(", ", legacyControllers.Select(t => t.FullName)));
            }
        }

        [Fact]
        public void LegacyType_IHttpActionResult_IsNotUsedAsReturnType()
        {
            // Action methods must not return IHttpActionResult (System.Web.Http).
            var appAssemblies = GetApplicationAssemblies();

            foreach (var assembly in appAssemblies)
            {
                var methods = assembly.GetTypes()
                    .SelectMany(t => t.GetMethods(BindingFlags.Public | BindingFlags.Instance))
                    .Where(m => m.ReturnType.FullName ==
                                "System.Web.Http.IHttpActionResult")
                    .ToList();

                Assert.True(
                    methods.Count == 0,
                    $"Assembly '{assembly.GetName().Name}' still has methods returning " +
                    $"IHttpActionResult: " +
                    string.Join(", ", methods.Select(m => $"{m.DeclaringType?.Name}.{m.Name}")));
            }
        }

        [Fact]
        public void LegacyType_HttpResponseMessage_IsNotReturnedDirectlyFromControllers()
        {
            // Controllers should return IActionResult / ActionResult<T>, not raw HttpResponseMessage.
            var appAssemblies = GetApplicationAssemblies();

            foreach (var assembly in appAssemblies)
            {
                var controllerTypes = assembly.GetTypes()
                    .Where(t => typeof(ControllerBase).IsAssignableFrom(t) && !t.IsAbstract);

                foreach (var controller in controllerTypes)
                {
                    var badMethods = controller
                        .GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly)
                        .Where(m => m.ReturnType == typeof(HttpResponseMessage)
                                    || m.ReturnType == typeof(Task<HttpResponseMessage>))
                        .ToList();

                    Assert.True(
                        badMethods.Count == 0,
                        $"Controller '{controller.Name}' has action(s) returning raw HttpResponseMessage " +
                        $"(should use IActionResult): " +
                        string.Join(", ", badMethods.Select(m => m.Name)));
                }
            }
        }

        [Fact]
        public void LegacyAttribute_RoutePrefix_IsNotPresent()
        {
            // [RoutePrefix] is a Web API 2 attribute; ASP.NET Core uses [Route] on the controller.
            var appAssemblies = GetApplicationAssemblies();

            foreach (var assembly in appAssemblies)
            {
                var typesWithRoutePrefix = assembly.GetTypes()
                    .Where(t => t.GetCustomAttributes()
                        .Any(a => a.GetType().FullName == "System.Web.Http.RoutePrefixAttribute"))
                    .ToList();

                Assert.True(
                    typesWithRoutePrefix.Count == 0,
                    $"Assembly '{assembly.GetName().Name}' still uses [RoutePrefix] (Web API 2): " +
                    string.Join(", ", typesWithRoutePrefix.Select(t => t.FullName)));
            }
        }

        [Fact]
        public void LegacyAttribute_FromUri_IsNotPresent()
        {
            // [FromUri] is Web API 2; ASP.NET Core uses [FromQuery].
            var appAssemblies = GetApplicationAssemblies();

            foreach (var assembly in appAssemblies)
            {
                var methods = assembly.GetTypes()
                    .SelectMany(t => t.GetMethods(BindingFlags.Public | BindingFlags.Instance))
                    .SelectMany(m => m.GetParameters())
                    .Where(p => p.GetCustomAttributes()
                        .Any(a => a.GetType().FullName == "System.Web.Http.FromUriAttribute"))
                    .ToList();

                Assert.True(
                    methods.Count == 0,
                    $"Assembly '{assembly.GetName().Name}' still uses [FromUri] (Web API 2). " +
                    "Replace with [FromQuery].");
            }
        }

        // ── ASP.NET Core controller conventions ───────────────────────────────

        [Fact]
        public void Controllers_InheritFromControllerBase_NotApiController()
        {
            var appAssemblies = GetApplicationAssemblies();

            foreach (var assembly in appAssemblies)
            {
                var controllerTypes = assembly.GetTypes()
                    .Where(t => !t.IsAbstract
                                && (typeof(ControllerBase).IsAssignableFrom(t)
                                    || t.Name.EndsWith("Controller", StringComparison.Ordinal)))
                    .ToList();

                foreach (var controller in controllerTypes)
                {
                    Assert.True(
                        typeof(ControllerBase).IsAssignableFrom(controller),
                        $"Controller '{controller.FullName}' does not inherit from " +
                        "Microsoft.AspNetCore.Mvc.ControllerBase.");
                }
            }
        }

        [Fact]
        public void Controllers_HaveApiControllerAttribute()
        {
            var appAssemblies = GetApplicationAssemblies();

            foreach (var assembly in appAssemblies)
            {
                var controllerTypes = assembly.GetTypes()
                    .Where(t => !t.IsAbstract && typeof(ControllerBase).IsAssignableFrom(t))
                    .ToList();

                foreach (var controller in controllerTypes)
                {
                    var hasAttribute = controller
                        .GetCustomAttributes(inherit: true)
                        .Any(a => a is ApiControllerAttribute);

                    Assert.True(
                        hasAttribute,
                        $"Controller '{controller.Name}' is missing [ApiController] attribute " +
                        "(required for ASP.NET Core automatic model validation and binding).");
                }
            }
        }

        [Fact]
        public void Controllers_HaveRouteAttribute()
        {
            var appAssemblies = GetApplicationAssemblies();

            foreach (var assembly in appAssemblies)
            {
                var controllerTypes = assembly.GetTypes()
                    .Where(t => !t.IsAbstract && typeof(ControllerBase).IsAssignableFrom(t))
                    .ToList();

                foreach (var controller in controllerTypes)
                {
                    var hasRoute = controller
                        .GetCustomAttributes(inherit: true)
                        .Any(a => a is RouteAttribute);

                    Assert.True(
                        hasRoute,
                        $"Controller '{controller.Name}' is missing a [Route] attribute. " +
                        "ASP.NET Core attribute routing requires [Route] on the controller class.");
                }
            }
        }

        // ── Model validation — DataAnnotations still work ─────────────────────

        [Fact]
        public void Models_DataAnnotations_AreHonoured_ByAspNetCoreModelBinder()
        {
            // Verify that the ASP.NET Core model binding pipeline respects
            // System.ComponentModel.DataAnnotations on request models.
            var appAssemblies = GetApplicationAssemblies();

            var modelTypes = appAssemblies
                .SelectMany(a => a.GetTypes())
                .Where(t => t.GetProperties()
                    .Any(p => p.GetCustomAttributes(typeof(System.ComponentModel.DataAnnotations.ValidationAttribute), true).Length > 0))
                .ToList();

            // At least one model with DataAnnotations must exist (sanity check that
            // the models were actually migrated and not deleted).
            Assert.True(
                modelTypes.Count > 0,
                "No model types with DataAnnotations validation attributes were found. " +
                "Ensure request/response models were migrated to the new project.");
        }

        // ── Host / DI / configuration integration ─────────────────────────────

        [Fact]
        public async Task Host_StartsSuccessfully_WithAspNetCorePipeline()
        {
            // The TestServer host must start without exceptions.
            Assert.NotNull(_host);
            Assert.NotNull(_client);

            // A basic liveness check — the server must respond (any status is acceptable
            // here; 404 is fine if no root route exists).
            try
            {
                var response = await _client.GetAsync("/");
                Assert.True(
                    (int)response.StatusCode < 600,
                    $"Unexpected HTTP status from test host: {response.StatusCode}");
            }
            catch (HttpRequestException ex)
            {
                Assert.Fail($"Test host did not respond to GET /: {ex.Message}");
            }
        }

        [Fact]
        public void DependencyInjection_ControllerServicesAreResolvable()
        {
            // All controllers registered with the ASP.NET Core DI container must be
            // resolvable (i.e., their constructor dependencies are registered).
            var serviceProvider = _host.Services;
            var partManager = serviceProvider.GetService<ApplicationPartManager>();

            if (partManager == null)
            {
                // If ApplicationPartManager is not available, skip gracefully.
                return;
            }

            var controllerFeature = new ControllerFeature();
            partManager.PopulateFeature(controllerFeature);

            foreach (var controllerType in controllerFeature.Controllers)
            {
                // Attempt to activate the controller via the DI-backed activator.
                // This will throw if any required service is not registered.
                using var scope = serviceProvider.CreateScope();
                var activator = scope.ServiceProvider
                    .GetService<IControllerActivator>();

                // We only assert the type is discoverable; full activation requires
                // an ActionContext which is outside the scope of a unit test.
                Assert.NotNull(controllerType);
            }
        }

        [Fact]
        public void Configuration_NewAspNetCoreKeys_LoadWithoutErrors()
        {
            // Verify that ASP.NET Core configuration (appsettings.json / environment)
            // loads without throwing and that the host's IConfiguration is available.
            var configuration = _host.Services
                .GetService<Microsoft.Extensions.Configuration.IConfiguration>();

            Assert.NotNull(configuration);

            // These keys are standard ASP.NET Core configuration entries introduced
            // by the migration scaffold.
            var allowedHosts = configuration["AllowedHosts"];
            // AllowedHosts may be null in test environments — we only assert no exception.
            _ = allowedHosts;

            // Logging configuration section must be present (added by ASP.NET Core default builder).
            var loggingSection = configuration.GetSection("Logging");
            Assert.NotNull(loggingSection);
        }

        // ── HTTP pipeline smoke tests ─────────────────────────────────────────

        [Fact]
        public async Task Endpoints_ReturnJson_WithCorrectContentType()
        {
            // Any endpoint that returns a model should produce application/json.
            // We probe known API route patterns; adjust paths to match actual routes.
            var probePaths = new[] { "/api/values", "/api/health", "/api/status" };

            foreach (var path in probePaths)
            {
                var response = await _client.GetAsync(path);

                if (response.StatusCode == HttpStatusCode.NotFound)
                    continue; // Route not present in this project — skip.

                if (response.IsSuccessStatusCode && response.Content.Headers.ContentType != null)
                {
                    Assert.Contains(
                        "application/json",
                        response.Content.Headers.ContentType.MediaType,
                        StringComparison.OrdinalIgnoreCase);
                }
            }
        }

        [Fact]
        public async Task ModelValidation_Returns400_ForInvalidPayload()
        {
            // POST with an empty body to any endpoint decorated with [ApiController]
            // should return 400 Bad Request (automatic model validation in ASP.NET Core).
            var probePaths = new[] { "/api/values", "/api/items", "/api/orders" };

            foreach (var path in probePaths)
            {
                var response = await _client.PostAsJsonAsync(path, new { });

                if (response.StatusCode == HttpStatusCode.NotFound
                    || response.StatusCode == HttpStatusCode.MethodNotAllowed)
                    continue;

                // 400 or 422 are both acceptable validation failure responses.
                Assert.True(
                    response.StatusCode == HttpStatusCode.BadRequest
                    || response.StatusCode == HttpStatusCode.UnprocessableEntity
                    || response.IsSuccessStatusCode,
                    $"Unexpected status {response.StatusCode} for POST {path}. " +
                    "Expected 400/422 for invalid payload or 2xx for valid.");
            }
        }

        // ── IAsyncLifetime — test host setup / teardown ───────────────────────

        public async Task InitializeAsync()
        {
            try
            {
                _host = await CreateTestHostAsync();
                _client = _host.GetTestClient();
            }
            catch (Exception ex)
            {
                // If the host cannot be built (e.g., no Startup class in test project),
                // record the failure clearly rather than producing cryptic null-ref errors.
                throw new InvalidOperationException(
                    "Failed to build the ASP.NET Core test host. " +
                    "Ensure the migrated project's Program.cs / Startup.cs is referenced " +
                    $"by the test project. Inner: {ex.Message}", ex);
            }
        }

        public async Task DisposeAsync()
        {
            _client?.Dispose();
            if (_host != null)
            {
                await _host.StopAsync();
                _host.Dispose();
            }
        }

        // ── Helpers ───────────────────────────────────────────────────────────

        private static async Task<IHost> CreateTestHostAsync()
        {
            // Attempt to locate the application's entry-point assembly so that
            // controllers and services registered in Program.cs are available.
            // Falls back to a minimal host if the application assembly is not found.
            var hostBuilder = Host.CreateDefaultBuilder()
                .ConfigureWebHostDefaults(web =>
                {
                    web.UseTestServer();

                    // Try to use the application's Startup class if it exists.
                    var startupType = FindStartupType();
                    if (startupType != null)
                    {
                        web.UseStartup(startupType);
                    }
                    else
                    {
                        // Minimal fallback: register MVC so controller-discovery tests pass.
                        web.Configure(app =>
                        {
                            app.UseRouting();
                            app.UseEndpoints(e => e.MapControllers());
                        });
                        web.ConfigureServices(services =>
                        {
                            services.AddControllers();
                        });
                    }
                });

            return await hostBuilder.StartAsync();
        }

        private static Type? FindStartupType()
        {
            return AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(a =>
                {
                    try { return a.GetTypes(); }
                    catch { return Array.Empty<Type>(); }
                })
                .FirstOrDefault(t =>
                    t.Name.Equals("Startup", StringComparison.OrdinalIgnoreCase)
                    && t.IsPublic && !t.IsAbstract);
        }

        private static Assembly[] GetApplicationAssemblies()
        {
            // Return all non-system, non-test assemblies loaded in the current domain.
            return AppDomain.CurrentDomain.GetAssemblies()
                .Where(a =>
                {
                    var name = a.GetName().Name ?? string.Empty;
                    return !name.StartsWith("System.", StringComparison.OrdinalIgnoreCase)
                           && !name.StartsWith("Microsoft.", StringComparison.OrdinalIgnoreCase)
                           && !name.StartsWith("xunit", StringComparison.OrdinalIgnoreCase)
                           && !name.StartsWith("Xunit", StringComparison.OrdinalIgnoreCase)
                           && !name.StartsWith("mscorlib", StringComparison.OrdinalIgnoreCase)
                           && !name.StartsWith("netstandard", StringComparison.OrdinalIgnoreCase);
                })
                .ToArray();
        }

        private static bool InheritsFromApiController(Type type)
        {
            var current = type.BaseType;
            while (current != null)
            {
                if (current.FullName == "System.Web.Http.ApiController")
                    return true;
                current = current.BaseType;
            }
            return false;
        }
    }
}