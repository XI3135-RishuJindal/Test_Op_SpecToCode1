```csharp
using Xunit;

public class DependencyScanTests
{
    [Fact]
    public void DependencyScan_ShouldNotContainPaymentSDKs()
    {
        // Arrange
        var scanResults = GetDependencyScanResults(); // Replace with actual method to retrieve scan results

        // Act
        bool containsPaymentSDKs = scanResults.Any(r => 
            r.Name.StartsWith("payment-sdk-"));

        // Assert
        Assert.False(containsPaymentSDKs, "Dependency scan contained payment SDKs.");
    }

    private List<DependencyResult> GetDependencyScanResults()
    {
        // Placeholder for actual implementation to retrieve dependency scan results
        return new List<DependencyResult>();
    }
}

public class DependencyResult
{
    public string Name { get; set; }
    public string Version { get; set; }
}
```