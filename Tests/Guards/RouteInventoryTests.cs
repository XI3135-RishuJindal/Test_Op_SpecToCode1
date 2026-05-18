using System;
using System.Linq;
using System.Reflection;
using Xunit;
using Microsoft.AspNetCore.Mvc;

namespace ApiGateway.Tests.Guards
{
    public class RouteInventoryTests
    {
        [Fact]
        public void EnsureNoPaymentRelatedRoutesExist()
        {
            // Banned segments
            string[] bannedSegments = new[] { "payment", "payments", "billing", "checkout", "webhook", "webhooks", "stripe", "paypal", "braintree", "square", "adyen" };

            // Get all controller types
            var controllerTypes = Assembly.GetExecutingAssembly().GetTypes()
                .Where(type => typeof(ControllerBase).IsAssignableFrom(type) && type.GetCustomAttributes<ApiControllerAttribute>().Any())
                .ToList();

            // Discover all routes
            var discoveredRoutes = controllerTypes.SelectMany(controllerType =>
            {
                var controllerName = controllerType.Name.Replace("Controller", string.Empty).ToLower();
                var classRouteTemplate = controllerType.GetCustomAttributes<RouteAttribute>().FirstOrDefault()?.Template.Replace("[controller]", controllerName) ?? string.Empty;

                var methods = controllerType.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly)
                    .Where(m => m.GetCustomAttributes<HttpMethodAttribute>().Any());

                return methods.Select(method =>
                {
                    var methodRouteTemplate = method.GetCustomAttributes<RouteAttribute>().FirstOrDefault()?.Template ?? string.Empty;
                    var httpAttributes = method.GetCustomAttributes<HttpMethodAttribute>();

                    return httpAttributes.Select(httpAttr =>
                    {
                        var fullRoute = $"{classRouteTemplate}/{methodRouteTemplate}".ToLower();
                        return new { Verb = httpAttr.HttpMethods.First(), Route = $"/{fullRoute.Trim('/')}", Method = method.Name };
                    });
                }).SelectMany(route => route);
            }).ToList();

            // Check for banned segments
            var offendingRoutes = discoveredRoutes.Where(route => bannedSegments.Any(segment => route.Route.Contains(segment, StringComparison.OrdinalIgnoreCase))).ToList();

            // Assert no offending routes exist
            Assert.True(!offendingRoutes.Any(), $"Offending routes found:\n{string.Join("\n", offendingRoutes.Select(r => $"- {r.Verb} {r.Route} ({r.Method})"))}\n\nFull route inventory:\n{string.Join("\n", discoveredRoutes.Select(r => $"- {r.Verb} {r.Route} ({r.Method})"))}");
        }
    }
}
