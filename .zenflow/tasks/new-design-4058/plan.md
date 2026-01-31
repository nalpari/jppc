# Spec and build

## Configuration
- **Artifacts Path**: {@artifacts_path} → `.zenflow/tasks/{task_id}`

---

## Agent Instructions

Ask the user questions when anything is unclear or needs their input. This includes:
- Ambiguous or incomplete requirements
- Technical decisions that affect architecture or user experience
- Trade-offs that require business context

Do not make assumptions on important decisions — get clarification first.

---

## Workflow Steps

### [x] Step: Technical Specification

**Difficulty**: Medium
**Spec**: See `spec.md` for full technical specification

Summary:
- Transform UI to modern Black & Yellow color scheme
- Update CSS variables in globals.css (core design tokens)
- Update hardcoded colors in components (Header, StatsCard, RecentCrawlsWidget)
- Update badge/button variants for theme consistency
- Verify with lint, build, and visual testing

---

### [x] Step: Update Core Design System
<!-- chat-id: 2a680103-28f0-4123-9329-eb5e31b449f9 -->

Update the foundational design tokens and Tailwind configuration.

1. Update `frontend/src/app/globals.css`:
   - Replace all CSS variable values with new Black & Yellow palette
   - Update both light mode and dark mode variables
   - Primary color: Yellow (#ffd700 / HSL 48 96% 53%)
   - Foreground: Near black, Background: White (light) / Near black (dark)

2. Verify Tailwind config compatibility in `frontend/tailwind.config.js`

**Verification**: Run `npm run lint` and `npm run build` in frontend folder

---

### [x] Step: Update UI Component Variants
<!-- chat-id: 22ae38fb-ffb5-4fc0-8a25-73438bc88e8d -->

Update reusable UI component color variants.

1. Update `frontend/src/components/ui/badge.tsx`:
   - Change `info` variant from blue to neutral gray
   - Keep `success` green and `error` red for semantic clarity
   - Keep `warning` yellow (aligns with theme)

2. Review `frontend/src/components/ui/button.tsx`:
   - Primary buttons will use yellow via CSS vars (automatic)
   - Review `success` variant - keep green for semantic meaning

**Verification**: Visual check of badge and button components

---

### [x] Step: Update Layout Components
<!-- chat-id: e1bad4fa-d717-41b4-a195-8033fb24b335 -->

Update Header and navigation with new design colors.

1. Update `frontend/src/components/layout/Header.tsx`:
   - Line 48: Zap icon already uses `text-yellow-500` (enhance if needed)
   - Line 61: Change status badge dot from `bg-green-500` to `bg-yellow-500`

2. Sidebar will automatically use new primary color via CSS variables

**Verification**: Visual check of header and navigation

---

### [x] Step: Update Dashboard Components
<!-- chat-id: 0adcc4be-c0fc-4ace-90bf-df723a50ed0e -->

Update dashboard widgets with consistent color scheme.

1. Update `frontend/src/components/dashboard/StatsCard.tsx`:
   - Keep trend colors (green/red) for semantic meaning (positive/negative)

2. Update `frontend/src/components/dashboard/RecentCrawlsWidget.tsx`:
   - Line 32: Keep `text-green-500` for success (semantic)
   - Line 34: Keep `text-red-500` for failed (semantic)
   - Line 36: Change `text-blue-500` (running) to `text-yellow-500`

**Verification**: Visual check of dashboard page

---

### [x] Step: Final Verification and Report
<!-- chat-id: e4c1cd24-54b8-4211-b97b-d2b71a9a81a6 -->

Run full verification suite and document changes.

1. Run linter: `cd frontend && npm run lint`
2. Run build: `cd frontend && npm run build`
3. Visual verification of all pages in browser
4. Test dark mode if available
5. Write report to `{@artifacts_path}/report.md`:
   - What was implemented
   - How the solution was tested
   - Any issues or challenges encountered
