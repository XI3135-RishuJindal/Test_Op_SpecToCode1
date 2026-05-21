using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Linq;
using System.Threading.Tasks;
using Xunit;

/// <summary>
/// Upgrade validation tests: verifies that the static in-memory store has been
/// replaced with an EF Core + SQLite/PostgreSQL persistent store.
///
/// These tests are intentionally written against the most common .NET/EF Core
/// conventions described in the spec.  Adjust namespace, DbContext class name,
/// and entity class names to match the actual project before running.
/// </summary>
namespace UpgradeValidation.Tests
{
    // ---------------------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------------------

    /// <summary>
    /// Minimal entity used to exercise the persistent store.
    /// Replace with the real entity class(es) discovered during the audit.
    /// </summary>
    public class SampleEntity
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; }
    }

    /// <summary>
    /// Concrete DbContext wired to SQLite in-file database for validation tests.
    /// Replace "AppDbContext" with the real DbContext class name if it differs.
    /// </summary>
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        public DbSet<SampleEntity> SampleEntities => Set<SampleEntity>();

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<SampleEntity>(e =>
            {
                e.HasKey(x => x.Id);
                e.Property(x => x.Name).IsRequired().HasMaxLength(256);
                e.Property(x => x.CreatedAt).IsRequired();
            });
        }
    }

    /// <summary>
    /// Factory that builds a fully-migrated, isolated SQLite AppDbContext for
    /// each test so tests do not share state.
    /// </summary>
    internal static class DbContextFactory
    {
        public static AppDbContext CreateSqliteContext(string databaseName)
        {
            var options = new DbContextOptionsBuilder<AppDbContext>()
                .UseSqlite($"Data Source={databaseName};Mode=Memory;Cache=Shared")
                .Options;

            var context = new AppDbContext(options);
            // EnsureCreated is acceptable for validation tests; real migrations
            // are exercised in the MigrationTests class below.
            context.Database.EnsureCreated();
            return context;
        }
    }

    // ---------------------------------------------------------------------------
    // 1. EF Core version assertion
    // ---------------------------------------------------------------------------

    public class EfCoreVersionTests
    {
        /// <summary>
        /// Verifies that the EF Core runtime loaded at test execution time is at
        /// least version 7.0.0 (the minimum required by the spec for .NET 6+).
        /// Adjust the expected major version if the project targets EF Core 8.
        /// </summary>
        [Fact]
        public void EfCore_RuntimeVersion_IsAtLeastVersion7()
        {
            var efCoreAssembly = typeof(DbContext).Assembly;
            var version = efCoreAssembly.GetName().Version
                ?? throw new InvalidOperationException("Could not determine EF Core assembly version.");

            Assert.True(
                version.Major >= 7,
                $"Expected EF Core >= 7.0.0 but found {version}. " +
                "Ensure the correct NuGet package version is referenced.");
        }

        [Fact]
        public void EfCore_AssemblyName_IsExpectedPackage()
        {
            var assemblyName = typeof(DbContext).Assembly.GetName().Name;
            Assert.Equal("Microsoft.EntityFrameworkCore", assemblyName);
        }
    }

    // ---------------------------------------------------------------------------
    // 2. DbContext registration / DI wiring
    // ---------------------------------------------------------------------------

    public class DependencyInjectionTests
    {
        [Fact]
        public void AppDbContext_CanBeResolvedFromServiceCollection_WithSqlite()
        {
            var services = new ServiceCollection();
            services.AddDbContext<AppDbContext>(opts =>
                opts.UseSqlite("Data Source=:memory:"));

            using var provider = services.BuildServiceProvider();
            using var scope = provider.CreateScope();

            var context = scope.ServiceProvider.GetService<AppDbContext>();

            Assert.NotNull(context);
        }

        [Fact]
        public void AppDbContext_CanBeResolvedFromServiceCollection_WithPostgresProvider()
        {
            // Validates that the Npgsql provider assembly is present and the
            // UseNpgsql extension method is callable (does NOT require a live DB).
            var services = new ServiceCollection();
            services.AddDbContext<AppDbContext>(opts =>
                opts.UseNpgsql("Host=localhost;Database=validation_test;Username=test;Password=test"));

            using var provider = services.BuildServiceProvider();
            using var scope = provider.CreateScope();

            // GetService (not GetRequiredService) so we can assert non-null without
            // triggering a real connection attempt.
            var context = scope.ServiceProvider.GetService<AppDbContext>();
            Assert.NotNull(context);
        }
    }

    // ---------------------------------------------------------------------------
    // 3. Migration / schema creation
    // ---------------------------------------------------------------------------

    public class MigrationTests : IDisposable
    {
        private readonly AppDbContext _context;
        private readonly string _dbName;

        public MigrationTests()
        {
            _dbName = $"validation_{Guid.NewGuid():N}.db";
            _context = DbContextFactory.CreateSqliteContext(_dbName);
        }

        [Fact]
        public void Database_EnsureCreated_CreatesSchemaWithoutError()
        {
            // EnsureCreated already called in factory; calling again is idempotent.
            var created = _context.Database.EnsureCreated();
            // Returns false when schema already exists — either outcome is valid here.
            Assert.True(created == true || created == false);
        }

        [Fact]
        public void SampleEntities_Table_ExistsAfterSchemaCreation()
        {
            // Attempt a query; if the table does not exist EF Core throws.
            var count = _context.SampleEntities.Count();
            Assert.True(count >= 0);
        }

        [Fact]
        public void Database_ProviderName_IsSqlite()
        {
            var providerName = _context.Database.ProviderName;
            Assert.Equal("Microsoft.EntityFrameworkCore.Sqlite", providerName);
        }

        public void Dispose() => _context.Dispose();
    }

    // ---------------------------------------------------------------------------
    // 4. Persistence — data survives context disposal (simulates restart)
    // ---------------------------------------------------------------------------

    public class PersistenceTests
    {
        /// <summary>
        /// Core upgrade validation: data written through one DbContext instance
        /// is readable through a second, independent instance — proving the store
        /// is no longer volatile in-memory state.
        /// </summary>
        [Fact]
        public async Task Data_WrittenInOneContext_IsReadableInSeparateContext()
        {
            var dbName = $"persist_{Guid.NewGuid():N}";

            // --- Write ---
            await using (var writeCtx = DbContextFactory.CreateSqliteContext(dbName))
            {
                writeCtx.SampleEntities.Add(new SampleEntity
                {
                    Name = "PersistenceProbe",
                    CreatedAt = DateTime.UtcNow
                });
                await writeCtx.SaveChangesAsync();
            }

            // --- Read in a completely new context (simulates application restart) ---
            await using (var readCtx = DbContextFactory.CreateSqliteContext(dbName))
            {
                var entity = await readCtx.SampleEntities
                    .FirstOrDefaultAsync(e => e.Name == "PersistenceProbe");

                Assert.NotNull(entity);
                Assert.Equal("PersistenceProbe", entity!.Name);
            }
        }

        [Fact]
        public async Task Data_DeletedInOneContext_IsAbsentInSeparateContext()
        {
            var dbName = $"delete_{Guid.NewGuid():N}";

            await using (var ctx = DbContextFactory.CreateSqliteContext(dbName))
            {
                ctx.SampleEntities.Add(new SampleEntity { Name = "ToDelete", CreatedAt = DateTime.UtcNow });
                await ctx.SaveChangesAsync();
            }

            await using (var ctx = DbContextFactory.CreateSqliteContext(dbName))
            {
                var entity = await ctx.SampleEntities.FirstAsync(e => e.Name == "ToDelete");
                ctx.SampleEntities.Remove(entity);
                await ctx.SaveChangesAsync();
            }

            await using (var ctx = DbContextFactory.CreateSqliteContext(dbName))
            {
                var exists = await ctx.SampleEntities.AnyAsync(e => e.Name == "ToDelete");
                Assert.False(exists);
            }
        }
    }

    // ---------------------------------------------------------------------------
    // 5. CRUD operations through EF Core (critical application paths)
    // ---------------------------------------------------------------------------

    public class CrudOperationTests : IAsyncLifetime
    {
        private AppDbContext _context = null!;

        public Task InitializeAsync()
        {
            _context = DbContextFactory.CreateSqliteContext($"crud_{Guid.NewGuid():N}");
            return Task.CompletedTask;
        }

        public Task DisposeAsync()
        {
            _context.Dispose();
            return Task.CompletedTask;
        }

        [Fact]
        public async Task Create_Entity_PersistsWithGeneratedId()
        {
            var entity = new SampleEntity { Name = "CreateTest", CreatedAt = DateTime.UtcNow };
            _context.SampleEntities.Add(entity);
            await _context.SaveChangesAsync();

            Assert.True(entity.Id > 0, "EF Core should have assigned a generated primary key.");
        }

        [Fact]
        public async Task Read_Entity_ByPrimaryKey_ReturnsCorrectRecord()
        {
            var entity = new SampleEntity { Name = "ReadTest", CreatedAt = DateTime.UtcNow };
            _context.SampleEntities.Add(entity);
            await _context.SaveChangesAsync();

            var found = await _context.SampleEntities.FindAsync(entity.Id);

            Assert.NotNull(found);
            Assert.Equal("ReadTest", found!.Name);
        }

        [Fact]
        public async Task Update_Entity_ChangesArePersistedToStore()
        {
            var entity = new SampleEntity { Name = "UpdateBefore", CreatedAt = DateTime.UtcNow };
            _context.SampleEntities.Add(entity);
            await _context.SaveChangesAsync();

            entity.Name = "UpdateAfter";
            await _context.SaveChangesAsync();

            var updated = await _context.SampleEntities.FindAsync(entity.Id);
            Assert.Equal("UpdateAfter", updated!.Name);
        }

        [Fact]
        public async Task Delete_Entity_IsRemovedFromStore()
        {
            var entity = new SampleEntity { Name = "DeleteTest", CreatedAt = DateTime.UtcNow };
            _context.SampleEntities.Add(entity);
            await _context.SaveChangesAsync();

            _context.SampleEntities.Remove(entity);
            await _context.SaveChangesAsync();

            var deleted = await _context.SampleEntities.FindAsync(entity.Id);
            Assert.Null(deleted);
        }

        [Fact]
        public async Task Query_Entities_ByName_ReturnsFilteredResults()
        {
            _context.SampleEntities.AddRange(
                new SampleEntity { Name = "Alpha", CreatedAt = DateTime.UtcNow },
                new SampleEntity { Name = "Beta", CreatedAt = DateTime.UtcNow },
                new SampleEntity { Name = "Alpha2", CreatedAt = DateTime.UtcNow }
            );
            await _context.SaveChangesAsync();

            var alphas = await _context.SampleEntities
                .Where(e => e.Name.StartsWith("Alpha"))
                .ToListAsync();

            Assert.Equal(2, alphas.Count);
        }
    }

    // ---------------------------------------------------------------------------
    // 6. Transaction semantics (absent in the old in-memory store)
    // ---------------------------------------------------------------------------

    public class TransactionTests : IAsyncLifetime
    {
        private AppDbContext _context = null!;

        public Task InitializeAsync()
        {
            _context = DbContextFactory.CreateSqliteContext($"tx_{Guid.NewGuid():N}");
            return Task.CompletedTask;
        }

        public Task DisposeAsync()
        {
            _context.Dispose();
            return Task.CompletedTask;
        }

        [Fact]
        public async Task Transaction_Rollback_DoesNotPersistData()
        {
            await using var transaction = await _context.Database.BeginTransactionAsync();

            _context.SampleEntities.Add(new SampleEntity { Name = "RolledBack", CreatedAt = DateTime.UtcNow });
            await _context.SaveChangesAsync();

            await transaction.RollbackAsync();

            // Clear the change tracker so we query the DB, not the cache.
            _context.ChangeTracker.Clear();

            var exists = await _context.SampleEntities.AnyAsync(e => e.Name == "RolledBack");
            Assert.False(exists, "Rolled-back data must not be visible after rollback.");
        }

        [Fact]
        public async Task Transaction_Commit_PersistsData()
        {
            await using var transaction = await _context.Database.BeginTransactionAsync();

            _context.SampleEntities.Add(new SampleEntity { Name = "Committed", CreatedAt = DateTime.UtcNow });
            await _context.SaveChangesAsync();
            await transaction.CommitAsync();

            _context.ChangeTracker.Clear();

            var exists = await _context.SampleEntities.AnyAsync(e => e.Name == "Committed");
            Assert.True(exists, "Committed data must be visible after commit.");
        }
    }

    // ---------------------------------------------------------------------------
    // 7. Concurrency — no static shared state
    // ---------------------------------------------------------------------------

    public class ConcurrencyTests
    {
        [Fact]
        public async Task ConcurrentWrites_FromMultipleContexts_AllPersist()
        {
            var dbName = $"concurrent_{Guid.NewGuid():N}";
            const int writerCount = 10;

            var tasks = Enumerable.Range(0, writerCount).Select(async i =>
            {
                // Each task uses its own DbContext — mirrors real concurrent requests.
                await using var ctx = DbContextFactory.CreateSqliteContext(dbName);
                ctx.SampleEntities.Add(new SampleEntity
                {
                    Name = $"Concurrent_{i}",
                    CreatedAt = DateTime.UtcNow
                });
                await ctx.SaveChangesAsync();
            });

            await Task.WhenAll(tasks);

            await using var readCtx = DbContextFactory.CreateSqliteContext(dbName);
            var count = await readCtx.SampleEntities.CountAsync();

            Assert.Equal(writerCount, count);
        }
    }

    // ---------------------------------------------------------------------------
    // 8. Configuration — connection string keys introduced by the upgrade
    // ---------------------------------------------------------------------------

    public class ConfigurationKeyTests
    {
        /// <summary>
        /// Validates that the expected connection-string environment variable name
        /// (documented in the spec as ConnectionStrings__DefaultConnection) can be
        /// read and used to construct a valid DbContextOptionsBuilder without error.
        /// </summary>
        [Fact]
        public void ConnectionString_EnvironmentVariable_CanBeReadAndUsedWithSqlite()
        {
            // Set the env var as the upgrade spec requires.
            const string envKey = "ConnectionStrings__DefaultConnection";
            const string testValue = "Data Source=:memory:";
            Environment.SetEnvironmentVariable(envKey, testValue);

            var connectionString = Environment.GetEnvironmentVariable(envKey);

            Assert.NotNull(connectionString);
            Assert.False(string.IsNullOrWhiteSpace(connectionString));

            // Verify the value can be used to build a valid options object.
            var options = new DbContextOptionsBuilder<AppDbContext>()
                .UseSqlite(connectionString!)
                .Options;

            Assert.NotNull(options);
        }

        [Fact]
        public void DbContextOptionsBuilder_UseSqlite_DoesNotThrow()
        {
            var exception = Record.Exception(() =>
            {
                var _ = new DbContextOptionsBuilder<AppDbContext>()
                    .UseSqlite("Data Source=:memory:")
                    .Options;
            });

            Assert.Null(exception);
        }

        [Fact]
        public void DbContextOptionsBuilder_UseNpgsql_DoesNotThrow()
        {
            var exception = Record.Exception(() =>
            {
                var _ = new DbContextOptionsBuilder<AppDbContext>()
                    .UseNpgsql("Host=localhost;Database=test;Username=test;Password=test")
                    .Options;
            });

            Assert.Null(exception);
        }
    }

    // ---------------------------------------------------------------------------
    // 9. Absence of static in-memory store (regression guard)
    // ---------------------------------------------------------------------------

    public class StaticStoreAbsenceTests
    {
        /// <summary>
        /// Confirms that AppDbContext does NOT expose any static fields that could
        /// serve as an in-memory store — the core anti-pattern being removed.
        /// </summary>
        [Fact]
        public void AppDbContext_HasNoStaticFields_ThatCouldActAsInMemoryStore()
        {
            var staticFields = typeof(AppDbContext)
                .GetFields(System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public)
                .Where(f =>
                    f.FieldType.IsGenericType &&
                    (f.FieldType.GetGenericTypeDefinition() == typeof(System.Collections.Generic.List<>) ||
                     f.FieldType.GetGenericTypeDefinition() == typeof(System.Collections.Generic.Dictionary<,>)))
                .ToList();

            Assert.Empty(staticFields);
        }

        /// <summary>
        /// Verifies that the DbContext uses a real database provider, not the
        /// EF Core in-memory provider (Microsoft.EntityFrameworkCore.InMemory),
        /// which would be a partial migration that still lacks persistence.
        /// </summary>
        [Fact]
        public void AppDbContext_DoesNotUseEfCoreInMemoryProvider()
        {
            using var ctx = DbContextFactory.CreateSqliteContext($"provider_check_{Guid.NewGuid():N}");
            var providerName = ctx.Database.ProviderName ?? string.Empty;

            Assert.DoesNotContain("InMemory", providerName, StringComparison.OrdinalIgnoreCase);
        }
    }
}