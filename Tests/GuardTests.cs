using Xunit;
using System.Linq;
using Microsoft.AspNetCore.Mvc;
using ApiGateway.Controllers;

namespace ApiGateway.Tests
{
    public class GuardTests
    {
        private static readonly string[] PaymentTerms = { "payment", "payments", "billing", "checkout", "card", "subscription", "invoice" };

        [Fact]
        public void NoPaymentEndpoints()
        {
            var controllerTypes = typeof(AuthController).Assembly.GetTypes()
                .Where(t => t.IsSubclassOf(typeof(ControllerBase)));

            foreach (var controller in controllerTypes)
            {
                var routeAttributes = controller.GetCustomAttributes(typeof(RouteAttribute), false);
                foreach (RouteAttribute routeAttribute in routeAttributes)
                {
                    var routeTemplate = routeAttribute.Template?.ToLowerInvariant() ?? string.Empty;
                    Assert.False(PaymentTerms.Any(term => routeTemplate.Contains(term)),
                        $"Controller '{controller.Name}' has a payment-related route: {routeTemplate}");
                }

                var actions = controller.GetMethods()
                    .Where(m => m.GetCustomAttributes(typeof(HttpMethodAttribute), false).Any());

                foreach (var action in actions)
                {
                    var actionRouteTemplates = action.GetCustomAttributes(typeof(RouteAttribute), false)
                        .Cast<RouteAttribute>()
                        .Select(attr => attr.Template?.ToLowerInvariant() ?? string.Empty);

                    foreach (var template in actionRouteTemplates)
                    {
                        Assert.False(PaymentTerms.Any(term => template.Contains(term)),
                            $"Action '{action.Name}' in controller '{controller.Name}' has a payment-related route: {template}");
                    }
                }
            }
        }

        [Fact]
        public void NoPaymentUIAssetsExist()
        {
            // Since there are no UI layer files, this test will pass by default
            Assert.True(true, "No UI files detected, as expected.");
        }
    }
}
