# SPEC: Update Runtime Configuration and Application Settings for .NET 8

## Current State

- **.NET Runtime**: Application targets a pre-.NET 8 runtime (e.g., .NET Core 3.1, .NET 5, .NET 6, or .NET 7).
- **Configuration Files**: 
  - `runtimeconfig.json` may specify a previous .NET version.
  - Application settings managed via `appsettings.json`, `appsettings.{Environment}.json`, and (optionally) environment variables.
- **Configuration APIs**: Uses `Microsoft.Extensions.Configuration` APIs (pre-.NET 8).
- **Host Builder**: Uses `Host.CreateDefaultBuilder()` or `WebApplication.CreateBuilder()`.
- **Relevant Behaviors**:
  - Configuration providers are loaded in a specific order.
  - Some newer features (e.g., configuration hot-reload, direct environment binding) may not be available.
- **Key Settings & Values**:
  - `DOTNET_ENVIRONMENT` set to current environment (`Development`, `Staging`, `Production`).
  - In `runtimeconfig.json`: 
    - `"tfm": "netX.Y"` (for pre-.NET 8), where `X.Y` < 8.0
    - `"rollForward": "LatestMinor"` or similar.
    - Other runtime options like `"System.GC.Server"` or `"System.GC.Concurrent"`.

## Target State

- **.NET Runtime**: Application targets .NET 8 (`net8.0`) in all configuration files.
- **Configuration Files**:
  - `runtimeconfig.json` reflects `"tfm": "net8.0"` and latest runtime options.
  - App settings files structure remains, but can leverage new .NET 8 features.
- **Configuration APIs**:
  - Continue to use `Microsoft.Extensions.Configuration`, but can use .NET 8 enhancements:
    - New, improved binding (e.g., binding directly to records).
    - Enhanced source generator support for configs.
    - Improvements in configuration reload/refresh behaviors.
- **Host Builder**: Continue to use default builder approach; minor differences may apply for .NET 8 template projects.
- **Relevant Behaviors**:
  - Can use features like hot reload for appsettings, direct mapping to options/POCOs, etc.
- **Key Settings & Values**:
  - `DOTNET_ENVIRONMENT` remains relevant; `appsettings.*.json` is unchanged.
  - In `runtimeconfig.json`:
    - `"tfm": "net8.0"` is required.
    - Runtime options update for .NET 8 available settings, as applicable.

## Compatibility & Breaking Changes

| Breaking Change                                 | Migration Path                                                      |
|-------------------------------------------------|---------------------------------------------------------------------|
| `"tfm"` in `runtimeconfig.json` must be `net8.0`| Update `"tfm": "net8.0"` and re-build application                   |
| Deprecated or changed runtime options           | Review .NET 8 docs and adjust/remove invalid settings               |
| Changed default behaviors in configuration      | Validate configuration loading order per .NET 8 documentation       |
| AppSettings structure: NO format change         | N/A                                                                |
| Source generator APIs for binding (if used)     | Update to .NET 8 source generator patterns and supported APIs       |

## Key Flows (before vs after)

### 1. Application Startup

**Before (.NET < 8)**  
1. `runtimeconfig.json` indicates `"tfm": "net6.0"` (for example).
2. `Host.CreateDefaultBuilder()` loads providers in default order.
3. `appsettings.json` & environment-specific loaded.
4. Environment variables (`DOTNET_ENVIRONMENT`) chosen.

**After (.NET 8)**  
1. `runtimeconfig.json` indicates `"tfm": "net8.0"`.
2. `Host.CreateDefaultBuilder()` (now with .NET 8) loads providers, leveraging any ordering or hot reload enhancements.
3. `appsettings.json` & environment-specific loaded.
4. Environment variables used as before.
5. (Optional) Can enable/configure new configuration features (e.g., improved binding).

## Data Model Changes

N/A — not applicable to this task

## Configuration Changes

### 1. `runtimeconfig.json`
- **Before**:
  ```json
  {
    "runtimeOptions": {
      "tfm": "net6.0",
      "framework": {
        "name": "Microsoft.NETCore.App",
        "version": "6.0.0"
      },
      ...
    }
  }
  ```
- **After**:
  ```json
  {
    "runtimeOptions": {
      "tfm": "net8.0",
      "framework": {
        "name": "Microsoft.NETCore.App",
        "version": "8.0.0"
      },
      ...
    }
  }
  ```
- **Migration**: Change `"tfm"` to `"net8.0"` and `"version"` to `"8.0.0"`.

### 2. AppSettings:  
- No format change required in `appsettings.json` or `appsettings.{Environment}.json`.
- Can optionally enable new .NET 8 features via config, if desired.

### 3. Environment Variables:
- `DOTNET_ENVIRONMENT` remains. No new env vars required for .NET 8 upgrade.

---

**Summary:**  
To update runtime configuration and application settings for .NET 8:
- Change `"tfm"` to `"net8.0"` in `runtimeconfig.json` and verify other runtime options.
- No breaking appsettings.json changes.
- Optionally use new configuration/binding APIs or features when refactoring code for .NET 8.  
- Check .NET 8 docs for any obsolete/deprecated `runtimeconfig.json` options.