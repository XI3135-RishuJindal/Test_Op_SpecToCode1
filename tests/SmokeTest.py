using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace EfCoreMigrationUpgradeTests
{
    /// <summary>
    /// Validates that the initial EF Core migration infrastructure is correctly
    /// authored and applied. These tests are intentionally upgrade-specific:
    /// they verify the migration baseline exists, the schema is consistent with
    /// the model snapshot, and the __EFMigrationsHistory table is populated after
    /// applying the migration — not just that EF Core loads.
    /// </summary>
    public class InitialEfCoreMigrationUpgradeTests : IDisposable
    {
        // -----------------------------------------------------------------------
        // Configuration — adjust these constants to match the actual project once
        // the TODO items in the spec are resolved.
        // -----------------------------------------------------------------------

        /// <summary>
        /// The name of the initial migration as passed to `dotnet ef migrations add`.
        /// Convention: the generated class name equals the migration name.
        /// </summary>
        private const string ExpectedInitialMigrationName = "InitialCreate";

        /// <summary>
        /// Minimum EF Core major version that must be active.
        /// Update to the exact version confirmed in the project's .csproj once known.
        /// </summary>
        private const int MinEfCoreMajorVersion = 8;

        /// <summary>
        /// SQLite in-memory database name used for isolated schema tests.
        /// Each test class instance gets its own named database so tests are isolated.
        /// </summary>
        private readonly string _testDatabaseName;

        private readonly ServiceProvider _serviceProvider;
        private readonly IConfiguration _configuration;

        public InitialEfCoreMigrationUpgradeTests()
        {
            _testDatabaseName = $"efcore_upgrade_test_{Guid.NewGuid():N}";

            _configuration = new ConfigurationBuilder()
                .AddInMemoryCollection(new[]
                {
                    new System.Collections.Generic.KeyValuePair<string, string>(
                        "ConnectionStrings:DefaultConnection",
                        $"DataSource={_testDatabaseName};Mode=Memory;Cache=Shared")
                })
                .Build();

            var services = new ServiceCollection();

            // Register the application DbContext using SQLite in-memory so tests
            // run without an external database server.  Replace AppDbContext with
            // the real DbContext class name once confirmed.
            services.AddDbContext<AppDbContext>(options =>
                options.UseSqlite(
                    _configuration.GetConnectionString("DefaultConnection")
                    ?? $"DataSource={_testDatabaseName};Mode=Memory;Cache=Shared"));

            _serviceProvider = services.BuildServiceProvider();
        }

        // -----------------------------------------------------------------------
        // 1. Version assertion — the active EF Core runtime must meet the minimum
        //    major version required by this upgrade.
        // -----------------------------------------------------------------------

        [Fact]
        public void EfCore_RuntimeVersion_MeetsMinimumUpgradeTarget()
        {
            // Microsoft.EntityFrameworkCore is the canonical assembly for the EF Core
            // runtime version.
            var efCoreAssembly = typeof(DbContext).Assembly;
            var version = efCoreAssembly.GetName().Version
                ?? throw new InvalidOperationException(
                    "Could not determine EF Core assembly version.");

            Assert.True(
                version.Major >= MinEfCoreMajorVersion,
                $"EF Core runtime version {version} does not meet the minimum " +
                $"required major version {MinEfCoreMajorVersion}. " +
                $"Upgrade the Microsoft.EntityFrameworkCore NuGet package.");
        }

        [Fact]
        public void EfCore_RuntimeVersion_IsNotPreRelease()
        {
            var efCoreAssembly = typeof(DbContext).Assembly;
            var informationalVersion = efCoreAssembly
                .GetCustomAttribute<AssemblyInformationalVersionAttribute>()
                ?.InformationalVersion ?? string.Empty;

            // Pre-release suffixes contain '-' (e.g., 8.0.0-rc.1).
            // Production upgrades must use a stable release.
            Assert.False(
                informationalVersion.Contains('-'),
                $"EF Core is running a pre-release version '{informationalVersion}'. " +
                $"The upgrade target requires a stable release.");
        }

        // -----------------------------------------------------------------------
        // 2. Migration file existence — the InitialCreate migration files must be
        //    present in source control as evidence the migration was authored.
        // -----------------------------------------------------------------------

        [Fact]
        public void MigrationFiles_InitialCreate_ExistOnDisk()
        {
            // Walk up from the test assembly location to find the Migrations folder.
            // Adjust the relative path if the data project is in a different location.
            var assemblyDir = Path.GetDirectoryName(
                Assembly.GetExecutingAssembly().Location)
                ?? Directory.GetCurrentDirectory();

            var repoRoot = FindRepositoryRoot(assemblyDir);
            Assert.NotNull(repoRoot);

            var migrationsDir = FindMigrationsDirectory(repoRoot!);
            Assert.True(
                migrationsDir != null && Directory.Exists(migrationsDir),
                $"No 'Migrations' directory was found under '{repoRoot}'. " +
                $"Run `dotnet ef migrations add {ExpectedInitialMigrationName}` to create it.");

            var migrationFiles = Directory.GetFiles(migrationsDir!, "*.cs",
                SearchOption.TopDirectoryOnly);

            var initialMigrationFile = migrationFiles.FirstOrDefault(f =>
                Path.GetFileName(f).EndsWith(
                    $"_{ExpectedInitialMigrationName}.cs",
                    StringComparison.OrdinalIgnoreCase));

            Assert.True(
                initialMigrationFile != null,
                $"No migration file ending with '_{ExpectedInitialMigrationName}.cs' " +
                $"was found in '{migrationsDir}'. " +
                $"Ensure `dotnet ef migrations add {ExpectedInitialMigrationName}` was run " +
                $"and the generated files were committed.");
        }

        [Fact]
        public void MigrationFiles_InitialCreate_DesignerFileExists()
        {
            var assemblyDir = Path.GetDirectoryName(
                Assembly.GetExecutingAssembly().Location)
                ?? Directory.GetCurrentDirectory();

            var repoRoot = FindRepositoryRoot(assemblyDir);
            var migrationsDir = FindMigrationsDirectory(repoRoot ?? assemblyDir);

            if (migrationsDir == null || !Directory.Exists(migrationsDir))
            {
                // Skip gracefully if the Migrations folder is absent — the previous
                // test already fails in that case.
                return;
            }

            var designerFile = Directory.GetFiles(migrationsDir, "*.cs",
                    SearchOption.TopDirectoryOnly)
                .FirstOrDefault(f =>
                    Path.GetFileName(f).EndsWith(
                        $"_{ExpectedInitialMigrationName}.Designer.cs",
                        StringComparison.OrdinalIgnoreCase));

            Assert.True(
                designerFile != null,
                $"Designer file '_{ExpectedInitialMigrationName}.Designer.cs' is missing. " +
                $"EF Core generates this file automatically alongside the migration. " +
                $"Do not delete it — it contains the model snapshot used for diff detection.");
        }

        [Fact]
        public void MigrationFiles_ModelSnapshot_Exists()
        {
            var assemblyDir = Path.GetDirectoryName(
                Assembly.GetExecutingAssembly().Location)
                ?? Directory.GetCurrentDirectory();

            var repoRoot = FindRepositoryRoot(assemblyDir);
            var migrationsDir = FindMigrationsDirectory(repoRoot ?? assemblyDir);

            if (migrationsDir == null || !Directory.Exists(migrationsDir))
            {
                return;
            }

            var snapshotFile = Directory.GetFiles(migrationsDir, "*ModelSnapshot.cs",
                SearchOption.TopDirectoryOnly).FirstOrDefault();

            Assert.True(
                snapshotFile != null,
                $"No '*ModelSnapshot.cs' file found in '{migrationsDir}'. " +
                $"EF Core requires this file to compute incremental migrations. " +
                $"Ensure the initial migration was scaffolded correctly.");
        }

        // -----------------------------------------------------------------------
        // 3. DbContext can be resolved and is correctly configured.
        // -----------------------------------------------------------------------

        [Fact]
        public void DbContext_CanBeResolvedFromDI()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetService<AppDbContext>();

            Assert.NotNull(context);
        }

        [Fact]
        public void DbContext_DatabaseProvider_IsConfigured()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            // The provider name must not be null — an unconfigured context throws
            // before reaching this assertion.
            var providerName = context.Database.ProviderName;
            Assert.False(
                string.IsNullOrWhiteSpace(providerName),
                "DbContext has no database provider configured. " +
                "Ensure UseSqlite / UseSqlServer / UseNpgsql is called in DI registration.");
        }

        // -----------------------------------------------------------------------
        // 4. Migration is registered in the EF Core migration assembly.
        // -----------------------------------------------------------------------

        [Fact]
        public void MigrationAssembly_ContainsInitialCreateMigration()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            var migrator = context.GetInfrastructure()
                .GetRequiredService<IMigrator>();

            // IMigrationsAssembly lists all migrations known to EF Core at runtime.
            var migrationsAssembly = context.GetInfrastructure()
                .GetRequiredService<IMigrationsAssembly>();

            Assert.True(
                migrationsAssembly.Migrations.Count > 0,
                "No migrations are registered in the EF Core migrations assembly. " +
                $"Run `dotnet ef migrations add {ExpectedInitialMigrationName}` and " +
                $"ensure the Migrations folder is included in the data project.");

            var hasInitialCreate = migrationsAssembly.Migrations.Keys.Any(k =>
                k.EndsWith(ExpectedInitialMigrationName, StringComparison.OrdinalIgnoreCase));

            Assert.True(
                hasInitialCreate,
                $"The migration named '{ExpectedInitialMigrationName}' is not registered " +
                $"in the EF Core migrations assembly. " +
                $"Registered migrations: [{string.Join(", ", migrationsAssembly.Migrations.Keys)}]");
        }

        [Fact]
        public void MigrationAssembly_InitialCreate_IsFirstMigration()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            var migrationsAssembly = context.GetInfrastructure()
                .GetRequiredService<IMigrationsAssembly>();

            if (migrationsAssembly.Migrations.Count == 0)
            {
                // Covered by the previous test.
                return;
            }

            // Migrations are keyed by timestamp prefix; ordering by key gives
            // chronological order.
            var firstMigrationKey = migrationsAssembly.Migrations.Keys
                .OrderBy(k => k)
                .First();

            Assert.True(
                firstMigrationKey.EndsWith(
                    ExpectedInitialMigrationName,
                    StringComparison.OrdinalIgnoreCase),
                $"The first (oldest) migration is '{firstMigrationKey}', not " +
                $"'{ExpectedInitialMigrationName}'. " +
                $"The initial migration must be the chronologically first migration.");
        }

        // -----------------------------------------------------------------------
        // 5. Migration can be applied — schema is created and
        //    __EFMigrationsHistory is populated.
        // -----------------------------------------------------------------------

        [Fact]
        public void ApplyMigrations_CreatesSchema_WithoutErrors()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            // EnsureDeleted + Migrate gives a clean slate for each test run.
            context.Database.EnsureDeleted();

            var exception = Record.Exception(() => context.Database.Migrate());

            Assert.Null(exception);
        }

        [Fact]
        public void ApplyMigrations_PopulatesMigrationsHistoryTable()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            context.Database.EnsureDeleted();
            context.Database.Migrate();

            // GetAppliedMigrations() queries __EFMigrationsHistory directly.
            var appliedMigrations = context.Database
                .GetAppliedMigrations()
                .ToList();

            Assert.True(
                appliedMigrations.Count > 0,
                "__EFMigrationsHistory table is empty after calling Migrate(). " +
                "EF Core should have recorded at least the InitialCreate migration.");

            Assert.Contains(
                appliedMigrations,
                m => m.EndsWith(ExpectedInitialMigrationName,
                    StringComparison.OrdinalIgnoreCase));
        }

        [Fact]
        public void ApplyMigrations_NoPendingMigrationsRemain()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            context.Database.EnsureDeleted();
            context.Database.Migrate();

            var pendingMigrations = context.Database
                .GetPendingMigrations()
                .ToList();

            Assert.Empty(pendiedMigrations: pendingMigrations);
        }

        // -----------------------------------------------------------------------
        // 6. Model consistency — no pending model changes exist after the initial
        //    migration is applied (i.e., the snapshot matches the current model).
        // -----------------------------------------------------------------------

        [Fact]
        public void ModelSnapshot_IsConsistentWithCurrentModel_NoPendingChanges()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            context.Database.EnsureDeleted();
            context.Database.Migrate();

            // If the model has drifted from the snapshot, GetPendingMigrations()
            // will not catch it — but HasPendingModelChanges() will.
            // This method is available in EF Core 8+.
            var hasPendingChanges = context.Database.HasPendingModelChanges();

            Assert.False(
                hasPendingChanges,
                "The EF Core model has pending changes that are not covered by any " +
                "migration. Run `dotnet ef migrations add <MigrationName>` to capture " +
                "the outstanding model changes before proceeding.");
        }

        // -----------------------------------------------------------------------
        // 7. Configuration key validation — connection string key must be present.
        // -----------------------------------------------------------------------

        [Fact]
        public void Configuration_DefaultConnectionString_IsPresent()
        {
            var connectionString = _configuration.GetConnectionString("DefaultConnection");

            Assert.False(
                string.IsNullOrWhiteSpace(connectionString),
                "The 'ConnectionStrings:DefaultConnection' configuration key is missing " +
                "or empty. Ensure appsettings.json / environment variables supply this " +
                "key before running migrations.");
        }

        [Fact]
        public void Configuration_DefaultConnectionString_DoesNotContainPlaceholder()
        {
            var connectionString = _configuration.GetConnectionString("DefaultConnection")
                ?? string.Empty;

            // Guard against accidentally committed placeholder values.
            var placeholders = new[] { "TODO", "PLACEHOLDER", "YOUR_CONNECTION_STRING", "<connection>" };

            foreach (var placeholder in placeholders)
            {
                Assert.False(
                    connectionString.Contains(placeholder, StringComparison.OrdinalIgnoreCase),
                    $"Connection string contains placeholder text '{placeholder}'. " +
                    $"Replace it with a real connection string before applying migrations.");
            }
        }

        // -----------------------------------------------------------------------
        // 8. Rollback (Down) method — verify the migration can be reverted.
        // -----------------------------------------------------------------------

        [Fact]
        public void Migration_Down_CanBeApplied_WithoutErrors()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            context.Database.EnsureDeleted();
            context.Database.Migrate();

            // Migrate to "0" reverts all migrations, exercising every Down() method.
            var exception = Record.Exception(() =>
                context.Database.GetInfrastructure()
                    .GetRequiredService<IMigrator>()
                    .Migrate("0"));

            Assert.Null(exception);
        }

        [Fact]
        public void Migration_UpAfterDown_ReappliesCleanly()
        {
            using var scope = _serviceProvider.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            context.Database.EnsureDeleted();
            context.Database.Migrate();

            var migrator = context.GetInfrastructure()
                .GetRequiredService<IMigrator>();

            // Down
            migrator.Migrate("0");

            // Up again — simulates a re-deploy after a rollback.
            var exception = Record.Exception(() => migrator.Migrate());

            Assert.Null(exception);

            var appliedAfterReapply = context.Database
                .GetAppliedMigrations()
                .ToList();

            Assert.Contains(
                appliedAfterReapply,
                m => m.EndsWith(ExpectedInitialMigrationName,
                    StringComparison.OrdinalIgnoreCase));
        }

        // -----------------------------------------------------------------------
        // Helpers
        // -----------------------------------------------------------------------

        private static string? FindRepositoryRoot(string startDirectory)
        {
            var dir = new DirectoryInfo(startDirectory);
            while (dir != null)
            {
                if (dir.GetDirectories(".git").Any() ||
                    dir.GetFiles("*.sln").Any() ||
                    dir.GetFiles("*.csproj").Any())
                {
                    return dir.FullName;
                }
                dir = dir.Parent;
            }
            return null;
        }

        private static string? FindMigrationsDirectory(string rootDirectory)
        {
            try
            {
                return Directory
                    .EnumerateDirectories(rootDirectory, "Migrations",
                        SearchOption.AllDirectories)
                    .FirstOrDefault();
            }
            catch (UnauthorizedAccessException)
            {
                return null;
            }
        }

        public void Dispose()
        {
            _serviceProvider.Dispose();
        }
    }

    // ---------------------------------------------------------------------------
    // Minimal AppDbContext stub — replace with the real DbContext once the TODO
    // items in the spec are resolved and the actual entity classes are known.
    // The stub is intentionally minimal: it only needs to be resolvable by DI and
    // carry the Migrations assembly reference so the migration tests above work.
    // ---------------------------------------------------------------------------

    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options)
            : base(options)
        {
        }

        // TODO: Replace with actual DbSet<T> properties once entity classes are confirmed.
        // Example:
        //   public DbSet<Customer> Customers => Set<Customer>();

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // TODO: Add Fluent API configuration here once entity classes are confirmed.
            // Example:
            //   modelBuilder.Entity<Customer>(entity =>
            //   {
            //       entity.HasKey(e => e.Id);
            //       entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            //   });
        }
    }

    // ---------------------------------------------------------------------------
    // xUnit collection fixture — ensures the SQLite shared-cache databases used
    // by individual tests do not collide when tests run in parallel.
    // ---------------------------------------------------------------------------

    [CollectionDefinition("EfCoreMigrationUpgrade", DisableParallelization = true)]
    public class EfCoreMigrationUpgradeCollection { }
}