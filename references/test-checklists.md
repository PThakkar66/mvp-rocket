# Test Checklists

Detailed checklists for each audit category. The agent should select applicable items based on the detected product type and stack.

## Critical User Journey Catalog

Identify which of these apply before testing:

- Registration and account creation
- Login and logout
- Password recovery
- Onboarding flow
- Creating the primary product object
- Reading/viewing the primary product object
- Updating the primary product object
- Deleting the primary product object
- Search, filter, and sorting
- Checkout or subscription
- File upload and download
- Form submission
- Invitation and collaboration
- Role and permission changes
- Saving and retrieving user data
- Error recovery
- Cancellation or account deletion

## Functional Testing Checklist

### Installation and Startup
- [ ] Dependencies install without errors
- [ ] Application starts successfully
- [ ] Build completes without errors
- [ ] Production build works
- [ ] Database migrations run cleanly

### Authentication and Sessions
- [ ] Account creation with valid data
- [ ] Account creation rejects invalid/duplicate data
- [ ] Login with correct credentials
- [ ] Login rejects incorrect credentials
- [ ] Logout clears session completely
- [ ] Session expiration behavior
- [ ] Password reset flow
- [ ] Social login when present
- [ ] Remember-me functionality
- [ ] Multi-tab session consistency

### Authorization
- [ ] Role-based access control at UI level
- [ ] Role-based access control at API level
- [ ] Horizontal privilege escalation blocked
- [ ] Vertical privilege escalation blocked
- [ ] Unauthenticated access to protected routes blocked

### Navigation and Routing
- [ ] All navigation links work
- [ ] Browser back/forward behavior correct
- [ ] Deep links resolve correctly
- [ ] Page refresh preserves state
- [ ] 404 page for unknown routes
- [ ] Redirect behavior correct

### Forms and Validation
- [ ] Required fields enforced
- [ ] Optional fields work correctly
- [ ] Malformed input rejected with clear messages
- [ ] Boundary values handled (min/max length, min/max number)
- [ ] Duplicate submissions prevented
- [ ] Form preserves input after recoverable errors
- [ ] Validation runs on both client and server

### CRUD Operations
- [ ] Create with valid data
- [ ] Create rejects invalid data
- [ ] Read displays correct data
- [ ] Update persists changes
- [ ] Delete with confirmation
- [ ] Delete actually removes data
- [ ] Optimistic updates roll back on failure

### Search, Filters, and Pagination
- [ ] Search returns relevant results
- [ ] Search handles empty results
- [ ] Search handles special characters
- [ ] Filters apply correctly
- [ ] Filter combinations work
- [ ] Pagination works correctly
- [ ] Sorting works for all sortable columns
- [ ] Sort direction toggles

### Data Handling
- [ ] Dates and time zones display correctly
- [ ] Currency formatting correct
- [ ] Localization when applicable
- [ ] Data persists after refresh
- [ ] Data persists after logout/login
- [ ] Data isolation between accounts/tenants
- [ ] Import behavior
- [ ] Export behavior

### States
- [ ] Empty states show guidance
- [ ] Loading states visible during async operations
- [ ] Error states show actionable messages
- [ ] Offline/interrupted-network behavior when relevant

### Edge Cases
- [ ] Rapid repeated clicks handled
- [ ] Concurrent updates from multiple sessions
- [ ] Very long content handled
- [ ] Very large datasets handled
- [ ] Special characters in all text inputs
- [ ] Unicode and emoji support

### File Upload
- [ ] Valid file types accepted
- [ ] Invalid file types rejected
- [ ] File size limits enforced
- [ ] Upload cancellation works
- [ ] Upload failure shows error
- [ ] Progress indication

### Integrations
- [ ] Email/notification delivery
- [ ] SMS delivery when applicable
- [ ] Webhook behavior
- [ ] Third-party integration failure handling
- [ ] Payment success (test mode)
- [ ] Payment decline (test mode)
- [ ] Payment cancellation (test mode)
- [ ] Payment retry (test mode)
- [ ] Webhook idempotency

### Account Lifecycle
- [ ] Account cancellation/deletion
- [ ] Data cleanup after deletion
- [ ] Legal consent and privacy controls when applicable

## Visual and Responsive Checklist

Test at these representative widths:
- 320px (small mobile)
- 414px (large mobile)
- 768px (tablet)
- 1024px (laptop)
- 1440px (desktop)
- 1920px+ (wide desktop)

Check for:
- [ ] Overflow and horizontal scrolling
- [ ] Clipped or truncated text
- [ ] Overlapping elements
- [ ] Broken modals or dialogs
- [ ] Unreachable controls
- [ ] Incorrect z-index stacking
- [ ] Missing responsive states
- [ ] Unreadable typography (too small/large)
- [ ] Incorrect image scaling
- [ ] Layout shifts during load
- [ ] Sticky header/footer problems
- [ ] Mobile keyboard obstruction of inputs
- [ ] Orientation change behavior
- [ ] Zoom behavior (up to 200%)
- [ ] Long content overflow
- [ ] Empty content layout
- [ ] Validation message positioning
- [ ] Loading and error state layout

## Security Review Checklist

Perform a safe review without destructive exploitation.

### Secrets and Configuration
- [ ] No secrets committed to source control
- [ ] No secrets exposed to browser (client bundles, HTML, JS)
- [ ] No debug endpoints accessible
- [ ] No default credentials active
- [ ] Environment variables used for configuration

### Authentication and Session
- [ ] Strong password requirements
- [ ] Secure password storage (bcrypt/scrypt/argon2)
- [ ] Session cookies: HttpOnly, Secure, SameSite
- [ ] Token expiration configured
- [ ] Logout invalidates session server-side

### Authorization
- [ ] All endpoints check authorization
- [ ] Horizontal privilege escalation blocked
- [ ] Vertical privilege escalation blocked
- [ ] Insecure direct object references prevented

### Input and Output
- [ ] Cross-site scripting (XSS) mitigated
- [ ] SQL injection prevented
- [ ] NoSQL injection prevented
- [ ] Command injection prevented
- [ ] Cross-site request forgery (CSRF) protection
- [ ] Unsafe redirects prevented
- [ ] Path traversal prevented
- [ ] Server-side request forgery (SSRF) prevented

### Infrastructure
- [ ] CORS configuration restrictive
- [ ] Security headers present (CSP, HSTS, X-Frame-Options, etc.)
- [ ] File upload validation (type, size, content)
- [ ] Rate limiting on sensitive endpoints
- [ ] Brute-force protection on login

### Data Protection
- [ ] Sensitive data not logged
- [ ] Personal information not exposed in URLs
- [ ] Dependency vulnerabilities checked
- [ ] Webhook signatures verified
- [ ] Tenant/account data isolation
- [ ] Data retention and deletion behavior

## Accessibility Checklist

- [ ] All interactive elements keyboard-accessible
- [ ] Visible focus indicator on all focusable elements
- [ ] Logical focus order (tab order)
- [ ] Modal focus trapping and restoration
- [ ] Semantic heading hierarchy (h1 > h2 > h3)
- [ ] All form inputs have associated labels
- [ ] All interactive elements have accessible names
- [ ] Error messages identify the field and the problem
- [ ] Color contrast meets WCAG AA (4.5:1 text, 3:1 large text)
- [ ] Status information not conveyed by color alone
- [ ] All images have meaningful alt text (or empty alt for decorative)
- [ ] Buttons use `<button>`, links use `<a>`
- [ ] Dynamic content changes announced to screen readers
- [ ] Skip navigation link present
- [ ] Reduced-motion support (`prefers-reduced-motion`)
- [ ] Touch targets at least 44x44px
- [ ] Page title is descriptive and unique
- [ ] `lang` attribute set on `<html>`
- [ ] Page usable at 200% zoom
- [ ] Data tables have proper headers and semantics
- [ ] Media has captions or transcripts when applicable

## Reliability and Resilience Checklist

- [ ] API timeout handling
- [ ] Database unavailable handling
- [ ] Third-party service unavailable handling
- [ ] Slow network behavior
- [ ] Expired token handling
- [ ] Partial response handling
- [ ] Invalid response handling
- [ ] Duplicate event handling
- [ ] Out-of-order webhook handling
- [ ] Browser refresh during form submission
- [ ] Multiple tabs open simultaneously
- [ ] Concurrent updates to same resource
- [ ] Useful error messages shown to user
- [ ] Retries are safe (idempotent)
- [ ] Transactions are consistent
- [ ] Rollback works correctly
- [ ] Data remains consistent after failures
- [ ] Recovery without duplicate side effects
- [ ] Health check endpoint exists
- [ ] Structured logging present
- [ ] Alerting configured
- [ ] Backup and restoration plan exists
- [ ] Deployment rollback procedure documented

## Load, Spike, and Endurance Testing Checklist

Only run load tests against an authorized local, test, or staging environment.

### Before Running

Establish:
- [ ] Expected concurrent users
- [ ] Expected request rate
- [ ] Expected daily or peak traffic
- [ ] Maximum safe test intensity
- [ ] Test duration
- [ ] Protected endpoints (do not load test)
- [ ] Stop conditions

### When Authorized, Test

- [ ] Expected load
- [ ] Short traffic spikes
- [ ] Sustained load
- [ ] Graceful degradation
- [ ] Recovery after load
- [ ] Rate limiting behavior
- [ ] Queue growth
- [ ] Connection exhaustion
- [ ] Database contention
- [ ] Timeout behavior under load
- [ ] Retry behavior under load
- [ ] Duplicate processing under load
- [ ] Resource leakage (connections, memory, file handles)

Immediately stop the test if it risks damaging data, creating unexpected costs, or affecting real users.

## Usability Review Checklist

Separate objective defects from subjective product suggestions.

- [ ] A first-time user understands the product purpose
- [ ] The primary action is obvious on each page
- [ ] Terminology is consistent throughout
- [ ] Destructive actions require confirmation
- [ ] Users can recover from mistakes (undo, edit, go back)
- [ ] Progress and loading indicators are visible during async operations
- [ ] Error messages explain what happened and what to do next
- [ ] Empty states guide the user toward the next action
- [ ] The product prevents duplicate submissions
- [ ] Forms preserve user input after recoverable errors
- [ ] Users receive confirmation after important actions (save, delete, submit, purchase)
- [ ] Navigation and calls to action are consistent across pages
- [ ] The information hierarchy is clear and scannable
- [ ] No dead-end pages without navigation options

## Code and Architecture Review Checklist

When source code is available, inspect applicable items. Do not equate a lint warning with a user-facing defect. Classify findings by actual risk.

### Structure and Logic
- [ ] Application structure is organized and navigable
- [ ] Critical business logic is correct
- [ ] Error handling covers expected failure modes
- [ ] Validation runs on both client and server boundaries
- [ ] Dead code on critical paths is removed

### Security and Auth
- [ ] Authentication implementation is sound
- [ ] Authorization checks are present on all protected routes/endpoints
- [ ] Database access uses parameterized queries

### Data and State
- [ ] Transaction handling maintains consistency
- [ ] Async and concurrency behavior is correct
- [ ] Retry and timeout configuration is appropriate
- [ ] Caching strategy is sound
- [ ] Resource cleanup occurs (connections, streams, handles)
- [ ] Database migrations are reversible
- [ ] Rollback readiness is confirmed

### Quality
- [ ] Logging is structured and useful (not excessive)
- [ ] Environment configuration uses env vars (no hardcoded secrets)
- [ ] Feature flags are clean (no stale flags)
- [ ] Test coverage exists around critical behavior
- [ ] Type safety is maintained (no unsafe casts on critical paths)
- [ ] Dependency health: no abandoned, vulnerable, or unnecessary packages
- [ ] Build produces no warnings
- [ ] Runtime produces no warnings or deprecation notices
- [ ] Deployment configuration is complete and correct

## Automated Checks Checklist

Detect and use the repository's existing commands before inventing new ones. Do not silently change lockfiles, upgrade dependencies, or install global software.

- [ ] Dependency installation completes without errors
- [ ] Type checking passes (tsc, mypy, pyright, etc.)
- [ ] Linting passes (eslint, ruff, golint, etc.)
- [ ] Formatting validation passes (prettier, black, gofmt, etc.)
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] Development build succeeds
- [ ] Production build succeeds
- [ ] Static analysis passes (sonarqube, semgrep, bandit, etc.)
- [ ] Dependency audit shows no critical vulnerabilities (npm audit, pip-audit, etc.)
- [ ] Accessibility automation passes (axe, lighthouse, etc.)
- [ ] Browser automation tests pass (playwright, cypress, etc.)
- [ ] API contract tests pass (when present)
- [ ] Performance tests pass (when present)
- [ ] Bundle analysis shows no unexpected growth

Explain what additional tooling is required when it is unavailable.

