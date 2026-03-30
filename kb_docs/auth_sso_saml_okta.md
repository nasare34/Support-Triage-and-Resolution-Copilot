# SSO (SAML) with Okta

Required fields:
- ACS URL
- Entity ID
- x509 certificate

Common issues:
- "Invalid SAML response" due to clock skew or incorrect Audience/Recipient
- Redirect loops when the IdP initiated flow is misconfigured

When contacting support, include:
- SAML response (redacted)
- correlation/request ID
