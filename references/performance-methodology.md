# Performance Methodology

Performance testing must measure real behavior rather than relying on visual impressions.

## Performance Budget

Establish a budget before declaring a pass. Use the user's targets when supplied. If none are supplied, use the provisional targets below, label them as assumptions, and invite the user to adjust.

### Provisional Web Targets

| Metric | Target | Source |
|--------|--------|--------|
| Largest Contentful Paint (LCP) | ≤ 2.5s | Google Web Vitals |
| Interaction to Next Paint (INP) | ≤ 200ms | Google Web Vitals |
| Cumulative Layout Shift (CLS) | ≤ 0.1 | Google Web Vitals |
| Time to First Byte (TTFB) | ≤ 800ms | Provisional |
| First Contentful Paint (FCP) | ≤ 1.8s | Provisional |
| No visibly blocking critical interaction | — | Mandatory |
| No uncontrolled memory growth during repeated journeys | — | Mandatory |
| No unexplained 4xx/5xx during successful journeys | — | Mandatory |

### Provisional API Targets

| Metric | Target |
|--------|--------|
| p50 latency | ≤ 200ms |
| p95 latency | ≤ 500ms |
| p99 latency | ≤ 1000ms |
| Error rate | < 0.1% |

These are starting assumptions, not universal guarantees. Evaluate results in context of the product, users, hosting environment, device class, and network conditions.

## Metrics to Measure

Select applicable metrics based on product type:

### Web Core Vitals
- Largest Contentful Paint (LCP)
- Interaction to Next Paint (INP)
- Cumulative Layout Shift (CLS)
- Time to First Byte (TTFB)
- First Contentful Paint (FCP)

### Page Performance
- Initial page-load time
- Route-change time
- JavaScript execution time
- Main-thread blocking time
- Long tasks (>50ms)
- Requests per page
- Transferred bytes
- JavaScript bundle size
- CSS bundle size
- Image size and format efficiency

### Interaction Performance
- Search response time
- Form submission time
- File upload time
- Animation smoothness (frame drops)

### API Performance
- Latency at p50, p95, p99
- Error rate
- Cold-start time

### Resource Usage
- Memory usage and growth during repeated navigation
- CPU usage
- Database query duration
- Slow query frequency
- Cache hit rate
- Connection pool utilization
- Server resource saturation under load

## Testing Conditions

Test under representative conditions:

| Condition | Variations |
|-----------|------------|
| Cache | Warm cache, cold cache |
| Network | Normal broadband, throttled mobile (3G/4G) |
| Hardware | Desktop-class, constrained mobile-class when possible |
| Visit type | First visit, repeat visit |
| Auth state | Authenticated, anonymous |
| Data volume | Small dataset, large dataset |

## Root Cause Analysis

When performance issues are found, analyze likely causes:

### Asset Issues
- Oversized images
- Unoptimized fonts
- Render-blocking resources
- Excessive JavaScript
- Unused code
- Missing compression (gzip/brotli)
- Missing CDN

### Network Issues
- Too many requests
- Waterfall dependencies
- Client-side request waterfalls
- Repeated API calls
- Missing caching headers
- Slow external scripts

### Backend Issues
- N+1 database queries
- Missing database indexes
- Inefficient queries
- Unbounded data loading
- Synchronous processing blocking async paths
- Slow cold starts
- Connection pool limits
- Excessive logging
- Poor pagination
- Inefficient serialization

### Frontend Issues
- Large DOM size
- Expensive re-renders
- Memory leaks
- Lack of lazy loading
- Missing virtualization for large lists

## Fix Reporting

For every performance fix, report:

| Field | Required |
|-------|----------|
| Baseline measurement | Yes |
| Suspected bottleneck | Yes |
| Change made | Yes |
| Post-fix measurement | Yes |
| Percentage improvement | When meaningful |
| Testing conditions | Yes |
| Possible tradeoffs | Yes |

Never report a fix based solely on code inspection. Always measure.
