#!/bin/sh
set -e

flask --app shpr init-db

if [ "$ENABLE_HTTPS" = "true" ]; then
  flask --app shpr run --cert "$SSL_CERT_PATH" --key "$SSL_KEY_PATH"
else
  exec flask --app shpr run
fi