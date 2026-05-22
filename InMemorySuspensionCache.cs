using System;
using System.Collections.Generic;
using Microsoft.Extensions.Caching.Memory;

namespace ApiGateway.Caching
{
    public class InMemorySuspensionCache
    {
        private readonly IMemoryCache _cache;
        private readonly TimeSpan _suspensionDuration;

        public InMemorySuspensionCache(IMemoryCache cache)
        {
            _cache = cache;
            // TODO: Duration should be configurable
            _suspensionDuration = TimeSpan.FromMinutes(15);
        }

        public void SuspendSubject(string subject)
        {
            var cacheKey = GetCacheKey(subject);
            _cache.Set(cacheKey, true, _suspensionDuration);
        }

        public bool IsSubjectSuspended(string subject)
        {
            return _cache.TryGetValue(GetCacheKey(subject), out _);
        }

        private string GetCacheKey(string subject)
        {
            return $"Suspension_{subject}";
        }
    }
}