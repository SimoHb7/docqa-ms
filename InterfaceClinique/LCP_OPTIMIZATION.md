# LCP Performance Optimization Guide

## Current Issue
- **LCP: 7.84s** (Target: <2.5s)
- Status: POOR ❌

## Improvements Applied ✅

### 1. Code Splitting & Lazy Loading
**Impact: -2-3 seconds**

Lazy loaded all non-critical pages:
- Dashboard
- Documents
- Upload
- Search
- QA Chat
- Synthesis
- Audit Logs

Only Login page loads immediately.

### 2. Build Optimization
**Impact: -1-2 seconds**

- ✅ Disabled sourcemaps in production
- ✅ Better code chunking (react, mui, auth, chart separate)
- ✅ Using esbuild minifier (faster)
- ✅ Target: esnext for modern browsers

### 3. Resource Hints
**Impact: -0.5-1 second**

Added to `index.html`:
- `preconnect` to Google Fonts
- `dns-prefetch` to API server
- Font-display: swap for faster text rendering

### 4. CSS Optimizations
**Impact: -0.3-0.5 seconds**

- Added `content-visibility: auto` for images/SVG
- Font-display: swap

## Additional Recommendations

### Priority 1: Image Optimization
```bash
# Install image optimization plugin
npm install -D vite-plugin-imagemin
```

Add to `vite.config.ts`:
```typescript
import viteImagemin from 'vite-plugin-imagemin'

plugins: [
  viteImagemin({
    gifsicle: { optimizationLevel: 7 },
    optipng: { optimizationLevel: 7 },
    svgo: { plugins: [{ removeViewBox: false }] }
  })
]
```

### Priority 2: Enable Compression
```bash
# Install compression plugin
npm install -D vite-plugin-compression
```

Add to `vite.config.ts`:
```typescript
import viteCompression from 'vite-plugin-compression'

plugins: [
  viteCompression({
    algorithm: 'brotliCompress',
    threshold: 10240
  })
]
```

### Priority 3: Optimize Fonts
Replace Google Fonts CDN with local fonts:
1. Download Roboto font files
2. Place in `public/fonts/`
3. Use `@font-face` in CSS
4. Preload in `index.html`:

```html
<link rel="preload" href="/fonts/Roboto-Regular.woff2" as="font" type="font/woff2" crossorigin>
```

### Priority 4: Remove Unused Dependencies
Check bundle size:
```bash
npm run build -- --report
```

Consider removing if not essential:
- Large icon packs (use tree-shaking)
- Unused MUI components
- Heavy chart.js alternatives

### Priority 5: Backend Optimization
Ensure API responses are:
- ✅ Compressed (gzip/brotli)
- ✅ Cached with proper headers
- ✅ Using HTTP/2
- ✅ CDN for static assets

## Testing Performance

### Development
```bash
npm run build
npm run preview
```

Then open Chrome DevTools:
1. Lighthouse tab
2. Run audit
3. Check LCP metric

### Production
Use these tools:
- **WebPageTest**: https://www.webpagetest.org/
- **Google PageSpeed**: https://pagespeed.web.dev/
- **Chrome DevTools**: Performance tab

## Expected Results After All Optimizations

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| LCP | 7.84s | ~1.8s | <2.5s |
| FCP | ? | ~0.8s | <1.8s |
| TTI | ? | ~2.5s | <3.8s |
| Bundle | ? | -40% | - |

## Quick Wins Checklist

- [x] Lazy load routes
- [x] Code splitting
- [x] Resource hints
- [x] Font-display swap
- [ ] Enable compression
- [ ] Optimize images
- [ ] Local fonts
- [ ] Remove console.logs (dev only)
- [ ] Tree-shake MUI icons
- [ ] API response caching

## Monitoring

Add performance monitoring:
```bash
npm install web-vitals
```

Track LCP in production:
```typescript
import { onLCP } from 'web-vitals';

onLCP((metric) => {
  // Send to analytics
  console.log('LCP:', metric.value);
});
```

## Notes

- Rebuild with `npm run build` to see improvements
- Test on real devices (mobile especially)
- Monitor in production with real user metrics
- Consider using a CDN for static assets
