import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.ThreadContext;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.config.Configuration;
import org.apache.logging.log4j.core.lookup.Interpolator;
import org.apache.logging.log4j.core.lookup.JndiLookup;
import org.apache.logging.log4j.core.lookup.StrLookup;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.lang.reflect.Field;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Upgrade validation tests for log4j-core CVE-2021-44228 (Log4Shell) remediation.
 *
 * Verifies that:
 *  1. The active log4j-core version is 2.17.2 or later.
 *  2. JNDI lookup is disabled / not reachable via message interpolation.
 *  3. Core logging paths (info, warn, error, fatal, ThreadContext/MDC) work correctly.
 *  4. The log4j2.formatMsgNoLookups workaround property is no longer required.
 *  5. Self-referential lookups do not cause infinite recursion (CVE-2021-45105).
 */
@DisplayName("Log4j-core upgrade validation — CVE-2021-44228 remediation")
public class Log4jUpgradeValidationTest {

    private static final String MINIMUM_SAFE_VERSION = "2.17.2";

    private Logger logger;
    private LoggerContext loggerContext;
    private Configuration configuration;

    @BeforeEach
    void setUp() {
        logger = LogManager.getLogger(Log4jUpgradeValidationTest.class);
        loggerContext = (LoggerContext) LogManager.getContext(false);
        configuration = loggerContext.getConfiguration();
    }

    @AfterEach
    void tearDown() {
        ThreadContext.clearAll();
    }

    // -------------------------------------------------------------------------
    // 1. Version assertion — must be >= 2.17.2
    // -------------------------------------------------------------------------

    @Test
    @DisplayName("Active log4j-core version must be 2.17.2 or later")
    void activeVersionMustBeAtLeast2_17_2() {
        Package log4jPackage = org.apache.logging.log4j.core.Logger.class.getPackage();
        assertNotNull(log4jPackage, "log4j-core package must be present on the classpath");

        String implementationVersion = log4jPackage.getImplementationVersion();
        assertNotNull(implementationVersion,
                "log4j-core Implementation-Version manifest attribute must be present");

        assertTrue(
                isVersionAtLeast(implementationVersion, MINIMUM_SAFE_VERSION),
                String.format(
                        "log4j-core version '%s' is below the minimum safe version '%s'. " +
                        "CVE-2021-44228 is NOT remediated.",
                        implementationVersion, MINIMUM_SAFE_VERSION));

        System.out.println("[PASS] Active log4j-core version: " + implementationVersion);
    }

    @Test
    @DisplayName("log4j-core version must NOT be 2.14.1 (the vulnerable baseline)")
    void versionMustNotBeVulnerableBaseline() {
        Package log4jPackage = org.apache.logging.log4j.core.Logger.class.getPackage();
        assertNotNull(log4jPackage);

        String implementationVersion = log4jPackage.getImplementationVersion();
        assertNotNull(implementationVersion);

        assertNotEquals("2.14.1", implementationVersion,
                "log4j-core is still at the vulnerable 2.14.1 baseline — upgrade has NOT been applied.");
        assertFalse(implementationVersion.startsWith("2.15."),
                "log4j-core 2.15.x is still vulnerable to CVE-2021-45046.");
        assertFalse(implementationVersion.startsWith("2.16."),
                "log4j-core 2.16.x is still vulnerable to CVE-2021-45105.");
        assertFalse("2.17.0".equals(implementationVersion),
                "log4j-core 2.17.0 is still vulnerable to CVE-2021-44832.");
        assertFalse("2.17.1".equals(implementationVersion),
                "log4j-core 2.17.1 is still vulnerable to CVE-2021-44832 on Java 8.");
    }

    // -------------------------------------------------------------------------
    // 2. JNDI lookup disabled — CVE-2021-44228 / CVE-2021-45046 remediation
    // -------------------------------------------------------------------------

    @Test
    @DisplayName("JNDI lookup must be disabled or absent from the StrLookup registry")
    void jndiLookupMustBeDisabledOrAbsent() {
        // In 2.17.2 the JndiLookup is present in the jar but disabled by default.
        // The Interpolator (the component that resolves ${...} expressions) must
        // not expose a functional 'jndi' lookup that can reach remote resources.
        Interpolator interpolator = new Interpolator(configuration);

        // Attempt to resolve a JNDI expression — in a patched release this must
        // either return the literal string, null, or throw a disabled-lookup
        // exception rather than performing an outbound network call.
        String jndiExpression = "${jndi:ldap://127.0.0.1:1099/exploit}";
        String resolved;
        try {
            resolved = interpolator.lookup(jndiExpression);
        } catch (Exception e) {
            // Any exception from the lookup itself is acceptable — it means the
            // lookup was blocked before any network I/O occurred.
            assertTrue(
                    e.getMessage() == null ||
                    e.getMessage().toLowerCase().contains("disabled") ||
                    e.getMessage().toLowerCase().contains("jndi") ||
                    e instanceof IllegalArgumentException ||
                    e instanceof UnsupportedOperationException,
                    "Unexpected exception type when JNDI lookup was attempted: " + e);
            return;
        }

        // If no exception was thrown the resolved value must NOT be a remote
        // class reference — it must be null or the unexpanded literal.
        assertTrue(
                resolved == null || resolved.equals(jndiExpression),
                "JNDI lookup returned a non-null, non-literal value '" + resolved +
                "' — the JNDI vector may still be active.");
    }

    @Test
    @DisplayName("JndiLookup class must be present but its lookup() must be disabled")
    void jndiLookupClassMustBeDisabled() throws Exception {
        // The recommended remediation for 2.17.2 disables JNDI at runtime rather
        // than removing the class.  Verify the class is loadable but non-functional.
        Class<?> jndiClass;
        try {
            jndiClass = Class.forName("org.apache.logging.log4j.core.lookup.JndiLookup");
        } catch (ClassNotFoundException e) {
            // Class was removed entirely (e.g., via zip-strip remediation) — also acceptable.
            System.out.println("[PASS] JndiLookup class has been removed from the jar.");
            return;
        }

        // Class is present — instantiate and call lookup(); it must not perform
        // any network I/O and must return null or throw a disabled exception.
        StrLookup jndiLookup = (StrLookup) jndiClass.getDeclaredConstructor().newInstance();
        String result;
        try {
            result = jndiLookup.lookup("ldap://127.0.0.1:1099/exploit");
        } catch (Exception e) {
            // Disabled lookup throws — this is the expected patched behaviour.
            System.out.println("[PASS] JndiLookup.lookup() threw as expected: " + e.getClass().getSimpleName());
            return;
        }

        assertNull(result,
                "JndiLookup.lookup() returned a non-null value '" + result +
                "' — JNDI may still be active.");
    }

    @Test
    @DisplayName("log4j2.enableJndiLookup system property must default to false / disabled")
    void jndiLookupSystemPropertyDefaultMustBeFalse() {
        // In 2.17.2 JNDI is opt-in via log4j2.enableJndiLookup.
        // Unless explicitly set to true by the application, it must be absent or false.
        String enableJndi = System.getProperty("log4j2.enableJndiLookup");
        assertFalse(
                "true".equalsIgnoreCase(enableJndi),
                "System property log4j2.enableJndiLookup is set to 'true' — " +
                "this re-enables the JNDI vector and must not be present in production.");
    }

    // -------------------------------------------------------------------------
    // 3. CVE-2021-45105 — self-referential lookup must not cause infinite recursion
    // -------------------------------------------------------------------------

    @Test
    @DisplayName("Self-referential lookup must not cause StackOverflowError (CVE-2021-45105)")
    void selfReferentialLookupMustNotCauseStackOverflow() {
        // In 2.16.0 and earlier a message like ${${::-j}ndi:...} or a self-referential
        // context lookup could cause infinite recursion.  In 2.17.0+ a recursion guard
        // was introduced.  Logging such a string must complete without error.
        assertDoesNotThrow(() -> {
            logger.info("Self-referential lookup test: ${ctx:key:-${ctx:key}}");
            logger.info("Nested lookup test: ${${lower:j}${lower:n}${lower:d}${lower:i}:ldap://127.0.0.1/x}");
        }, "Logging a self-referential lookup expression must not throw StackOverflowError");
    }

    // -------------------------------------------------------------------------
    // 4. Core logging paths work correctly after the upgrade
    // -------------------------------------------------------------------------

    @Test
    @DisplayName("Standard log levels (trace/debug/info/warn/error/fatal) must work without exception")
    void standardLogLevelsMustWork() {
        assertDoesNotThrow(() -> {
            logger.trace("Upgrade validation — TRACE level");
            logger.debug("Upgrade validation — DEBUG level");
            logger.info("Upgrade validation — INFO level");
            logger.warn("Upgrade validation — WARN level");
            logger.error("Upgrade validation — ERROR level");
            logger.fatal("Upgrade validation — FATAL level");
        }, "All standard log levels must be callable without exception after the upgrade");
    }

    @Test
    @DisplayName("Logging with Throwable argument must work correctly")
    void loggingWithThrowableMustWork() {
        assertDoesNotThrow(() -> {
            Exception testException = new RuntimeException("Upgrade validation test exception");
            logger.error("Error with exception", testException);
            logger.warn("Warn with exception", testException);
        }, "Logging with a Throwable must work correctly after the upgrade");
    }

    @Test
    @DisplayName("Parameterised log messages must work correctly")
    void parameterisedLogMessagesMustWork() {
        assertDoesNotThrow(() -> {
            logger.info("Parameterised message: {} {}", "hello", "world");
            logger.debug("Multiple params: {}, {}, {}", 1, 2, 3);
            logger.warn("Named param test: value={}", "test-value");
        }, "Parameterised log messages must work correctly after the upgrade");
    }

    @Test
    @DisplayName("ThreadContext (MDC) put/get/remove must work correctly")
    void threadContextMdcMustWork() {
        assertDoesNotThrow(() -> {
            ThreadContext.put("requestId", "req-12345");
            ThreadContext.put("userId", "user-67890");

            assertEquals("req-12345", ThreadContext.get("requestId"),
                    "ThreadContext.get() must return the value that was put");
            assertEquals("user-67890", ThreadContext.get("userId"),
                    "ThreadContext.get() must return the value that was put");

            logger.info("Log with MDC context");

            ThreadContext.remove("requestId");
            assertNull(ThreadContext.get("requestId"),
                    "ThreadContext.get() must return null after remove()");

            ThreadContext.clearMap();
            assertTrue(ThreadContext.isEmpty(),
                    "ThreadContext must be empty after clearMap()");
        }, "ThreadContext (MDC) operations must work correctly after the upgrade");
    }

    @Test
    @DisplayName("ThreadContext stack (NDC) must work correctly")
    void threadContextNdcMustWork() {
        assertDoesNotThrow(() -> {
            ThreadContext.push("outer-context");
            ThreadContext.push("inner-context");

            assertFalse(ThreadContext.getDepth() == 0,
                    "ThreadContext stack must have entries after push()");

            logger.info("Log with NDC stack");

            ThreadContext.pop();
            ThreadContext.clearStack();
        }, "ThreadContext NDC stack operations must work correctly after the upgrade");
    }

    @Test
    @DisplayName("LogManager.getLogger() must return a functional logger instance")
    void logManagerGetLoggerMustReturnFunctionalLogger() {
        Logger namedLogger = LogManager.getLogger("com.example.upgrade.validation");
        assertNotNull(namedLogger, "LogManager.getLogger() must return a non-null logger");
        assertDoesNotThrow(() -> namedLogger.info("Named logger test"),
                "Named logger must be callable without exception");
    }

    @Test
    @DisplayName("LoggerContext must be accessible and return a valid Configuration")
    void loggerContextMustReturnValidConfiguration() {
        assertNotNull(loggerContext, "LoggerContext must not be null");
        assertNotNull(configuration, "Configuration obtained from LoggerContext must not be null");
        assertNotNull(configuration.getName(),
                "Configuration must have a non-null name");
    }

    // -------------------------------------------------------------------------
    // 5. Deprecated workaround property must NOT be relied upon
    // -------------------------------------------------------------------------

    @Test
    @DisplayName("log4j2.formatMsgNoLookups workaround property must not be the sole mitigation")
    void formatMsgNoLookupsWorkaroundMustNotBeSoleMitigation() {
        // formatMsgNoLookups=true was the interim workaround for 2.10–2.14.1.
        // After upgrading to 2.17.2 the fix is structural; the property is no
        // longer needed and its presence may indicate the upgrade was not applied.
        // We verify the version is safe regardless of this property's value.
        String formatMsgNoLookups = System.getProperty("log4j2.formatMsgNoLookups");
        Package log4jPackage = org.apache.logging.log4j.core.Logger.class.getPackage();
        String version = log4jPackage != null ? log4jPackage.getImplementationVersion() : null;

        if ("true".equalsIgnoreCase(formatMsgNoLookups)) {
            // Property is still set — warn but also assert the version is safe.
            System.out.println("[WARN] log4j2.formatMsgNoLookups=true is still set. " +
                    "This property is no longer required in 2.17.2+ and can be removed.");
        }

        // The version check is the authoritative assertion.
        assertNotNull(version, "log4j-core version must be determinable");
        assertTrue(isVersionAtLeast(version, MINIMUM_SAFE_VERSION),
                "Even with formatMsgNoLookups set, the version '" + version +
                "' must be >= " + MINIMUM_SAFE_VERSION + " for full remediation.");
    }

    // -------------------------------------------------------------------------
    // 6. log4j-api version must match log4j-core version
    // -------------------------------------------------------------------------

    @Test
    @DisplayName("log4j-api version must match log4j-core version")
    void log4jApiVersionMustMatchCoreVersion() {
        Package corePackage = org.apache.logging.log4j.core.Logger.class.getPackage();
        Package apiPackage = org.apache.logging.log4j.Logger.class.getPackage();

        assertNotNull(corePackage, "log4j-core package must be present");
        assertNotNull(apiPackage, "log4j-api package must be present");

        String coreVersion = corePackage.getImplementationVersion();
        String apiVersion = apiPackage.getImplementationVersion();

        assertNotNull(coreVersion, "log4j-core version must be present in manifest");
        assertNotNull(apiVersion, "log4j-api version must be present in manifest");

        assertEquals(coreVersion, apiVersion,
                String.format(
                        "log4j-api version '%s' must match log4j-core version '%s'. " +
                        "Mismatched versions can cause runtime incompatibilities.",
                        apiVersion, coreVersion));
    }

    // -------------------------------------------------------------------------
    // Helper utilities
    // -------------------------------------------------------------------------

    /**
     * Compares two version strings of the form MAJOR.MINOR.PATCH.
     *
     * @param actual  the version string to test (e.g. "2.17.2")
     * @param minimum the minimum acceptable version (e.g. "2.17.2")
     * @return true if actual >= minimum
     */
    private static boolean isVersionAtLeast(String actual, String minimum) {
        int[] actualParts = parseVersion(actual);
        int[] minimumParts = parseVersion(minimum);
        for (int i = 0; i < Math.max(actualParts.length, minimumParts.length); i++) {
            int a = i < actualParts.length ? actualParts[i] : 0;
            int m = i < minimumParts.length ? minimumParts[i] : 0;
            if (a > m) return true;
            if (a < m) return false;
        }
        return true; // equal
    }

    private static int[] parseVersion(String version) {
        // Strip any trailing qualifier (e.g. "-SNAPSHOT", ".RC1")
        String cleaned = version.replaceAll("[^0-9.].*$", "");
        String[] parts = cleaned.split("\\.");
        int[] result = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            try {
                result[i] = Integer.parseInt(parts[i]);
            } catch (NumberFormatException e) {
                result[i] = 0;
            }
        }
        return result;
    }
}