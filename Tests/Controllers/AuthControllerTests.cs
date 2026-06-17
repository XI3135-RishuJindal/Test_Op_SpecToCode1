```csharp
using Xunit;
using Moq;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using ApiGateway.Controllers;
using ApiGateway.Models;
using Microsoft.AspNetCore.Mvc;

namespace ApiGateway.Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly Mock<IConfiguration> _mockConfiguration;
        private readonly Mock<ILogger<AuthController>> _mockLogger;
        private readonly AuthController _authController;

        public AuthControllerTests()
        {
            _mockConfiguration = new Mock<IConfiguration>();
            _mockLogger = new Mock<ILogger<AuthController>>();
            _authController = new AuthController(_mockConfiguration.Object, _mockLogger.Object);
        }

        [Theory]
        [InlineData("1234567890", true)]
        [InlineData("123-456-7890", false)]
        [InlineData("+11234567890", true)]
        [InlineData("+1 (123) 456-7890", false)]
        [InlineData("", false)]
        [InlineData(null, false)]
        public void ValidatePhoneNumberFormat_ShouldWorkCorrectly(string phoneNumber, bool expectedIsValid)
        {
            // Assume a hypothetical method in AuthController that validates phone number format
            var result = _authController.ValidatePhoneNumberFormat(phoneNumber);

            Assert.Equal(expectedIsValid, result);
        }

        [Fact]
        public void DispatchSms_ShouldOnlyDispatchWhenPhoneNumberIsValid()
        {
            // Hypothetical method to simulate SMS dispatch
            var validPhoneNumber = "+11234567890";
            var invalidPhoneNumber = "123-456-7890";

            var validResult = _authController.DispatchSms(validPhoneNumber);
            var invalidResult = _authController.DispatchSms(invalidPhoneNumber);

            Assert.True(validResult);
            Assert.False(invalidResult);
        }

        [Fact]
        public void Registration_WithInvalidPhoneNumber_ShouldReturnBadRequest()
        {
            var invalidRequest = new PhoneRegistrationRequest { PhoneNumber = "invalid-phone" };

            var result = _authController.RegisterPhoneNumber(invalidRequest) as BadRequestObjectResult;

            Assert.NotNull(result);
            Assert.Equal(400, result.StatusCode);
        }

        [Fact]
        public void Registration_WithValidPhoneNumber_ShouldDispatchSmsAndReturnOk()
        {
            var validRequest = new PhoneRegistrationRequest { PhoneNumber = "+11234567890" };

            var result = _authController.RegisterPhoneNumber(validRequest) as OkResult;

            Assert.NotNull(result);
            Assert.Equal(200, result.StatusCode);
        }
    }
}
```

Note: In this code, `ValidatePhoneNumberFormat`, `DispatchSms`, and `RegisterPhoneNumber` methods are hypothetical and should exist in the `AuthController` class for the tests to work. Modify the tests accordingly once those methods are implemented in the `AuthController`.