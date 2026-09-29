-- backend/app/db/schema.sql
-- Modeon Full Supabase Schema — PLACEHOLDER
-- Run this in the Supabase SQL editor to initialise all tables and RLS policies.
-- Requires the Supabase auth schema (auth.users) to be present.

-- ─── EXTENSIONS ─────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── USER PROFILES ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_profiles (
  id                UUID        PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name      TEXT,
  gender_pref       TEXT,
  style_archetypes  TEXT[]      DEFAULT '{}',
  occasion_prefs    TEXT[]      DEFAULT '{}',
  colour_palette    TEXT,
  notif_daily       BOOLEAN     DEFAULT TRUE,
  notif_tips        BOOLEAN     DEFAULT FALSE,
  notif_features    BOOLEAN     DEFAULT TRUE,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ─── SUBSCRIPTIONS ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subscriptions (
  id                  UUID  PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID  NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  stripe_customer_id  TEXT,
  stripe_sub_id       TEXT,
  plan                TEXT  NOT NULL DEFAULT 'free',    -- 'free' | 'premium'
  status              TEXT  NOT NULL DEFAULT 'active',  -- 'active' | 'cancelled' | 'past_due'
  period_end          TIMESTAMPTZ,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─── WARDROBE ITEMS ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wardrobe_items (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  blob_path     TEXT        NOT NULL,   -- Azure Blob path in wardrobe-originals container
  thumb_path    TEXT,                   -- Azure Blob path in wardrobe-thumbnails container
  category      TEXT,
  color         TEXT,                   -- primary colour label
  colours       TEXT[]      DEFAULT '{}',
  pattern       TEXT,
  formality     TEXT,
  seasons       TEXT[]      DEFAULT '{}',
  custom_tags   TEXT[]      DEFAULT '{}',
  in_laundry    BOOLEAN     DEFAULT FALSE,
  archived_at   TIMESTAMPTZ,            -- soft-delete timestamp
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ─── GENERATED OUTFITS ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS generated_outfits (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  item_ids        UUID[]      DEFAULT '{}',
  occasion        TEXT,
  name            TEXT,
  explanation     TEXT,
  saved_at        TIMESTAMPTZ,           -- NULL = not saved by user
  share_token     TEXT        UNIQUE,
  share_expires   TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── OUTFIT SWIPES ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS outfit_swipes (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  outfit_id   UUID        REFERENCES generated_outfits(id) ON DELETE SET NULL,
  direction   TEXT        NOT NULL CHECK (direction IN ('like', 'dislike', 'save')),
  swiped_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ─── OUTFIT CHECKS ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS outfit_checks (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  blob_path       TEXT        NOT NULL,
  overall_score   NUMERIC(3,1),
  colour_harmony  JSONB,      -- { score, feedback }
  fit_proportion  JSONB,      -- { score, feedback }
  occasion_match  JSONB,      -- { score, feedback }
  summary         TEXT,
  checked_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── SHOPPING UPLOADS ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shopping_uploads (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  blob_path   TEXT        NOT NULL,
  tags        JSONB,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ─── SHOPPING LIST ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shopping_list_items (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  upload_id   UUID        REFERENCES shopping_uploads(id) ON DELETE SET NULL,
  blob_path   TEXT,
  tags        JSONB,
  added_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ─── ROW LEVEL SECURITY ──────────────────────────────────────────────────────
ALTER TABLE user_profiles       ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions       ENABLE ROW LEVEL SECURITY;
ALTER TABLE wardrobe_items      ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_outfits   ENABLE ROW LEVEL SECURITY;
ALTER TABLE outfit_swipes       ENABLE ROW LEVEL SECURITY;
ALTER TABLE outfit_checks       ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_uploads    ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_list_items ENABLE ROW LEVEL SECURITY;

-- Each user can only see/modify their own rows
CREATE POLICY "own_data" ON user_profiles       FOR ALL USING (auth.uid() = id);
CREATE POLICY "own_data" ON subscriptions       FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_data" ON wardrobe_items      FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_data" ON generated_outfits   FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_data" ON outfit_swipes       FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_data" ON outfit_checks       FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_data" ON shopping_uploads    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_data" ON shopping_list_items FOR ALL USING (auth.uid() = user_id);

-- Public shared outfits — readable by anyone with a valid non-expired token
CREATE POLICY "public_share" ON generated_outfits
  FOR SELECT
  USING (share_token IS NOT NULL AND share_expires > NOW());

-- ─── UPDATED_AT TRIGGER ──────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_user_profiles_updated   BEFORE UPDATE ON user_profiles       FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_subscriptions_updated   BEFORE UPDATE ON subscriptions        FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_wardrobe_items_updated  BEFORE UPDATE ON wardrobe_items       FOR EACH ROW EXECUTE FUNCTION update_updated_at();
