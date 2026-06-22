# User Management Service

This is a Node.js service for managing user registration, authentication, and password management.

## Features
- **User Registration**: Allow new users to register with a username and password.
- **Authentication**: Securely authenticate users and issue JWT tokens.
- **Password Management**: Secure storage and verification of user passwords using bcrypt.

## Technology Stack
- **Node.js**
- **Express**
- **JWT for authentication**
- **Bcrypt for password hashing**

## Getting Started
1. Clone the repository.
2. Install dependencies: `npm install`
3. Set up environment variables using the provided `.env.example` as a guide.
4. Start the application: `npm start`

## Docker
You can run the application in a Docker container:
```bash
# Build the Docker image
docker build -t user-management-service .

# Run the Docker container
docker run -p 3000:3000 user-management-service
```

## API Endpoints
- **Health Check**: GET /health

## Testing
Run tests using Jest:
```bash
npm test
```
