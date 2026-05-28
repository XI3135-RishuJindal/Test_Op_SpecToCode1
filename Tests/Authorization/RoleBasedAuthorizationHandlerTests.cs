using Microsoft.AspNetCore.Authorization;
using Moq;
using System.Security.Claims;
using System.Threading.Tasks;
using Xunit;
using ApiGateway.Authorization;

namespace ApiGateway.Tests.Authorization
{
    public class RoleBasedAuthorizationHandlerTests
    {
        [Fact]
        public async Task HandleRequirementAsync_ShouldSucceed_WhenUserHasRequiredRole()
        {
            // Arrange
            var requirement = new RoleBasedAuthorizationRequirement("Administrator");
            var roleClaim = new Claim(ClaimTypes.Role, "Administrator");
            var user = new ClaimsPrincipal(new ClaimsIdentity(new[] { roleClaim }));
            var context = new AuthorizationHandlerContext(new[] { requirement }, user, null);

            var handler = new RoleBasedAuthorizationHandler();

            // Act
            await handler.HandleAsync(context);

            // Assert
            Assert.True(context.HasSucceeded);
        }

        [Fact]
        public async Task HandleRequirementAsync_ShouldFail_WhenUserDoesNotHaveRequiredRole()
        {
            // Arrange
            var requirement = new RoleBasedAuthorizationRequirement("Administrator");
            var roleClaim = new Claim(ClaimTypes.Role, "User");
            var user = new ClaimsPrincipal(new ClaimsIdentity(new[] { roleClaim }));
            var context = new AuthorizationHandlerContext(new[] { requirement }, user, null);

            var handler = new RoleBasedAuthorizationHandler();

            // Act
            await handler.HandleAsync(context);

            // Assert
            Assert.False(context.HasSucceeded);
        }
    }
}
