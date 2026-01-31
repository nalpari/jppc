# Technical Specification: New Design (Black & Yellow Theme)

## Task Overview
Transform the current UI to a modern, minimalist design using a **Black & Yellow** color scheme.

**Difficulty Assessment**: **Medium**
- Moderate complexity with well-structured CSS variable system
- Multiple files need updates but changes are systematic
- No architectural changes required - purely visual transformation

---

## Technical Context

### Technology Stack
- **Framework**: Next.js 14.1.0 (React 18.2.0)
- **Styling**: Tailwind CSS 3.4.1 with CSS Variables
- **UI Library**: Radix UI primitives with CVA (Class Variance Authority)
- **Icons**: Lucide React 0.323.0

### Current Design System
- CSS variables defined in `globals.css` using HSL color space
- Tailwind config extends theme with semantic color tokens
- Component variants managed via CVA (button, badge)
- Dark mode supported via CSS class strategy

---

## Implementation Approach

### Design Philosophy
- **Modern & Minimalist**: Clean lines, ample whitespace, subtle shadows
- **Black & Yellow Palette**: High contrast, bold accent color
- **Consistency**: Unified color language across all components

### Color Palette (HSL Values)

#### Light Mode
| Token | Current | New (Black & Yellow) |
|-------|---------|---------------------|
| `--background` | White | `0 0% 100%` (Pure White) |
| `--foreground` | Dark Blue | `0 0% 9%` (Near Black) |
| `--card` | White | `0 0% 100%` |
| `--card-foreground` | Dark Blue | `0 0% 9%` |
| `--primary` | Blue | `48 96% 53%` (Vibrant Yellow) |
| `--primary-foreground` | Light | `0 0% 9%` (Black text on yellow) |
| `--secondary` | Light Gray | `0 0% 96%` (Light Gray) |
| `--secondary-foreground` | Dark | `0 0% 9%` |
| `--muted` | Light Gray | `0 0% 96%` |
| `--muted-foreground` | Gray | `0 0% 45%` |
| `--accent` | Light Gray | `48 96% 93%` (Light Yellow tint) |
| `--accent-foreground` | Dark | `0 0% 9%` |
| `--destructive` | Red | `0 84% 60%` (Keep Red for errors) |
| `--border` | Light Gray | `0 0% 90%` |
| `--input` | Light Gray | `0 0% 90%` |
| `--ring` | Blue | `48 96% 53%` (Yellow focus ring) |

#### Dark Mode
| Token | New (Black & Yellow) |
|-------|---------------------|
| `--background` | `0 0% 7%` (Near Black) |
| `--foreground` | `0 0% 98%` (Off White) |
| `--card` | `0 0% 10%` (Slightly lighter black) |
| `--card-foreground` | `0 0% 98%` |
| `--primary` | `48 96% 53%` (Same Yellow) |
| `--primary-foreground` | `0 0% 9%` |
| `--secondary` | `0 0% 15%` (Dark Gray) |
| `--secondary-foreground` | `0 0% 98%` |
| `--muted` | `0 0% 15%` |
| `--muted-foreground` | `0 0% 65%` |
| `--accent` | `48 50% 15%` (Muted Yellow tint) |
| `--accent-foreground` | `0 0% 98%` |
| `--destructive` | `0 62% 30%` |
| `--border` | `0 0% 18%` |
| `--input` | `0 0% 18%` |
| `--ring` | `48 96% 53%` |

---

## Source Code Changes

### Critical Files (Design System Core)

#### 1. `frontend/src/app/globals.css`
**Changes**: Update all CSS variable values to new Black & Yellow palette
- Replace blue-based primary with yellow
- Adjust grayscale values for better contrast
- Update dark mode variables

#### 2. `frontend/tailwind.config.js`
**Changes**: Add custom yellow color scale for direct usage
- Add `yellow` color tokens for semantic yellow shades
- Potentially add `success` color token (green for positive states)

### Component Files (Hardcoded Colors)

#### 3. `frontend/src/components/ui/button.tsx`
**Changes**: Update button variants
- `success` variant: Keep green or change to yellow variant
- Primary buttons will automatically use new yellow via CSS vars

#### 4. `frontend/src/components/ui/badge.tsx`
**Changes**: Update badge variants
- `success`: Change from green-100/green-800 to yellow tones
- `warning`: Keep yellow (already aligns with theme)
- `info`: Change from blue to neutral gray
- `error`: Keep red for semantic meaning

#### 5. `frontend/src/components/layout/Header.tsx`
**Changes**: Update hardcoded colors
- Line 48: `text-yellow-500` for Zap icon (already yellow - keep or enhance)
- Line 61: `bg-green-500` status indicator - change to yellow

#### 6. `frontend/src/components/dashboard/StatsCard.tsx`
**Changes**: Update trend colors
- Line 44-45: `text-green-600` / `text-red-600` - consider using yellow for positive trends

#### 7. `frontend/src/components/dashboard/RecentCrawlsWidget.tsx`
**Changes**: Update status colors
- Line 32: `text-green-500` (success) - consider yellow
- Line 34: `text-red-500` (failed) - keep red
- Line 36: `text-blue-500` (running) - change to yellow
- Line 38: `text-gray-500` (default) - keep gray

---

## Design Token Reference

### Yellow Shades (for tailwind.config.js)
```javascript
yellow: {
  50: '#fffef0',
  100: '#fffccc',
  200: '#fff599',
  300: '#ffed66',
  400: '#ffe433',
  500: '#ffd700', // Primary yellow (Gold)
  600: '#ccac00',
  700: '#998100',
  800: '#665600',
  900: '#332b00',
  950: '#1a1500',
}
```

### Semantic Color Mapping
| Purpose | Color |
|---------|-------|
| Primary Action | Yellow 500 (#ffd700) |
| Hover State | Yellow 600 (#ccac00) |
| Active State | Yellow 700 (#998100) |
| Success | Green 500 (keep for semantic clarity) |
| Error | Red 500 (keep for semantic clarity) |
| Warning | Yellow 500 |
| Info | Gray 500 |

---

## Verification Approach

### Visual Testing
1. Run development server: `npm run dev`
2. Verify all pages render with new color scheme:
   - Dashboard (`/`)
   - Companies (`/companies`)
   - Prices (`/prices`, `/prices/compare`, `/prices/history`)
   - Crawling (`/crawling`)
   - Settings (`/settings`)
3. Test light/dark mode toggle if available
4. Verify responsive design on mobile breakpoints

### Code Quality
1. Run linter: `npm run lint`
2. Run type check: `npm run type-check` (if available)
3. Build verification: `npm run build`

### Accessibility
1. Verify WCAG contrast ratios (yellow on white needs careful handling)
2. Ensure focus states are visible (yellow ring on dark backgrounds)
3. Test color blindness compatibility

---

## Implementation Plan

### Phase 1: Core Design System
1. Update `globals.css` with new CSS variables
2. Verify Tailwind config compatibility

### Phase 2: Component Updates
3. Update badge variants in `badge.tsx`
4. Update button variants if needed in `button.tsx`
5. Update Header component colors
6. Update Dashboard component colors (StatsCard, RecentCrawlsWidget)

### Phase 3: Verification
7. Run lint and build
8. Visual verification across all pages
9. Dark mode verification

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Yellow text on white background (low contrast) | Use yellow only for backgrounds/accents, black text on yellow |
| Dark mode yellow visibility | Use slightly brighter yellow in dark mode |
| Semantic color confusion (success vs primary both yellow) | Keep green for success states, yellow for primary actions |
| Existing hardcoded colors missed | Search for `green-`, `blue-`, `yellow-` Tailwind classes |

---

## Files Summary

| File | Change Type | Priority |
|------|-------------|----------|
| `globals.css` | Modify | High |
| `tailwind.config.js` | Modify | High |
| `badge.tsx` | Modify | Medium |
| `button.tsx` | Review/Modify | Medium |
| `Header.tsx` | Modify | Medium |
| `StatsCard.tsx` | Modify | Low |
| `RecentCrawlsWidget.tsx` | Modify | Low |
