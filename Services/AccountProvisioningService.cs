using System.Security.Claims;
using ApiGateway.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace ApiGateway.Services
{
    public class AccountProvisioningService
    {
        private readonly RoleMappingService _roleMappingService;
        private readonly IConfiguration _configuration;
        private readonly ILogger<AccountProvisioningService> _logger;

        public AccountProvisioningService(RoleMappingService roleMappingService,
                                          IConfiguration configuration,
                                          ILogger<AccountProvisioningService> logger)
        {
            _roleMappingService = roleMappingService;
            _configuration = configuration;
            _logger = logger;
        }

        public Account ProvisionAccount(ClaimsPrincipal principal)
        {
            var nameIdentifier = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            var username = principal.Identity?.Name ?? "unknown";

            var idpRoles = principal.FindAll("idp_roles").Select(c => c.Value);
            var platformRoles = _roleMappingService.MapIdpRoles(idpRoles);

            Account account;
            if (platformRoles.Any())
            {
                // Create account with roles
                account = CreateAccount(nameIdentifier, username, platformRoles);
            }
            else
            {
                // Use default role
                platformRoles = new[] { _configuration["Authorization:DefaultRole"] };
                account = CreateAccount(nameIdentifier, username, platformRoles);
            }

            _logger.LogInformation(
                "Provisioning account for SubjectId: {SubjectId}, Username: {Username}, Roles: {Roles}",
                nameIdentifier, username, string.Join(", ", platformRoles));

            return account;
        }

        private Account CreateAccount(string? subjectId, string username, string[] roles)
        {
            // Create and return a new Account
            return new Account
            {
                SubjectId = subjectId ?? "unknown",
                Username = username,
                Roles = roles,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };
        }
    }
}