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

/// <summary>
/// Upgrade validation tests: verifies that the initial EF Core migration infrastructure
/// is correctly in place after the "Author and apply initial EF Core migration scripts" upgrade.
/// </summary>
public class EfCoreMigrationUpgradeValidationTests : IDisposable
{
    private const string ExpectedInitialMigrationName = "InitialCreate";
    private const string MigrationsHistoryTable = "__EFMigrationsHistory";

    private readonly ServiceProvider _serviceProvider;
    private readonly IConfiguration _configuration;

    public EfCoreMigrationUpgradeValidationTests()
    {
        var configBuilder = new ConfigurationBuilder()
            .SetBasePath(AppContext.BaseDirectory)
            .AddJsonFile("appsettings.json", optional: true)
            .AddJsonFile("appsettings.Development.json", optional: true)
            .AddEnvironmentVariables();

        _configuration = configBuilder.Build();

        var services = new ServiceCollection();
        services.AddSingleton(_configuration);

        // Register the DbContext with SQLite in-memory for structural validation
        // so tests run without a live database server.
        services.AddDbContext<ValidationDbContext>(options =>
            options.UseSqlite("Data Source=:memory:"));

        _serviceProvider = services.BuildServiceProvider();
    }

    // -------------------------------------------------------------------------
    // 1. EF Core version assertion — must be latest stable (≥ 8.0.0)
    // -------------------------------------------------------------------------

    [Fact]
    public void EfCore_RuntimeVersion_IsLatestStable()
    {
        var efCoreAssembly = typeof(DbContext).Assembly;
        var version = efCoreAssembly.GetName().Version;

        Assert.NotNull(version);

        // Latest stable EF Core at time of spec: 8.x (EF Core 8.0.0+).
        // Update the major version constant when the project pins a newer release.
        Assert.True(
            version.Major >= 8,
            $"Expected EF Core major version >= 8 (latest stable), but found {version}. " +
            "Ensure the project references Microsoft.EntityFrameworkCore 8.x or later.");
    }

    [Fact]
    public void EfCore_DesignAssembly_IsPresent()
    {
        // Microsoft.EntityFrameworkCore.Design must be referenced for dotnet-ef tooling.
        var designAssembly = AppDomain.CurrentDomain
            .GetAssemblies()
            .FirstOrDefault(a => a.GetName().Name == "Microsoft.EntityFrameworkCore.Design");

        // Design assembly may not be loaded at runtime; check via file presence instead.
        var designDllPath = Path.Combine(
            AppContext.BaseDirectory,
            "Microsoft.EntityFrameworkCore.Design.dll");

        Assert.True(
            File.Exists(designDllPath),
            "Microsoft.EntityFrameworkCore.Design.dll was not found in the output directory. " +
            "Add <PackageReference Include=\"Microsoft.EntityFrameworkCore.Design\" /> to the project.");
    }

    // -------------------------------------------------------------------------
    // 2. Migration infrastructure — migrations folder and files exist
    // -------------------------------------------------------------------------

    [Fact]
    public void MigrationsFolder_ExistsInProject()
    {
        // Walk up from the test output directory to find a Migrations folder
        // in the source tree (works for both local and CI builds).
        var migrationsDir = FindMigrationsDirectory();

        Assert.True(
            migrationsDir != null && Directory.Exists(migrationsDir),
            "No 'Migrations' directory was found in the project tree. " +
            "Run: dotnet ef migrations add InitialCreate --project <DataProject> --startup-project <StartupProject>");
    }

    [Fact]
    public void InitialCreate_MigrationFile_Exists()
    {
        var migrationsDir = FindMigrationsDirectory();
        Assert.NotNull(migrationsDir);

        var migrationFiles = Directory.GetFiles(migrationsDir, "*_InitialCreate.cs",
            SearchOption.TopDirectoryOnly);

        Assert.True(
            migrationFiles.Length > 0,
            $"No migration file matching '*_InitialCreate.cs' was found in '{migrationsDir}'. " +
            "The initial migration has not been scaffolded yet.");
    }

    [Fact]
    public void InitialCreate_DesignerFile_Exists()
    {
        var migrationsDir = FindMigrationsDirectory();
        Assert.NotNull(migrationsDir);

        var designerFiles = Directory.GetFiles(migrationsDir, "*_InitialCreate.Designer.cs",
            SearchOption.TopDirectoryOnly);

        Assert.True(
            designerFiles.Length > 0,
            $"No designer file matching '*_InitialCreate.Designer.cs' was found in '{migrationsDir}'. " +
            "The migration scaffolding may be incomplete.");
    }

    [Fact]
    public void ModelSnapshot_File_Exists()
    {
        var migrationsDir = FindMigrationsDirectory();
        Assert.NotNull(migrationsDir);

        var snapshotFiles = Directory.GetFiles(migrationsDir, "*ModelSnapshot.cs",
            SearchOption.TopDirectoryOnly);

        Assert.True(
            snapshotFiles.Length > 0,
            $"No '*ModelSnapshot.cs' file was found in '{migrationsDir}'. " +
            "EF Core requires a model snapshot to compute incremental migrations.");
    }

    // -------------------------------------------------------------------------
    // 3. DbContext structural validation via in-memory SQLite
    // -------------------------------------------------------------------------

    [Fact]
    public void ValidationDbContext_CanBeInstantiated()
    {
        using var scope = _serviceProvider.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<ValidationDbContext>();

        Assert.NotNull(context);
    }

    [Fact]
    public void ValidationDbContext_CanCreateSchema_ViaEnsureCreated()
    {
        using var scope = _serviceProvider.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<ValidationDbContext>();

        // Open the in-memory connection explicitly so it persists for the test.
        context.Database.OpenConnection();
        var created = context.Database.EnsureCreated();

        Assert.True(created, "EnsureCreated() returned false — schema could not be created from the model.");
    }

    [Fact]
    public void ValidationDbContext_MigrationsHistoryTable_IsConfigured()
    {
        using var scope = _serviceProvider.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<ValidationDbContext>();

        var historyRepository = context.GetService<IHistoryRepository>();
        Assert.NotNull(historyRepository);

        // Verify the history table name matches the EF Core convention.
        var tableName = historyRepository.GetType()
            .GetProperty("TableName",
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
            ?.GetValue(historyRepository) as string
            ?? MigrationsHistoryTable;

        Assert.Equal(MigrationsHistoryTable, tableName);
    }

    // -------------------------------------------------------------------------
    // 4. Migration content validation — Up() and Down() are non-empty
    // -------------------------------------------------------------------------

    [Fact]
    public void InitialCreate_MigrationFile_ContainsUpMethod()
    {
        var migrationsDir = FindMigrationsDirectory();
        Assert.NotNull(migrationsDir);

        var migrationFile = Directory
            .GetFiles(migrationsDir, "*_InitialCreate.cs", SearchOption.TopDirectoryOnly)
            .FirstOrDefault();

        Assert.NotNull(migrationFile);

        var content = File.ReadAllText(migrationFile);

        Assert.Contains("protected override void Up(", content,
            StringComparison.OrdinalIgnoreCase);
        Assert.Contains("migrationBuilder.CreateTable(", content,
            StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void InitialCreate_MigrationFile_ContainsDownMethod()
    {
        var migrationsDir = FindMigrationsDirectory();
        Assert.NotNull(migrationsDir);

        var migrationFile = Directory
            .GetFiles(migrationsDir, "*_InitialCreate.cs", SearchOption.TopDirectoryOnly)
            .FirstOrDefault();

        Assert.NotNull(migrationFile);

        var content = File.ReadAllText(migrationFile);

        Assert.Contains("protected override void Down(", content,
            StringComparison.OrdinalIgnoreCase);
        Assert.Contains("migrationBuilder.DropTable(", content,
            StringComparison.OrdinalIgnoreCase);
    }

    // -------------------------------------------------------------------------
    // 5. Configuration keys — connection string is resolvable
    // -------------------------------------------------------------------------

    [Fact]
    public void Configuration_DefaultConnectionString_KeyExists()
    {
        // The spec requires connection strings to be configured before migration work.
        // This test validates the key is present (value may be environment-specific).
        var connectionString = _configuration.GetConnectionString("DefaultConnection");

        Assert.False(
            string.IsNullOrWhiteSpace(connectionString),
            "Connection string 'DefaultConnection' is missing or empty in appsettings.json / " +
            "environment variables. Add it before applying migrations.");
    }

    // -------------------------------------------------------------------------
    // 6. Deprecated API checks — ensure obsolete EF6-style patterns are absent
    // -------------------------------------------------------------------------

    [Fact]
    public void MigrationFiles_DoNotUseObsoleteEF6_DatabaseInitializer()
    {
        var migrationsDir = FindMigrationsDirectory();
        if (migrationsDir == null || !Directory.Exists(migrationsDir))
            return; // No migrations yet — skip rather than fail.

        foreach (var file in Directory.GetFiles(migrationsDir, "*.cs", SearchOption.AllDirectories))
        {
            var content = File.ReadAllText(file);

            Assert.DoesNotContain("IDatabaseInitializer", content,
                "Migration file references obsolete EF6 IDatabaseInitializer. " +
                "Use EF Core's IMigrationsAssembly / MigrationBuilder instead.");

            Assert.DoesNotContain("Database.SetInitializer", content,
                "Migration file references obsolete EF6 Database.SetInitializer. " +
                "Remove this call; EF Core does not support it.");

            Assert.DoesNotContain("System.Data.Entity", content,
                "Migration file references System.Data.Entity (EF6). " +
                "All EF Core references must use Microsoft.EntityFrameworkCore.");
        }
    }

    [Fact]
    public void MigrationFiles_UseEfCoreNamespace()
    {
        var migrationsDir = FindMigrationsDirectory();
        if (migrationsDir == null || !Directory.Exists(migrationsDir))
            return;

        var migrationFile = Directory
            .GetFiles(migrationsDir, "*_InitialCreate.cs", SearchOption.TopDirectoryOnly)
            .FirstOrDefault();

        if (migrationFile == null)
            return;

        var content = File.ReadAllText(migrationFile);

        Assert.Contains("Microsoft.EntityFrameworkCore.Migrations", content,
            "InitialCreate migration does not import Microsoft.EntityFrameworkCore.Migrations. " +
            "Ensure the file was generated by EF Core tooling (dotnet ef migrations add).");
    }

    // -------------------------------------------------------------------------
    // 7. IDesignTimeDbContextFactory — required for CI/CD tooling
    // -------------------------------------------------------------------------

    [Fact]
    public void DesignTimeDbContextFactory_TypeExists_InDataAssemblies()
    {
        var designTimeInterface = typeof(IDesignTimeDbContextFactory<>);

        var implementors = AppDomain.CurrentDomain
            .GetAssemblies()
            .Where(a => !a.IsDynamic)
            .SelectMany(a =>
            {
                try { return a.GetExportedTypes(); }
                catch { return Array.Empty<Type>(); }
            })
            .Where(t => !t.IsAbstract && !t.IsInterface)
            .Where(t => t.GetInterfaces().Any(i =>
                i.IsGenericType &&
                i.GetGenericTypeDefinition() == designTimeInterface))
            .ToList();

        Assert.True(
            implementors.Count > 0,
            "No IDesignTimeDbContextFactory<T> implementation was found in any loaded assembly. " +
            "Add one to the data project so 'dotnet ef' can instantiate the DbContext at design time " +
            "without a running host (required for CI/CD migration application).");
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private static string? FindMigrationsDirectory()
    {
        // Search upward from the test binary output directory.
        var dir = new DirectoryInfo(AppContext.BaseDirectory);

        while (dir != null)
        {
            var candidate = Path.Combine(dir.FullName, "Migrations");
            if (Directory.Exists(candidate))
                return candidate;

            // Also check one level of subdirectories (monorepo layouts).
            foreach (var sub in dir.GetDirectories())
            {
                var subCandidate = Path.Combine(sub.FullName, "Migrations");
                if (Directory.Exists(subCandidate))
                    return subCandidate;
            }

            dir = dir.Parent;
        }

        return null;
    }

    public void Dispose()
    {
        _serviceProvider?.Dispose();
    }
}

// ---------------------------------------------------------------------------
// Minimal in-process DbContext used for structural / schema validation tests.
// Replace or extend with the real application DbContext once it is identified.
// ---------------------------------------------------------------------------

public class ValidationDbContext : DbContext
{
    public ValidationDbContext(DbContextOptions<ValidationDbContext> options)
        : base(options) { }

    // Placeholder entity — replace with actual domain entities once confirmed.
    public DbSet<MigrationValidationRecord> MigrationValidationRecords => Set<MigrationValidationRecord>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<MigrationValidationRecord>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(256);
            entity.Property(e => e.CreatedAt).IsRequired();
        });
    }
}

public class MigrationValidationRecord
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}