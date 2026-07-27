import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import test from "node:test";
import assert from "node:assert/strict";

const TARGET_SBOM_SPEC_VERSION = "1.5";
const WORKFLOWS_DIR = path.resolve(process.cwd(), ".github", "workflows");

function listWorkflowFiles() {
  if (!fs.existsSync(WORKFLOWS_DIR)) return [];
  return fs
    .readdirSync(WORKFLOWS_DIR)
    .filter((f) => f.endsWith(".yml") || f.endsWith(".yaml"))
    .map((f) => path.join(WORKFLOWS_DIR, f));
}

function readAllWorkflowsText() {
  return listWorkflowFiles()
    .map((p) => fs.readFileSync(p, "utf8"))
    .join("\n\n---\n\n");
}

function findSbomWorkflowFiles() {
  const files = listWorkflowFiles();
  const matches = [];
  for (const file of files) {
    const txt = fs.readFileSync(file, "utf8");
    if (
      /sbom/i.test(txt) ||
      /cyclonedx/i.test(txt) ||
      /cyclonedx-bom/i.test(txt) ||
      /dependency[-_ ]track/i.test(txt)
    ) {
      matches.push(file);
    }
  }
  return matches;
}

function parseCycloneDxSbomJson(sbomPath) {
  const raw = fs.readFileSync(sbomPath, "utf8");
  let json;
  try {
    json = JSON.parse(raw);
  } catch (e) {
    throw new Error(`SBOM is not valid JSON: ${sbomPath}\n${e?.message || e}`);
  }
  return json;
}

function detectSbomArtifactPatternFromWorkflowText(workflowText) {
  // Try to find common upload-artifact 'path' values for SBOM.
  // This is heuristic but helps validate "critical path": artifact name/path aligns with SBOM output.
  const lines = workflowText.split(/\r?\n/);

  // Common SBOM filenames
  const common = [
    "bom.json",
    "bom.xml",
    "sbom.json",
    "sbom.xml",
    "cyclonedx.json",
    "cyclonedx.xml",
    "cyclonedx-bom.json",
    "cyclonedx-bom.xml",
  ];

  for (const l of lines) {
    const m = l.match(/^\s*path:\s*(.+)\s*$/i);
    if (!m) continue;
    const val = m[1].trim().replace(/^["']|["']$/g, "");
    for (const c of common) {
      if (val.toLowerCase().includes(c)) return val;
    }
  }

  return null;
}

function findLocalSbomFiles() {
  const candidates = [
    "bom.json",
    "bom.xml",
    "sbom.json",
    "sbom.xml",
    "cyclonedx.json",
    "cyclonedx.xml",
    "cyclonedx-bom.json",
    "cyclonedx-bom.xml",
    path.join("dist", "bom.json"),
    path.join("dist", "sbom.json"),
    path.join("build", "bom.json"),
    path.join("build", "sbom.json"),
    path.join("artifacts", "bom.json"),
    path.join("artifacts", "sbom.json"),
  ];

  const found = [];
  for (const rel of candidates) {
    const abs = path.resolve(process.cwd(), rel);
    if (fs.existsSync(abs) && fs.statSync(abs).isFile()) found.push(abs);
  }

  // Also search in repo root for JSON that looks like CycloneDX BOM (limited depth).
  // Avoid deep recursive traversal for test runtime.
  const root = process.cwd();
  const entries = fs.readdirSync(root, { withFileTypes: true });
  for (const e of entries) {
    if (!e.isFile()) continue;
    if (!/\.json$/i.test(e.name)) continue;
    const abs = path.join(root, e.name);
    try {
      const txt = fs.readFileSync(abs, "utf8");
      if (/"bomFormat"\s*:\s*"CycloneDX"/.test(txt)) found.push(abs);
    } catch {
      // ignore
    }
  }

  return Array.from(new Set(found));
}

function tryRunSbomGeneratorFromWorkflow(workflowText) {
  // Attempt to extract a CLI invocation we can run locally in CI validation.
  // Supported patterns:
  //  - npm exec -- cyclonedx-bom ...
  //  - npx cyclonedx-bom ...
  //  - cyclonedx-bom ...
  //  - cycloneDX action is not locally runnable; will be validated by workflow presence + config.
  const lines = workflowText.split(/\r?\n/);

  const cmdPatterns = [
    /\b(npm\s+exec\s+--\s+cyclonedx-bom[^\n\r#]*)/i,
    /\b(npx\s+cyclonedx-bom[^\n\r#]*)/i,
    /\b(cyclonedx-bom[^\n\r#]*)/i,
  ];

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed.toLowerCase().startsWith("run:")) continue;

    const runBody = trimmed.replace(/^run:\s*/i, "");
    for (const re of cmdPatterns) {
      const m = runBody.match(re);
      if (m && m[1]) {
        return m[1].trim();
      }
    }
  }
  return null;
}

test("SBOM CI upgrade: workflow(s) exist that generate SBOM and upload it as an artifact", () => {
  const sbomWorkflows = findSbomWorkflowFiles();
  assert.ok(
    sbomWorkflows.length > 0,
    `Expected at least one workflow referencing SBOM/CycloneDX. Found none in ${WORKFLOWS_DIR}.`
  );

  const combined = readAllWorkflowsText();

  // Critical path: SBOM generation should be present.
  assert.ok(
    /cyclonedx/i.test(combined) ||
      /cyclonedx-bom/i.test(combined) ||
      /bomFormat/i.test(combined) ||
      /\bsbom\b/i.test(combined),
    "Expected workflow text to reference CycloneDX/SBOM generation."
  );

  // Critical path: SBOM should be uploaded or otherwise published as an artifact/output.
  assert.ok(
    /actions\/upload-artifact@/i.test(combined) ||
      /\bupload-artifact\b/i.test(combined) ||
      /\bartifact\b/i.test(combined),
    "Expected workflow to upload/publish SBOM as an artifact (e.g., actions/upload-artifact)."
  );

  // Configuration keys introduced by the upgrade: ensure a permissions block exists (least privilege requirement).
  // This validates that the workflow config loads with those keys (syntactically present).
  assert.ok(
    /^\s*permissions\s*:/m.test(combined),
    "Expected workflow to define a top-level or job-level 'permissions:' block."
  );

  // Ensure SBOM job runs after build artifacts are produced (needs:)
  assert.ok(
    /^\s*needs\s*:/m.test(combined) || /needs:\s*\[/m.test(combined),
    "Expected SBOM job to declare 'needs:' to run after build job."
  );
});

test("SBOM CI upgrade: deprecated SBOM APIs/tools are not used (SPDX-only generation or retired actions)", () => {
  const combined = readAllWorkflowsText();

  // This upgrade specifically targets CycloneDX (or explicitly approved equivalent).
  // Ensure it isn't implemented as SPDX-only generation with no CycloneDX mention.
  const mentionsCycloneDx = /cyclonedx/i.test(combined) || /cyclonedx-bom/i.test(combined);
  const mentionsSpdx = /\bspdx\b/i.test(combined);

  assert.ok(
    mentionsCycloneDx || !mentionsSpdx,
    "Workflow appears to generate SPDX SBOM without CycloneDX (or equivalent) referenced; expected CycloneDX or an approved equivalent."
  );

  // Deprecated/legacy patterns to avoid (examples of old/incorrect APIs for CycloneDX SBOM publishing).
  // Fail only if present.
  const deprecatedPatterns = [
    /cyclonedx\/cyclonedx-action@v1\b/i, // hypothetical legacy major
    /CycloneDX\/gh-action\b/i, // placeholder legacy naming
  ];

  for (const re of deprecatedPatterns) {
    assert.ok(!re.test(combined), `Deprecated SBOM action/tool reference detected: ${re}`);
  }
});

test("SBOM CI upgrade: can produce a valid CycloneDX SBOM with exact target specVersion (1.5) if SBOM is present or generator is runnable", () => {
  const combined = readAllWorkflowsText();

  const localSboms = findLocalSbomFiles();
  if (localSboms.length === 0) {
    // Try to run a detected SBOM generator command (best-effort).
    // This makes the test validate an actual critical path beyond static checks.
    const sbomWorkflows = findSbomWorkflowFiles();
    let cmd = null;
    for (const wf of sbomWorkflows) {
      const txt = fs.readFileSync(wf, "utf8");
      cmd = tryRunSbomGeneratorFromWorkflow(txt);
      if (cmd) break;
    }

    // If we cannot run a generator locally and no SBOM is present, we still require that the workflow
    // pins the CycloneDX specVersion in configuration (new config key) so we can assert the exact target version.
    if (!cmd) {
      assert.ok(
        /specVersion\s*:\s*["']?1\.5["']?/i.test(combined) ||
          /--spec-version\s+1\.5\b/i.test(combined) ||
          /--specVersion\s+1\.5\b/i.test(combined) ||
          /"specVersion"\s*:\s*"1\.5"/i.test(combined),
        `No local SBOM found and no runnable generator command detected. Expected workflow configuration to pin CycloneDX specVersion to ${TARGET_SBOM_SPEC_VERSION}.`
      );
      return;
    }

    // Run command best-effort; it must not error.
    try {
      execSync(cmd, { stdio: "inherit" });
    } catch (e) {
      assert.fail(`Detected SBOM generator command failed: ${cmd}\n${e?.message || e}`);
    }
  }

  const sbomsAfter = findLocalSbomFiles();
  assert.ok(sbomsAfter.length > 0, "Expected a CycloneDX SBOM file to exist after SBOM generation validation.");

  // Validate the "active version" of the SBOM format equals the exact target specVersion.
  // We check all found SBOM JSON files; XML support is not validated here (unknown tooling).
  const jsonSboms = sbomsAfter.filter((p) => p.toLowerCase().endsWith(".json"));
  assert.ok(jsonSboms.length > 0, `Expected at least one CycloneDX SBOM JSON file. Found: ${sbomsAfter.join(", ")}`);

  for (const sbomPath of jsonSboms) {
    const json = parseCycloneDxSbomJson(sbomPath);

    assert.equal(
      json.bomFormat,
      "CycloneDX",
      `Expected bomFormat "CycloneDX" in ${sbomPath}, got: ${JSON.stringify(json.bomFormat)}`
    );

    assert.equal(
      json.specVersion,
      TARGET_SBOM_SPEC_VERSION,
      `Expected CycloneDX specVersion ${TARGET_SBOM_SPEC_VERSION} in ${sbomPath}, got: ${JSON.stringify(json.specVersion)}`
    );

    assert.ok(
      typeof json.version === "number" || typeof json.version === "string",
      `Expected 'version' field in SBOM (${sbomPath}).`
    );

    // Critical path: SBOM should contain components/metadata for dependencies/artifacts.
    // Some generators may omit 'components' but should include metadata.
    assert.ok(
      json.metadata || (Array.isArray(json.components) && json.components.length >= 0),
      `Expected SBOM to include 'metadata' and/or 'components' (${sbomPath}).`
    );
  }
});

test("SBOM CI upgrade: workflow upload-artifact path targets an SBOM file (critical artifact path)", () => {
  const sbomWorkflows = findSbomWorkflowFiles();
  assert.ok(sbomWorkflows.length > 0, "No SBOM-related workflows found to validate artifact paths.");

  let foundUploadPath = false;
  for (const wf of sbomWorkflows) {
    const txt = fs.readFileSync(wf, "utf8");

    if (!/actions\/upload-artifact@/i.test(txt) && !/\bupload-artifact\b/i.test(txt)) continue;

    const artifactPath = detectSbomArtifactPatternFromWorkflowText(txt);
    if (artifactPath) {
      foundUploadPath = true;

      // New configuration key validation: ensure the upload includes retention-days if specified in the upgrade.
      // If present, it must be an integer.
      const retentionMatch = txt.match(/^\s*retention-days:\s*([0-9]+)\s*$/im);
      if (retentionMatch) {
        assert.ok(Number.isInteger(Number(retentionMatch[1])), "retention-days must be an integer.");
      }

      // Ensure the path looks like an SBOM.
      assert.ok(
        /bom|sbom|cyclonedx/i.test(artifactPath),
        `Upload artifact path does not look like an SBOM: ${artifactPath}`
      );
    }
  }

  assert.ok(
    foundUploadPath,
    "Expected an upload-artifact step with a path pointing to an SBOM file (e.g., bom.json, sbom.json)."
  );
});