using System.Reflection;
using System.Text;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Routing;
using Xunit;

namespace ApiGateway.Tests.Policies;

public class NoPaymentUiElementsTests
{
    private static readonly string[] ForbiddenTokens =
    [
        "payment", "payments", "payout", "billing", "invoice", "invoices", "checkout",
        "creditcard", "debitcard", "cardnumber", "cvv", "stripe", "paypal", "applepay",
        "googlepay", "wallet"
    ];

    [Fact]
    public void Controllers_And_Routes_Must_Not_Contain_Payment_Related_Tokens()
    {
        var asm = typeof(Program).Assembly;
        var controllerTypes = asm
            .GetTypes()
            .Where(t => typeof(ControllerBase).IsAssignableFrom(t) && !t.IsAbstract)
            .ToList();

        var violations = new List<string>();

        foreach (var controller in controllerTypes)
        {
            var controllerName = controller.Name;
            CheckString(controllerName, $"Controller '{controllerName}'", violations);

            // Class-level route attributes
            foreach (var attr in controller.GetCustomAttributes(inherit: true))
            {
                if (attr is RouteAttribute ra && !string.IsNullOrWhiteSpace(ra.Template))
                {
                    CheckString(ra.Template!, $"Controller '{controllerName}' [Route] template", violations);
                }
            }

            // Public instance methods (candidate actions)
            var methods = controller.GetMethods(BindingFlags.Instance | BindingFlags.Public | BindingFlags.DeclaredOnly);
            foreach (var method in methods)
            {
                var methodName = method.Name;
                CheckString(methodName, $"Controller '{controllerName}' Action '{methodName}'", violations);

                foreach (var attr in method.GetCustomAttributes(inherit: true))
                {
                    switch (attr)
                    {
                        case RouteAttribute ra when !string.IsNullOrWhiteSpace(ra.Template):
                            CheckString(ra.Template!, $"Controller '{controllerName}' Action '{methodName}' [Route] template", violations);
                            break;

                        case HttpMethodAttribute hma when !string.IsNullOrWhiteSpace(hma.Template):
                            CheckString(hma.Template!, $"Controller '{controllerName}' Action '{methodName}' [{attr.GetType().Name}] template", violations);
                            break;
                    }
                }
            }
        }

        if (violations.Count > 0)
        {
            var message = "Forbidden payment-related tokens found in controller/action names or route templates:\n - " +
                          string.Join("\n - ", violations);
            Assert.True(false, message);
        }
    }

    [Fact]
    public void Source_Content_Must_Not_Contain_Payment_Related_Tokens()
    {
        var root = FindRepositoryRoot();
        Assert.True(Directory.Exists(root), $"Repository root not found. Searched upward from {AppContext.BaseDirectory}");

        var allowedExtensions = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            ".cs", ".cshtml", ".html", ".js", ".ts", ".css"
        };

        // Directories to ignore (case-insensitive contains match on path segments)
        var ignoreDirs = new[]
        {
            PathCombineInsensitive(root, "bin"),
            PathCombineInsensitive(root, "obj"),
            PathCombineInsensitive(root, ".git"),
            PathCombineInsensitive(root, ".github"),
            PathCombineInsensitive(root, ".vs"),
            PathCombineInsensitive(root, "node_modules"),
            PathCombineInsensitive(root, "Tests"),
            PathCombineInsensitive(root, "specs"),
            PathCombineInsensitive(root, ".specify"),
            PathCombineInsensitive(root, "openspec"),
            PathCombineInsensitive(root, "coverage")
        };

        var violations = new List<string>();

        foreach (var file in Directory.EnumerateFiles(root, "*.*", SearchOption.AllDirectories))
        {
            var ext = Path.GetExtension(file);
            if (!allowedExtensions.Contains(ext))
                continue;

            var normalized = NormalizePath(file);

            if (ignoreDirs.Any(d => IsUnderDirectory(normalized, d)))
                continue;

            string content;
            try
            {
                content = File.ReadAllText(file, Encoding.UTF8);
            }
            catch
            {
                // Skip unreadable files
                continue;
            }

            foreach (var token in ForbiddenTokens)
            {
                if (content.Contains(token, StringComparison.OrdinalIgnoreCase))
                {
                    var rel = ToRelativePath(root, file);
                    violations.Add($"{rel} contains forbidden token '{token}'");
                }
            }
        }

        if (violations.Count > 0)
        {
            var message = "Forbidden payment-related tokens found in source/content files:\n - " +
                          string.Join("\n - ", violations);
            Assert.True(false, message);
        }
    }

    private static void CheckString(string value, string context, List<string> violations)
    {
        foreach (var token in ForbiddenTokens)
        {
            if (value.Contains(token, StringComparison.OrdinalIgnoreCase))
            {
                violations.Add($"{context} contains forbidden token '{token}' (value: '{value}')");
            }
        }
    }

    private static string FindRepositoryRoot()
    {
        // Start from test base directory and ascend to find the solution or project file
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        for (int i = 0; i < 10 && dir != null; i++)
        {
            var sln = dir.GetFiles("ApiGateway.sln").FirstOrDefault();
            var proj = dir.GetFiles("ApiGateway.csproj").FirstOrDefault();
            if (sln != null || proj != null)
            {
                return dir.FullName;
            }
            dir = dir.Parent;
        }

        // Fallback to current base directory if not found
        return AppContext.BaseDirectory;
    }

    private static string NormalizePath(string path)
    {
        return path.Replace('\\', '/');
    }

    private static string PathCombineInsensitive(string baseDir, string child)
    {
        return NormalizePath(Path.Combine(baseDir, child));
    }

    private static bool IsUnderDirectory(string filePath, string directoryPath)
    {
        var fileNorm = NormalizePath(Path.GetFullPath(filePath));
        var dirNorm = NormalizePath(Path.GetFullPath(directoryPath)).TrimEnd('/');
        return fileNorm.StartsWith(dirNorm + "/", StringComparison.OrdinalIgnoreCase);
    }

    private static string ToRelativePath(string root, string fullPath)
    {
        var rootNorm = NormalizePath(Path.GetFullPath(root)).TrimEnd('/') + "/";
        var fileNorm = NormalizePath(Path.GetFullPath(fullPath));
        if (fileNorm.StartsWith(rootNorm, StringComparison.OrdinalIgnoreCase))
        {
            return fileNorm[rootNorm.Length..];
        }
        return fileNorm;
    }
}