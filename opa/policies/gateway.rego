package gateway.authz

import future.keywords.if
import future.keywords.in

# Default deny
default allow = false

# Allow if principal has required scope
allow if {
    some scope in input.principal.scopes
    scope == input.action
}

# Allow if principal is admin
allow if {
    "admin" in input.principal.roles
}

# Allow if principal has admin scope
allow if {
    "admin" in input.principal.scopes
}

# Scope-based rules per resource pattern
allow if {
    startswith(input.resource, "/api/v1/users")
    input.action in ["GET", "users:read"]
    "users:read" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/users")
    input.action in ["POST", "PUT", "users:write"]
    "users:write" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/users")
    input.action in ["DELETE", "users:delete"]
    "users:delete" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/reports")
    input.action in ["GET", "reports:read"]
    "reports:read" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/reports")
    input.action in ["POST", "PUT", "reports:write"]
    "reports:write" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/payments")
    input.action in ["GET", "payments:read"]
    "payments:read" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/payments")
    input.action in ["POST", "payments:write"]
    "payments:write" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/payments")
    contains(input.resource, "/refund")
    "payments:refund" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/gateway")
    "admin:gateway" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/gateway/rbac")
    "admin:rbac" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/gateway/audit-logs")
    "admin:audit" in input.principal.scopes
}

allow if {
    input.resource == "/metrics"
    "admin:metrics" in input.principal.scopes
}

allow if {
    startswith(input.resource, "/api/v1/auth/mfa/enroll")
    "mfa:enroll" in input.principal.scopes
}
