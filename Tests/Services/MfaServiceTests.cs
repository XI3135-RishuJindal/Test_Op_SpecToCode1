using System.Net;
using System.Net.Http;
using System.Text.Json;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Moq.Protected;
using Xunit;
using ApiGateway.Services;

namespace ApiGateway.Tests.Services
{
    /// <summary>
    /// Unit tests for <see cref="MfaService"/>.
    /// Each channel (SMS, Email, App) is tested for:
    ///   - Successful delivery (200 OK from provider)
    ///   - Provider error (non-2xx response)
    ///   - Missing configuration
    ///   - Empty / null input guard
    /// </summary>
    public class MfaServiceTests
    {
        // ── Helpers ──────────────────────────────────────────────────────────

        /// <summary>
        /// Builds an <see cref="IConfiguration"/> that contains the minimum MFA
        /// settings required for a given channel.
        /// </summary>
        private static IConfiguration BuildConfig(
            string smsUrl    = "https://sms.example.com/send",
            string smsKey    = "sms-key",
            string emailUrl  = "https://email.example.com/send",
            string emailKey  = "email-key",
            string appUrl    = "https://app.example.com/push",
            string appKey    = "app-key")
        {
            var dict = new Dictionary<string, string?>
            {
                ["Mfa:Sms:ApiUrl"]          = smsUrl,
                ["Mfa:Sms:ApiKey"]          = smsKey,
                ["Mfa:Sms:SenderNumber"]    = "+10000000000",
                ["Mfa:Email:ApiUrl"]        = emailUrl,
                ["Mfa:Email:ApiKey"]        = emailKey,
                ["Mfa:Email:SenderAddress"] = "noreply@example.com",
                ["Mfa:App:ApiUrl"]          = appUrl,
                ["Mfa:App:ApiKey"]          = appKey,
            };
            return new ConfigurationBuilder().AddInMemoryCollection(dict).Build();
        }

        /// <summary>
        /// Creates an <see cref="IHttpClientFactory"/> whose named client returns
        /// the supplied <paramref name="response"/> for every request.
        /// </summary>
        private static IHttpClientFactory BuildFactory(
            string clientName,
            HttpResponseMessage response)
        {
            var handlerMock = new Mock<HttpMessageHandler>();
            handlerMock
                .Protected()
                .Setup<Task<HttpResponseMessage>>(
                    "SendAsync",
                    ItExpr.IsAny<HttpRequestMessage>(),
                    ItExpr.IsAny<CancellationToken>())
                .ReturnsAsync(response);

            var client = new HttpClient(handlerMock.Object);

            var factoryMock = new Mock<IHttpClientFactory>();
            factoryMock
                .Setup(f => f.CreateClient(clientName))
                .Returns(client);

            return factoryMock.Object;
        }

        private static HttpResponseMessage OkResponse(string? referenceId = "ref-123")
        {
            var body = referenceId is not null
                ? JsonSerializer.Serialize(new { sid = referenceId })
                : "{}";
            return new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(body, System.Text.Encoding.UTF8, "application/json")
            };
        }

        private static HttpResponseMessage ErrorResponse(HttpStatusCode code = HttpStatusCode.BadGateway) =>
            new(code) { Content = new StringContent("provider error") };

        // ── SMS tests ─────────────────────────────────────────────────────────

        [Fact]
        public async Task SendViaSmsAsync_ReturnsSuccess_WhenProviderResponds200()
        {
            var factory = BuildFactory("MfaSmsClient", OkResponse());
            var svc     = new MfaService(factory, BuildConfig(), NullLogger<MfaService>.Instance);

            var result = await svc.SendViaSmsAsync("+447700900000", "123456");

            Assert.True(result.Success);
            Assert.Equal("ref-123", result.ProviderReferenceId);
        }

        [Fact]
        public async Task SendViaSmsAsync_ReturnsFail_WhenProviderReturnsError()
        {
            var factory = BuildFactory("MfaSmsClient", ErrorResponse());
            var svc     = new MfaService(factory, BuildConfig(), NullLogger<MfaService>.Instance);

            var result = await svc.SendViaSmsAsync("+447700900000", "123456");

            Assert.False(result.Success);
            Assert.Contains("502", result.Message);
        }

        [Fact]
        public async Task SendViaSmsAsync_ReturnsFail_WhenConfigMissing()
        {
            var emptyConfig = new ConfigurationBuilder().Build();
            // Factory won't be called — pass a dummy
            var factory = new Mock<IHttpClientFactory>().Object;
            var svc     = new MfaService(factory, emptyConfig, NullLogger<MfaService>.Instance);

            var result = await svc.SendViaSmsAsync("+447700900000", "123456");

            Assert.False(result.Success);
            Assert.Contains("not configured", result.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Theory]
        [InlineData("", "123456")]
        [InlineData("+447700900000", "")]
        public async Task SendViaSmsAsync_ReturnsFail_WhenInputEmpty(string phone, string code)
        {
            var factory = new Mock<IHttpClientFactory>().Object;
            var svc     = new MfaService(factory, BuildConfig(), NullLogger<MfaService>.Instance);

            var result = await svc.SendViaSmsAsync(phone, code);

            Assert.False(result.Success);
        }

        // ── Email tests ───────────────────────────────────────────────────────

        [Fact]
        public async Task SendViaEmailAsync_ReturnsSuccess_WhenProviderResponds200()
        {
            var factory = BuildFactory("MfaEmailClient", OkResponse());
            var svc     = new MfaService(factory, BuildConfig(), NullLogger<MfaService>.Instance);

            var result = await svc.SendViaEmailAsync("user@example.com", "654321");

            Assert.True(result.Success);
        }

        [Fact]
        public async Task SendViaEmailAsync_ReturnsFail_WhenProviderReturnsError()
        {
            var factory = BuildFactory("MfaEmailClient", ErrorResponse(HttpStatusCode.ServiceUnavailable));
            var svc     = new MfaService(factory, BuildConfig(), NullLogger<MfaService>.Instance);

            var result = await svc.SendViaEmailAsync("user@example.com", "654321");

            Assert.False(result.Success);
            Assert.Contains("503", result.Message);
        }

        [Fact]
        public async Task SendViaEmailAsync_ReturnsFail_WhenConfigMissing()
        {
            var emptyConfig = new ConfigurationBuilder().Build();
            var factory     = new Mock<IHttpClientFactory>().Object;
            var svc         = new MfaService(factory, emptyConfig, NullLogger<MfaService>.Instance);

            var result = await svc.SendViaEmailAsync("user@example.com", "654321");

            Assert.False(result.Success);
            Assert.Contains("not configured", result.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Theory]
        [InlineData("", "654321")]
        [InlineData("user@example.com", "")]
        public async Task SendViaEmailAsync_ReturnsFail_WhenInputEmpty(string email, string code)
        {
            var factory = new Mock<IHttpClientFactory>().Object;
            var svc     = new MfaService(factory, BuildConfig(), NullLogger<MfaService>.Instance);

            var result = await svc.SendViaEmailAsync(email, code);

            Assert.False(result.Success);
        }

        // ── App tests ─────────────────────────────────────────────────────────

        [Fact]
        public async Task SendViaAppAsync_ReturnsSuccess_WhenProviderResponds200()
        {
            var factory = BuildFactory("MfaAppClient", OkResponse("push-ref-456"));
            var svc     = new MfaService(factory, BuildConfig(), NullLogger<MfaService>.Instance);

            var result = await svc.SendViaAppAsync("user-id-001", "789012");

            Assert.True(result.Success);
            Assert.Equal("push-ref-456", result.ProviderReferenceId);
        }

        [Fact]
        public async Task SendViaAppAsync_ReturnsFail_WhenProviderReturnsError()
        {
            var factory = BuildFactory("MfaAppClient", ErrorResponse(HttpStatusCode.Unauthorized));
            var svc     = new MfaService(factory, BuildConfig(), NullLogger<MfaService>.Instance);

            var result = await svc.SendViaAppAsync("user-id-001", "789012");

            Assert.False(result.Success);
            Assert.Contains("401", result.Message);
        }

        [Fact]
        public async Task SendViaAppAsync_ReturnsFail_WhenConfigMissing()
        {
            var emptyConfig = new ConfigurationBuilder().Build();
            var factory     = new Mock<IHttpClientFactory>().Object;
            var svc         = new MfaService(factory, emptyConfig, NullLogger<MfaService>.Instance);

            var result = await svc.SendViaAppAsync("user-id-001", "789012");

            Assert.False(result.Success);
            Assert.Contains("not configured", result.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Theory]
        [InlineData("", "789012")]
        [InlineData("user-id-001", "")]
        public async Task SendViaAppAsync_ReturnsFail_WhenInputEmpty(string userId, string code)
        {
            var factory = new Mock<IHttpClientFactory>().Object;
            var svc     = new MfaService(factory, BuildConfig(), NullLogger<MfaService>.Instance);

            var result = await svc.SendViaAppAsync(userId, code);

            Assert.False(result.Success);
        }
    }
}
