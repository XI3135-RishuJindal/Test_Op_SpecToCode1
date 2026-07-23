```csharp
using System;
using NBomber.Contracts;
using NBomber.CSharp;

namespace LoadTest
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Starting NLP Performance Test...");
            NLPPerformanceTest.Run();
            Console.WriteLine("Test completed.");
        }
    }
}
```