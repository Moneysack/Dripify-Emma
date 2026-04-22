-- Emma Sales Agent — Supabase Schema
-- Run this once in the Supabase SQL editor

create extension if not exists "uuid-ossp";

-- ─── contacts ────────────────────────────────────────────────────────────────
create table if not exists contacts (
    id                  uuid primary key default uuid_generate_v4(),
    dripify_contact_id  text unique not null,
    linkedin_name       text,
    campaign_id         text,
    created_at          timestamptz default now()
);

-- ─── conversations ────────────────────────────────────────────────────────────
create table if not exists conversations (
    id                          uuid primary key default uuid_generate_v4(),
    contact_id                  uuid not null references contacts(id) on delete cascade,
    openai_thread_id            text,
    turn_count                  int default 0,
    last_message_at             timestamptz,
    last_dripify_message_id     text,
    created_at                  timestamptz default now()
);

create unique index if not exists conversations_contact_id_idx on conversations(contact_id);

-- ─── emma_state ───────────────────────────────────────────────────────────────
create table if not exists emma_state (
    id                      uuid primary key default uuid_generate_v4(),
    contact_id              uuid not null references contacts(id) on delete cascade,
    state_score             float default 5.0,
    clarity_score           float default 5.0,
    ease_score              float default 5.0,
    trust_score             float default 5.0,
    momentum_score          float default 5.0,
    authority_score         float default 5.0,
    authority_confidence    float default 0.5,
    decision_type           text default 'MIXED',  -- THINKER/DOER/VISUAL/SPEAKER/MIXED
    current_blocker         text,
    current_intervention    text,
    flow_mode               text default 'HOLD',   -- ADVANCE/HOLD/RECOVERY
    updated_at              timestamptz default now()
);

create unique index if not exists emma_state_contact_id_idx on emma_state(contact_id);

-- ─── agent_log ────────────────────────────────────────────────────────────────
create table if not exists agent_log (
    id                  uuid primary key default uuid_generate_v4(),
    contact_id          uuid not null references contacts(id) on delete cascade,
    turn                int,
    incoming_message    text,
    blocker             text,
    intervention        text,
    outgoing_message    text,
    flow_mode           text,
    layer_snapshot      jsonb,   -- full layer scores at decision time
    created_at          timestamptz default now()
);
