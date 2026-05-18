using System.Reflection;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using System.Text;

namespace Tests.Guards
{
    public static class RouteDiscoveryHelper
    {
        public static List<RouteInfo> DiscoverRoutes()
        {
            Assembly apiAssembly = Assembly.Load("ApiGateway");
            var routes = new List<RouteInfo>();

            foreach (var type in apiAssembly.GetTypes())
            {
                if (IsApiController(type))
                {
                    string baseRoute = ResolveBaseRoute(type);
                    bool classAuthRequired = type.GetCustomAttributes<AuthorizeAttribute>().Any() &&
                                             !type.GetCustomAttributes<AllowAnonymousAttribute>().Any();

                    foreach (var method in type.GetMethods(BindingFlags.Instance | BindingFlags.Public | BindingFlags.DeclaredOnly))
                    {
                        var methodAuthRequired = classAuthRequired &&
                                                  !method.GetCustomAttributes<AllowAnonymousAttribute>().Any();

                        foreach (var httpAttr in method.GetCustomAttributes<HttpMethodAttribute>())
                        {
                            string fullPath = NormalizePath($"{baseRoute}/{ResolveMethodRoute(httpAttr.Template)}");

                            routes.Add(new RouteInfo {
                                HttpMethod = httpAttr.HttpMethods.First().ToUpper(),
                                Path = fullPath,
                                AuthRequired = methodAuthRequired
                            });
                        }
                    }
                }
            }

            return routes;
        }

        private static bool IsApiController(Type type)
        {
            return type.IsClass &&
                   !type.IsAbstract &&
                   type.IsPublic &&
                   type.IsDefined(typeof(ApiControllerAttribute), inherit: false) &&
                   typeof(ControllerBase).IsAssignableFrom(type);
        }

        private static string ResolveBaseRoute(Type type)
        {
            var routeAttr = type.GetCustomAttribute<RouteAttribute>();
            string template = routeAttr?.Template ?? string.Empty;
            return template.ToLower().Replace("[controller]", type.Name.Replace("Controller", "").ToLower());
        }

        private static string ResolveMethodRoute(string template)
        {
            return template?.ToLower() ?? string.Empty;
        }

        private static string NormalizePath(string path)
        {
            return $"/{path.Trim('/')}/".Replace("//", "/").ToLower();
        }

        public static string PrettyPrintRoutes(IEnumerable<RouteInfo> routes)
        {
            var builder = new StringBuilder();
            foreach (var route in routes)
            {
                builder.AppendLine($"- {route.HttpMethod} {route.Path} {(route.AuthRequired ? "(auth required)" : "")}");
            }
            return builder.ToString();
        }
    }

    public class RouteInfo
    {
        public string HttpMethod { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public bool AuthRequired { get; set; }
    }
}