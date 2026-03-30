# Webhooks: Troubleshooting delivery failures

If webhooks fail with 401/403:
- verify your endpoint auth
- confirm signature validation and shared secret
- check if the secret rotated

If retries are happening:
- ensure 2xx response within 5 seconds

Collect:
- endpoint URL (redacted)
- response code
- signature header example
