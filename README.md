# User Management Service

This service provides user management capabilities.

## Getting Started

### Prerequisites
- Python 3.9
- Docker

### Running Locally
1. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
2. Run the application:
    ```
    python app/main.py
    ```

### Using Docker
1. Build the docker image:
    ```
    docker build -t user-management-service .
    ```
2. Run the docker container:
    ```
    docker run -p 5000:5000 user-management-service
    ```

### Environment Variables
- `DATABASE_URL`: URL to the database
- `DEBUG`: Enables debug mode if set to `True`
