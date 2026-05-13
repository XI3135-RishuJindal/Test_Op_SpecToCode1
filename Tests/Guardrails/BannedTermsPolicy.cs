using System.Text.RegularExpressions;

namespace ApiGateway.Tests.Guardrails;

internal static class BannedTermsPolicy
{
    private static readonly Lazy<string[]> _terms = new(() => LoadTerms());

    public static string[] Terms => _terms.Value;

    public static string RepoRoot => FindRepoRoot();

    public static IEnumerable<string> GetUiScanDirectories()
    {
        var root = RepoRoot;
        var candidates = new[]
        {
            Path.Combine(root, "Views"),
            Path.Combine(root, "Pages"),
            Path.Combine(root, "wwwroot"),
            Path.Combine(root, "ClientApp")
        };

        return candidates.Where(Directory.Exists);
    }

    public static bool ContainsBannedTerm(string input, out string matchedTerm)
    {
        matchedTerm = string.Empty;
        if (string.IsNullOrWhiteSpace(input)) return false;

        var normalized = Normalize(input);

        // For single-word terms: compare against tokens
        var tokens = normalized.Split(' ', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        foreach (var term in Terms)
        {
            if (string.IsNullOrWhiteSpace(term)) continue;

            var termNormalized = Normalize(term);
            if (!termNormalized.Contains(' '))
            {
                if (tokens.Any(t => string.Equals(t, termNormalized, StringComparison.OrdinalIgnoreCase)))
                {
                    matchedTerm = term;
                    return true;
                }
            }
            else
            {
                // Phrase: check with boundaries against normalized string
                // surround normalized string with spaces to check whole-word phrases
                var haystack = $" {normalized} ";
                var needle = $" {termNormalized} ";
                if (haystack.Contains(needle, StringComparison.OrdinalIgnoreCase))
                {
                    matchedTerm = term;
                    return true;
                }
            }
        }

        return false;
    }

    private static string Normalize(string s)
    {
        if (string.IsNullOrEmpty(s)) return string.Empty;

        // Replace common separators with space
        var replaced = s
            .Replace("/", " ")
            .Replace("\\", " ")
            .Replace("-", " ")
            .Replace("_", " ")
            .Replace(".", " ")
            .Replace("{", " ")
            .Replace("}", " ")
            .Replace("(", " ")
            .Replace(")", " ")
            .Replace("[", " ")
            .Replace("]", " ");

        // Insert space at PascalCase boundaries: "PaymentController" -> "Payment Controller"
        replaced = Regex.Replace(replaced, "([a-z0-9])([A-Z])", "$1 $2");
        replaced = Regex.Replace(replaced, "([A-Z]+)([A-Z][a-z])", "$1 $2");

        // Collapse whitespace and to lower
        replaced = Regex.Replace(replaced, "\\s+", " ").Trim();

        return replaced.ToLowerInvariant();
    }

    private static string[] LoadTerms()
    {
        var root = FindRepoRoot();
        var policyPath = Path.Combine(root, "policy", "banned-ui-terms.txt");
        if (!File.Exists(policyPath))
        {
            throw new FileNotFoundException($"Banned terms policy file not found at: {policyPath}");
        }

        var lines = File.ReadAllLines(policyPath)
            .Select(l => l.Trim())
            .Where(l => !string.IsNullOrWhiteSpace(l) && !l.StartsWith("#"))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToArray();

        return lines;
    }

    private static string FindRepoRoot()
    {
        // Start from the base directory of the test assembly and move upwards
        var dir = AppContext.BaseDirectory;
        var maxLevels = 10;

        for (int i = 0; i < maxLevels && dir != null; i++)
        {
            // Heuristic: repo