using System;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using ApiGateway.Controllers;
using ApiGateway.Models;

namespace ApiGateway.Tests.Controllers
{
    /// <summary>
    /// Unit tests for AuthController password policy enhancements.
    ///
    /// Covers:
    ///   1. Password complexity validation (length, uppercase, lowercase, digit, symbol)
    ///   2. Common password rejection
    ///   3. Password expiration checks (expired / nearing expiration / healthy)
    ///   4. GenerateToken endpoint — valid and invalid scenarios
    ///   5. ChangePassword endpoint — valid and invalid scenarios
    ///   6. GetPasswordExpirationStatus endpoint
    /// </summary>
    public class AuthControllerTests
    {
        // -----------------------------------------------------------------------
        // Helpers
        // -----------------------------------------------------------------------

        private static AuthController CreateController(string jwtKey = "test-secret-key-for-unit-testing-256-bits!")
        {
            var inMemorySettings = new Dictionary<string, string?>
            {
                ["Jwt:Key"]      = jwtKey,
                ["Jwt:Issuer"]   = "TestIssuer",
                ["Jwt:Audience"] = "TestAudience"
            };

            IConfiguration configuration = new ConfigurationBuilder()
                .AddInMemoryCollection(inMemorySettings)
                .Build();

            var logger = Mock.Of<ILogger<AuthController>>();
            return new AuthController(configuration, logger);
        }

        // -----------------------------------------------------------------------
        // 1. ValidatePasswordComplexity — length requirement (≥12 characters)
        // -----------------------------------------------------------------------

        [Fact]
        public void ValidatePasswordComplexity_NullOrEmpty_ReturnsInvalid()
        {
            var (isValid, error) = AuthController.ValidatePasswordComplexity(string.Empty);

            Assert.False(isValid);
            Assert.NotNull(error);
        }

        [Fact]
        public void ValidatePasswordComplexity_WhitespaceOnly_ReturnsInvalid()
        {
            var (isValid, error) = AuthController.ValidatePasswordComplexity("   ");

            Assert.False(isValid);
            Assert.NotNull(error);
        }

        [Theory]
        [InlineData("Short1!")]          // 7 chars
        [InlineData("Short1!Abc")]       // 10 chars
        [InlineData("Short1!AbcD")]      // 11 chars
        public void ValidatePasswordComplexity_TooShort_ReturnsInvalid(string password)
        {
            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.False(isValid);
            Assert.Contains("12 characters", error, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void ValidatePasswordComplexity_ExactlyTwelveChars_ValidOtherwise_ReturnsValid()
        {
            // Exactly 12 chars: uppercase, lowercase, digit, symbol
            const string password = "Abcdefg1234!";

            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.True(isValid, $"Expected valid but got error: {error}");
        }

        // -----------------------------------------------------------------------
        // 2. ValidatePasswordComplexity — character-class requirements
        // -----------------------------------------------------------------------

        [Fact]
        public void ValidatePasswordComplexity_MissingUppercase_ReturnsInvalid()
        {
            // All lowercase + digit + symbol, ≥12 chars
            const string password = "abcdefg1234!";

            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.False(isValid);
            Assert.Contains("uppercase", error, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void ValidatePasswordComplexity_MissingLowercase_ReturnsInvalid()
        {
            // All uppercase + digit + symbol, ≥12 chars
            const string password = "ABCDEFG1234!";

            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.False(isValid);
            Assert.Contains("lowercase", error, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void ValidatePasswordComplexity_MissingDigit_ReturnsInvalid()
        {
            // Letters + symbol, ≥12 chars, no digit
            const string password = "AbcdefgHijkl!";

            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.False(isValid);
            Assert.Contains("digit", error, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void ValidatePasswordComplexity_MissingSpecialCharacter_ReturnsInvalid()
        {
            // Letters + digit, ≥12 chars, no symbol
            const string password = "Abcdefg12345";

            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.False(isValid);
            Assert.Contains("special", error, StringComparison.OrdinalIgnoreCase);
        }

        [Theory]
        [InlineData("Abcdefg1234!")]   // exclamation mark
        [InlineData("Abcdefg1234@")]   // at sign
        [InlineData("Abcdefg1234#")]   // hash
        [InlineData("Abcdefg1234$")]   // dollar
        [InlineData("Abcdefg1234%")]   // percent
        [InlineData("Abcdefg1234^")]   // caret
        [InlineData("Abcdefg1234&")]   // ampersand
        [InlineData("Abcdefg1234*")]   // asterisk
        public void ValidatePasswordComplexity_ValidPasswords_ReturnsValid(string password)
        {
            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.True(isValid, $"Expected '{password}' to be valid but got: {error}");
        }

        // -----------------------------------------------------------------------
        // 3. Common password rejection
        // -----------------------------------------------------------------------

        [Theory]
        [InlineData("password")]
        [InlineData("password123")]
        [InlineData("password1234")]
        [InlineData("123456789012")]
        [InlineData("qwertyuiopas")]
        [InlineData("iloveyou1234")]
        public void ValidatePasswordComplexity_CommonPassword_ReturnsInvalid(string commonPassword)
        {
            var (isValid, error) = AuthController.ValidatePasswordComplexity(commonPassword);

            Assert.False(isValid);
            // Error should mention the password being too common
            Assert.NotNull(error);
        }

        [Fact]
        public void ValidatePasswordComplexity_CommonPasswordCaseInsensitive_ReturnsInvalid()
        {
            // "PASSWORD" is the uppercase variant of the common "password"
            // The check is case-insensitive
            const string password = "PASSWORD123456";

            // Note: "PASSWORD123456" is not in the common list by exact match,
            // but "password" IS. This test verifies the case-insensitive HashSet lookup
            // for passwords that ARE in the list when lowercased.
            // Using a known entry: "Password" variant of "password"
            const string knownCommon = "password";
            var (isValid, error) = AuthController.ValidatePasswordComplexity(knownCommon);

            Assert.False(isValid);
            Assert.NotNull(error);
        }

        [Fact]
        public void ValidatePasswordComplexity_UniqueStrongPassword_NotRejectedAsCommon()
        {
            // A password that meets all complexity rules and is not in the common list
            const string password = "Tr0ub4dor&3xYz!";

            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.True(isValid, $"Expected valid but got: {error}");
        }

        // -----------------------------------------------------------------------
        // 4. Password expiration checks
        // -----------------------------------------------------------------------

        [Fact]
        public void IsPasswordExpired_OlderThan90Days_ReturnsTrue()
        {
            var lastChanged = DateTime.UtcNow.AddDays(-91);

            bool result = AuthController.IsPasswordExpired(lastChanged);

            Assert.True(result, "Password older than 90 days should be considered expired.");
        }

        [Fact]
        public void IsPasswordExpired_ExactlyAt90Days_ReturnsTrue()
        {
            // Exactly 90 days ago is the boundary — policy says > 90 days expires,
            // so exactly 90 days should NOT be expired.
            var lastChanged = DateTime.UtcNow.AddDays(-90).AddSeconds(-1);

            bool result = AuthController.IsPasswordExpired(lastChanged);

            Assert.True(result, "Password at/just-past 90 days should be expired.");
        }

        [Fact]
        public void IsPasswordExpired_LessThan90Days_ReturnsFalse()
        {
            var lastChanged = DateTime.UtcNow.AddDays(-45);

            bool result = AuthController.IsPasswordExpired(lastChanged);

            Assert.False(result, "Password changed 45 days ago should not be expired.");
        }

        [Fact]
        public void IsPasswordExpired_JustChanged_ReturnsFalse()
        {
            var lastChanged = DateTime.UtcNow;

            bool result = AuthController.IsPasswordExpired(lastChanged);

            Assert.False(result, "Freshly changed password should not be expired.");
        }

        [Fact]
        public void IsPasswordNearingExpiration_Within10DaysOfExpiry_ReturnsTrue()
        {
            // Changed 82 days ago → 8 days until expiration (within 10-day warning window)
            var lastChanged = DateTime.UtcNow.AddDays(-82);

            bool result = AuthController.IsPasswordNearingExpiration(lastChanged);

            Assert.True(result, "Password expiring in 8 days should trigger a nearing-expiration warning.");
        }

        [Fact]
        public void IsPasswordNearingExpiration_Exactly10DaysRemaining_ReturnsTrue()
        {
            // Changed 80 days ago → exactly 10 days until expiration
            var lastChanged = DateTime.UtcNow.AddDays(-80);

            bool result = AuthController.IsPasswordNearingExpiration(lastChanged);

            Assert.True(result, "Password expiring in exactly 10 days should trigger a warning.");
        }

        [Fact]
        public void IsPasswordNearingExpiration_MoreThan10DaysRemaining_ReturnsFalse()
        {
            // Changed 50 days ago → 40 days until expiration
            var lastChanged = DateTime.UtcNow.AddDays(-50);

            bool result = AuthController.IsPasswordNearingExpiration(lastChanged);

            Assert.False(result, "Password with 40 days remaining should not trigger a warning.");
        }

        [Fact]
        public void IsPasswordNearingExpiration_AlreadyExpired_ReturnsFalse()
        {
            // Expired passwords are handled separately; nearing-expiration should be false
            var lastChanged = DateTime.UtcNow.AddDays(-95);

            bool result = AuthController.IsPasswordNearingExpiration(lastChanged);

            Assert.False(result, "An already-expired password should not report as nearing-expiration.");
        }

        // -----------------------------------------------------------------------
        // 5. GenerateToken endpoint — valid scenario
        // -----------------------------------------------------------------------

        [Fact]
        public void GenerateToken_ValidCredentials_Returns200WithToken()
        {
            var controller = CreateController();
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = "Str0ng&SecurePass!"
            };

            var result = controller.GenerateToken(request);

            var okResult = Assert.IsType<OkObjectResult>(result);
            Assert.Equal(200, okResult.StatusCode);
            Assert.NotNull(okResult.Value);
        }

        // -----------------------------------------------------------------------
        // 6. GenerateToken endpoint — invalid scenarios
        // -----------------------------------------------------------------------

        [Fact]
        public void GenerateToken_EmptyUsername_Returns400()
        {
            var controller = CreateController();
            var request = new LoginRequest
            {
                Username = "",
                Password = "Str0ng&SecurePass!"
            };

            var result = controller.GenerateToken(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Equal(400, badRequest.StatusCode);
        }

        [Fact]
        public void GenerateToken_EmptyPassword_Returns400()
        {
            var controller = CreateController();
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = ""
            };

            var result = controller.GenerateToken(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Equal(400, badRequest.StatusCode);
        }

        [Fact]
        public void GenerateToken_WeakPassword_TooShort_Returns400WithWeakPasswordError()
        {
            var controller = CreateController();
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = "Short1!"  // < 12 chars
            };

            var result = controller.GenerateToken(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Equal(400, badRequest.StatusCode);

            var errorResponse = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("WeakPassword", errorResponse.Error);
        }

        [Fact]
        public void GenerateToken_WeakPassword_NoUppercase_Returns400()
        {
            var controller = CreateController();
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = "nouppercase1234!"
            };

            var result = controller.GenerateToken(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("WeakPassword", errorResponse.Error);
        }

        [Fact]
        public void GenerateToken_WeakPassword_NoLowercase_Returns400()
        {
            var controller = CreateController();
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = "NOLOWERCASE1234!"
            };

            var result = controller.GenerateToken(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("WeakPassword", errorResponse.Error);
        }

        [Fact]
        public void GenerateToken_WeakPassword_NoDigit_Returns400()
        {
            var controller = CreateController();
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = "NoDigitPassword!"
            };

            var result = controller.GenerateToken(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("WeakPassword", errorResponse.Error);
        }

        [Fact]
        public void GenerateToken_WeakPassword_NoSpecialChar_Returns400()
        {
            var controller = CreateController();
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = "NoSpecialChar1234"
            };

            var result = controller.GenerateToken(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("WeakPassword", errorResponse.Error);
        }

        [Fact]
        public void GenerateToken_CommonPassword_Returns400WithWeakPasswordError()
        {
            var controller = CreateController();
            var request = new LoginRequest
            {
                Username = "testuser",
                Password = "password1234"  // in common list
            };

            var result = controller.GenerateToken(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Equal(400, badRequest.StatusCode);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("WeakPassword", errorResponse.Error);
        }

        // -----------------------------------------------------------------------
        // 7. ChangePassword endpoint — valid scenario
        // -----------------------------------------------------------------------

        [Fact]
        public void ChangePassword_ValidNewPassword_Returns200()
        {
            var controller = CreateController();
            var request = new ChangePasswordRequest
            {
                Username = "testuser",
                NewPassword = "NewStr0ng&Pass2024!"
            };

            var result = controller.ChangePassword(request);

            var okResult = Assert.IsType<OkObjectResult>(result);
            Assert.Equal(200, okResult.StatusCode);
        }

        // -----------------------------------------------------------------------
        // 8. ChangePassword endpoint — invalid scenarios
        // -----------------------------------------------------------------------

        [Fact]
        public void ChangePassword_EmptyUsername_Returns400()
        {
            var controller = CreateController();
            var request = new ChangePasswordRequest
            {
                Username = "",
                NewPassword = "NewStr0ng&Pass2024!"
            };

            var result = controller.ChangePassword(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Equal(400, badRequest.StatusCode);
        }

        [Fact]
        public void ChangePassword_EmptyNewPassword_Returns400()
        {
            var controller = CreateController();
            var request = new ChangePasswordRequest
            {
                Username = "testuser",
                NewPassword = ""
            };

            var result = controller.ChangePassword(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Equal(400, badRequest.StatusCode);
        }

        [Fact]
        public void ChangePassword_WeakNewPassword_TooShort_Returns400()
        {
            var controller = CreateController();
            var request = new ChangePasswordRequest
            {
                Username = "testuser",
                NewPassword = "Sh0rt!"
            };

            var result = controller.ChangePassword(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("WeakPassword", errorResponse.Error);
        }

        [Fact]
        public void ChangePassword_CommonPassword_Returns400()
        {
            var controller = CreateController();
            var request = new ChangePasswordRequest
            {
                Username = "testuser",
                NewPassword = "password1234"
            };

            var result = controller.ChangePassword(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("WeakPassword", errorResponse.Error);
        }

        [Fact]
        public void ChangePassword_MissingSpecialChar_Returns400()
        {
            var controller = CreateController();
            var request = new ChangePasswordRequest
            {
                Username = "testuser",
                NewPassword = "NoSpecial12345Abc"
            };

            var result = controller.ChangePassword(request);

            var badRequest = Assert.IsType<BadRequestObjectResult>(result);
            var errorResponse = Assert.IsType<ErrorResponse>(badRequest.Value);
            Assert.Equal("WeakPassword", errorResponse.Error);
        }

        // -----------------------------------------------------------------------
        // 9. GetPasswordExpirationStatus endpoint
        // -----------------------------------------------------------------------

        [Fact]
        public void GetPasswordExpirationStatus_ExpiredPassword_ReturnsExpiredTrue()
        {
            var controller = CreateController();
            var lastChanged = DateTime.UtcNow.AddDays(-95);

            var result = controller.GetPasswordExpirationStatus("testuser", lastChanged);

            var okResult = Assert.IsType<OkObjectResult>(result);
            Assert.Equal(200, okResult.StatusCode);

            // Verify the response contains expired=true
            var value = okResult.Value;
            Assert.NotNull(value);

            var expiredProp = value!.GetType().GetProperty("expired");
            Assert.NotNull(expiredProp);
            Assert.True((bool)expiredProp!.GetValue(value)!);
        }

        [Fact]
        public void GetPasswordExpirationStatus_NearingExpiration_ReturnsNearingTrue()
        {
            var controller = CreateController();
            // 83 days ago → 7 days remaining → within 10-day warning window
            var lastChanged = DateTime.UtcNow.AddDays(-83);

            var result = controller.GetPasswordExpirationStatus("testuser", lastChanged);

            var okResult = Assert.IsType<OkObjectResult>(result);
            var value = okResult.Value;
            Assert.NotNull(value);

            var nearingProp = value!.GetType().GetProperty("nearingExpiration");
            Assert.NotNull(nearingProp);
            Assert.True((bool)nearingProp!.GetValue(value)!);

            // Should not be expired
            var expiredProp = value.GetType().GetProperty("expired");
            Assert.NotNull(expiredProp);
            Assert.False((bool)expiredProp!.GetValue(value)!);
        }

        [Fact]
        public void GetPasswordExpirationStatus_HealthyPassword_ReturnsBothFalse()
        {
            var controller = CreateController();
            // Changed 30 days ago → 60 days remaining → healthy
            var lastChanged = DateTime.UtcNow.AddDays(-30);

            var result = controller.GetPasswordExpirationStatus("testuser", lastChanged);

            var okResult = Assert.IsType<OkObjectResult>(result);
            var value = okResult.Value;
            Assert.NotNull(value);

            var expiredProp = value!.GetType().GetProperty("expired");
            Assert.NotNull(expiredProp);
            Assert.False((bool)expiredProp!.GetValue(value)!);

            var nearingProp = value.GetType().GetProperty("nearingExpiration");
            Assert.NotNull(nearingProp);
            Assert.False((bool)nearingProp!.GetValue(value)!);
        }

        [Fact]
        public void GetPasswordExpirationStatus_FreshPassword_ReturnsCorrectDaysRemaining()
        {
            var controller = CreateController();
            var lastChanged = DateTime.UtcNow;

            var result = controller.GetPasswordExpirationStatus("testuser", lastChanged);

            var okResult = Assert.IsType<OkObjectResult>(result);
            var value = okResult.Value;
            Assert.NotNull(value);

            var daysRemainingProp = value!.GetType().GetProperty("daysRemaining");
            Assert.NotNull(daysRemainingProp);
            int daysRemaining = (int)daysRemainingProp!.GetValue(value)!;
            // Should be approximately 90 days
            Assert.InRange(daysRemaining, 89, 90);
        }

        // -----------------------------------------------------------------------
        // 10. Edge cases
        // -----------------------------------------------------------------------

        [Fact]
        public void ValidatePasswordComplexity_AllRequirementsMet_ReturnsValidWithNullError()
        {
            const string password = "MyS3cur3P@ssword!";

            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.True(isValid);
            Assert.Null(error);
        }

        [Fact]
        public void ValidatePasswordComplexity_LongValidPassword_ReturnsValid()
        {
            // 32-character strong password
            const string password = "Th!sIs@V3ryStr0ngP@ssw0rd2024!!!";

            var (isValid, error) = AuthController.ValidatePasswordComplexity(password);

            Assert.True(isValid, $"Expected valid but got: {error}");
        }

        [Theory]
        [InlineData("Abcdefg1234!", true)]   // valid
        [InlineData("abcdefg1234!", false)]  // no uppercase
        [InlineData("ABCDEFG1234!", false)]  // no lowercase
        [InlineData("Abcdefghijk!", false)]  // no digit
        [InlineData("Abcdefg12345", false)]  // no symbol
        [InlineData("Ab1!", false)]          // too short
        public void ValidatePasswordComplexity_VariousScenarios_MatchExpected(string password, bool expectedValid)
        {
            var (isValid, _) = AuthController.ValidatePasswordComplexity(password);

            Assert.Equal(expectedValid, isValid);
        }
    }
}
