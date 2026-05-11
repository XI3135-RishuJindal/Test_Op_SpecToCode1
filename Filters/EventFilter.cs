using Microsoft.Extensions.Logging;
using System;

namespace Filters
{
    public class EventFilter : ILoggingEventFilter
    {
        private readonly string[] _excludedEvents;

        public EventFilter(IConfiguration configuration)
        {
            _excludedEvents = configuration["FinancialEventLogging:ExcludedEvents"].Split(',');
        }

        public bool ShouldLogEvent(LogEvent logEvent)
        {
            return !_excludedEvents.Any(eventType => logEvent.Message.Contains(eventType, StringComparison.OrdinalIgnoreCase));
        }
    }
}