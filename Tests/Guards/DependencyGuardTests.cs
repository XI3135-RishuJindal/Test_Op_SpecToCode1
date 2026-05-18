using System;
using System.IO;
using System.Linq;
using Xunit;

namespace ApiGateway.Tests.Guards
{
    public class DependencyGuardTests
    {
        private readonly string[] bannedTokens = new[]
        {
            "payment", "payments", "billing", "checkout", "webhook", "webhooks",
            "stripe", "paypal", "braintree", "square", "adyen"
        };

        [Fact]
        public void EnsureNoBannedDependencies()
        {
            var projectFilePath = Path.Combine(AppContext.BaseDirectory, "../../../ApiGateway.csproj");
            Assert.True(File.Exists(projectFilePath), "ApiGateway.csproj file is missing.");

            var projectFileContent = File.ReadAllText(projectFilePath);
            var lowerCaseContent = projectFileContent.ToLowerInvariant();

            var offendingTokens = bannedTokens
                .Where(token => lowerCaseContent.Contains(token))
                .ToArray();

            Assert.False(offendingTokens.Any(),
                $"ApiGateway.csproj references banned tokens: {string.Join(", ", offendingTokens)}. " +
                "Please remove them to comply with the dependency guard guidelines.");
        }
    }
}