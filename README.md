# Modeon — Open Source AI Fashion Advisor

> v4.0 · React 18 + Vite · April 2026

Modeon is a free, open-source AI wardrobe manager and personal stylist. Upload your clothes, swipe outfit suggestions, shop smarter, and dress with more intention — all in your browser.

---

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Copy environment variables
cp .env.example .env.local

# 3. Start dev server
npm run dev
# → http://localhost:3000
```

The app boots in **demo mode** by default — a mock user (Sara Chen) is auto-authenticated so you can explore every screen without setting up a backend.

---

## Environment Variables

```env
# Required for real auth
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Required for AI features
VITE_API_URL=https://your-railway-backend.up.railway.app

# Optional analytics
VITE_POSTHOG_KEY=phc_your_key
```

---

## Project Structure

```
modeon/
├── src/
│   ├── api/                  # All backend API stubs (stub → real)
│   │   ├── auth.api.js
│   │   ├── wardrobe.api.js
│   │   ├── outfits.api.js
│   │   ├── shopping.api.js
│   │   └── ...
│   ├── components/
│   │   ├── layout/           # AppShell, Sidebar, TopBar, PageWrapper
│   │   ├── outfits/          # DailyOutfitCard, SwipeCardStack, OutfitGallery…
│   │   ├── wardrobe/         # WardrobeGrid, UploadModal, FilterPanel…
│   │   ├── shopping/         # ShoppingUploadZone, CompareResultCard…
│   │   ├── outfitcheck/      # OutfitCheckUploader, OutfitCheckResult…
│   │   └── ui/               # Modal, Toast, EmptyState, ThemeToggle…
│   ├── constants/            # routes, categories, styleArchetypes, occasions
│   ├── hooks/                # useWardrobe, useOutfits, useSwipeSession…
│   ├── lib/                  # posthog, queryClient, supabaseClient stub
│   ├── pages/                # One file per route
│   │   ├── LandingPage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── OnboardingPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── WardrobePage.jsx
│   │   ├── SwipeSessionPage.jsx
│   │   ├── MyOutfitsPage.jsx
│   │   ├── OccasionStylingPage.jsx
│   │   ├── MixMatchPage.jsx
│   │   ├── OutfitCheckPage.jsx
│   │   ├── ShoppingPage.jsx
│   │   ├── AccountPage.jsx
│   │   └── PublicOutfitPage.jsx
│   ├── stores/               # Zustand: useAuthStore, useUIStore, useWardrobeStore
│   └── styles/globals.css    # Tailwind + design tokens
├── public/
│   └── modeon-logo.svg
├── index.html
├── tailwind.config.js
├── vite.config.js
└── package.json
```

---

## Design System

All design tokens are CSS custom properties in `globals.css`:

| Token | Value | Usage |
|---|---|---|
| `--color-canvas` | `#EDE8DF` | Page backgrounds |
| `--color-card` | `#F7F3EE` | Card backgrounds |
| `--color-gold` | `#C8A97E` | Primary accent / CTAs |
| `--color-ink` | `#1C1916` | Body text |
| `--color-ok` | `#7BAE8E` | Success states |
| `--color-danger` | `#C47B72` | Error / danger states |

Fonts: **Playfair Display** (headings) + **DM Sans** (body)

Component classes: `.btn-gold`, `.btn-secondary`, `.btn-danger`, `.btn-ghost`, `.card`, `.badge`, `.input`, `.label`

---

## Backend Wiring (TODO markers)

Every backend call is stubbed with a `// TODO (Backend):` comment. Search the codebase:

```bash
grep -r "TODO (Backend)" src/
```

Key integration points:
- `src/lib/supabaseClient.js` — wire Supabase project URL + anon key
- `src/main.jsx` — uncomment `onAuthStateChange` listener
- `src/api/*.api.js` — replace stub functions with real `fetch` / Supabase SDK calls

---

## P0 Feature Status

| Feature | Frontend | Backend |
|---|---|---|
| Auth (email + OAuth) | ✅ Complete | 🔧 Stub → wire Supabase |
| Onboarding quiz | ✅ Complete | 🔧 Stub → POST /api/profile |
| Wardrobe upload + grid | ✅ Complete | 🔧 Stub → Azure Blob + CV |
| Swipe session | ✅ Complete | 🔧 Stub → GPT-4o-mini |
| Daily outfit card | ✅ Complete | 🔧 Stub → POST /api/outfits/generate |
| Shopping compare | ✅ Complete | 🔧 Stub → GPT-4o vision |
| Shopping list | ✅ Complete | 🔧 Stub → CRUD endpoints |
| Occasion styling | ✅ Complete | 🔧 Stub → GET /api/outfits/occasion |
| Mix & Match canvas | ✅ Complete | 🔧 Stub → POST /api/mix-match/score |
| Outfit Check | ✅ Complete | 🔧 Stub → POST /api/outfit-check |
| Social export | ✅ Complete | 🔧 Stub → GET /api/outfits/{id}/export |
| Public share page | ✅ Complete | 🔧 Stub → GET /api/outfits/public/{token} |
| Dark mode | ✅ Complete | — |
| WCAG 2.1 AA | ✅ Partial | — |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Routing | React Router v6 |
| Styling | Tailwind CSS (no component library) |
| Animation | Framer Motion |
| State | Zustand |
| Data fetching | TanStack Query v5 |
| Icons | Lucide React |
| Analytics | PostHog (stubbed) |
| Auth | Supabase Auth (stubbed) |
| Database | Supabase Postgres (stubbed) |
| Storage | Azure Blob Storage (stubbed) |
| AI | Azure OpenAI GPT-4o (stubbed) |
| Backend | FastAPI on Railway (separate repo) |
| Deploy | Vercel |

---

## Contributing

```bash
# Lint
npm run lint

# Build check
npm run build

# Preview production build
npm run preview
```

PRs welcome. See `plan.md` for the full sprint breakdown.

---

*Modeon — Open Source — modeon.com*  
*Frontend scaffold v4.0 | April 2026*

