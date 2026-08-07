# Release Readiness Report Template

Use this structure for the final audit report. Adapt sections to the product type.

## 1. Executive Summary

Brief overview of the audit scope, approach, key findings, and recommendation.

## 2. Verdict

**Recommendation**: `GO` | `CONDITIONAL GO` | `NO-GO`

**Confidence Level**: `High` | `Medium` | `Low`

**Rationale**: [1-3 sentences explaining the recommendation]

## 3. Scope Tested

- Product type: [detected type]
- Stack: [languages, frameworks, databases]
- Environment: [local / staging / preview / production read-only]
- Operating mode: [audit-only / audit-and-fix / verify-fixes]
- Date: [audit date]

## 4. Environment and Testing Conditions

| Condition | Value |
|-----------|-------|
| Browser(s) | |
| Device/viewport | |
| Network | |
| Dataset size | |
| Auth state | |

## 5. Assumptions

List any assumptions made due to incomplete requirements or unavailable information.

## 6. Critical User Journeys

| Journey | Status | Evidence | Notes |
|---------|--------|----------|-------|
| Registration | ✅ PASS / ❌ FAIL / ⚠️ WARN / ⏭️ NOT TESTED | | |
| Login/Logout | | | |
| [Primary CRUD] | | | |
| [Add journeys] | | | |

## 7. Performance Budget and Results

| Journey or Endpoint | Metric | Budget | Measured | Status | Conditions |
|---------------------|--------|-------:|--------:|--------|------------|
| Homepage load | LCP | ≤2.5s | | ✅/❌ | Cold cache, broadband |
| API endpoint | p95 | ≤500ms | | | |
| [Add rows] | | | | | |

## 8. Findings by Severity

### Summary Table

| ID | Finding | Severity | Status | Impact | Evidence | Recommended Action |
|----|---------|----------|--------|--------|----------|-------------------|
| F-001 | | Blocker/Critical/High/Medium/Low | Open/Fixed/Accepted/Won't Fix | | | |

### Detailed Findings

For each finding:

#### F-001: [Title]

| Field | Value |
|-------|-------|
| **Severity** | |
| **Product Area** | |
| **Environment** | |
| **Preconditions** | |
| **Steps to Reproduce** | 1. ... 2. ... 3. ... |
| **Expected Result** | |
| **Actual Result** | |
| **User/Business Impact** | |
| **Frequency** | Always / Intermittent / Rare |
| **Evidence** | [screenshot, log, measurement] |
| **Suspected Root Cause** | [Confirmed / Unconfirmed] |
| **Recommended Correction** | |
| **Retest Result** | [if retested] |

## 9. Security Findings

Separate section for security issues. Redact secret values and exploit details.

| ID | Finding | Severity | Status | Remediation |
|----|---------|----------|--------|-------------|
| S-001 | | | | |

## 10. Accessibility Findings

| ID | Finding | WCAG Criterion | Severity | Status |
|----|---------|---------------|----------|--------|
| A-001 | | | | |

## 11. Cross-Browser and Responsive Results

| Page/Feature | Chromium | Firefox | Safari/WebKit | Mobile (320px) | Tablet (768px) | Desktop (1440px) |
|-------------|----------|---------|--------------|----------------|----------------|------------------|
| Homepage | ✅/❌/⏭️ | | | | | |

Clearly state when a browser or viewport **could not be tested**.

## 12. Reliability and Recovery Results

| Scenario | Result | Evidence |
|----------|--------|----------|
| API timeout handling | | |
| Database unavailable | | |
| Browser refresh during submit | | |
| [Add scenarios] | | |

## 13. Automated Test Results

| Check | Command | Result | Notes |
|-------|---------|--------|-------|
| Unit tests | | ✅ X passed / ❌ Y failed | |
| Type check | | | |
| Lint | | | |
| Build | | | |
| Dependency audit | | | |

## 14. Fixes Implemented

_Only in audit-and-fix mode._

| Fix | Files Changed | Before | After | Improvement | Tradeoffs |
|-----|--------------|--------|-------|-------------|----------|
| | | | | | |

## 15. Areas Not Tested

| Area | Reason |
|------|--------|
| Load testing | No staging environment available |
| Safari | WebKit engine not available |
| [Add areas] | |

## 16. Remaining Risks

Explicitly list risks that remain after the audit.

## 17. Recommended Next Actions

Prioritized list of actions before launch.

1. [Highest priority]
2. ...

## 18. Release Checklist

- [ ] All Blocker and Critical issues resolved
- [ ] High-severity issues resolved or explicitly accepted
- [ ] Performance within budget
- [ ] Security review complete
- [ ] Deployment procedure tested
- [ ] Rollback procedure documented
- [ ] Monitoring and alerting configured
- [ ] Backup strategy in place
- [ ] Legal/compliance requirements met
