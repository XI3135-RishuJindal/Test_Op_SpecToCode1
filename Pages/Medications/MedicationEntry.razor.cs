// MedicationEntry.razor.cs
// Code-behind for MedicationEntry.razor.
// Keeps UI logic separate from markup, following team Blazor conventions.
// Review: docs/code-reviews/medication-entry-placement-review.md

using System.ComponentModel.DataAnnotations;

namespace ApiGateway.Pages.Medications
{
    /// <summary>
    /// View model for the medication entry form.
    /// Maps to the relevant subset of MedicationDTO fields required for data entry.
    /// Backend persistence is out-of-scope for this user story.
    /// </summary>
    public class MedicationEntryModel
    {
        /// <summary>Generic medication name (e.g., "Amoxicillin").</summary>
        [Required(ErrorMessage = "Medication name is required.")]
        [StringLength(200, ErrorMessage = "Medication name must not exceed 200 characters.")]
        public string Name { get; set; } = string.Empty;

        /// <summary>Numeric dose amount. Unit is captured separately in MedicationDTO.</summary>
        [Required(ErrorMessage = "Dose is required.")]
        [Range(0.001, double.MaxValue, ErrorMessage = "Dose must be a positive number.")]
        public decimal Dosage { get; set; }

        /// <summary>
        /// How often the medication is taken (e.g., "Once daily", "Twice daily").
        /// Stored as free text; a future iteration may use a controlled vocabulary.
        /// </summary>
        [Required(ErrorMessage = "Frequency is required.")]
        [StringLength(100, ErrorMessage = "Frequency must not exceed 100 characters.")]
        public string Frequency { get; set; } = string.Empty;

        /// <summary>
        /// Administration route (e.g., "Oral", "IV", "Topical").
        /// Stored as free text; a future iteration may use a controlled vocabulary.
        /// </summary>
        [Required(ErrorMessage = "Route is required.")]
        [StringLength(100, ErrorMessage = "Route must not exceed 100 characters.")]
        public string Route { get; set; } = string.Empty;
    }
}
