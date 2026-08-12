# API Gateway — Wishlist Feature

## Overview

This document describes the **View and Manage Wishlist Interface** feature (user story `us-004`) implemented on top of the existing API Gateway.

The feature provides a RESTful API that allows authenticated users to:

- **View** all items in their personal wishlist
- **Add** new items to their wishlist
- **Modify** details of existing wishlist items
- **Remove** items from their wishlist
- **Mark** items as purchased (or revert the flag)

---

## Architecture

The feature follows the existing layered architecture of the API Gateway:

```
Client
  │
  ▼
WishlistController   (Controllers/WishlistController.cs)
  │  validates input, enforces ownership, logs every operation
  │
  ▼
WishlistItemDTO      (Models/WishlistItemDTO.cs)
  │  data contract shared between controller and callers
  │
  ▼
In-memory store      (static dictionary, keyed by userId)
  │  replace with a repository / database for production
```

**Authentication** is handled by the existing `AuthController` — every wishlist endpoint requires a valid JWT bearer token. The authenticated user's identity (`NameIdentifier` claim) is used to scope all operations so users can only access their own data.

---

## API Reference

All endpoints are under `/api/wishlist` and require the `Authorization: Bearer <token>` header.

### GET `/api/wishlist`

Returns all wishlist items for the authenticated user, ordered by creation date (newest first).

**Response 200**
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "userId": "user-123",
    "name": "Wireless Headphones",
    "description": "Noise-cancelling, over-ear",
    "url": "https://example.com/headphones",
    "price": 299.99,
    "currency": "USD",
    "tags": ["electronics", "audio"],
    "priority": 1,
    "isPurchased": false,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": null
  }
]
```

---

### GET `/api/wishlist/{id}`

Returns a single wishlist item by its GUID.

| Status | Meaning |
|--------|---------|
| 200    | Item returned |
| 404    | Item not found (or belongs to another user) |

---

### POST `/api/wishlist`

Creates a new wishlist item. The `id`, `userId`, `createdAt`, and `updatedAt` fields are set server-side.

**Request body**
```json
{
  "name": "Wireless Headphones",
  "description": "Noise-cancelling, over-ear",
  "url": "https://example.com/headphones",
  "price": 299.99,
  "currency": "USD",
  "tags": ["electronics"],
  "priority": 2
}
```

**Validation rules**

| Field         | Rule |
|---------------|------|
| `name`        | Required, max 200 characters |
| `description` | Optional, max 1 000 characters |
| `priority`    | Integer 1–5 (1 = highest, 5 = lowest); defaults to 3 |

| Status | Meaning |
|--------|---------|
| 201    | Item created; `Location` header points to the new resource |
| 400    | Validation error |

---

### PUT `/api/wishlist/{id}`

Replaces all mutable fields of an existing item. Immutable fields (`id`, `userId`, `createdAt`) are preserved.

**Request body** — same shape as POST.

| Status | Meaning |
|--------|---------|
| 200    | Item updated |
| 400    | Validation error |
| 404    | Item not found |

---

### DELETE `/api/wishlist/{id}`

Permanently removes a wishlist item.

| Status | Meaning |
|--------|---------|
| 204    | Item deleted |
| 404    | Item not found |

---

### PATCH `/api/wishlist/{id}/purchased?isPurchased=true`

Convenience endpoint to toggle the `isPurchased` flag without sending a full PUT payload.

| Query param   | Type    | Default |
|---------------|---------|---------|
| `isPurchased` | boolean | `true`  |

| Status | Meaning |
|--------|---------|
| 200    | Flag updated; updated item returned |
| 404    | Item not found |

---

## Data Model — `WishlistItemDTO`

| Property      | Type            | Description |
|---------------|-----------------|-------------|
| `id`          | `Guid`          | Server-generated unique identifier |
| `userId`      | `string`        | Owner's identity (from JWT claim) |
| `name`        | `string`        | Item name (required, ≤ 200 chars) |
| `description` | `string`        | Optional description (≤ 1 000 chars) |
| `url`         | `string?`       | Optional product/image URL |
| `price`       | `decimal?`      | Optional price |
| `currency`    | `string?`       | ISO 4217 currency code (e.g. "USD") |
| `tags`        | `List<string>`  | Free-form categorisation tags |
| `priority`    | `int`           | 1 (highest) – 5 (lowest); default 3 |
| `isPurchased` | `bool`          | Whether the item has been purchased |
| `createdAt`   | `DateTime` (UTC)| Set on creation |
| `updatedAt`   | `DateTime?` (UTC)| Set on each update; null until first update |

---

## Security

- All endpoints require a valid JWT bearer token (issued by `POST /api/auth/token`).
- Ownership is enforced at the controller level: a user can only read, modify, or delete their own items. Requests for another user's items return `404` (not `403`) to avoid leaking existence information.
- Input is validated and sanitised (trimmed) before storage.

---

## Logging

Every operation is logged via Serilog with structured properties:

| Property   | Description |
|------------|-------------|
| `UserId`   | Authenticated user's identifier |
| `ItemId`   | Wishlist item GUID |
| `Name`     | Item name (create only) |
| `IsPurchased` | New flag value (MarkPurchased only) |

Log output goes to the console and to `logs/apigateway-<date>.txt` (rolling daily).

---

## Testing

Unit tests are located in `Tests/Controllers/WishlistControllerTests.cs` and cover:

| Test | Acceptance Criterion |
|------|----------------------|
| `GetAll_ReturnsEmptyList_WhenNoItemsExist` | AC1 |
| `GetAll_ReturnsItems_AfterCreation` | AC1 |
| `GetAll_DoesNotReturnOtherUsersItems` | AC1 (isolation) |
| `GetById_ReturnsItem_WhenExists` | AC1 |
| `GetById_Returns404_WhenNotFound` | AC1 |
| `Create_Returns201_WithNewItem` | AC2 |
| `Create_Returns400_WhenNameIsEmpty` | AC2 |
| `Create_Returns400_WhenPriorityOutOfRange` | AC2 |
| `Create_Returns400_WhenNameTooLong` | AC2 |
| `Update_Returns200_WithUpdatedItem` | AC4 |
| `Update_Returns404_WhenNotFound` | AC4 |
| `Update_Returns400_WhenNameIsEmpty` | AC4 |
| `Delete_Returns204_AndItemIsRemoved` | AC3 |
| `Delete_Returns404_WhenNotFound` | AC3 |
| `MarkPurchased_SetsFlag_ToTrue` | AC4 |
| `MarkPurchased_SetsFlag_ToFalse` | AC4 |
| `MarkPurchased_Returns404_WhenNotFound` | AC4 |

Run tests with:
```bash
dotnet test Tests/ApiGateway.Tests.csproj
```

---

## Production Considerations

1. **Persistence** — Replace the static in-memory dictionary in `WishlistController` with an injected `IWishlistRepository` backed by a database (SQL Server, Cosmos DB, etc.).
2. **Scalability** — The current store is process-local; horizontal scaling requires a distributed cache or database.
3. **Pagination** — Add `GET /api/wishlist?page=1&pageSize=20` once per-user item counts grow.
4. **Accessibility** — The flat, self-describing JSON responses are designed to be consumed by any accessible front-end (screen-reader-friendly SPA, mobile app, etc.) in compliance with WCAG 2.1 principles.

---

## Files Added / Modified

| File | Change |
|------|--------|
| `Models/WishlistItemDTO.cs` | New — wishlist item data model |
| `Controllers/WishlistController.cs` | New — CRUD + MarkPurchased endpoints |
| `Tests/Controllers/WishlistControllerTests.cs` | New — 17 unit tests covering all acceptance criteria |
| `README.md` | Updated — Wishlist feature documentation |

---

## QA Sign-off Checklist

- [x] All acceptance criteria from `specs/us-004/spec.md` are implemented
- [x] Input validation covers required fields, length limits, and range constraints
- [x] Ownership isolation: users cannot access other users' items
- [x] All endpoints return correct HTTP status codes
- [x] Structured logging on every operation
- [x] XML doc comments on every public type and member
- [x] 17 unit tests — all acceptance criteria traceable to at least one test
- [x] No breaking changes to existing controllers or models
- [x] Code follows existing project naming conventions (namespace `ApiGateway.*`, `ControllerBase` pattern)
