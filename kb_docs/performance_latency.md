# Performance: Latency troubleshooting

If the app is slow:
- capture region, time window, and affected pages
- collect correlation IDs from API responses

Mitigations:
- reduce heavy filters in searches
- paginate exports

Escalate P0 if:
- widespread outage
- 500 errors across multiple endpoints
