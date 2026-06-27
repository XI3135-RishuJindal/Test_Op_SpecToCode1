# Email Service

## Overview
A service for managing and sending emails, following the principles of hexagonal architecture.

## Project Structure
- **src/application/**: Application-specific logic.
- **src/domain/**: Core business logic and domain models.
- **src/infrastructure/**: Data access and external interaction.
- **src/interfaces/**: User interaction interfaces (e.g., API).

## Setup & Run

1. Clone the repository.
2. Create a virtual environment `python -m venv venv`
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On Unix or MacOS: `source venv/bin/activate`
4. Install dependencies:
   ```shell
   pip install -r requirements.txt
   ```
5. Run the application:
   ```shell
   python src/interfaces/api.py
   ```

## Docker

To run the service in a Docker container:
