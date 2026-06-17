using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml.Linq;
using ApiGateway.Controllers;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Routing;
using Xunit;

namespace ApiGateway.Tests.Compliance
{
    public static class ProhibitedKeywords
    {
        // Intent keywords
        public static readonly string[] Intent = new[]
        {
            "payment", "pay", "billing", "charge", "checkout", "invoice", "refund",
            "transaction", "wallet", "subscription", "webhook", "webhooks", "callback"
        };

        // Provider keywords
        public static readonly string[] Providers = new[]
        {
            "stripe", "paypal", "braintree", "square", "razorpay", "adyen", "mollie", "authorize.net", "worldpay"
        };

        public static readonly string[] AllRouteTokens =
            Intent.Concat(Providers).ToArray();

        public static readonly string[] PackageTokens =
            Providers;
    }

    public class RouteInventoryTests
    {
        private record RouteInfo(string HttpMethod, string Path, string Controller, string Action)
        {
            public override string ToString() => $"{HttpMethod.ToUpperInvariant(),-6} {Path} => {Controller}.{Action}";
        }

        [Fact]
        public void RouteInventory_HasNoPaymentOrWebhookEndpoints()
        {
            var routes = EnumerateRoutes();

            var offenders = new List<(RouteInfo Route, string Keyword, string Where)>();
            foreach (var r in routes)
            {
                var ctrl = r.Controller.ToLowerInvariant();
                var action = r.Action.ToLowerInvariant();
                var path = r.Path.ToLowerInvariant();

                foreach (var kw in ProhibitedKeywords.AllRouteTokens)
                {
                    if (ctrl.Contains(kw)) offenders.Add((r, kw, "controller"));
                    if (action.Contains(kw)) offenders.Add((r, kw, "action"));
                    if (path.Contains(kw)) offenders.Add((r, kw, "path"));
                }
            }

            if (offenders.Count > 0)
            {
                var sb = new StringBuilder();
                sb.AppendLine("Prohibited payment/webhook keywords detected in API route inventory.");
                sb.AppendLine();
                sb.AppendLine("Offenders:");
                foreach (var (route, keyword, where) in offenders)
                {
                    sb.AppendLine($" - '{keyword}' found in {where} of: {route}");
                }
                sb.AppendLine();
                sb.AppendLine("Discovered routes:");
                foreach (var r in routes.OrderBy(r => r.Path).ThenBy(r => r.HttpMethod))
                {
                    sb.AppendLine($" - {r}");
                }

                Assert.True(false, sb.ToString());
            }

            // If needed, diagnostics for visibility in test output during local runs
            // OutputHelpers.WriteLine("Discovered routes:\n" + string.Join("\n", routes.Select(r => $" - {r}")));
        }

        [Fact]
        public void PackageReferences_DoNotContainPaymentProviders()
        {
            var csproj = FindFileUpwards("ApiGateway.csproj");
            Assert.True(File