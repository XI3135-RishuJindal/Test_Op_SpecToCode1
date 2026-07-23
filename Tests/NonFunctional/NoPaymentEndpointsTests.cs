using System.Reflection;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Routing;
using Xunit;

namespace ApiGateway.Tests.NonFunctional
{
    public class NoPaymentEndpointsTests
    {
        private static readonly string[] ForbiddenTerms = new[]
        {
            "payment", "payments", "billing", "checkout", "subscription", "invoice",
            "card", "creditcard", "stripe", "paypal"
        };

        private static bool ContainsForbiddenTerm(string? input, out string match)
        {
            match = string.Empty;
            if (string.IsNullOrWhiteSpace(input)) return false;

            var lower = input.ToLowerInvariant();
            foreach (var term in ForbiddenTerms)
            {
                if (lower.Contains(term))
                {
                    match = term;
                    return true;
                }
            }
            return false;
        }

        [Fact]
        public void Controllers_And_Routes_Should_Not_Contain_Payment_Related_Terms()
        {
            // Use a known controller type from the ApiGateway assembly to load it
            var assembly = typeof(ApiGateway.Controllers.HealthController).Assembly;

            var violations = new List<string>();

            var controllerTypes = assembly
                .GetTypes()
                .Where(t =>
                    t.IsClass &&
                    !t.IsAbstract &&
                    (typeof(ControllerBase).IsAssignableFrom(t) ||
                     t.GetCustomAttribute<ApiControllerAttribute>() != null))
                .ToList();

            foreach (var controller in controllerTypes)
            {
                // Check controller type name
                if (ContainsForbiddenTerm(controller.Name, out var match))
                {
                    violations.Add($"Controller name '{controller.FullName}' contains forbidden term '{match}'.");
                }

                // Check class-level route templates
                var classRouteAttributes = controller
                    .GetCustomAttributes(inherit: true)
                    .OfType<IRouteTemplateProvider>()
                    .ToList();

                foreach (var attr in classRouteAttributes)
                {
                    var template = attr.Template ?? string.Empty;
                    if (ContainsForbiddenTerm(template, out match))
                    {
                        violations.Add($"Route template on '{controller.FullName}' contains forbidden term '{match}': '{template}'.");
                    }
                }

                // Check action names and method-level route templates
                var actionMethods = controller
                    .GetMethods(BindingFlags.Instance | BindingFlags.Public | BindingFlags.DeclaredOnly)
                    .Where(m => !m.IsSpecialName) // exclude property getters/setters
                    .ToList();

                foreach (var method in actionMethods)
                {
                    if (ContainsForbiddenTerm(method.Name, out match))
                    {
                        violations.Add($"Action name '{controller.FullName}.{method.Name}' contains forbidden term '{match}'.");
                    }

                    var methodRouteAttributes = method
                        .GetCustomAttributes(inherit: true)
                        .OfType<IRouteTemplateProvider>()
                        .ToList();

                    foreach (var attr in methodRouteAttributes)
                    {
                        var template = attr.Template ?? string.Empty;
                        if (ContainsForbiddenTerm(template, out match))
                        {
                            violations.Add($"Action route template on '{controller.FullName}.{method.Name}' contains forbidden term '{match}': '{template}'.");
                        }
                    }
                }
            }

            Assert.True(
                violations.Count == 0,
                "Payment-related terms detected in API surface:\n - " + string.Join("\n - ", violations)
            );
        }
    }
}