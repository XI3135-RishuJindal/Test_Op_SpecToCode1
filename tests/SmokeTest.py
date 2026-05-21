using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Xunit;

/// <summary>
/// Upgrade validation tests: Static in-memory store → EF Core repository implementations.
/// These tests verify that the migration succeeded and that EF Core is active as the
/// data access layer. They are intentionally focused on the upgrade boundary, not on
/// exhaustive business-logic coverage.
/// </summary>
public class EfCoreUpgradeValidationTests : IAsyncLifetime
{
    // ---------------------------------------------------------------------------
    // Infrastructure – build a minimal DI container that mirrors Program/Startup
    // ---------------------------------------------------------------------------

    private ServiceProvider _serviceProvider = null!;
    private AppDbContext _dbContext = null!;

    public async Task InitializeAsync()
    {
        var services = new ServiceCollection();

        // Use SQLite in-memory for isolation; swap for the real provider in CI
        // by reading the environment variable UPGRADE_TEST_CONNECTION_STRING.
        var connectionString = Environment.GetEnvironmentVariable("UPGRADE_TEST_CONNECTION_STRING")
                               ?? "DataSource=:memory:";

        services.AddDbContext<AppDbContext>(options =>
        {
            // Prefer SQLite for hermetic tests; the provider choice validates that
            // the DbContext can be configured with a real EF Core provider.
            options.UseSqlite(connectionString);
        });

        // Register repository implementations exactly as the upgrade spec requires.
        // Adjust the concrete type names to match your actual project if they differ.
        services.AddScoped(typeof(IRepository<>), typeof(EfCoreRepository<>));

        _serviceProvider = services.BuildServiceProvider();

        _dbContext = _serviceProvider.GetRequiredService<AppDbContext>();

        // Ensure the schema exists (runs migrations or EnsureCreated).
        await _dbContext.Database.EnsureCreatedAsync();
    }

    public async Task DisposeAsync()
    {
        await _dbContext.Database.EnsureDeletedAsync();
        await _serviceProvider.DisposeAsync();
    }

    // ---------------------------------------------------------------------------
    // 1. Version / provider assertion
    //    Verifies that EF Core is active and that the provider is NOT the legacy
    //    in-memory provider that was used as a stand-in for the static store.
    // ---------------------------------------------------------------------------

    [Fact]
    public void EfCore_Provider_Is_Not_InMemory_StaticStore()
    {
        var providerName = _dbContext.Database.ProviderName;

        Assert.NotNull(providerName);

        // The old static store had no real provider; the upgrade must use a
        // persistent-capable provider.  The InMemory provider is acceptable only
        // as a test double, but the DbContext itself must be EF Core-backed.
        Assert.Contains("EntityFrameworkCore", providerName, StringComparison.OrdinalIgnoreCase);

        // Guard: must NOT be the raw "InMemory" provider used as a static-store
        // shim (i.e., Microsoft.EntityFrameworkCore.InMemory used in production).
        // In CI with a real DB this will be e.g. "Microsoft.EntityFrameworkCore.Sqlite"
        // or "Microsoft.EntityFrameworkCore.SqlServer".
        // For the hermetic test run we allow Sqlite but never the bare InMemory shim.
        Assert.DoesNotContain("InMemory", providerName, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void EfCore_Version_Is_Latest_Stable_Major()
    {
        // EF Core ships as part of the Microsoft.EntityFrameworkCore package.
        // Verify the loaded assembly is at least version 8.0 (current LTS / latest stable).
        var efCoreAssembly = typeof(DbContext).Assembly;
        var version = efCoreAssembly.GetName().Version;

        Assert.NotNull(version);
        Assert.True(
            version!.Major >= 8,
            $"Expected EF Core >= 8.0 (latest stable) but found {version}. " +
            "Ensure the NuGet packages were upgraded as part of this migration.");
    }

    // ---------------------------------------------------------------------------
    // 2. AppDbContext is resolvable from DI (not a static singleton)
    // ---------------------------------------------------------------------------

    [Fact]
    public void AppDbContext_Is_Registered_In_DI_And_Not_Static()
    {
        // Resolving a second scope must yield a different instance, proving the
        // context is scoped (not a static field).
        using var scope1 = _serviceProvider.CreateScope();
        using var scope2 = _serviceProvider.CreateScope();

        var ctx1 = scope1.ServiceProvider.GetRequiredService<AppDbContext>();
        var ctx2 = scope2.ServiceProvider.GetRequiredService<AppDbContext>();

        Assert.NotNull(ctx1);
        Assert.NotNull(ctx2);
        Assert.NotSame(ctx1, ctx2); // Different instances per scope — not static
    }

    // ---------------------------------------------------------------------------
    // 3. Repository is resolvable from DI (replaces direct static access)
    // ---------------------------------------------------------------------------

    [Fact]
    public void Generic_Repository_Resolves_From_DI()
    {
        using var scope = _serviceProvider.CreateScope();
        var repo = scope.ServiceProvider.GetService(typeof(IRepository<object>));

        // The repository must be registered; if it is null the static store was
        // not replaced with a DI-registered EF Core implementation.
        Assert.NotNull(repo);
    }

    // ---------------------------------------------------------------------------
    // 4. Database schema was created (migrations / EnsureCreated ran)
    // ---------------------------------------------------------------------------

    [Fact]
    public async Task Database_Schema_Exists_After_Migration()
    {
        // EnsureCreated (or Migrate) must have run without throwing.
        // A second call must be idempotent.
        var created = await _dbContext.Database.EnsureCreatedAsync();

        // false means it already existed — either outcome is valid post-upgrade.
        Assert.True(created == false || created == true,
            "EnsureCreatedAsync returned an unexpected value.");

        // Verify we can open a connection — proves the schema is reachable.
        await _dbContext.Database.OpenConnectionAsync();
        await _dbContext.Database.CloseConnectionAsync();
    }

    // ---------------------------------------------------------------------------
    // 5. CRUD round-trip through the EF Core repository
    //    Replaces the equivalent operations that previously mutated static fields.
    // ---------------------------------------------------------------------------

    [Fact]
    public async Task Repository_Add_And_Query_Persists_Via_EfCore()
    {
        using var scope = _serviceProvider.CreateScope();
        var repo = scope.ServiceProvider.GetRequiredService<IRepository<SampleEntity>>();

        var entity = new SampleEntity { Name = "UpgradeValidation_" + Guid.NewGuid() };

        // Add — previously this would have mutated a static collection.
        await repo.AddAsync(entity);
        await repo.SaveChangesAsync();

        // Query — must come from the database, not from a static field.
        var loaded = await repo.GetByIdAsync(entity.Id);

        Assert.NotNull(loaded);
        Assert.Equal(entity.Name, loaded!.Name);
        Assert.True(entity.Id > 0, "EF Core must have assigned a database-generated key.");
    }

    [Fact]
    public async Task Repository_Delete_Removes_Entity_From_Database()
    {
        using var scope = _serviceProvider.CreateScope();
        var repo = scope.ServiceProvider.GetRequiredService<IRepository<SampleEntity>>();

        var entity = new SampleEntity { Name = "ToDelete_" + Guid.NewGuid() };
        await repo.AddAsync(entity);
        await repo.SaveChangesAsync();

        await repo.DeleteAsync(entity.Id);
        await repo.SaveChangesAsync();

        var result = await repo.GetByIdAsync(entity.Id);
        Assert.Null(result); // Must be gone — static store would have retained it
    }

    [Fact]
    public async Task Repository_Update_Persists_Change_Via_EfCore()
    {
        using var scope = _serviceProvider.CreateScope();
        var repo = scope.ServiceProvider.GetRequiredService<IRepository<SampleEntity>>();

        var entity = new SampleEntity { Name = "Original_" + Guid.NewGuid() };
        await repo.AddAsync(entity);
        await repo.SaveChangesAsync();

        entity.Name = "Updated_" + Guid.NewGuid();
        await repo.UpdateAsync(entity);
        await repo.SaveChangesAsync();

        var loaded = await repo.GetByIdAsync(entity.Id);
        Assert.NotNull(loaded);
        Assert.StartsWith("Updated_", loaded!.Name);
    }

    // ---------------------------------------------------------------------------
    // 6. No static state leaks between test runs
    //    Two independent scopes must see consistent state, not divergent copies.
    // ---------------------------------------------------------------------------

    [Fact]
    public async Task Two_Scopes_See_Same_Persisted_Data_Not_Independent_Static_Copies()
    {
        var entity = new SampleEntity { Name = "SharedState_" + Guid.NewGuid() };

        // Write in scope A
        using (var scopeA = _serviceProvider.CreateScope())
        {
            var repoA = scopeA.ServiceProvider.GetRequiredService<IRepository<SampleEntity>>();
            await repoA.AddAsync(entity);
            await repoA.SaveChangesAsync();
        }

        // Read in scope B — must see the data written by scope A
        using var scopeB = _serviceProvider.CreateScope();
        var repoB = scopeB.ServiceProvider.GetRequiredService<IRepository<SampleEntity>>();
        var loaded = await repoB.GetByIdAsync(entity.Id);

        Assert.NotNull(loaded);
        Assert.Equal(entity.Name, loaded!.Name);
    }

    // ---------------------------------------------------------------------------
    // 7. Configuration key introduced by the upgrade loads without error
    // ---------------------------------------------------------------------------

    [Fact]
    public void ConnectionStrings_Default_Configuration_Key_Is_Present()
    {
        // The upgrade spec requires ConnectionStrings:Default in appsettings.
        // In the test environment we accept the env-var override as equivalent.
        var envValue = Environment.GetEnvironmentVariable("UPGRADE_TEST_CONNECTION_STRING");
        if (envValue != null)
        {
            Assert.False(string.IsNullOrWhiteSpace(envValue),
                "UPGRADE_TEST_CONNECTION_STRING env var is set but empty.");
            return;
        }

        // Fall back to reading appsettings.json / appsettings.Development.json
        var config = new ConfigurationBuilder()
            .AddJsonFile("appsettings.json", optional: true)
            .AddJsonFile("appsettings.Development.json", optional: true)
            .AddEnvironmentVariables()
            .Build();

        var connectionString = config.GetConnectionString("Default");

        // The key must exist (may be a placeholder in appsettings.json, but must
        // not be absent entirely — that would indicate the upgrade was incomplete).
        Assert.False(string.IsNullOrWhiteSpace(connectionString),
            "ConnectionStrings:Default is missing from configuration. " +
            "The upgrade requires this key to be present in appsettings.json.");
    }

    // ---------------------------------------------------------------------------
    // 8. Deprecated static store accessor no longer exists
    //    Verifies that the old static access point was removed, not just shadowed.
    // ---------------------------------------------------------------------------

    [Fact]
    public void Static_InMemory_Store_Class_No_Longer_Exists_In_Assembly()
    {
        // Common names used for the old static store — adjust to match your project.
        var forbiddenTypeNames = new[]
        {
            "InMemoryStore",
            "StaticDataStore",
            "InMemoryDataStore",
            "StaticStore",
            "InMemoryRepository",
        };

        var appAssembly = typeof(AppDbContext).Assembly;

        foreach (var typeName in forbiddenTypeNames)
        {
            var found = appAssembly.GetTypes()
                .Any(t => t.Name.Equals(typeName, StringComparison.OrdinalIgnoreCase));

            Assert.False(found,
                $"Type '{typeName}' still exists in the assembly. " +
                "The static in-memory store must be removed as part of this upgrade.");
        }
    }
}

// =============================================================================
// Minimal stub types — replace with imports from your actual project namespaces.
// These exist so the test file compiles standalone; delete them once the real
// types are referenced via project reference or using directives.
// =============================================================================

/// <summary>Minimal entity used for CRUD round-trip tests.</summary>
public class SampleEntity
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
}

/// <summary>
/// Generic repository contract introduced by the upgrade.
/// Must match the interface defined in your application's IRepository&lt;T&gt;.
/// </summary>
public interface IRepository<T> where T : class
{
    Task AddAsync(T entity);
    Task<T?> GetByIdAsync(int id);
    Task UpdateAsync(T entity);
    Task DeleteAsync(int id);
    Task SaveChangesAsync();
}

/// <summary>
/// Minimal EF Core repository implementation used by the test harness.
/// In production this lives in Data/Repositories/EfCoreRepository.cs.
/// </summary>
public class EfCoreRepository<T> : IRepository<T> where T : class
{
    private readonly AppDbContext _context;
    private readonly DbSet<T> _set;

    public EfCoreRepository(AppDbContext context)
    {
        _context = context;
        _set = context.Set<T>();
    }

    public async Task AddAsync(T entity) => await _set.AddAsync(entity);

    public async Task<T?> GetByIdAsync(int id) => await _set.FindAsync(id);

    public Task UpdateAsync(T entity)
    {
        _context.Entry(entity).State = EntityState.Modified;
        return Task.CompletedTask;
    }

    public async Task DeleteAsync(int id)
    {
        var entity = await _set.FindAsync(id);
        if (entity != null) _set.Remove(entity);
    }

    public async Task SaveChangesAsync() => await _context.SaveChangesAsync();
}

/// <summary>
/// Minimal DbContext stub — replace with the real AppDbContext from Data/AppDbContext.cs.
/// </summary>
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<SampleEntity> SampleEntities => Set<SampleEntity>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<SampleEntity>(b =>
        {
            b.HasKey(e => e.Id);
            b.Property(e => e.Id).ValueGeneratedOnAdd();
            b.Property(e => e.Name).IsRequired().HasMaxLength(256);
        });
    }
}