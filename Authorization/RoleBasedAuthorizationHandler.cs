using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;
using System.Threading.Tasks;

namespace ApiGateway.Authorization
{
    public class RoleBasedAuthorizationRequirement : IAuthorizationRequirement
    {
        public string Role { get; }

        public RoleBasedAuthorizationRequirement(string role)
        {
            Role = role;
        }
    }

    public class RoleBasedAuthorizationHandler : AuthorizationHandler<RoleBasedAuthorizationRequirement>
    {
        protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, RoleBasedAuthorizationRequirement requirement)
        {
            if (context.User.HasClaim(c => c.Type == ClaimTypes.Role && c.Value.Contains(requirement.Role)))
            {
                context.Succeed(requirement);
            }

            return Task.CompletedTask;
        }
    }
}
