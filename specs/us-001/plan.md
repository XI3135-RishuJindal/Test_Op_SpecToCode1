To deliver this story:
- Add a new registration form UI, using either an MVC Razor page (Register.cshtml + Register.cshtml.cs) under Pages or a static HTML file as appropriate for the codebase. Semantic markup is required, including <form>, <label>, and <input> elements.
- Ensure all input fields ("Name", "Email", "Password") are present, properly labeled, and have matching aria attributes for accessibility.
- Implement basic responsive CSS—either in a dedicated CSS file, inline in cshtml, or using a framework if present—ensuring the form remains usable on mobile and desktop.
- Add minimal navigation to the form (either via a dedicated URL route or action method in a new RegistrationController.cs if using MVC).
- Add at least one accessibility-focused automated or manual test (e.g., test tab order, screen reader text, element roles).
Files to change:
- Pages/Register.cshtml (new)
- Pages/Register.cshtml.cs (new if Razor Pages)
- wwwroot/css/register.css or inline styles
- Tests/Controllers/RegisterPageTests.cs or equivalent UI test