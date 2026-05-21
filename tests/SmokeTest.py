using System;
using System.Linq;
using System.Reflection;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace DependencyInjection.UpgradeValidation.Tests
{
    /// <summary>
    /// Validates that the Unity IoC → Microsoft.Extensions.DependencyInjection migration
    /// succeeded. Every test in this file is specifically scoped to upgrade verification.
    /// </summary>
    [TestClass]
    public class MsdiUpgradeValidationTests
    {
        // -----------------------------------------------------------------------
        // 1. VERSION ASSERTION
        //    Confirms that the MSDI runtime assembly is present and at the
        //    expected major version (8.x — adjust if the project targets 6.x/7.x).
        // -----------------------------------------------------------------------

        private const int ExpectedMsdiMajorVersion = 8;

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void MicrosoftExtensionsDependencyInjection_AssemblyVersion_IsTargetMajorVersion()
        {
            // Resolve the assembly that ships the concrete ServiceCollection type.
            var assembly = typeof(ServiceCollection).Assembly;
            var version = assembly.GetName().Version;

            Assert.IsNotNull(version,
                "Could not read version from Microsoft.Extensions.DependencyInjection assembly.");

            Assert.AreEqual(
                ExpectedMsdiMajorVersion,
                version.Major,
                $"Expected Microsoft.Extensions.DependencyInjection major version {ExpectedMsdiMajorVersion} " +
                $"but found {version}. Update the target version constant or re-run the upgrade.");
        }

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void MicrosoftExtensionsDependencyInjectionAbstractions_AssemblyVersion_IsTargetMajorVersion()
        {
            // Abstractions assembly ships IServiceCollection, IServiceProvider extensions, etc.
            var assembly = typeof(IServiceCollection).Assembly;
            var version = assembly.GetName().Version;

            Assert.IsNotNull(version,
                "Could not read version from Microsoft.Extensions.DependencyInjection.Abstractions assembly.");

            Assert.AreEqual(
                ExpectedMsdiMajorVersion,
                version.Major,
                $"Expected Abstractions major version {ExpectedMsdiMajorVersion} but found {version}.");
        }

        // -----------------------------------------------------------------------
        // 2. UNITY PACKAGES ARE ABSENT
        //    Confirms that no Unity-related assemblies are loaded into the
        //    current AppDomain — the strongest runtime signal that Unity has
        //    been fully removed.
        // -----------------------------------------------------------------------

        private static readonly string[] UnityAssemblyPrefixes = new[]
        {
            "Unity",
            "Microsoft.Practices.Unity",
            "CommonServiceLocator",
            "Unity.Container",
            "Unity.Abstractions",
            "Unity.Microsoft.DependencyInjection",
        };

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void UnityAssemblies_AreNotLoadedInAppDomain()
        {
            var loadedAssemblies = AppDomain.CurrentDomain.GetAssemblies();

            var unityAssemblies = loadedAssemblies
                .Select(a => a.GetName().Name ?? string.Empty)
                .Where(name => UnityAssemblyPrefixes.Any(prefix =>
                    name.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)))
                .ToList();

            Assert.AreEqual(
                0,
                unityAssemblies.Count,
                "The following Unity assemblies are still loaded and must be removed: " +
                string.Join(", ", unityAssemblies));
        }

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void IUnityContainer_TypeDoesNotExist_InLoadedAssemblies()
        {
            // Belt-and-suspenders: even if the assembly name changed, verify
            // the canonical Unity interface is not resolvable via reflection.
            var unityContainerType = AppDomain.CurrentDomain
                .GetAssemblies()
                .SelectMany(SafeGetTypes)
                .FirstOrDefault(t => t.FullName == "Unity.IUnityContainer"
                                  || t.FullName == "Microsoft.Practices.Unity.IUnityContainer");

            Assert.IsNull(
                unityContainerType,
                $"Unity.IUnityContainer was found in type '{unityContainerType?.AssemblyQualifiedName}'. " +
                "Unity must be fully removed.");
        }

        // -----------------------------------------------------------------------
        // 3. MSDI CORE ABSTRACTIONS ARE FUNCTIONAL
        //    Verifies that IServiceCollection, ServiceProvider, and the three
        //    canonical lifetimes work end-to-end.
        // -----------------------------------------------------------------------

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void ServiceCollection_CanBeInstantiated()
        {
            var services = new ServiceCollection();
            Assert.IsNotNull(services, "ServiceCollection could not be instantiated.");
        }

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void ServiceProvider_CanBeBuiltFromServiceCollection()
        {
            var services = new ServiceCollection();
            services.AddTransient<IValidationSampleService, ValidationSampleService>();

            IServiceProvider provider = services.BuildServiceProvider();

            Assert.IsNotNull(provider, "BuildServiceProvider() returned null.");
        }

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void Transient_Registration_ReturnsNewInstanceEachTime()
        {
            var services = new ServiceCollection();
            services.AddTransient<IValidationSampleService, ValidationSampleService>();
            var provider = services.BuildServiceProvider();

            var first = provider.GetRequiredService<IValidationSampleService>();
            var second = provider.GetRequiredService<IValidationSampleService>();

            Assert.IsNotNull(first);
            Assert.IsNotNull(second);
            Assert.AreNotSame(first, second,
                "Transient registrations must return a new instance on each resolution.");
        }

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void Singleton_Registration_ReturnsSameInstanceEachTime()
        {
            var services = new ServiceCollection();
            services.AddSingleton<IValidationSampleService, ValidationSampleService>();
            var provider = services.BuildServiceProvider();

            var first = provider.GetRequiredService<IValidationSampleService>();
            var second = provider.GetRequiredService<IValidationSampleService>();

            Assert.IsNotNull(first);
            Assert.AreSame(first, second,
                "Singleton registrations must return the same instance on every resolution.");
        }

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void Scoped_Registration_ReturnsSameInstanceWithinScope_AndDifferentAcrossScopes()
        {
            var services = new ServiceCollection();
            services.AddScoped<IValidationSampleService, ValidationSampleService>();
            var provider = services.BuildServiceProvider();

            IValidationSampleService fromScope1a, fromScope1b, fromScope2;

            using (var scope1 = provider.CreateScope())
            {
                fromScope1a = scope1.ServiceProvider.GetRequiredService<IValidationSampleService>();
                fromScope1b = scope1.ServiceProvider.GetRequiredService<IValidationSampleService>();
            }

            using (var scope2 = provider.CreateScope())
            {
                fromScope2 = scope2.ServiceProvider.GetRequiredService<IValidationSampleService>();
            }

            Assert.AreSame(fromScope1a, fromScope1b,
                "Scoped registrations must return the same instance within a single scope.");
            Assert.AreNotSame(fromScope1a, fromScope2,
                "Scoped registrations must return different instances across different scopes.");
        }

        // -----------------------------------------------------------------------
        // 4. INSTANCE REGISTRATION (replaces Unity RegisterInstance)
        // -----------------------------------------------------------------------

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void RegisterInstance_ViaAddSingleton_ResolvesCorrectInstance()
        {
            var services = new ServiceCollection();
            var knownInstance = new ValidationSampleService { Tag = "known-instance" };
            services.AddSingleton<IValidationSampleService>(knownInstance);
            var provider = services.BuildServiceProvider();

            var resolved = provider.GetRequiredService<IValidationSampleService>();

            Assert.AreSame(knownInstance, resolved,
                "AddSingleton(instance) must resolve the exact registered instance.");
            Assert.AreEqual("known-instance", resolved.Tag);
        }

        // -----------------------------------------------------------------------
        // 5. FACTORY REGISTRATION (replaces Unity RegisterFactory / InjectionFactory)
        // -----------------------------------------------------------------------

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void RegisterFactory_ViaAddTransientFactory_ResolvesCorrectly()
        {
            var services = new ServiceCollection();
            services.AddTransient<IValidationSampleService>(sp =>
                new ValidationSampleService { Tag = "factory-created" });
            var provider = services.BuildServiceProvider();

            var resolved = provider.GetRequiredService<IValidationSampleService>();

            Assert.IsNotNull(resolved);
            Assert.AreEqual("factory-created", resolved.Tag,
                "Factory-based registration must produce an instance with the expected state.");
        }

        // -----------------------------------------------------------------------
        // 6. CONSTRUCTOR INJECTION (primary DI pattern)
        // -----------------------------------------------------------------------

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void ConstructorInjection_ResolvesTransitiveDependencies()
        {
            var services = new ServiceCollection();
            services.AddTransient<IValidationSampleService, ValidationSampleService>();
            services.AddTransient<ValidationConsumer>();
            var provider = services.BuildServiceProvider();

            var consumer = provider.GetRequiredService<ValidationConsumer>();

            Assert.IsNotNull(consumer,
                "ValidationConsumer could not be resolved via constructor injection.");
            Assert.IsNotNull(consumer.Service,
                "The IValidationSampleService dependency was not injected into ValidationConsumer.");
        }

        // -----------------------------------------------------------------------
        // 7. GetRequiredService THROWS FOR UNREGISTERED TYPES
        //    (validates that the container behaves per MSDI contract, not Unity's
        //    auto-registration behaviour which could mask missing registrations)
        // -----------------------------------------------------------------------

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        [ExpectedException(typeof(InvalidOperationException))]
        public void GetRequiredService_ThrowsInvalidOperationException_ForUnregisteredType()
        {
            var services = new ServiceCollection();
            var provider = services.BuildServiceProvider();

            // Must throw — Unity would have attempted auto-resolution here.
            provider.GetRequiredService<IValidationSampleService>();
        }

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void GetService_ReturnsNull_ForUnregisteredType()
        {
            var services = new ServiceCollection();
            var provider = services.BuildServiceProvider();

            var result = provider.GetService<IValidationSampleService>();

            Assert.IsNull(result,
                "GetService<T>() must return null for an unregistered type (MSDI contract).");
        }

        // -----------------------------------------------------------------------
        // 8. OPEN-GENERIC REGISTRATION (common pattern; Unity supported this too)
        // -----------------------------------------------------------------------

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void OpenGeneric_Registration_ResolvesClosedGeneric()
        {
            var services = new ServiceCollection();
            services.AddTransient(typeof(IGenericValidationService<>), typeof(GenericValidationService<>));
            var provider = services.BuildServiceProvider();

            var resolved = provider.GetRequiredService<IGenericValidationService<string>>();

            Assert.IsNotNull(resolved,
                "Open-generic registration must resolve a closed generic type.");
        }

        // -----------------------------------------------------------------------
        // 9. NAMED / KEYED SERVICES (MSDI 8 feature — replaces Unity named registrations)
        // -----------------------------------------------------------------------

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void KeyedServices_AreSupported_InMsdi8()
        {
            // KeyedService support was introduced in Microsoft.Extensions.DependencyInjection 8.0.
            // This test verifies the API is available, confirming the target version is active.
            var services = new ServiceCollection();
            services.AddKeyedTransient<IValidationSampleService, ValidationSampleService>("keyA");
            services.AddKeyedTransient<IValidationSampleService, ValidationSampleService>("keyB");
            var provider = services.BuildServiceProvider();

            var resolvedA = provider.GetRequiredKeyedService<IValidationSampleService>("keyA");
            var resolvedB = provider.GetRequiredKeyedService<IValidationSampleService>("keyB");

            Assert.IsNotNull(resolvedA, "Keyed service 'keyA' could not be resolved.");
            Assert.IsNotNull(resolvedB, "Keyed service 'keyB' could not be resolved.");
            Assert.AreNotSame(resolvedA, resolvedB,
                "Different keys must resolve independent transient instances.");
        }

        // -----------------------------------------------------------------------
        // 10. SCOPE VALIDATION (ValidateScopes catches lifetime mismatches)
        // -----------------------------------------------------------------------

        [TestMethod]
        [TestCategory("UpgradeValidation")]
        public void BuildServiceProvider_WithValidateScopes_DoesNotThrow_ForCorrectRegistrations()
        {
            var services = new ServiceCollection();
            services.AddSingleton<IValidationSampleService, ValidationSampleService>();
            services.AddTransient<ValidationConsumer>();

            // Should not throw when lifetimes are correctly configured.
            var provider = services.BuildServiceProvider(
                new ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = true });

            Assert.IsNotNull(provider);
        }

        // -----------------------------------------------------------------------
        // Helper: safely enumerate types from an assembly without crashing on
        // assemblies that cannot be reflected (e.g., native / mixed-mode).
        // -----------------------------------------------------------------------

        private static Type[] SafeGetTypes(Assembly assembly)
        {
            try
            {
                return assembly.GetTypes();
            }
            catch (ReflectionTypeLoadException ex)
            {
                return ex.Types?.Where(t => t != null).ToArray() ?? Array.Empty<Type>();
            }
            catch
            {
                return Array.Empty<Type>();
            }
        }
    }

    // ---------------------------------------------------------------------------
    // Minimal in-test service types used exclusively by the upgrade validation
    // tests above. These are NOT production types.
    // ---------------------------------------------------------------------------

    public interface IValidationSampleService
    {
        string Tag { get; set; }
    }

    public class ValidationSampleService : IValidationSampleService
    {
        public string Tag { get; set; } = string.Empty;
    }

    public class ValidationConsumer
    {
        public IValidationSampleService Service { get; }

        public ValidationConsumer(IValidationSampleService service)
        {
            Service = service ?? throw new ArgumentNullException(nameof(service));
        }
    }

    public interface IGenericValidationService<T> { }

    public class GenericValidationService<T> : IGenericValidationService<T> { }
}