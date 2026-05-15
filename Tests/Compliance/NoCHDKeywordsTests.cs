using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Xunit;

namespace ApiGateway.Tests.Compliance
{
    public class NoCHDKeywordsTests
    {
        private static readonly string[] DisallowedKeywords = new[]
        {
            "cardNumber", "pan", "cvv", "cvc", "expiry", "track1", "track2", "pin", "payment", "checkout"
        };

        private const string SuppressionToken = "PCI-ALLOW";

        [Fact]
        public void NoCHDKeywordsPresentInAppCode()
        {
            var repoRoot = FindRepoRoot() ?? throw new InvalidOperationException("Could not locate repository root (directory containing ApiGateway.csproj).");

            // Limit scan strictly to application source files
            var targetFiles = new List<string>();

            var programCs = Path.Combine(repoRoot, "Program.cs");
            if (File.Exists(programCs))
                targetFiles.Add(programCs);

            var controllersDir = Path.Combine(repoRoot, "Controllers");
            if (Directory.Exists(controllersDir))
                targetFiles.AddRange(Directory.GetFiles(controllersDir, "*.cs", SearchOption.AllDirectories));

            var modelsDir = Path.Combine(repoRoot, "Models");
            if (Directory.Exists(modelsDir))
                targetFiles.AddRange(Directory.GetFiles(modelsDir, "*.cs", SearchOption.AllDirectories));

            // Explicitly do not scan Tests/, docs/, openspec/ or any non-.cs files
            targetFiles = targetFiles
                .Where(f =>
                    f.EndsWith(".cs", StringComparison.OrdinalIgnoreCase) &&
                    !IsUnderDirectory(f, repoRoot, "Tests") &&
                    !IsUnderDirectory(f, repoRoot, "docs") &&
                    !IsUnderDirectory(f, repoRoot, "openspec"))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToList();

            var findings = new List<string>();

            foreach (var file in targetFiles)
            {
                int lineNumber = 0;
                foreach (var line in File.ReadLines(file))
                {
                    lineNumber++;

                    // Skip lines that explicitly include the suppression token
                    if (line.IndexOf(SuppressionToken, StringComparison.OrdinalIgnoreCase) >= 0)
                        continue;

                    foreach (var keyword in DisallowedKeywords)
                    {
                        if (line.IndexOf(keyword, StringComparison.OrdinalIgnoreCase) >= 0)
                        {
                            findings.Add($"{RelativePath(repoRoot, file)}:{lineNumber} contains '{keyword}' -> {line.Trim()}");
                        }
                    }
                }
            }

            if (findings.Count > 0)
            {
                var message =
                    "Disallowed CHD/SAD-related term(s) detected in application source files.\n" +
                    "Our PCI scope statement requires that the MVP does not store, process, or transmit CHD/SAD.\n" +
                    "Please reference docs/compliance/pci/scope-statement.md and either remove the field/term " +
                    "or initiate PCI re-scoping. If and only if approved by Compliance, add a suppression comment " +
                    $"containing '{SuppressionToken}' on that line.\n\n" +
                    "Findings:\n - " + string.Join("\n - ", findings);

                Assert.True(false, message);
            }
        }

        private static string? FindRepoRoot()
        {
            // Search upwards from the test assembly base directory for the repo root (has ApiGateway.csproj)
            string? dir = AppContext.BaseDirectory;

            for (int i = 0; i < 10 && !string.IsNullOrEmpty(dir); i++)
            {
                var csprojPath = Path.Combine(dir, "ApiGateway.csproj");
                if (File.Exists(csprojPath))
                    return dir;

                dir = Directory.GetParent(dir)?.FullName;
            }

            // Fallback to current directory search
            dir = Directory.GetCurrentDirectory();
            for (int i = 0; i < 10 && !string.IsNullOrEmpty(dir); i++)
            {
                var csprojPath = Path.Combine(dir, "ApiGateway.csproj");
                if (File.Exists(csprojPath))
                    return dir;

                dir = Directory.GetParent(dir)?.FullName;
            }

            return null;
        }

        private static bool IsUnderDirectory(string filePath, string root, string childDirName)
        {
            var fullRoot = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            var fullPath = Path.GetFullPath(filePath);

            var targetDir = Path.Combine(fullRoot, childDirName) + Path.DirectorySeparatorChar;

            return fullPath.StartsWith(targetDir, StringComparison.OrdinalIgnoreCase);
        }

        private static string RelativePath(string root, string fullPath)
        {
            var fullRoot = Path.GetFullPath(root);
            var path = Path.GetFullPath(fullPath);

            if (!path.StartsWith(fullRoot, StringComparison.OrdinalIgnoreCase))
                return path;

            return path.Substring(fullRoot.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        }
    }
}