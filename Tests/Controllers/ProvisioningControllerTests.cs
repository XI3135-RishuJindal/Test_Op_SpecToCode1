using ApiGateway.Controllers;
using ApiGateway.Interfaces;
using ApiGateway.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using System.Threading;
using System.Threading.Tasks;
using Xunit;

namespace ApiGateway.Tests.Controllers
{
    public class ProvisioningControllerTests
    {
        private readonly Mock<IJitProvisioningService> _mockService;

        public ProvisioningControllerTests()
        {
            _mockService = new Mock<IJitProvisioningService>();
        }

        [Fact]
        public async Task JitProvisioning_ReturnsOkIfAccountExists()
        {
            // Arrange
            var controller = new ProvisioningController(_mockService.Object)
            {
                ControllerContext = new ControllerContext
                {
                    HttpContext = new DefaultHttpContext { User = TestClaimsPrincipalProvider.GetPrincipalWithSubClaim() }
                }
            };

            var account = new AccountDTO { Sub = "existing-sub", Username = "Existing User" };
            _mockService.Setup(s => s.ProvisionAsync(It.IsAny<string>(), It.IsAny<ProvisioningRequest>(), CancellationToken.None))
                .ReturnsAsync(new ProvisioningResponse { Account = account, Created = false });

            // Act
            var result = await controller.JitProvisioning(new ProvisioningRequest());

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var response = Assert.IsType<ProvisioningResponse>(okResult.Value);
            Assert.Equal(account.Sub, response.Account.Sub);
            Assert.False(response.Created);
        }

        // Additional test cases: Account creation, 404 on GET, etc.
    }
}