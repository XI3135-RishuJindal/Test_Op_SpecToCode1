using Microsoft.AspNetCore.Mvc.RazorPages;

namespace ApiGateway.Pages
{
    /// <summary>
    /// Page model for the user registration form (US-001).
    /// No backend submission logic is in scope for this story.
    /// </summary>
    public class RegisterModel : PageModel
    {
        public void OnGet()
        {
            // Static page — no data retrieval required for this story.
        }
    }
}
