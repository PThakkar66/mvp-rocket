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
