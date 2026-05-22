using System.Security.Claims;
using System.Collections.Generic;

namespace ApiGateway.Tests
{
    public static class TestClaimsPrincipalProvider
    {
        public static ClaimsPrincipal GetPrincipalWithSubClaim()
        {
            return new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(JwtRegisteredClaimNames.Sub, "existing-sub")
            }, "TestAuthentication"));
        }
    }
}
