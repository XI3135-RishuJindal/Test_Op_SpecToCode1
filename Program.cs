```csharp
using ApiGateway.Data;
using ApiGateway.Services;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
// Existing Serilog configuration...

builder.Services.AddControllers();

// Register DbContext with ConnectionString
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// Register WishlistService
builder.Services.AddScoped<WishlistService>();

// Existing Middleware and settings...

var app = builder.Build();

// Existing Configuration...

app.MapControllers();

try
{
    Log.Information("Starting API Gateway");
    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "API Gateway terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
```

#### Update Connection String in appsettings.json