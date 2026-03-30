# API: Rate limits (429)

Default rate limits:
- 60 requests/minute per token
- burst up to 20 requests

Mitigation:
- use exponential backoff
- cache results
- batch endpoints where available

If you need higher limits:
- provide use case + expected throughput
