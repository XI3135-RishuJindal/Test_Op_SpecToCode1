using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Xml.Linq;
using Xunit;

namespace UpgradeValidation.Tests
{
    /// <summary>
    /// Validates that the ASP.NET Core 8 SDK-style project structure upgrade succeeded.
    /// These tests verify the exact target version, project file format, and structural
    /// requirements defined in the upgrade spec.
    /// </summary>
    public class AspNetCore8UpgradeValidationTests
    {
        // -----------------------------------------------------------------------
        // Helpers — locate solution root and project files
        // -----------------------------------------------------------------------

        /// <summary>
        /// Walks up from the test assembly's directory until it finds a .sln file,
        /// which is treated as the repository / solution root.
        /// </summary>
        private static string FindSolutionRoot()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null)
            {
                if (dir.GetFiles("*.sln").Length > 0)
                    return dir.FullName;
                dir = dir.Parent;
            }
            throw new InvalidOperationException(
                "Could not locate solution root (no *.sln file found in any ancestor directory).");
        }

        private static string[] FindCsprojFiles(string root) =>
            Directory.GetFiles(root, "*.csproj", SearchOption.AllDirectories);

        private static XDocument LoadCsproj(string path) =>
            XDocument.Load(path);

        // -----------------------------------------------------------------------
        // 1. Runtime version — EXACT target version assertion
        // -----------------------------------------------------------------------

        [Fact]
        public void Runtime_MajorVersion_IsExactly8()
        {
            var version = Environment.Version;
            Assert.True(
                version.Major == 8,
                $"Expected .NET runtime major version 8, but found {version}. " +
                "Ensure the project targets net8.0 and is being executed on the .NET 8 runtime.");
        }

        [Fact]
        public void Runtime_FrameworkDescription_ContainsDotNet8()
        {
            var description = RuntimeInformation.FrameworkDescription;
            Assert.Contains("8.", description,
                StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void Runtime_Version_IsAtLeast_8_0_0()
        {
            var version = Environment.Version;
            var minimum = new Version(8, 0, 0);
            Assert.True(
                version >= minimum,
                $"Runtime version {version} is below the required minimum {minimum}.");
        }

        // -----------------------------------------------------------------------
        // 2. SDK-style .csproj — TargetFramework must be net8.0
        // -----------------------------------------------------------------------

        [Fact]
        public void AllCsprojFiles_TargetFramework_IsNet8()
        {
            var root = FindSolutionRoot();
            var csprojFiles = FindCsprojFiles(root);

            Assert.True(csprojFiles.Length > 0,
                "No .csproj files found under the solution root. " +
                "Ensure the SDK-style project has been scaffolded.");

            foreach (var csproj in csprojFiles)
            {
                var doc = LoadCsproj(csproj);
                var targetFramework = doc
                    .Descendants("TargetFramework")
                    .FirstOrDefault()?.Value;

                Assert.True(
                    targetFramework == "net8.0",
                    $"Expected <TargetFramework>net8.0</TargetFramework> in '{csproj}', " +
                    $"but found '{targetFramework ?? "(missing)"}'.");
            }
        }

        [Fact]
        public void AllCsprojFiles_UseSdkStyle_SdkAttribute()
        {
            var root = FindSolutionRoot();
            var csprojFiles = FindCsprojFiles(root);

            Assert.True(csprojFiles.Length > 0,
                "No .csproj files found under the solution root.");

            foreach (var csproj in csprojFiles)
            {
                var doc = LoadCsproj(csproj);
                var sdkAttribute = doc.Root?.Attribute("Sdk")?.Value;

                Assert.False(
                    string.IsNullOrWhiteSpace(sdkAttribute),
                    $"'{csproj}' is missing the Sdk attribute on the root <Project> element. " +
                    "SDK-style projects must declare Sdk=\"Microsoft.NET.Sdk\" (or a variant).");

                Assert.StartsWith(
                    "Microsoft.NET.Sdk",
                    sdkAttribute,
                    StringComparison.OrdinalIgnoreCase);
            }
        }

        // -----------------------------------------------------------------------
        // 3. Nullable reference types enabled
        // -----------------------------------------------------------------------

        [Fact]
        public void MainCsprojOrDirectoryBuildProps_NullableIsEnabled()
        {
            var root = FindSolutionRoot();

            // Check Directory.Build.props first (centralised setting)
            var directoryBuildProps = Path.Combine(root, "Directory.Build.props");
            if (File.Exists(directoryBuildProps))
            {
                var doc = XDocument.Load(directoryBuildProps);
                var nullable = doc.Descendants("Nullable").FirstOrDefault()?.Value;
                if (!string.IsNullOrWhiteSpace(nullable))
                {
                    Assert.Equal("enable", nullable, ignoreCase: true);
                    return; // satisfied via Directory.Build.props
                }
            }

            // Fall back to individual .csproj files
            var csprojFiles = FindCsprojFiles(root)
                .Where(f => !f.Contains(".Tests", StringComparison.OrdinalIgnoreCase))
                .ToArray();

            Assert.True(csprojFiles.Length > 0,
                "No main (non-test) .csproj files found.");

            foreach (var csproj in csprojFiles)
            {
                var doc = LoadCsproj(csproj);
                var nullable = doc.Descendants("Nullable").FirstOrDefault()?.Value;
                Assert.True(
                    string.Equals(nullable, "enable", StringComparison.OrdinalIgnoreCase),
                    $"Expected <Nullable>enable</Nullable> in '{csproj}' or Directory.Build.props, " +
                    $"but found '{nullable ?? "(missing)"}'.");
            }
        }

        // -----------------------------------------------------------------------
        // 4. ImplicitUsings enabled
        // -----------------------------------------------------------------------

        [Fact]
        public void MainCsprojOrDirectoryBuildProps_ImplicitUsingsIsEnabled()
        {
            var root = FindSolutionRoot();

            var directoryBuildProps = Path.Combine(root, "Directory.Build.props");
            if (File.Exists(directoryBuildProps))
            {
                var doc = XDocument.Load(directoryBuildProps);
                var implicitUsings = doc.Descendants("ImplicitUsings").FirstOrDefault()?.Value;
                if (!string.IsNullOrWhiteSpace(implicitUsings))
                {
                    Assert.Equal("enable", implicitUsings, ignoreCase: true);
                    return;
                }
            }

            var csprojFiles = FindCsprojFiles(root)
                .Where(f => !f.Contains(".Tests", StringComparison.OrdinalIgnoreCase))
                .ToArray();

            Assert.True(csprojFiles.Length > 0,
                "No main (non-test) .csproj files found.");

            foreach (var csproj in csprojFiles)
            {
                var doc = LoadCsproj(csproj);
                var implicitUsings = doc.Descendants("ImplicitUsings").FirstOrDefault()?.Value;
                Assert.True(
                    string.Equals(implicitUsings, "enable", StringComparison.OrdinalIgnoreCase),
                    $"Expected <ImplicitUsings>enable</ImplicitUsings> in '{csproj}' or Directory.Build.props, " +
                    $"but found '{implicitUsings ?? "(missing)"}'.");
            }
        }

        // -----------------------------------------------------------------------
        // 5. Directory.Build.props exists at solution root
        // -----------------------------------------------------------------------

        [Fact]
        public void SolutionRoot_ContainsDirectoryBuildProps()
        {
            var root = FindSolutionRoot();
            var path = Path.Combine(root, "Directory.Build.props");
            Assert.True(File.Exists(path),
                $"Directory.Build.props not found at solution root '{root}'. " +
                "This file is required to centralise shared MSBuild properties per the upgrade spec.");
        }

        [Fact]
        public void DirectoryBuildProps_IsValidXml()
        {
            var root = FindSolutionRoot();
            var path = Path.Combine(root, "Directory.Build.props");
            if (!File.Exists(path))
                return; // covered by existence test above

            var exception = Record.Exception(() => XDocument.Load(path));
            Assert.Null(exception);
        }

        // -----------------------------------------------------------------------
        // 6. Directory.Packages.props — Central Package Management
        // -----------------------------------------------------------------------

        [Fact]
        public void SolutionRoot_ContainsDirectoryPackagesProps()
        {
            var root = FindSolutionRoot();
            var path = Path.Combine(root, "Directory.Packages.props");
            Assert.True(File.Exists(path),
                $"Directory.Packages.props not found at solution root '{root}'. " +
                "Central Package Management is required per the upgrade spec.");
        }

        [Fact]
        public void DirectoryPackagesProps_HasManagePackageVersionsCentrally_True()
        {
            var root = FindSolutionRoot();
            var path = Path.Combine(root, "Directory.Packages.props");
            if (!File.Exists(path))
                return; // covered by existence test above

            var doc = XDocument.Load(path);
            var value = doc.Descendants("ManagePackageVersionsCentrally")
                           .FirstOrDefault()?.Value;

            Assert.True(
                string.Equals(value, "true", StringComparison.OrdinalIgnoreCase),
                $"Expected <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally> " +
                $"in Directory.Packages.props, but found '{value ?? "(missing)"}'.");
        }

        // -----------------------------------------------------------------------
        // 7. Solution file (.sln) exists at root
        // -----------------------------------------------------------------------

        [Fact]
        public void SolutionRoot_ContainsSlnFile()
        {
            var root = FindSolutionRoot();
            var slnFiles = Directory.GetFiles(root, "*.sln", SearchOption.TopDirectoryOnly);
            Assert.True(slnFiles.Length > 0,
                $"No .sln file found at solution root '{root}'.");
        }

        // -----------------------------------------------------------------------
        // 8. Test project exists and targets net8.0
        // -----------------------------------------------------------------------

        [Fact]
        public void TestProject_Exists_AndTargetsNet8()
        {
            var root = FindSolutionRoot();
            var testCsprojFiles = FindCsprojFiles(root)
                .Where(f => f.Contains(".Tests", StringComparison.OrdinalIgnoreCase) ||
                            f.Contains(".Test", StringComparison.OrdinalIgnoreCase))
                .ToArray();

            Assert.True(testCsprojFiles.Length > 0,
                "No test project (.Tests.csproj) found under the solution root. " +
                "A unit test project targeting net8.0 is required per the upgrade spec.");

            foreach (var csproj in testCsprojFiles)
            {
                var doc = LoadCsproj(csproj);
                var targetFramework = doc.Descendants("TargetFramework").FirstOrDefault()?.Value;
                Assert.Equal("net8.0", targetFramework);
            }
        }

        [Fact]
        public void TestProject_HasIsPackable_False()
        {
            var root = FindSolutionRoot();
            var testCsprojFiles = FindCsprojFiles(root)
                .Where(f => f.Contains(".Tests", StringComparison.OrdinalIgnoreCase) ||
                            f.Contains(".Test", StringComparison.OrdinalIgnoreCase))
                .ToArray();

            if (testCsprojFiles.Length == 0)
                return; // covered by existence test above

            foreach (var csproj in testCsprojFiles)
            {
                var doc = LoadCsproj(csproj);
                var isPackable = doc.Descendants("IsPackable").FirstOrDefault()?.Value;
                Assert.True(
                    string.Equals(isPackable, "false", StringComparison.OrdinalIgnoreCase),
                    $"Expected <IsPackable>false</IsPackable> in test project '{csproj}', " +
                    $"but found '{isPackable ?? "(missing)"}'.");
            }
        }

        // -----------------------------------------------------------------------
        // 9. Program.cs — minimal hosting model (no Startup.cs)
        // -----------------------------------------------------------------------

        [Fact]
        public void MainProject_ContainsProgramCs_WithMinimalHostingModel()
        {
            var root = FindSolutionRoot();

            // Find Program.cs files that are NOT inside test projects
            var programFiles = Directory.GetFiles(root, "Program.cs", SearchOption.AllDirectories)
                .Where(f => !f.Contains(".Tests", StringComparison.OrdinalIgnoreCase) &&
                            !f.Contains(".Test", StringComparison.OrdinalIgnoreCase))
                .ToArray();

            Assert.True(programFiles.Length > 0,
                "No Program.cs found in the main project. " +
                "The minimal hosting model requires a Program.cs entry point.");

            foreach (var programCs in programFiles)
            {
                var content = File.ReadAllText(programCs);
                Assert.Contains("WebApplication.CreateBuilder", content,
                    StringComparison.Ordinal);
            }
        }

        [Fact]
        public void MainProject_DoesNotContain_StartupCs()
        {
            var root = FindSolutionRoot();

            var startupFiles = Directory.GetFiles(root, "Startup.cs", SearchOption.AllDirectories)
                .Where(f => !f.Contains(".Tests", StringComparison.OrdinalIgnoreCase))
                .ToArray();

            Assert.True(startupFiles.Length == 0,
                $"Found Startup.cs file(s): {string.Join(", ", startupFiles)}. " +
                "The ASP.NET Core 8 minimal hosting model does not use Startup.cs. " +
                "Remove or migrate this file to Program.cs.");
        }

        // -----------------------------------------------------------------------
        // 10. Legacy packages.config must not exist
        // -----------------------------------------------------------------------

        [Fact]
        public void NoPackagesConfig_FilesExist()
        {
            var root = FindSolutionRoot();
            var packagesConfigFiles = Directory.GetFiles(root, "packages.config",
                SearchOption.AllDirectories);

            Assert.True(packagesConfigFiles.Length == 0,
                $"Found packages.config file(s): {string.Join(", ", packagesConfigFiles)}. " +
                "SDK-style projects must use <PackageReference> elements, not packages.config.");
        }

        // -----------------------------------------------------------------------
        // 11. No legacy web.config application configuration (appsettings.json expected)
        // -----------------------------------------------------------------------

        [Fact]
        public void MainProject_ContainsAppSettingsJson()
        {
            var root = FindSolutionRoot();

            var appSettingsFiles = Directory.GetFiles(root, "appsettings.json",
                SearchOption.AllDirectories)
                .Where(f => !f.Contains(".Tests", StringComparison.OrdinalIgnoreCase))
                .ToArray();

            Assert.True(appSettingsFiles.Length > 0,
                "No appsettings.json found in the main project. " +
                "ASP.NET Core 8 projects should use appsettings.json for configuration.");
        }

        // -----------------------------------------------------------------------
        // 12. LangVersion in Directory.Build.props (or csproj) is 'latest'
        // -----------------------------------------------------------------------

        [Fact]
        public void DirectoryBuildProps_LangVersion_IsLatest()
        {
            var root = FindSolutionRoot();
            var path = Path.Combine(root, "Directory.Build.props");
            if (!File.Exists(path))
                return; // not required to be in Directory.Build.props exclusively

            var doc = XDocument.Load(path);
            var langVersion = doc.Descendants("LangVersion").FirstOrDefault()?.Value;

            if (langVersion != null)
            {
                Assert.True(
                    string.Equals(langVersion, "latest", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(langVersion, "preview", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(langVersion, "12.0", StringComparison.OrdinalIgnoreCase),
                    $"Expected <LangVersion>latest</LangVersion> (or 'preview' / '12.0') " +
                    $"in Directory.Build.props, but found '{langVersion}'.");
            }
        }

        // -----------------------------------------------------------------------
        // 13. No legacy WeatherForecast placeholder files
        // -----------------------------------------------------------------------

        [Fact]
        public void MainProject_DoesNotContain_WeatherForecastPlaceholders()
        {
            var root = FindSolutionRoot();

            var weatherFiles = Directory.GetFiles(root, "WeatherForecast*.cs",
                SearchOption.AllDirectories)
                .Where(f => !f.Contains(".Tests", StringComparison.OrdinalIgnoreCase))
                .ToArray();

            Assert.True(weatherFiles.Length == 0,
                $"Found scaffolding placeholder file(s): {string.Join(", ", weatherFiles)}. " +
                "Remove auto-generated WeatherForecast placeholder files per the upgrade spec.");
        }

        // -----------------------------------------------------------------------
        // 14. Test project references main project (not a package)
        // -----------------------------------------------------------------------

        [Fact]
        public void TestProject_HasProjectReference_ToMainProject()
        {
            var root = FindSolutionRoot();
            var testCsprojFiles = FindCsprojFiles(root)
                .Where(f => f.Contains(".Tests", StringComparison.OrdinalIgnoreCase) ||
                            f.Contains(".Test", StringComparison.OrdinalIgnoreCase))
                .ToArray();

            if (testCsprojFiles.Length == 0)
                return; // covered by existence test above

            foreach (var csproj in testCsprojFiles)
            {
                var doc = LoadCsproj(csproj);
                var projectReferences = doc.Descendants("ProjectReference").ToArray();
                Assert.True(projectReferences.Length > 0,
                    $"Test project '{csproj}' has no <ProjectReference> elements. " +
                    "The test project must reference the main project.");
            }
        }
    }
}