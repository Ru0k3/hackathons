-- =============================================================================
-- ModeOn — Supabase Schema
-- Run this in the Supabase SQL editor (Dashboard → SQL Editor → New query)
-- =============================================================================

-- ── Extensions ────────────────────────────────────────────────────────────────
create extension if not exists "uuid-ossp";

-- =============================================================================
-- TABLES
-- =============================================================================

-- ── Profiles ──────────────────────────────────────────────────────────────────
create table if not exists public.profiles (
  id              uuid primary key references auth.users(id) on delete cascade,
  full_name       text,
  gender          text,
  colour_palette  text,
  style_tags      text[]  default '{}',
  onboarded       boolean default false,
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

-- ── Wardrobe items ────────────────────────────────────────────────────────────
create table if not exists public.wardrobe_items (
  id                 uuid primary key default uuid_generate_v4(),
  user_id            uuid not null references auth.users(id) on delete cascade,
  image_url          text not null,
  category           text not null,          -- tops|bottoms|outerwear|shoes|accessories|dresses|suits
  colour             text,
  brand              text,
  tags               text[]  default '{}',
  description        text,
  care_instructions  text,
  notes              text,
  laundry_status     text    default 'clean', -- clean|dirty|washing
  created_at         timestamptz default now(),
  updated_at         timestamptz default now()
);

create index if not exists wardrobe_items_user_id_idx  on public.wardrobe_items(user_id);
create index if not exists wardrobe_items_category_idx on public.wardrobe_items(category);

-- ── Outfits ───────────────────────────────────────────────────────────────────
create table if not exists public.outfits (
  id           uuid primary key default uuid_generate_v4(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  name         text not null,
  item_ids     uuid[]  default '{}',
  occasion     text,
  notes        text,
  share_token  text unique,                   -- non-null = publicly shared
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);

create index if not exists outfits_user_id_idx    on public.outfits(user_id);
create index if not exists outfits_share_token_idx on public.outfits(share_token);

-- ── Outfit checks ─────────────────────────────────────────────────────────────
create table if not exists public.outfit_checks (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  image_url  text not null,
  result     jsonb,
  context    jsonb default '{}',
  created_at timestamptz default now()
);

create index if not exists outfit_checks_user_id_idx on public.outfit_checks(user_id);

-- ── Shopping items ────────────────────────────────────────────────────────────
create table if not exists public.shopping_items (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  name       text not null,
  category   text,
  colour     text,
  url        text,
  image_url  text,
  notes      text,
  purchased  boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists shopping_items_user_id_idx on public.shopping_items(user_id);

-- =============================================================================
-- UPDATED_AT TRIGGER
-- =============================================================================
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create or replace trigger set_profiles_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at();

create or replace trigger set_wardrobe_updated_at
  before update on public.wardrobe_items
  for each row execute function public.set_updated_at();

create or replace trigger set_outfits_updated_at
  before update on public.outfits
  for each row execute function public.set_updated_at();

create or replace trigger set_shopping_updated_at
  before update on public.shopping_items
  for each row execute function public.set_updated_at();

-- =============================================================================
-- ROW LEVEL SECURITY
-- =============================================================================
alter table public.profiles        enable row level security;
alter table public.wardrobe_items  enable row level security;
alter table public.outfits         enable row level security;
alter table public.outfit_checks   enable row level security;
alter table public.shopping_items  enable row level security;

-- ── Profiles ──────────────────────────────────────────────────────────────────
create policy "profiles: owner full access"
  on public.profiles for all
  using  (auth.uid() = id)
  with check (auth.uid() = id);

-- ── Wardrobe items ────────────────────────────────────────────────────────────
create policy "wardrobe: owner full access"
  on public.wardrobe_items for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- ── Outfits ───────────────────────────────────────────────────────────────────
create policy "outfits: owner full access"
  on public.outfits for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Shared outfits are publicly readable (no auth required)
create policy "outfits: public read via share_token"
  on public.outfits for select
  using (share_token is not null);

-- ── Outfit checks ─────────────────────────────────────────────────────────────
create policy "outfit_checks: owner full access"
  on public.outfit_checks for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- ── Shopping items ────────────────────────────────────────────────────────────
create policy "shopping: owner full access"
  on public.shopping_items for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- =============================================================================
-- AUTO-CREATE PROFILE ON SIGN-UP
-- =============================================================================
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles (id, full_name)
  values (
    new.id,
    new.raw_user_meta_data->>'full_name'
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

create or replace trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- =============================================================================
-- DONE
-- =============================================================================
-- Run this file once in the Supabase SQL editor.
-- Service-role operations (backend) bypass RLS automatically.
-- Anon/authenticated keys (frontend) are governed by the policies above.
