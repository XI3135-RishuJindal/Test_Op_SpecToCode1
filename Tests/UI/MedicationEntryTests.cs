using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Xunit;
using Microsoft.Playwright;
using System.Text.RegularExpressions;

namespace Tests.UI
{
    /// <summary>
    /// Automated UI tests for Medication Entry form responsiveness and accessibility.
    /// Requires Playwright (see README for setup instructions).
    /// </summary>
    public class MedicationEntryTests : IAsyncLifetime
    {
        private IPlaywright _playwright = null!;
        private IBrowser _browser = null!;
        private readonly List<ViewportSize> _breakpoints = new()
        {
            // Common mobile, tablet, desktop breakpoints
            new ViewportSize { Width = 375, Height = 667 },    // iPhone 8
            new ViewportSize { Width = 768, Height = 1024 },   // iPad portrait
            new ViewportSize { Width = 1280, Height = 800 }    // Desktop
        };

        private readonly Dictionary<string, string> _expectedLabels = new()
        {
            { "medication-name", "Medication Name" },
            { "dosage", "Dosage" },
            { "frequency", "Frequency" },
            { "route", "Route" }
        };

        // Define selector info used for ARIA, roles, etc.
        private readonly Dictionary<string, string> _fieldInputSelectors = new()
        {
            { "medication-name", "input[name='MedicationName']" },
            { "dosage", "input[name='Dosage']" },
            { "frequency", "input[name='Frequency']" },
            { "route", "input[name='Route']" }
        };

        private readonly string _formUrl = "http://localhost:5000/Medications/MedicationEntry";

        public async Task InitializeAsync()
        {
            _playwright = await Playwright.CreateAsync();
            _browser = await _playwright.Chromium.LaunchAsync(new BrowserTypeLaunchOptions
            {
                Headless = true,
            });
        }

        public async Task DisposeAsync()
        {
            await _browser.CloseAsync();
            _playwright.Dispose();
        }

        [Fact(DisplayName = "All medication entry fields render with correct labels and required marker")]
        public async Task MedicationFields_RenderCorrectly_WithLabels()
        {
            var context = await _browser.NewContextAsync();
            var page = await context.NewPageAsync();
            await page.GotoAsync(_formUrl);

            foreach (var pair in _expectedLabels)
            {
                var labelSelector = $"label[for='{pair.Key}']";
                var label = await page.QuerySelectorAsync(labelSelector);
                Assert.NotNull(label);

                var labelText = await label!.InnerTextAsync();
                Assert.Contains(pair.Value, labelText);

                // Required marker (assuming <span>*</span> or aria-required)
                var input = await page.QuerySelectorAsync(_fieldInputSelectors[pair.Key]);
                Assert.NotNull(input);
                var ariaRequired = await input!.GetAttributeAsync("aria-required");
                Assert.True(ariaRequired == "true", $"Field {pair.Key} should be marked as required");

                // Input and label must be associated
                var labelFor = await label.GetAttributeAsync("for");
                var inputId = await input.GetAttributeAsync("id");
                Assert.Equal(labelFor, inputId);
            }

            await context.CloseAsync();
        }

        [Fact(DisplayName = "Validation errors appear and block submission on invalid data")]
        public async Task MedicationForm_Validation_ShowsErrorsAndBlocksSubmission()
        {
            var context = await _browser.NewContextAsync();
            var page = await context.NewPageAsync();
            await page.GotoAsync(_formUrl);

            // Ensure all fields are empty, submit the form
            var submitBtn = await page.QuerySelectorAsync("button[type='submit']");
            Assert.NotNull(submitBtn);

            await submitBtn!.ClickAsync();

            // Validation: error messages should be present
            foreach (var pair in _expectedLabels)
            {
                var errorSelector = $"#{pair.Key}-error, .validation-message[for='{pair.Key}'], [data-testid='{pair.Key}-error']";
                var err = await page.QuerySelectorAsync(errorSelector);
                Assert.NotNull(err);
                var errText = await err!.InnerTextAsync();
                Assert.Contains("required", errText, StringComparison.OrdinalIgnoreCase);
            }

            // Form should NOT submit (no success message, confirm no navigation)
            Assert.Equal(_formUrl, page.Url);

            // Optionally, fill one field and check that error for that field disappears, but others remain
            await page.FillAsync(_fieldInputSelectors["medication-name"], "Paracetamol");
            await submitBtn.ClickAsync();

            var medicationNameError = await page.QuerySelectorAsync("#medication-name-error");
            Assert.True(medicationNameError == null || !(await medicationNameError.IsVisibleAsync()));

            // Other errors remain
            foreach (var key in new[] { "dosage", "frequency", "route" })
            {
                var errorSelector = $"#{key}-error, .validation-message[for='{key}'], [data-testid='{key}-error']";
                var err = await page.QuerySelectorAsync(errorSelector);
                Assert.NotNull(err);
                var errText = await err!.InnerTextAsync();
                Assert.Contains("required", errText, StringComparison.OrdinalIgnoreCase);
            }

            await context.CloseAsync();
        }

        [Fact(DisplayName = "Tab order and keyboard navigation are logical and correct")]
        public async Task MedicationForm_KeyboardNav_TabOrder()
        {
            var context = await _browser.NewContextAsync(new()
            {
                HasTouch = false
            });
            var page = await context.NewPageAsync();
            await page.GotoAsync(_formUrl);

            // Focus should go from Name -> Dosage -> Frequency -> Route -> Submit button
            var fieldOrder = new[]
            {
                _fieldInputSelectors["medication-name"],
                _fieldInputSelectors["dosage"],
                _fieldInputSelectors["frequency"],
                _fieldInputSelectors["route"],
                "button[type='submit']"
            };

            await page.FocusAsync(fieldOrder[0]);
            for (int i = 1; i < fieldOrder.Length; i++)
            {
                await page.Keyboard.PressAsync("Tab");
                var active = await page.EvaluateAsync<string>(@"() => document.activeElement.getAttribute('name') || document.activeElement.getAttribute('type')");
                if (i < fieldOrder.Length - 1)
                    Assert.Equal(
                        fieldOrder[i].Replace("input[name='", "").Replace("']", ""),
                        active
                    );
                else
                    Assert.Equal("submit", active); // Button type
            }

            await context.CloseAsync();
        }

        [Fact(DisplayName = "Accessibility: role/aria attributes are present and inputs are label-associated")]
        public async Task MedicationForm_A11y_Roles_And_Aria()
        {
            var context = await _browser.NewContextAsync();
            var page = await context.NewPageAsync();
            await page.GotoAsync(_formUrl);

            foreach (var pair in _fieldInputSelectors)
            {
                var label = await page.QuerySelectorAsync($"label[for='{pair.Key}']");
                var input = await page.QuerySelectorAsync(pair.Value);

                Assert.NotNull(label);
                Assert.NotNull(input);

                // Label must be associated with input
                var labelFor = await label!.GetAttributeAsync("for");
                var inputId = await input!.GetAttributeAsync("id");
                Assert.Equal(labelFor, inputId);

                // aria-required
                var ariaRequired = await input.GetAttributeAsync("aria-required");
                Assert.Equal("true", ariaRequired);

                // role attributes
                var role = await input.GetAttributeAsync("role");
                Assert.True(role == null || role == "textbox");
            }

            // Error messages should have role="alert" for screen readers
            foreach (var pair in _expectedLabels)
            {
                var errorSelector = $"#{pair.Key}-error, .validation-message[for='{pair.Key}'], [data-testid='{pair.Key}-error']";
                var err = await page.QuerySelectorAsync(errorSelector);
                if (err != null)
                {
                    var role = await err.GetAttributeAsync("role");
                    Assert.Equal("alert", role);
                }
            }

            await context.CloseAsync();
        }

        [Fact(DisplayName = "Form layout is responsive on mobile, tablet, desktop (no horizontal scroll, fields visible)")]
        public async Task MedicationForm_ResponsiveLayout_NoScrollAndCorrectFieldArrangement()
        {
            foreach (var bp in _breakpoints)
            {
                var context = await _browser.NewContextAsync(new BrowserNewContextOptions
                {
                    ViewportSize = bp
                });
                var page = await context.NewPageAsync();
                await page.GotoAsync(_formUrl);

                // No horizontal scrollbar
                bool scrollBar = await page.EvaluateAsync<bool>(@"() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2");
                Assert.False(scrollBar);

                // All fields visible and not clipped
                foreach (var selector in _fieldInputSelectors.Values)
                {
                    var box = await page.EvalOnSelectorAsync<ElementHandleBoxModelResult>(selector, "el => el.getBoundingClientRect()");
                    Assert.NotNull(box);
                    Assert.True(box!["x"].AsInt() >= 0);
                    Assert.True(box!["y"].AsInt() >= 0);
                }

                // (OPTIONAL) On mobile, fields stack vertically; on desktop, fields are at least partially side-by-side
                var firstFieldPos = await page.EvaluateAsync<decimal>(@$"() => document.querySelector('{_fieldInputSelectors["medication-name"]}').getBoundingClientRect().top");
                var lastFieldPos = await page.EvaluateAsync<decimal>(@$"() => document.querySelector('{_fieldInputSelectors["route"]}').getBoundingClientRect().top");
                if (bp.Width <= 480)
                {
                    Assert.True(lastFieldPos > firstFieldPos); // Stacked vertically
                }

                await context.CloseAsync();
            }
        }

        // Helper for bounding rect type
        private class ElementHandleBoxModelResult : Dictionary<string, object>
        {
            public int AsInt() => int.Parse(ToString() ?? "0");
        }
    }
}