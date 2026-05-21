FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

WORKDIR /app

COPY *.csproj ./
RUN dotnet restore

COPY . ./
RUN dotnet build -c Release --no-restore

RUN dotnet tool install --global dotnet-ef
ENV PATH="$PATH:/root/.dotnet/tools"

FROM build AS migration

WORKDIR /app

RUN dotnet ef migrations add InitialMigration --no-build -c Release || true

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime

WORKDIR /app

COPY --from=build /app/bin/Release/net8.0/publish ./

ENTRYPOINT ["dotnet"]