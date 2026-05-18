using System;
using System.IO;
using System.Linq;
using Xunit;

namespace ApiGateway.Tests.Policies
{
    public class NoPaymentUiElementsTests
    {
        private static readonly string[] PaymentKeywords = { "payment", "payments", "billing", "checkout", "pay" };
        private const string ControllersPath = "../../../../Controllers";

        [Fact]
        public void EnsureNoPaymentUIInControllers()
        {
            var controllerFiles = Directory.GetFiles(ControllersPath, "*.cs", SearchOption.AllDirectories);

            foreach (var file in controllerFiles)
            {
                var fileName = Path.GetFileName(file).ToLower();
                Assert.False(PaymentKeywords.Any(keyword => fileName.Contains(keyword)),
                    $"File '{fileName}' contains payment-related keywords.");

                var fileContent = File.ReadAllText(file).ToLower();
                Assert.False(PaymentKeywords.Any(keyword => fileContent.Contains(keyword)),
                    $"File '{fileName}' contains payment-related content.");
            }
        }

        [Theory]
        [InlineData("api/[controller]")]
        public void EnsureNoPaymentRoutesInAttributes(string routePattern)
        {
            var controllerFiles = Directory.GetFiles(ControllersPath, "*.cs", SearchOption.AllDirectories);

            foreach (var file in controllerFiles)
            {
                var fileContent = File.ReadAllText(file).ToLower();
                var routes = fileContent.Split(new[] { "[route(" }, StringSplitOptions.None);

                foreach (var route in routes.Skip(1))
                {
                    var endOfRouteAttribute = route.IndexOf(')');
                    if (endOfRouteAttribute != -1)
                    {
                        var routeString = route.Substring(0, endOfRouteAttribute + 1);
                        Assert.False(PaymentKeywords.Any(keyword => routeString.Contains(keyword)),
                            $"Route '{routeString}' in file '{Path.GetFileName(file)}' contains payment-related keywords.");
                    }
                }
            }
        }
    }
}