FROM mcr.microsoft.com/dotnet/sdk:latest AS build
WORKDIR /app
COPY . .
RUN dotnet restore
RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:latest
WORKDIR /app
COPY --from=build /app/out .
ENTRYPOINT ["dotnet", "YourAssemblyName.dll"]