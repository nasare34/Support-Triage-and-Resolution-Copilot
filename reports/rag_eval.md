# RAG Evaluation Report

## Summary

| Metric | Value |
|--------|-------|
| Questions evaluated | 40 |
| Top-K | 5 |
| Avg Recall@5 | 0.488 |
| Avg MRR | 0.755 |
| Avg Coverage | 0.875 |
| Perfect recall | 6 / 40 |
| Failures (recall < 0.5) | 17 / 40 |

## Metrics Explanation

- **Recall@K**: fraction of expected KB docs found in top-K results.
- **MRR**: reciprocal rank of the first expected doc. Higher = relevant docs ranked earlier.
- **Coverage**: did at least one expected doc appear in top-K results.

## Per-Question Results

| ID | Subject | Recall@K | MRR | Coverage | Missed Docs |
|----|---------|----------|-----|----------|-------------|
| E001 | API returns 429 rate limit too quickly | 0.4 | 1.0 | 1 | api_tokens_scopes, webhooks_troubleshooting, slack_integration |
| E002 | Feature request: bulk tag tickets | 1.0 | 0.5 | 1 | — |
| E003 | Need help creating API token | 0.2 | 1.0 | 1 | api_tokens_scopes, webhooks_troubleshooting, slack_integration, zapier_integration |
| E004 | Change billing email for account | 0.333 | 0.2 | 1 | account_upgrade_proration, account_ownership_transfer |
| E005 | Charged twice for my subscription | 0.667 | 1.0 | 1 | account_upgrade_proration |
| E006 | Getting intermittent 500 errors | 0.5 | 0.333 | 1 | incidents_status_page |
| E007 | Mobile app crashes on launch | 0.5 | 0.333 | 1 | bugs_notifications |
| E008 | Feature request: bulk tag tickets | 1.0 | 0.5 | 1 | — |
| E009 | SSO login loop with Okta | 0.75 | 1.0 | 1 | auth_password_reset |
| E010 | Mobile app crashes on launch | 0.0 | 0.0 | 0 | bugs_attachments, bugs_notifications |
| E011 | Notifications not sending | 0.5 | 1.0 | 1 | bugs_attachments |
| E012 | Requesting SOC 2 report | 0.667 | 1.0 | 1 | security_gdpr_deletion |
| E013 | Zapier trigger stopped working | 0.2 | 1.0 | 1 | api_tokens_scopes, api_rate_limits, webhooks_troubleshooting, slack_integration |
| E014 | Would love a dark mode | 1.0 | 1.0 | 1 | — |
| E015 | Slack integration not posting messages | 0.2 | 1.0 | 1 | api_tokens_scopes, api_rate_limits, webhooks_troubleshooting, zapier_integration |
| E016 | CSV export missing columns | 0.667 | 1.0 | 1 | reports_dashboard_stale |
| E017 | Reports dashboard not updating | 0.667 | 1.0 | 1 | exports_csv |
| E018 | Notifications not sending | 0.5 | 1.0 | 1 | bugs_attachments |
| E019 | Need help creating API token | 0.2 | 1.0 | 1 | api_tokens_scopes, webhooks_troubleshooting, slack_integration, zapier_integration |
| E020 | Payment failed but card was charged | 0.333 | 1.0 | 1 | billing_invoices_vat, account_upgrade_proration |
| E021 | How to download audit logs? | 0.667 | 1.0 | 1 | exports_csv |
| E022 | How to configure IP allowlist? | 1.0 | 1.0 | 1 | — |
| E023 | Notifications not sending | 0.5 | 1.0 | 1 | bugs_attachments |
| E024 | Can you add SSO for Azure AD? | 0.0 | 0.0 | 0 | feature_requests_process |
| E025 | Reports dashboard not updating | 0.333 | 1.0 | 1 | exports_csv, reports_dashboard_stale |
| E026 | Search requests timing out | 0.0 | 0.0 | 0 | performance_latency, incidents_status_page |
| E027 | Cancel subscription and export data | 0.333 | 0.5 | 1 | account_upgrade_proration, account_ownership_transfer |
| E028 | Password reset email not arriving | 0.5 | 1.0 | 1 | auth_sso_saml_okta, auth_account_lockout |
| E029 | Search requests timing out | 0.5 | 1.0 | 1 | performance_latency |
| E030 | Possible security incident report | 0.667 | 1.0 | 1 | security_gdpr_deletion |
| E031 | API returns 429 rate limit too quickly | 0.4 | 1.0 | 1 | api_tokens_scopes, webhooks_troubleshooting, zapier_integration |
| E032 | Invoice shows incorrect VAT for May | 0.667 | 1.0 | 1 | account_upgrade_proration |
| E033 | Possible security incident report | 1.0 | 0.5 | 1 | — |
| E034 | Workspace ownership transfer | 0.333 | 1.0 | 1 | account_upgrade_proration, account_cancel_export |
| E035 | SSO login loop with Okta | 0.5 | 1.0 | 1 | auth_password_reset, auth_mfa_troubleshooting |
| E036 | Would love a dark mode | 0.0 | 0.0 | 0 | feature_requests_process |
| E037 | Roadmap question: AI summary per ticket | 0.0 | 0.0 | 0 | feature_requests_process |
| E038 | Service appears down for our team | 0.5 | 1.0 | 1 | performance_latency |
| E039 | Can you add SSO for Azure AD? | 1.0 | 0.333 | 1 | — |
| E040 | Change billing email for account | 0.333 | 1.0 | 1 | account_upgrade_proration, account_ownership_transfer |

## Failure Analysis

### Common failure patterns

**E001** — *API returns 429 rate limit too quickly*
- Expected: ['api_tokens_scopes', 'api_rate_limits', 'webhooks_troubleshooting', 'slack_integration', 'zapier_integration']
- Retrieved: ['zapier_integration', 'api_rate_limits', 'security_ip_allowlist', 'account_ownership_transfer', 'auth_mfa_troubleshooting']
- Missed: ['api_tokens_scopes', 'webhooks_troubleshooting', 'slack_integration']

**E003** — *Need help creating API token*
- Expected: ['api_tokens_scopes', 'api_rate_limits', 'webhooks_troubleshooting', 'slack_integration', 'zapier_integration']
- Retrieved: ['api_rate_limits', 'security_gdpr_deletion', 'account_cancel_export', 'exports_audit_logs', 'feature_requests_process']
- Missed: ['api_tokens_scopes', 'webhooks_troubleshooting', 'slack_integration', 'zapier_integration']

**E004** — *Change billing email for account*
- Expected: ['account_upgrade_proration', 'account_cancel_export', 'account_ownership_transfer']
- Retrieved: ['billing_invoices_vat', 'security_gdpr_deletion', 'auth_password_reset', 'billing_refunds', 'account_cancel_export']
- Missed: ['account_upgrade_proration', 'account_ownership_transfer']

**E010** — *Mobile app crashes on launch*
- Expected: ['bugs_attachments', 'bugs_notifications']
- Retrieved: ['security_ip_allowlist', 'billing_refunds', 'auth_password_reset', 'auth_mfa_troubleshooting', 'performance_latency']
- Missed: ['bugs_attachments', 'bugs_notifications']

**E013** — *Zapier trigger stopped working*
- Expected: ['api_tokens_scopes', 'api_rate_limits', 'webhooks_troubleshooting', 'slack_integration', 'zapier_integration']
- Retrieved: ['zapier_integration', 'security_gdpr_deletion', 'auth_password_reset', 'account_ownership_transfer', 'security_encryption']
- Missed: ['api_tokens_scopes', 'api_rate_limits', 'webhooks_troubleshooting', 'slack_integration']

**E015** — *Slack integration not posting messages*
- Expected: ['api_tokens_scopes', 'api_rate_limits', 'webhooks_troubleshooting', 'slack_integration', 'zapier_integration']
- Retrieved: ['slack_integration', 'security_ip_allowlist', 'account_ownership_transfer', 'auth_password_reset', 'auth_mfa_troubleshooting']
- Missed: ['api_tokens_scopes', 'api_rate_limits', 'webhooks_troubleshooting', 'zapier_integration']

**E019** — *Need help creating API token*
- Expected: ['api_tokens_scopes', 'api_rate_limits', 'webhooks_troubleshooting', 'slack_integration', 'zapier_integration']
- Retrieved: ['api_rate_limits', 'security_gdpr_deletion', 'account_cancel_export', 'exports_audit_logs', 'feature_requests_process']
- Missed: ['api_tokens_scopes', 'webhooks_troubleshooting', 'slack_integration', 'zapier_integration']

**E020** — *Payment failed but card was charged*
- Expected: ['billing_refunds', 'billing_invoices_vat', 'account_upgrade_proration']
- Retrieved: ['billing_refunds', 'security_gdpr_deletion', 'incidents_status_page', 'billing_refunds', 'security_encryption']
- Missed: ['billing_invoices_vat', 'account_upgrade_proration']

**E024** — *Can you add SSO for Azure AD?*
- Expected: ['feature_requests_process']
- Retrieved: ['security_ip_allowlist', 'exports_audit_logs', 'auth_mfa_troubleshooting', 'security_encryption', 'account_upgrade_proration']
- Missed: ['feature_requests_process']

**E025** — *Reports dashboard not updating*
- Expected: ['exports_csv', 'exports_audit_logs', 'reports_dashboard_stale']
- Retrieved: ['exports_audit_logs', 'billing_refunds', 'account_cancel_export', 'security_gdpr_deletion', 'security_encryption']
- Missed: ['exports_csv', 'reports_dashboard_stale']

**E026** — *Search requests timing out*
- Expected: ['performance_latency', 'incidents_status_page']
- Retrieved: ['security_gdpr_deletion', 'feature_requests_process', 'billing_refunds', 'security_encryption', 'security_ip_allowlist']
- Missed: ['performance_latency', 'incidents_status_page']

**E027** — *Cancel subscription and export data*
- Expected: ['account_upgrade_proration', 'account_cancel_export', 'account_ownership_transfer']
- Retrieved: ['billing_invoices_vat', 'account_cancel_export', 'security_gdpr_deletion', 'billing_refunds', 'auth_password_reset']
- Missed: ['account_upgrade_proration', 'account_ownership_transfer']

**E031** — *API returns 429 rate limit too quickly*
- Expected: ['api_tokens_scopes', 'api_rate_limits', 'webhooks_troubleshooting', 'slack_integration', 'zapier_integration']
- Retrieved: ['slack_integration', 'api_rate_limits', 'security_ip_allowlist', 'performance_latency', 'account_ownership_transfer']
- Missed: ['api_tokens_scopes', 'webhooks_troubleshooting', 'zapier_integration']

**E034** — *Workspace ownership transfer*
- Expected: ['account_upgrade_proration', 'account_cancel_export', 'account_ownership_transfer']
- Retrieved: ['account_ownership_transfer', 'billing_refunds', 'slack_integration', 'feature_requests_process', 'auth_password_reset']
- Missed: ['account_upgrade_proration', 'account_cancel_export']

**E036** — *Would love a dark mode*
- Expected: ['feature_requests_process']
- Retrieved: ['security_ip_allowlist', 'auth_mfa_troubleshooting', 'account_upgrade_proration', 'exports_audit_logs', 'auth_password_reset']
- Missed: ['feature_requests_process']

**E037** — *Roadmap question: AI summary per ticket*
- Expected: ['feature_requests_process']
- Retrieved: ['exports_audit_logs', 'security_ip_allowlist', 'api_rate_limits', 'security_gdpr_deletion', 'billing_invoices_vat']
- Missed: ['feature_requests_process']

**E040** — *Change billing email for account*
- Expected: ['account_upgrade_proration', 'account_cancel_export', 'account_ownership_transfer']
- Retrieved: ['account_cancel_export', 'billing_invoices_vat', 'security_gdpr_deletion', 'auth_password_reset', 'billing_refunds']
- Missed: ['account_upgrade_proration', 'account_ownership_transfer']

### Root causes

1. **Vocabulary mismatch**: informal query language does not overlap with KB terminology.
2. **Multi-doc queries**: some questions expect 5+ docs but top-K may not capture all.
3. **Short KB docs**: sparse TF-IDF targets. Semantic embeddings would improve this.

## Improvement Roadmap

- Replace TF-IDF with dense embeddings (sentence-transformers) for semantic similarity
- Add BM25 hybrid retrieval for vocabulary-exact matches
- Query expansion using LLM rephrasing before retrieval
- Re-rank retrieved chunks with a cross-encoder