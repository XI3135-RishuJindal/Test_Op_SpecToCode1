using Xunit;
using Serilog.Events;

public class EventFilterTests
{
    [Fact]
    public void ShouldLog_WhenEventIsNotFinancial_ReturnsTrue()
    {
        // Arrange
        var filter = new EventFilter(new[] { "Payment", "Transfer" });
        var logEvent = new LogEvent(DateTimeOffset.Now, LogEventLevel.Information, null, new MessageTemplate("Test", new List<MessageTemplateToken>()), new List<LogEventProperty>());

        // Act
        var result = filter.ShouldLog(logEvent);

        // Assert
        Assert.True(result);
    }

    [Fact]
    public void ShouldLog_WhenEventIsFinancial_ReturnsFalse()
    {
        // Arrange
        var filter = new EventFilter(new[] { "Payment", "Transfer" });
        var logEvent = new LogEvent(DateTimeOffset.Now, LogEventLevel.Information, null, new MessageTemplate("Test", new List<MessageTemplateToken>()), new List<LogEventProperty> {
            new LogEventProperty("EventType", new ScalarValue("Payment"))
        });

        // Act
        var result = filter.ShouldLog(logEvent);

        // Assert
        Assert.False(result);
    }
}
