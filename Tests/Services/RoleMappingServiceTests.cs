```csharp
using ApiGateway.Services;
using Xunit;

namespace ApiGateway.Tests.Services
{
    public class RoleMappingServiceTests
    {
        private readonly RoleMappingService _roleMappingService;

        public RoleMappingServiceTests()
        {
            _roleMappingService = new RoleMappingService();
        }

        [Fact]
        public void ExtractRolesFromToken_ValidJwtToken_ReturnsRoles()
        {
            // Arrange
            var token = CreateJwtTokenWithRoles(new[] { "IdP_Customer", "IdP_Admin" });

            // Act
            var roles = _roleMappingService.ExtractRolesFromToken(token);

            // Assert
            Assert.Contains("IdP_Customer", roles);
            Assert.Contains("IdP_Admin", roles);
        }

        [Theory]
        [InlineData("IdP_Customer", RoleMappingService.CustomerRole)]
        [InlineData("IdP_Admin", RoleMappingService.AdministratorRole)]
        public void MapRole_ValidIdentityProviderRole_ReturnsMappedRole(string inputRole, string expectedMappedRole)
        {
            // Act
            var mappedRole = _roleMappingService.MapRole(inputRole);

            // Assert
            Assert.Equal(expectedMappedRole, mappedRole);
        }

        [Fact]
        public void ValidateUserRole_RoleMatches_ReturnsTrue()
        {
            // Arrange
            var userRoles = new[] { RoleMappingService.CustomerRole, RoleMappingService.AdministratorRole };
            var requiredRole = RoleMappingService.CustomerRole;

            // Act
            var isValid = _roleMappingService.ValidateUserRole(userRoles, requiredRole);

            // Assert
            Assert.True(isValid);
        }

        private string CreateJwtTokenWithRoles(string[] roles)
        {
            // Helper method to create a JWT token with roles for testing
            var claims = roles.Select(role => new Claim(ClaimTypes.Role, role)).ToArray();
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.UTF8.GetBytes("default-secret-key-for-development");
            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(claims),
                Expires = DateTime.UtcNow.AddMinutes(5),
                SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
            };
            var token = tokenHandler.CreateToken(tokenDescriptor);
            return tokenHandler.WriteToken(token);
        }
    }
}
```