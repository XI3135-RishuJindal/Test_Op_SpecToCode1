using ApiGateway.Options;
using Microsoft.Extensions.Options;

namespace ApiGateway.Services
{
    public class RoleMappingService
    {
        private readonly AuthorizationOptions _options;

        public RoleMappingService(IOptions<AuthorizationOptions> options)
        {
            _options = options.Value;
        }

        public string[] MapIdpRoles(IEnumerable<string> idpRoles)
        {
            var platformRoles = new List<string>();

            foreach (var idpRole in idpRoles)
            {
                if (_options.RoleMappings.TryGetValue(idpRole, out var roles))
                {
                    platformRoles.AddRange(roles);
                }
            }

            return platformRoles.Distinct().ToArray();
        }
    }
}