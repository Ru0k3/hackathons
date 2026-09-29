-- =============================================================================
-- Modeon — Initial Database Schema
-- Migration: 001_initial_schema.sql
-- Created:   April 2026
-- =============================================================================
-- Run this against your Supabase project via the Supabase SQL editor or CLI.
-- All tables use Row Level Security (RLS) scoped to auth.uid().
-- =============================================================================


-- ── Extensions ─────────────────────────────────────────────────────────────────
-- gen_random_uuid() is available via pgcrypto in Supabase by default.
-- Enabling it explicitly is harmless.
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- =============================================================================
-- TABLES
-- =============================================================================


-- ── user_profiles ──────────────────────────────────────────────────────────────
-- Links to auth.users. One row per registered user.
-- Created automatically on first login via application logic.

CREATE TABLE IF NOT EXISTS public.user_profiles (
    id               uuid        PRIMARY KEY REFERENCES auth.users (id) ON DELETE CASCADE,
    style_archetypes text[]      DEFAULT '{}',
    occasion_prefs   text[]      DEFAULT '{}',
    colour_palette   text[]      DEFAULT '{}',
    gender_pref      text,
    created_at       timestamptz NOT NULL DEFAULT now(),
    updated_at       timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.user_profiles IS
    'User style preferences collected during onboarding and updated over time.';

COMMENT ON COLUMN public.user_profiles.style_archetypes IS
    'E.g. ["minimalist", "streetwear"] — selected during onboarding quiz.';
    'Azure Blob path only — never a public URL.';


-- ── wardrobe_items ─────────────────────────────────────────────────────────────
-- One row per uploaded clothing item.
-- blob paths reference Azure Blob Storage; SAS tokens are generated server-side.

CREATE TABLE IF NOT EXISTS public.wardrobe_items (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             uuid        NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    blob_original_path  text        NOT NULL,   -- Azure Blob path; never a public URL
    blob_thumb_path     text,                   -- Azure Blob thumbnail path
    category            text,                   -- top | bottom | outerwear | shoes | ...
    colours             text[]      DEFAULT '{}',
    pattern             text,                   -- solid | striped | checked | ...
    formality           text,                   -- casual | smart-casual | business | formal | athletic
    seasons             text[]      DEFAULT '{}',
    custom_tags         text[]      DEFAULT '{}',
    alt_text            text,                   -- AI-generated; used for accessibility
    is_archived         boolean     NOT NULL DEFAULT false,
    is_in_laundry       boolean     NOT NULL DEFAULT false,
    created_at          timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.wardrobe_items IS
    'Clothing items uploaded by a user. Blob paths reference Azure Blob Storage.';

COMMENT ON COLUMN public.wardrobe_items.blob_original_path IS
    'Azure Blob path (wardrobe-originals container). Never exposed as a public URL.';
COMMENT ON COLUMN public.wardrobe_items.blob_thumb_path IS
    'Azure Blob path (wardrobe-thumbnails container). Never exposed as a public URL.';
COMMENT ON COLUMN public.wardrobe_items.alt_text IS
    'GPT-4o-mini generated description for screen reader accessibility.';


-- ── generated_outfits ──────────────────────────────────────────────────────────
-- Records every outfit generated for a user, from any source.

CREATE TABLE IF NOT EXISTS public.generated_outfits (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     uuid        NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    item_ids    uuid[]      NOT NULL DEFAULT '{}',  -- wardrobe_item IDs forming this outfit
    source      text        NOT NULL CHECK (source IN ('swipe', 'daily', 'occasion', 'shopping_list')),
    occasion    text,
    explanation text,
    is_saved    boolean     NOT NULL DEFAULT false,
    created_at  timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.generated_outfits IS
    'Every AI-generated outfit record. Source indicates which feature produced it.';

COMMENT ON COLUMN public.generated_outfits.item_ids IS
    'Array of wardrobe_item UUIDs (or shopping_list_item UUIDs when source=shopping_list).';
COMMENT ON COLUMN public.generated_outfits.source IS
    'swipe | daily | occasion | shopping_list';


-- ── outfit_swipes ──────────────────────────────────────────────────────────────
-- Swipe interaction history. Primary preference signal for AI.
-- Active window: last 90 days. Rows > 180 days archived.

CREATE TABLE IF NOT EXISTS public.outfit_swipes (
    id         uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    uuid        NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    outfit_id  uuid        REFERENCES public.generated_outfits (id) ON DELETE CASCADE,
    swipe      smallint    NOT NULL CHECK (swipe IN (-1, 1)),  -- 1=like, -1=dislike
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.outfit_swipes IS
    'User swipe events on generated outfits. Preference signal for AI ranking.';

COMMENT ON COLUMN public.outfit_swipes.swipe IS
    '1 = like, -1 = dislike.';


-- ── shopping_list_items ────────────────────────────────────────────────────────
-- Items the user is considering purchasing.

CREATE TABLE IF NOT EXISTS public.shopping_list_items (
    id                   uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              uuid        NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    blob_path            text        NOT NULL,   -- Azure Blob path (shopping-uploads container)
    category             text,
    colours              text[]      DEFAULT '{}',
    notes                text,
    moved_to_wardrobe    boolean     NOT NULL DEFAULT false,
    added_at             timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.shopping_list_items IS
    'Items being considered for purchase. Blob paths reference the shopping-uploads container.';


-- ── share_tokens ───────────────────────────────────────────────────────────────
-- Public outfit sharing. Share links expire after 30 days.

CREATE TABLE IF NOT EXISTS public.share_tokens (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    outfit_id   uuid        NOT NULL REFERENCES public.generated_outfits (id) ON DELETE CASCADE,
    token       text        NOT NULL UNIQUE,
    expires_at  timestamptz NOT NULL DEFAULT (now() + INTERVAL '30 days'),
    created_at  timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.share_tokens IS
    'Short-lived public share tokens for generated outfits. Expire after 30 days.';


-- =============================================================================
-- INDEXES
-- =============================================================================

-- outfit_swipes: primary preference signal query pattern
CREATE INDEX IF NOT EXISTS idx_outfit_swipes_user_created
    ON public.outfit_swipes (user_id, created_at DESC);

-- wardrobe_items: most common filter (available items — not archived, not in laundry)
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_user_available
    ON public.wardrobe_items (user_id, is_archived, is_in_laundry);

-- generated_outfits: user feed ordering
CREATE INDEX IF NOT EXISTS idx_generated_outfits_user_created
    ON public.generated_outfits (user_id, created_at DESC);

-- share_tokens: public page lookup by token string
CREATE UNIQUE INDEX IF NOT EXISTS idx_share_tokens_token
    ON public.share_tokens (token);

-- shopping_list_items: user list ordering
CREATE INDEX IF NOT EXISTS idx_shopping_list_items_user_added
    ON public.shopping_list_items (user_id, added_at DESC);


-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-update user_profiles.updated_at on every UPDATE
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_user_profiles_updated_at ON public.user_profiles;

CREATE TRIGGER trg_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();


-- =============================================================================
-- ROW LEVEL SECURITY
-- =============================================================================

-- Enable RLS on all application tables
ALTER TABLE public.user_profiles         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wardrobe_items        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_outfits     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.outfit_swipes         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shopping_list_items   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.share_tokens          ENABLE ROW LEVEL SECURITY;


-- ── user_profiles ──────────────────────────────────────────────────────────────

-- SELECT: own row only
CREATE POLICY "user_profiles_select_own"
    ON public.user_profiles
    FOR SELECT
    TO authenticated
    USING (id = auth.uid());

-- INSERT: user creates their own profile on first login
CREATE POLICY "user_profiles_insert_own"
    ON public.user_profiles
    FOR INSERT
    TO authenticated
    WITH CHECK (id = auth.uid());

-- UPDATE: own row only
CREATE POLICY "user_profiles_update_own"
    ON public.user_profiles
    FOR UPDATE
    TO authenticated
    USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- DELETE: own row only (account deletion flow)
CREATE POLICY "user_profiles_delete_own"
    ON public.user_profiles
    FOR DELETE
    TO authenticated
    USING (id = auth.uid());


-- ── wardrobe_items ─────────────────────────────────────────────────────────────

CREATE POLICY "wardrobe_items_select_own"
    ON public.wardrobe_items
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "wardrobe_items_insert_own"
    ON public.wardrobe_items
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "wardrobe_items_update_own"
    ON public.wardrobe_items
    FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "wardrobe_items_delete_own"
    ON public.wardrobe_items
    FOR DELETE
    TO authenticated
    USING (user_id = auth.uid());


-- ── generated_outfits ──────────────────────────────────────────────────────────

CREATE POLICY "generated_outfits_select_own"
    ON public.generated_outfits
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "generated_outfits_insert_own"
    ON public.generated_outfits
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "generated_outfits_update_own"
    ON public.generated_outfits
    FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "generated_outfits_delete_own"
    ON public.generated_outfits
    FOR DELETE
    TO authenticated
    USING (user_id = auth.uid());


-- ── outfit_swipes ──────────────────────────────────────────────────────────────

CREATE POLICY "outfit_swipes_select_own"
    ON public.outfit_swipes
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "outfit_swipes_insert_own"
    ON public.outfit_swipes
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "outfit_swipes_update_own"
    ON public.outfit_swipes
    FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "outfit_swipes_delete_own"
    ON public.outfit_swipes
    FOR DELETE
    TO authenticated
    USING (user_id = auth.uid());


-- ── shopping_list_items ────────────────────────────────────────────────────────

CREATE POLICY "shopping_list_items_select_own"
    ON public.shopping_list_items
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "shopping_list_items_insert_own"
    ON public.shopping_list_items
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "shopping_list_items_update_own"
    ON public.shopping_list_items
    FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "shopping_list_items_delete_own"
    ON public.shopping_list_items
    FOR DELETE
    TO authenticated
    USING (user_id = auth.uid());


-- ── share_tokens ───────────────────────────────────────────────────────────────

-- Authenticated users can manage their own share tokens
-- (ownership is inferred via generated_outfits.user_id join)
CREATE POLICY "share_tokens_select_own"
    ON public.share_tokens
    FOR SELECT
    TO authenticated
    USING (
        outfit_id IN (
            SELECT id FROM public.generated_outfits WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "share_tokens_insert_own"
    ON public.share_tokens
    FOR INSERT
    TO authenticated
    WITH CHECK (
        outfit_id IN (
            SELECT id FROM public.generated_outfits WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "share_tokens_update_own"
    ON public.share_tokens
    FOR UPDATE
    TO authenticated
    USING (
        outfit_id IN (
            SELECT id FROM public.generated_outfits WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "share_tokens_delete_own"
    ON public.share_tokens
    FOR DELETE
    TO authenticated
    USING (
        outfit_id IN (
            SELECT id FROM public.generated_outfits WHERE user_id = auth.uid()
        )
    );

-- Public SELECT by token — allows the public outfit page (no auth required)
-- Enforces expiry at the DB layer.
CREATE POLICY "share_tokens_public_select_by_token"
    ON public.share_tokens
    FOR SELECT
    TO anon
    USING (expires_at > now());
