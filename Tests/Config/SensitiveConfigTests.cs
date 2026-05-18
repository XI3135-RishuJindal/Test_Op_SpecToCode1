using Xunit;
using System.IO;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;

public class SensitiveConfigTests
{
    private readonly List<string> disallowedKeys = new List<string>
    {
        "sk_live_", "pk_live_", "ClientSecret", "access_token", "MerchantId", "PublicKey", "PrivateKey", "TokenizationKey", "ApiKey", "KeyId", "KeySecret", "sq0atp"
    };

    private readonly string[] configFiles = new[]
    {
        "appsettings.json",
        "appsettings.Development.json",
        "Properties/launchSettings.json"
    };

    [Fact]
    public void ConfigFiles_DoNotContainSensitiveKeys()
    {
        foreach (var configFile in configFiles)
        {
            Assert.False(ContainsDisallowedKeys(configFile), $"Sensitive keys found in {configFile}");
        }
    }

    private bool ContainsDisallowedKeys(string configFile)
    {
        if (!File.Exists(configFile)) return false;

        var json = File.ReadAllText(configFile);
        var jObject = JObject.Parse(json);
        foreach (var key in disallowedKeys)
        {
            if (jObject.Descendants().OfType<JProperty>().Any(prop => prop.Name.Contains(key)))
            {
                return true;
            }
        }
        return false;
    }
}