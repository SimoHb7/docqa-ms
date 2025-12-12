#!/bin/bash
# Fix CSP headers to allow Swagger UI

sed -i "s|script-src 'self' 'unsafe-inline' 'unsafe-eval' https://\*\.auth0\.com;|script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.auth0.com https://cdn.jsdelivr.net;|g" /app/app/main.py

sed -i "s|style-src 'self' 'unsafe-inline' https://fonts\.googleapis\.com;|style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net;|g" /app/app/main.py

echo "CSP headers fixed!"
cat /app/app/main.py | grep "Content-Security-Policy" -A 8
