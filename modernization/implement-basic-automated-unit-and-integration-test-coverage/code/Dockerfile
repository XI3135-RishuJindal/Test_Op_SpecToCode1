# syntax=docker/dockerfile:1

FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /app
COPY . ./
RUN dotnet restore
RUN dotnet build --no-restore -c Release
RUN dotnet test --no-build --verbosity normal

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS runtime
WORKDIR /app
COPY --from=build /app/bin/Release/net8.0/publish/ ./
ENTRYPOINT ["dotnet", "YourApp.dll"]