# Fraud Detection Service

This service evaluates transactions for fraud and authorizes legitimate transactions. It is built using Java and incorporates various machine learning algorithms to detect fraudulent activities.

## Running the Service

To run the service, build the application and start the Docker container:

```bash
mvn clean package

# Build Docker image

docker build -t fraud-detection-service .

# Run Docker container

docker run -p $APP_PORT:8080 fraud-detection-service
```

Access the health check endpoint at `http://localhost:8080/health` to verify if the service is running correctly.