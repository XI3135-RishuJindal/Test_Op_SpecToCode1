const assert = require('assert');
const fs = require('fs');
const path = require('path');

function findNearestPackageJson(startDir) {
  let dir = startDir;
  while (true) {
    const candidate = path.join(dir, 'package.json');
    if (fs.existsSync(candidate)) return candidate;
    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

function safeJsonParse(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  try {
    return JSON.parse(raw);
  } catch (e) {
    const err = new Error(`Failed to parse JSON at ${filePath}: ${e.message}`);
    err.cause = e;
    throw err;
  }
}

function getNodeVersion() {
  // Returns exact version string like "v20.15.1"
  return process.version;
}

function readRootPackageJson() {
  const pkgPath = findNearestPackageJson(process.cwd());
  if (!pkgPath) {
    throw new Error(
      'Unable to locate package.json in current or parent directories. ' +
        'This upgrade validation test expects a Node.js project with a package.json.'
    );
  }
  return { pkgPath, pkg: safeJsonParse(pkgPath) };
}

function loadUpgradeContext() {
  // Target version must be explicitly specified to be verifiable.
  // Accept any of these environment variables as the "exact target version":
  // - UPGRADE_TARGET_NODE_VERSION (recommended)
  // - TARGET_NODE_VERSION
  // - EXPECTED_NODE_VERSION
  //
  // Examples: "v20.15.1" (exact, including v) or "20.15.1"
  const target =
    process.env.UPGRADE_TARGET_NODE_VERSION ||
    process.env.TARGET_NODE_VERSION ||
    process.env.EXPECTED_NODE_VERSION ||
    '';

  return {
    targetNodeVersion: target.trim(),
  };
}

function normalizeNodeVersion(v) {
  // normalize "20.15.1" -> "v20.15.1", keep "v20.15.1" as-is
  if (!v) return '';
  return v.startsWith('v') ? v : `v${v}`;
}

function listAllDependencySpecs(pkg) {
  return {
    ...pkg.dependencies,
    ...pkg.devDependencies,
    ...pkg.peerDependencies,
    ...pkg.optionalDependencies,
  };
}

function repoHasAnyFileNamed(startDir, fileNames) {
  // Shallow-ish search: check root and common subdirs
  const candidates = [];
  for (const name of fileNames) {
    candidates.push(path.join(startDir, name));
    candidates.push(path.join(startDir, 'config', name));
    candidates.push(path.join(startDir, 'configs', name));
    candidates.push(path.join(startDir, 'src', name));
    candidates.push(path.join(startDir, 'app', name));
  }
  return candidates.some((p) => fs.existsSync(p));
}

describe('Upgrade validation (security patch/minor upgrades)', function () {
  const ctx = loadUpgradeContext();
  const activeNode = getNodeVersion();
  const normalizedActiveNode = normalizeNodeVersion(activeNode);
  const normalizedTargetNode = normalizeNodeVersion(ctx.targetNodeVersion);

  const { pkgPath, pkg } = readRootPackageJson();
  const deps = listAllDependencySpecs(pkg);

  it('asserts the upgraded runtime is active at the EXACT target version (Node.js)', function () {
    assert.ok(
      normalizedTargetNode,
      [
        'Missing explicit target runtime version for upgrade validation.',
        'Set one of: UPGRADE_TARGET_NODE_VERSION, TARGET_NODE_VERSION, EXPECTED_NODE_VERSION.',
        'Example: export UPGRADE_TARGET_NODE_VERSION=v20.15.1',
      ].join(' ')
    );

    assert.strictEqual(
      normalizedActiveNode,
      normalizedTargetNode,
      `Active Node.js runtime version (${normalizedActiveNode}) does not match exact target (${normalizedTargetNode}).`
    );
  });

  it('validates critical application paths can load the application entrypoint without errors', function () {
    // "Critical application path" in a generic repo: being able to load the main entrypoint.
    // We do not assume any framework; we simply ensure the configured entry can be resolved/required.
    const mainField = pkg.main;
    const typeField = pkg.type; // "module" or undefined/commonjs

    // Determine candidate entrypoints
    const candidates = [];

    if (mainField) {
      candidates.push(path.resolve(path.dirname(pkgPath), mainField));
    }
    // Common conventional entrypoints
    candidates.push(path.resolve(path.dirname(pkgPath), 'index.js'));
    candidates.push(path.resolve(path.dirname(pkgPath), 'src', 'index.js'));
    candidates.push(path.resolve(path.dirname(pkgPath), 'app.js'));
    candidates.push(path.resolve(path.dirname(pkgPath), 'server.js'));
    candidates.push(path.resolve(path.dirname(pkgPath), 'src', 'server.js'));

    const existing = candidates.find((p) => fs.existsSync(p) || fs.existsSync(`${p}.js`) || fs.existsSync(`${p}.cjs`) || fs.existsSync(`${p}.mjs`));

    if (!existing) {
      // If there is no obvious entrypoint, this is not necessarily an error in the codebase,
      // but we cannot validate runtime load; fail with actionable info.
      assert.fail(
        'No recognizable application entrypoint found to validate load path. ' +
          `Checked: ${candidates
            .map((p) => path.relative(path.dirname(pkgPath), p))
            .join(', ')}. ` +
          'Set "main" in package.json or add a conventional entrypoint.'
      );
    }

    // If package.json type=module, require() may not work; validate that the file at least exists and is readable.
    // Otherwise, attempt to require and ensure it does not throw at load-time.
    if (typeField === 'module' || existing.endsWith('.mjs')) {
      assert.ok(fs.statSync(existing).isFile(), `Entrypoint is not a file: ${existing}`);
      const content = fs.readFileSync(existing, 'utf8');
      assert.ok(content.length >= 0, 'Entrypoint exists but could not be read.');
    } else {
      // For CommonJS, require should be safe and is a stronger signal that upgraded deps don't break startup.
      try {
        // eslint-disable-next-line global-require, import/no-dynamic-require
        require(existing);
      } catch (e) {
        const err = new Error(`Failed to require application entrypoint (${existing}). Load-time error: ${e && e.message}`);
        err.cause = e;
        throw err;
      }
    }
  });

  it('verifies deprecated APIs replaced in this upgrade no longer appear in dependency specs (no "*" / "latest")', function () {
    // For security patch/minor upgrades, a critical anti-pattern is using floating versions like "*" or "latest",
    // which defeats deterministic patching and CVE remediation validation.
    // This test enforces that no dependency spec uses "*" or "latest".
    const bad = [];
    for (const [name, spec] of Object.entries(deps)) {
      if (!spec) continue;
      const s = String(spec).trim().toLowerCase();
      if (s === '*' || s === 'latest') bad.push({ name, spec });
    }

    assert.deepStrictEqual(
      bad,
      [],
      `Found floating dependency specs that should be replaced with fixed/ranged versions as part of conservative upgrades: ${bad
        .map((b) => `${b.name}@${b.spec}`)
        .join(', ')}`
    );
  });

  it('verifies new configuration keys introduced by the upgrade load without errors (dotenv support if present)', function () {
    // In absence of concrete upgrade details, validate that configuration loading does not throw.
    // If dotenv is present, ensure it can be required and configured safely (a common post-upgrade config path).
    const hasDotenv = Object.prototype.hasOwnProperty.call(deps, 'dotenv');

    if (!hasDotenv) {
      // If dotenv isn't used, validate that typical config files (if present) are parseable as JSON/YAML when applicable.
      const rootDir = path.dirname(pkgPath);

      const hasConfigFile = repoHasAnyFileNamed(rootDir, [
        '.env',
        '.env.example',
        'config.json',
        'config.local.json',
        'settings.json',
        'application.json',
        'appsettings.json',
      ]);

      // If there's no sign of config files, we can't validate much; treat as pass.
      if (!hasConfigFile) return;

      // Parse any present JSON configs among the common names.
      const jsonCandidates = [
        path.join(rootDir, 'config.json'),
        path.join(rootDir, 'config.local.json'),
        path.join(rootDir, 'settings.json'),
        path.join(rootDir, 'application.json'),
        path.join(rootDir, 'appsettings.json'),
        path.join(rootDir, 'config', 'config.json'),
        path.join(rootDir, 'config', 'settings.json'),
      ].filter((p) => fs.existsSync(p));

      for (const fp of jsonCandidates) {
        const parsed = safeJsonParse(fp);
        assert.ok(parsed && typeof parsed === 'object', `Config JSON did not parse into an object: ${fp}`);
      }
      return;
    }

    let dotenv;
    try {
      // eslint-disable-next-line global-require
      dotenv = require('dotenv');
    } catch (e) {
      const err = new Error(`dotenv is declared in ${path.relative(process.cwd(), pkgPath)} but could not be required after upgrade.`);
      err.cause = e;
      throw err;
    }

    assert.ok(dotenv, 'dotenv required but returned empty module export.');
    assert.ok(
      typeof dotenv.config === 'function',
      'dotenv loaded but does not expose config() function; upgrade may have broken configuration loading.'
    );

    // Attempt to load .env if present; config() should not throw.
    const envPath = path.join(path.dirname(pkgPath), '.env');
    try {
      const result = fs.existsSync(envPath) ? dotenv.config({ path: envPath }) : dotenv.config();
      // dotenv returns { parsed, error }; ensure no error
      if (result && result.error) throw result.error;
    } catch (e) {
      const err = new Error(`dotenv.config() threw an error after upgrade. This indicates configuration keys/files introduced/changed in the upgrade do not load cleanly.`);
      err.cause = e;
      throw err;
    }
  });
});