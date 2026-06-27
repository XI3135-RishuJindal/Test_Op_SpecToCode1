```markdown
# AGENTS.md for Email Service

## Stack

- **Node.js**: Backend runtime environment.
- **Nodemailer**: Library for sending emails via SMTP.
- **Bull**: A Node library for handling job queues.
- **Jest**: Testing framework for unit tests.
- **Docker**: Containerization platform.
- **GitHub Actions**: For Continuous Integration and Deployment.

## Project Structure

```
/email-service
│
├── /src
│   ├── /config
│   │   └── smtp.js              # SMTP configuration.
│   ├── /controllers
│   │   └── emailController.js   # Logic for sending emails.
│   ├── /services
│   │   ├── queueService.js      # Job queue handling.
│   │   └── emailService.js      # Interaction with Nodemailer.
│   ├── /utils
│   │   └── logger.js            # Logger utility.
│   ├── app.js                   # Express application setup.
│   └── emailWorker.js           # Worker for processing email jobs.
│
├── /test
│   └── emailController.test.js  # Unit tests for emailController.
│
├── .env                         # Environment variables.
├── .gitignore                   # Git ignore settings.
├── Dockerfile                   # Docker setup instructions.
├── docker-compose.yml           # Docker Compose setup for multi-container application.
├── jest.config.js               # Jest configuration.
├── package.json                 # Metadata and dependencies for the project.
└── README.md                    # Project documentation.
```

## Required Workflow

1. **Analyze Specifications**: Investigate requirements for sending verification emails and handling job queues.
2. **Create `tasks.md`**: List and describe implementation tasks.
3. **Implement Features**: Develop services and controllers following tasks breakdown.
4. **Implement Tests**: Write Jest tests for all new features with 90% code coverage.
5. **Run Tests**: Use `npm test` to run Jest tests, ensuring all pass.
6. **Validate with CI**: Commit changes and ensure GitHub Actions validate the build and run tests automatically.

## Coding Conventions

- **Naming**: Use camelCase for variables and functions, and PascalCase for class names.
- **Style**: Follow Airbnb JavaScript Style Guide.
- **Architecture Pattern**: Use the Service Layer pattern to separate business logic.

## Testing

- **Unit Tests**: Utilize Jest for writing and running tests, ensuring 90% coverage.
- **Enforce Coverage**: Configure Jest to fail if coverage falls below 90%.
- **Test Structure**: Organize test files mirroring the directory structure of the implementation.

## Docker & CI

**Docker**

- **Dockerfile**: 
  ```dockerfile
  FROM node:14
  WORKDIR /usr/src/email-service
  COPY package*.json ./
  RUN npm install
  COPY . .
  CMD ["node", "src/app.js"]
  ```
- **docker-compose.yml**:
  ```yaml
  version: '3.8'
  services:
    email-service:
      build: .
      ports:
        - "3000:3000"
      env_file: .env
  ```

**CI/CD with GitHub Actions**

- **Workflow Configuration** (`.github/workflows/ci.yml`):
  ```yaml
  name: CI
  on: [push, pull_request]
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '14'
      - run: npm install
      - run: npm test
  ```

## Constraints

- **Do Not Use Deprecated Libraries**: Ensure all libraries are actively maintained.
- **RESTful Principles**: Follow RESTful conventions for designing API endpoints.
- **Logging**: All operations must be logged using the logger utility.
```