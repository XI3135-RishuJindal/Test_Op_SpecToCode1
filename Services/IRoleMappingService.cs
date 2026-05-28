```csharp
using System.Collections.Generic;

public interface IRoleMappingService
{
    IEnumerable<string> GetRolesForUser(string username);
}
```