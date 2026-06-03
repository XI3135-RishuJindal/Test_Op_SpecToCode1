# API Gateway + Medication Entry UI

## Overview
This repository contains the API Gateway service and a responsive, accessible Medication Entry UI, generated and maintained by ACE DevOps Agent.

---

## Medication Entry UI

### Accessing the Form
1. Start the application (see **Setup** below).
2. Navigate to `http://localhost:5000/medications/entry` (or `https://localhost:7000/medications/entry` for HTTPS).
3. The form will load with fields for **Medication Name**, **Dose**, **Frequency**, and **Route**.

### Using the Form
- Fill in all required fields (marked with an asterisk `*`).
- Click **Submit** to validate and submit the form.
- If any required field is empty or invalid, the field will be visually highlighted and an accessible error message will appear beneath it — submission is blocked until all errors are resolved.
- All fields are keyboard-navigable: use `Tab` / `Shift+Tab` to move between controls, `Enter` or `Space` to activate buttons.

---

## Accessibility Features

The Medication Entry UI is designed to meet **WCAG 2.1 AA** standards:

| Feature | Implementation |
|---|---|
| Semantic HTML | `<label>` elements are explicitly associated with their `<input>` via `for`/`id` pairs |
| Keyboard navigation | Logical tab order across all form controls; no keyboard traps |
| Screen reader support | `aria-required`, `aria-invalid`, and `aria-describedby` attributes on all inputs; error messages linked via `aria-describedby` |
| Visible focus states | High-contrast focus ring on all interactive elements |
| Error identification | Invalid fields are highlighted with a visible border color change and an inline error message |

### Known Limitations
- Colour contrast has been validated for the default light theme only. Dark-mode or high-contrast OS themes have not been independently audited.
- Complex assistive-technology combinations (e.g., JAWS + IE) are out of scope; testing targets modern screen readers (NVDA, VoiceOver) with evergreen browsers.

---

## Responsive Design

The form layout adapts automatically across device widths:

| Breakpoint | Layout |
|---|---|
| `< 576px` (mobile) | Single-column; all fields stack vertically |
| `576px – 991px` (tablet) | Two-column grid where space allows |
| `≥ 992px` (desktop) | Side-by-side field groups with wider inputs |

No horizontal scrolling is required at any supported viewport width (minimum 320 px).

---

## Running Automated UI Tests

The test suite covers field validation, responsive layout, and keyboard accessibility.

### Prerequisites
- [.NET 8 SDK](https://dotnet.microsoft.com/download)

### Run all tests
```bash
dotnet test Tests/ApiGateway.Tests.csproj
```

### Run with detailed output
```bash
dotnet test Tests/ApiGateway.Tests.csproj --logger "console;verbosity=detailed"
```

### Run a specific test class
```bash
dotnet test Tests/ApiGateway.Tests.csproj --filter "FullyQualifiedName~MedicationEntryTests"
```

### Generate a coverage report
```bash
dotnet test Tests/ApiGateway.Tests.csproj --collect:"XPlat Code Coverage"
```

Test files are located under `Tests/Controllers/` and any new UI-specific tests under `Tests/UI/`.

---

## Internationalization (i18n) — Updating UI Strings

All user-visible strings in the Medication Entry UI are externalized for easy translation. **Do not hardcode display text directly in `.razor` files.**

### Where to find UI strings
- Resource files are located at `Resources/Pages/Medications/MedicationEntry.{locale}.resx`
  - Default (English): `Resources/Pages/Medications/MedicationEntry.resx`
  - Example French locale: `Resources/Pages/Medications/MedicationEntry.fr.resx`

### Adding or updating a translation
1. Open (or create) the `.resx` file for the target locale.
2. Add or update the key-value pair, e.g.:
   ```xml
   <data name="Label_MedicationName" xml:space="preserve">
     <value>Medication Name</value>
   </data>
   ```
3. In the Razor component, reference the resource via the injected `IStringLocalizer<MedicationEntry>`:
   ```razor
   @inject IStringLocalizer<MedicationEntry> L
   <label for="medName">@L["Label_MedicationName"]</label>
   ```
4. Register the new locale in `Program.cs` under `builder.Services.AddLocalization(...)` and the supported cultures list.
5. Re-run the test suite to confirm no regressions.

---

## Project Files

| Path | Description |
|---|---|
| `Pages/Medications/MedicationEntry.razor` | Medication entry form component |
| `Pages/Medications/MedicationEntry.razor.cs` | Code-behind (validation logic) |
| `Pages/Medications/MedicationEntry.razor.css` | Component-scoped styles |
| `Resources/Pages/Medications/` | Localization resource files |
| `Models/MedicationDTO.cs` | Canonical medication data model |
| `Tests/` | Automated test project |
| `Controllers/` | API Gateway controllers |
| `openspec/changes/api-gateway/specs/spec.md` | API Gateway specification |

---

## Setup

1. Install [.NET 8 SDK](https://dotnet.microsoft.com/download).
2. Clone the repository and restore dependencies:
   ```bash
   dotnet restore
   ```
3. Configure required secrets in `appsettings.Development.json` (JWT key, issuer, audience).
4. Run the application:
   ```bash
   dotnet run --project ApiGateway.csproj
   ```
5. Open your browser and navigate to `http://localhost:5000/swagger` for the API explorer, or `http://localhost:5000/medications/entry` for the Medication Entry UI.

### Docker
```bash
docker build -t apigateway .
docker run -p 5000:80 apigateway
```

---

## Pipeline Features
- Automated build and test
- Security scanning
- Deployment automation
- Quality gates

---

## Generated by
ACE DevOps Agent — Automated DevOps Intelligence Platform
