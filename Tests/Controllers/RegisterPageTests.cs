using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace ApiGateway.Tests.Controllers
{
    /// <summary>
    /// Accessibility and UI tests for the Register page (US-001).
    ///
    /// These tests use Microsoft.AspNetCore.Mvc.Testing to spin up an in-process
    /// test server and fetch the rendered HTML of /Register, then assert that:
    ///   1. The page returns HTTP 200.
    ///   2. All three required fields (Name, Email, Password) are present.
    ///   3. Each field has a programmatically associated &lt;label&gt; (for= attribute).
    ///   4. Each field carries an aria-label attribute (screen-reader support).
    ///   5. The fields appear in the correct tab order (tabindex 1 → 2 → 3).
    ///   6. The form element is present in the rendered markup.
    /// </summary>
    public class RegisterPageTests : IClassFixture<WebApplicationFactory<Program>>
    {
        private readonly HttpClient _client;

        public RegisterPageTests(WebApplicationFactory<Program> factory)
        {
            // Configure the test server to use the Development environment so
            // Razor Pages are served correctly.
            _client = factory
                .WithWebHostBuilder(builder =>
                {
                    builder.UseEnvironment("Development");
                })
                .CreateClient(new WebApplicationFactoryClientOptions
                {
                    // Do not follow redirects so we can inspect raw status codes.
                    AllowAutoRedirect = false
                });
        }

        // ------------------------------------------------------------------ //
        // Helper: fetch the /Register page HTML once per test.
        // ------------------------------------------------------------------ //
        private async Task<string> GetRegisterPageHtmlAsync()
        {
            var response = await _client.GetAsync("/Register");

            // The page must be reachable (200 OK).
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);

            return await response.Content.ReadAsStringAsync();
        }

        // ------------------------------------------------------------------ //
        // TC-01: Page renders successfully (HTTP 200).
        // ------------------------------------------------------------------ //
        [Fact]
        public async Task RegisterPage_Returns200Ok()
        {
            var response = await _client.GetAsync("/Register");
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        }

        // ------------------------------------------------------------------ //
        // TC-02: Form element is present in the rendered HTML.
        // ------------------------------------------------------------------ //
        [Fact]
        public async Task RegisterPage_ContainsFormElement()
        {
            var html = await GetRegisterPageHtmlAsync();

            // A <form> element must exist.
            Assert.Contains("<form", html, System.StringComparison.OrdinalIgnoreCase);
        }

        // ------------------------------------------------------------------ //
        // TC-03: All three required input fields are present.
        // ------------------------------------------------------------------ //
        [Fact]
        public async Task RegisterPage_ContainsNameEmailPasswordInputs()
        {
            var html = await GetRegisterPageHtmlAsync();

            // Name field
            Assert.Contains("id=\"Name\"", html, System.StringComparison.OrdinalIgnoreCase);

            // Email field
            Assert.Contains("id=\"Email\"", html, System.StringComparison.OrdinalIgnoreCase);

            // Password field
            Assert.Contains("id=\"Password\"", html, System.StringComparison.OrdinalIgnoreCase);
        }

        // ------------------------------------------------------------------ //
        // TC-04: Each field has a <label> with a matching "for" attribute
        //        (programmatic label association — WCAG 2.1 SC 1.3.1).
        // ------------------------------------------------------------------ //
        [Fact]
        public async Task RegisterPage_FieldsHaveAssociatedLabels()
        {
            var html = await GetRegisterPageHtmlAsync();

            // <label for="Name"> must be present.
            Assert.Matches(new Regex(@"<label\s[^>]*for=""Name""", RegexOptions.IgnoreCase), html);

            // <label for="Email"> must be present.
            Assert.Matches(new Regex(@"<label\s[^>]*for=""Email""", RegexOptions.IgnoreCase), html);

            // <label for="Password"> must be present.
            Assert.Matches(new Regex(@"<label\s[^>]*for=""Password""", RegexOptions.IgnoreCase), html);
        }

        // ------------------------------------------------------------------ //
        // TC-05: Each field carries an aria-label attribute for screen readers
        //        (WCAG 2.1 SC 4.1.2).
        // ------------------------------------------------------------------ //
        [Fact]
        public async Task RegisterPage_FieldsHaveAriaLabels()
        {
            var html = await GetRegisterPageHtmlAsync();

            Assert.Contains("aria-label=\"Name\"", html, System.StringComparison.OrdinalIgnoreCase);
            Assert.Contains("aria-label=\"Email\"", html, System.StringComparison.OrdinalIgnoreCase);
            Assert.Contains("aria-label=\"Password\"", html, System.StringComparison.OrdinalIgnoreCase);
        }

        // ------------------------------------------------------------------ //
        // TC-06: Tab order — Name (tabindex=1) → Email (tabindex=2) →
        //        Password (tabindex=3).
        //
        //        Verifies that the tabindex attributes are present AND that
        //        the Name field appears before Email, which appears before
        //        Password in the document source (natural reading/tab order).
        // ------------------------------------------------------------------ //
        [Fact]
        public async Task RegisterPage_FieldsHaveCorrectTabOrder()
        {
            var html = await GetRegisterPageHtmlAsync();

            // Each field must carry the expected tabindex value.
            Assert.Matches(new Regex(@"id=""Name""[^>]*tabindex=""1""", RegexOptions.IgnoreCase), html);
            Assert.Matches(new Regex(@"id=""Email""[^>]*tabindex=""2""", RegexOptions.IgnoreCase), html);
            Assert.Matches(new Regex(@"id=""Password""[^>]*tabindex=""3""", RegexOptions.IgnoreCase), html);

            // The fields must appear in ascending tab-order in the document.
            int namePos     = html.IndexOf("id=\"Name\"",     System.StringComparison.OrdinalIgnoreCase);
            int emailPos    = html.IndexOf("id=\"Email\"",    System.StringComparison.OrdinalIgnoreCase);
            int passwordPos = html.IndexOf("id=\"Password\"", System.StringComparison.OrdinalIgnoreCase);

            Assert.True(namePos     >= 0, "Name field not found in HTML.");
            Assert.True(emailPos    >= 0, "Email field not found in HTML.");
            Assert.True(passwordPos >= 0, "Password field not found in HTML.");

            Assert.True(namePos < emailPos,
                "Name field must appear before Email field in document order.");
            Assert.True(emailPos < passwordPos,
                "Email field must appear before Password field in document order.");
        }

        // ------------------------------------------------------------------ //
        // TC-07: Password input uses type="password" (not plain text).
        // ------------------------------------------------------------------ //
        [Fact]
        public async Task RegisterPage_PasswordFieldUsesPasswordInputType()
        {
            var html = await GetRegisterPageHtmlAsync();

            // The Password input must be of type="password".
            Assert.Matches(
                new Regex(@"id=""Password""[^>]*type=""password""", RegexOptions.IgnoreCase),
                html);
        }

        // ------------------------------------------------------------------ //
        // TC-08: Email input uses type="email" for semantic correctness.
        // ------------------------------------------------------------------ //
        [Fact]
        public async Task RegisterPage_EmailFieldUsesEmailInputType()
        {
            var html = await GetRegisterPageHtmlAsync();

            Assert.Matches(
                new Regex(@"id=""Email""[^>]*type=""email""", RegexOptions.IgnoreCase),
                html);
        }

        // ------------------------------------------------------------------ //
        // TC-09: Page title contains "Register" for browser tab / screen reader
        //        page identification.
        // ------------------------------------------------------------------ //
        [Fact]
        public async Task RegisterPage_TitleContainsRegister()
        {
            var html = await GetRegisterPageHtmlAsync();

            Assert.Matches(
                new Regex(@"<title>[^<]*Register[^<]*</title>", RegexOptions.IgnoreCase),
                html);
        }
    }
}
