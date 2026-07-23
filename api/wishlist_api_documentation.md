# Wishlist API Documentation

## Overview
The Wishlist API enables users to manage their personal wishlists within the CarePay application. This API provides endpoints for adding and removing products from a wishlist and is only accessible to authenticated users.

## Authentication
All Wishlist API endpoints require the user to be authenticated. Ensure that the authentication token is included in the request headers.

## Endpoints

### 1. Add Product to Wishlist
- **Endpoint:** `/api/wishlist/add`
- **Method:** POST
- **Description:** Adds a product to the user's wishlist.
- **Request Headers:**
  - `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "product_id": "string"
  }
  ```
- **Response:**
  - **Success (200):** Product successfully added to wishlist.
    ```json
    {
      "message": "Product added to wishlist",
      "wishlist": {
        "user_id": "string",
        "products": ["string"]
      }
    }
    ```
  - **Failure (400):** Invalid request format or missing product ID.
    ```json
    {
      "error": "Invalid request"
    }
    ```
  - **Failure (401):** Unauthorized access.
    ```json
    {
      "error": "Unauthorized"
    }
    ```

### 2. Remove Product from Wishlist
- **Endpoint:** `/api/wishlist/remove`
- **Method:** POST
- **Description:** Removes a product from the user’s wishlist.
- **Request Headers:**
  - `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "product_id": "string"
  }
  ```
- **Response:**
  - **Success (200):** Product successfully removed from wishlist.
    ```json
    {
      "message": "Product removed from wishlist",
      "wishlist": {
        "user_id": "string",
        "products": ["string"]
      }
    }
    ```
  - **Failure (400):** Invalid request format or missing product ID.
    ```json
    {
      "error": "Invalid request"
    }
    ```
  - **Failure (401):** Unauthorized access.
    ```json
    {
      "error": "Unauthorized"
    }
    ```

## Error Codes
- **401 Unauthorized:** The user must be authenticated to access these endpoints.
- **400 Bad Request:** The request is malformed or missing required fields.

---

This document provides the details necessary for integrating the Wishlist API into client applications.