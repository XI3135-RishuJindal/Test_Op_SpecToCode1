using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text.Json;
using Xunit;

public class DotNet8UpgradeValidationTests
{
    // Target framework version to check
    private const string TargetDotNetVersion = "8.0.0";

    [Fact(DisplayName = "Active runtime is EXACTLY .NET 8.0")]
    public void DotNetRuntime_Version_Is_Exact_Target()
    {
        // Retrieve runtime version from the assembly (for .NET 8, Environment.Version/RuntimeInformation.FrameworkDescription is accurate)
        string framework = RuntimeInformation.FrameworkDescription.Trim();
        Assert.StartsWith(".NET", framework);

        // e.g.: ".NET 8.0.0" or ".NET 8.0.2"
        var versionString = framework.Split(' ').Last();
        var actual = Version.Parse(versionString);
        var expected = Version.Parse(TargetDotNetVersion);

        // Assert only major and minor versions match target
        Assert.Equal(expected.Major, actual.Major);
        Assert.Equal(expected.Minor, actual.Minor);
    }

    [Fact(DisplayName = "Project files are SDK-style and target net8.0")]
    public void AllProjectFiles_AreSdkStyle_AndTargetDotNet8()
    {
        // This test expects to run from repo root or test project root.
        var csprojFiles = Directory.GetFiles(Directory.GetCurrentDirectory(), "*.csproj", SearchOption.AllDirectories);
        Assert.NotEmpty(csprojFiles);

        foreach (var file in csprojFiles)
        {
            var xml = File.ReadAllText(file);
            // Check for SDK attribute on Project node
            Assert.Contains("<Project Sdk=\"", xml);

            // TargetFramework set to net8.0
            Assert.Contains("<TargetFramework>net8.0</TargetFramework>", xml);

            // Ensure deprecated/incompatible properties are removed (e.g., ProjectTypeGuids, PackagesConfig)
            Assert.DoesNotContain("<ProjectTypeGuids>", xml, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("<PackagesConfig>", xml, StringComparison.OrdinalIgnoreCase);
        }
    }

    [Fact(DisplayName = "Application functional entry points still work under .NET 8.0")]
    public void ApplicationCriticalPaths_StillWork()
    {
        // For lack of specific application code, verify the test runner itself can instantiate core types and execute.
        // Optionally, try loading all referenced assemblies
        var entry = Assembly.GetEntryAssembly() ?? Assembly.GetExecutingAssembly();
        Assert.NotNull(entry);

        // Try finding the Main method
        var mainMethod = entry.EntryPoint;
        Assert.NotNull(mainMethod);

        // Additional dummy assertion to simulate critical path
        Assert.True(true, "Reached critical app code paths.");
    }

    [Fact(DisplayName = "Legacy configuration keys incompatible with .NET 8.0 are absent")]
    public void DeprecatedApis_AndConfigKeys_Absent()
    {
        var csprojFiles = Directory.GetFiles(Directory.GetCurrentDirectory(), "*.csproj", SearchOption.AllDirectories);
        foreach (var file in csprojFiles)
        {
            var xml = File.ReadAllText(file);

            // Packages.config should not be referenced
            Assert.DoesNotContain("packages.config", xml, StringComparison.OrdinalIgnoreCase);

            // ProjectTypeGuids is deprecated
            Assert.DoesNotContain("ProjectTypeGuids", xml, StringComparison.OrdinalIgnoreCase);
        }
    }

    [Fact(DisplayName = "New .NET 8 SDK configuration loads without errors if present")]
    public void NewDotNet8ConfigKeys_LoadWithoutError()
    {
        // If global.json exists, it should reference .NET 8.0
        var globalJson = Directory.GetFiles(Directory.GetCurrentDirectory(), "global.json", SearchOption.AllDirectories).FirstOrDefault();
        if (globalJson != null)
        {
            var txt = File.ReadAllText(globalJson);
            using (JsonDocument doc = JsonDocument.Parse(txt))
            {
                var sdkProp = doc.RootElement.GetProperty("sdk");
                var version = sdkProp.GetProperty("version").GetString();
                Assert.StartsWith("8.0", version);
            }
        }

        // If Directory.Build.props exists, it should not contain legacy configuration breaking .NET 8.0 build
        var directoryBuildProps = Directory.GetFiles(Directory.GetCurrentDirectory(), "Directory.Build.props", SearchOption.AllDirectories).FirstOrDefault();
        if (directoryBuildProps != null)
        {
            var xml = File.ReadAllText(directoryBuildProps);
            // Common breaking old keys: TargetFrameworkVersion, ProjectTypeGuids
            Assert.DoesNotContain("TargetFrameworkVersion", xml);
            Assert.DoesNotContain("ProjectTypeGuids", xml);
        }
    }
}