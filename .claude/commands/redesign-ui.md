---
description: Redesign the Vue 3 app's UI to a modern SaaS-style layout with a vertical navigation sidebar
---

Redesign this Vue 3 application's interface from the current horizontal top-nav layout into a modern SaaS-style layout with a fixed vertical navigation sidebar on the left. The result must feel polished and professional — comparable to Linear, Notion, or Vercel's dashboards.

## Phase 1: Understand the current structure

Before writing any code, read these files to understand what exists:
- `client/src/App.vue` — current layout shell, global CSS, nav structure
- `client/src/main.js` — all routes (nav items to render in the sidebar)
- `client/src/components/FilterBar.vue` — filter controls (stays, but moves inside main content)
- `client/src/components/ProfileMenu.vue` — user avatar/menu (moves into sidebar footer)
- `client/src/components/LanguageSwitcher.vue` — language toggle (moves into sidebar)
- `client/src/composables/useI18n.js` — i18n pattern (use `t()` for all labels)
- `client/src/locales/en.js` — to find the `nav.*` translation keys

## Phase 2: Implement the sidebar layout

**MANDATORY: delegate ALL `.vue` file creation and editing to the `vue-expert` subagent.**

### New file: `client/src/components/AppSidebar.vue`

Create this component via vue-expert with the following spec:

**Layout** (fixed, full-height, no scroll):
```
┌──────────────────────┐
│  Brand / Logo area   │  ← 64px, dark bg
├──────────────────────┤
│  Nav items           │  ← flex-1, overflow-y: auto
│  ○ Overview          │
│  ○ Inventory         │
│  ● Orders  (active)  │
│  ○ Finance           │
│  ○ Demand Forecast   │
│  ○ Restocking        │
│  ○ Reports           │
├──────────────────────┤
│  Language + Profile  │  ← 80px, dark bg
└──────────────────────┘
```

**Design system**:
- Sidebar background: `#0f172a` (deep slate)
- Sidebar width: `240px`, `min-width: 240px`
- Brand section: padding `1.25rem 1.5rem`, company name `font-size: 1rem; font-weight: 700; color: #f1f5f9`, subtitle `font-size: 0.75rem; color: #64748b`
- Nav items: `padding: 0.5rem 0.75rem`, `border-radius: 6px`, `color: #94a3b8`, `font-size: 0.875rem; font-weight: 500`, `display: flex; align-items: center; gap: 0.625rem`
- Nav item hover: `background: rgba(255,255,255,0.06); color: #f1f5f9`
- Nav item **active**: `background: rgba(37,99,235,0.25); color: #60a5fa; font-weight: 600`
- Nav section (container for links): `padding: 0.5rem 0.75rem; display: flex; flex-direction: column; gap: 2px`
- Nav icons: 16×16 SVG inline, current color (use simple, recognisable SVG paths — one per route)
- Bottom footer: `padding: 0.75rem; border-top: 1px solid rgba(255,255,255,0.07)`, flex row: LanguageSwitcher + ProfileMenu

**Icons to use** (inline SVG, `width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"`):
- Overview / Dashboard: `<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>` (grid)
- Inventory: `<path d="M20 7H4a2 2 0 00-2 2v6a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2z"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/>` (layers)
- Orders: `<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>` (check square)
- Finance: `<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>` (dollar sign)
- Demand Forecast: `<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>` (activity)
- Restocking: `<path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>` (package)
- Reports: `<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>` (file text)

**Active state detection**: use `useRoute()` from `vue-router`; `isActive(path)` returns `route.path === path` (for `/`) or `route.path.startsWith(path)` (for all others).

**Component imports**: import `LanguageSwitcher` and `ProfileMenu` from their existing paths. Pass through the `@show-profile-details` and `@show-tasks` emits to the parent — define `emits: ['show-profile-details', 'show-tasks']` and forward events from `ProfileMenu`.

**No emojis. No external icon libraries.** Inline SVG only.

### Modify: `client/src/App.vue`

Via vue-expert, restructure the layout and global CSS:

**Template**: replace the current `<header class="top-nav">` + `<FilterBar />` + `<main class="main-content">` structure with:

```html
<div class="app">
  <AppSidebar
    @show-profile-details="showProfileDetails = true"
    @show-tasks="showTasks = true"
  />
  <div class="app-body">
    <div class="top-bar">
      <FilterBar />
    </div>
    <main class="main-content">
      <router-view />
    </main>
  </div>
  <!-- existing modals unchanged -->
</div>
```

Import `AppSidebar` and add it to `components`. Remove `LanguageSwitcher` and `ProfileMenu` from App.vue imports/components (they move into AppSidebar).

**Global CSS changes** (the `<style>` block is global, not scoped — update it):

Replace `.app` / `.top-nav` / `.nav-container` / `.nav-tabs` / `.logo` / `.subtitle` / `.main-content` with:

```css
.app {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.app-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f8fafc;
}

.top-bar {
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
  /* FilterBar renders inside here, picks up its existing padding */
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.75rem 2rem;
}
```

Remove the `max-width` centering from `.main-content` (with a sidebar the content uses all available width naturally). Keep all other global CSS (cards, tables, badges, stats-grid, etc.) unchanged.

## Phase 3: Verify

After all edits are saved:

1. Use Playwright MCP (`mcp__playwright__browser_navigate`) to open `http://localhost:3000`
2. Take a screenshot with `mcp__playwright__browser_take_screenshot`
3. Confirm:
   - The sidebar is visible on the left with a dark background
   - Nav items are listed vertically with icons
   - The main content area is on the right and scrollable
   - The filter bar appears as a horizontal strip above the content
   - The active route is highlighted in the sidebar
4. Navigate to at least two different routes to verify the active state updates correctly
5. If anything looks broken, fix it before reporting done

## Design constraints

- **No emojis** in the UI
- Match the existing slate/gray color palette for content areas
- Preserve all existing component functionality (filters, modals, i18n, profile)
- The sidebar must be fixed — it does not scroll with page content
- Body overflow: `hidden`; main content scrolls independently via `overflow-y: auto`
- Keep all global utility classes (`.card`, `.badge`, `.stats-grid`, etc.) intact
