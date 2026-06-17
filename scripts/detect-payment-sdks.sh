#!/bin/bash
set -euo pipefail

# Path to the allow-list
ALLOW_LIST_PATH=".security/allowed-payment-sdks.txt"

# Function to check if a given payment SDK is allowed
is_allowed() {
  local sdk_name="$1"
  grep -q -x "$sdk_name" "$ALLOW_LIST_PATH"
}

# Search for payment-related terms (example) in the codebase
for sdk in "Stripe" "PayPal" "Adyen"; do
  if grep -qr "$sdk" ./; then
    if ! is_allowed "$sdk"; then
      echo "Unapproved payment SDK detected: $sdk"
      exit 1
    fi
  fi
done

# If no disallowed SDKs are found
echo "No unapproved payment SDKs detected."