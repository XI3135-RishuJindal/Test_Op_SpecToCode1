FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY *.sln ./
COPY **/*.csproj ./
RUN find . -name "*.csproj" | while read f; do \
      dir=$(dirname "$f"); \
      mkdir -p "$dir"; \
      mv "$f" "$dir/"; \
    done

RUN dotnet restore

COPY . .
RUN dotnet publish -c Release -o /app/publish --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/publish .

ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production
ENV ConnectionStrings__DefaultConnection="Data Source=/data/app.db"

VOLUME ["/data"]

EXPOSE 8080

ENTRYPOINT ["dotnet", "app.dll"]