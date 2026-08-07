# Severity Definitions and Release Gates

## Severity Classifications

### Blocker
Prevents launch or makes the product unusable.

**Examples**: data loss, unavailable core journey, severe security exposure, corrupt deployment, payment/authentication failure affecting most users.

### Critical
Causes major security, privacy, financial, authorization, reliability, or data-integrity risk, or consistently breaks a critical journey.

### High
Seriously affects an important feature or causes unacceptable performance. A limited workaround may exist.

### Medium
Affects a secondary journey, a subset of users, or usability without blocking the primary product goal.

### Low
Minor visual, consistency, maintainability, or polish issue with limited user impact.

**Do not inflate severity.** Explain the concrete user and business impact.

## Release Gates

### GO — Recommend launch

All of the following must be true:
- All critical user journeys pass
- No Blocker or Critical defects remain open
- High-severity findings have been fixed or explicitly accepted
- Performance is within the agreed budget
- No critical security findings remain
- Data persistence and isolation tests pass
- Required browsers and devices pass
- Deployment and rollback readiness are acceptable
- Test evidence is sufficient
- Important untested areas are not launch-critical

### CONDITIONAL GO — Launch with documented risks

All of the following must be true:
- No Blocker or Critical defects remain
- Remaining risks are understood and explicitly documented
- Workarounds or monitoring exist
- Unresolved issues do not compromise security, privacy, payments, or data integrity

### NO-GO — Do not launch

Any of the following:
- A critical journey fails
- A Blocker or Critical issue remains
- Performance misses an essential target without acceptable mitigation
- Security, privacy, payment, or data-integrity risk is unresolved
- Testing was too incomplete to support a responsible launch recommendation
