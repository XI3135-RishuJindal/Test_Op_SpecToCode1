```csharp
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using Moq;
using System.Threading.Tasks;
using ApiGateway.Controllers;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using System.Collections.Generic;
using Microsoft.IdentityModel.Tokens;
using System.Security.Claims;

namespace ApiGateway.Tests.Controllers
{
    [TestClass]
    public class AuthControllerTests
    {
        private Mock<IConfiguration> _configMock;
        private Mock<ILogger<AuthController>> _loggerMock;
        private Mock<IHttpContextAccessor> _contextAccessorMock;

        [TestInitialize]
        public void Setup()
        {
            _configMock = new Mock<IConfiguration>();
            _loggerMock = new Mock<ILogger<AuthController>>();
            _contextAccessorMock = new Mock<IHttpContextAccessor>();

            _configMock.Setup(config => config["Jwt:Key"]).Returns("development-secret-key-for-testing-only-256-bits");
            _configMock.Setup(config => config["Jwt:Issuer"]).Returns("TestIssuer");
            _configMock.Setup(config => config["Jwt:Audience"]).Returns("TestAudience");
        }

        [TestMethod]
        public async Task SsoCallback_Returns_Redirect_On_Success()
        {
            _contextAccessorMock.Setup(_ => _.HttpContext.AuthenticateAsync(OpenIdConnectDefaults.AuthenticationScheme))
                .ReturnsAsync(AuthenticateResult.Success(new AuthenticationTicket(
                    new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                    {
                        new Claim(ClaimTypes.Name, "TestUser")
                    }, "mock")),
                    new AuthenticationProperties(),
                    OpenIdConnectDefaults.AuthenticationScheme)));

            var controller = new AuthController(_configMock.Object, _loggerMock.Object)
            {
                ControllerContext = new ControllerContext
                {
                    HttpContext = new DefaultHttpContext
                    {
                        RequestServices = _contextAccessorMock.Object.HttpContext.RequestServices
                    }
                }
            };

            var result = await controller.SsoCallback() as RedirectResult;

            Assert.IsNotNull(result);
            Assert.AreEqual("/products", result.Url);
        }
    }
}
```