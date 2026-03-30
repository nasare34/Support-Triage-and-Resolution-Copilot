# Authentication: MFA troubleshooting

Symptoms:
- MFA prompt loops
- Codes rejected

Steps:
1. Verify device time is correct (time drift breaks TOTP)
2. Try backup codes (if enabled)
3. Admin can disable/re-enable MFA for the user

Escalate if:
- multiple users affected (possible outage)
