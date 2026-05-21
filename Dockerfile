FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY ["*.sln", "./"]
COPY ["src/**/*.csproj", "src/"]
COPY ["tests/**/*.csproj", "tests/"]

RUN dotnet restore

COPY . .

RUN dotnet build --no-restore -c Release

FROM build AS test
WORKDIR /src
RUN dotnet test --no-build -c Release --logger "trx;LogFileName=test-results.trx" --results-directory /testresults

FROM build AS publish
WORKDIR /src
RUN dotnet publish --no-build -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

COPY --from=publish /app/publish .

EXPOSE 8080
ENTRYPOINT ["dotnet", "app.dll"]