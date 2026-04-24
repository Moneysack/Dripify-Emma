-- Run once in Supabase SQL Editor
-- Adds LLM-analysis columns to emma_state

alter table emma_state
  add column if not exists trust_conf        float   default 0.5,
  add column if not exists clarity_conf      float   default 0.5,
  add column if not exists ease_conf         float   default 0.5,
  add column if not exists momentum_conf     float   default 0.5,
  add column if not exists state_conf        float   default 0.5,
  add column if not exists state_cluster     text    default 'S0',
  add column if not exists movement_score    int     default 0,
  add column if not exists movement_stability text   default 'M0',
  add column if not exists output_mode       text    default 'NORMAL',
  add column if not exists escalation_eligible boolean default false,
  add column if not exists pain_points       jsonb   default '[]',
  add column if not exists prospect_summary  text    default '',
  add column if not exists analyzed_at       timestamptz;
