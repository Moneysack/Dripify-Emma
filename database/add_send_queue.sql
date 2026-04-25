-- Run once in Supabase SQL Editor
-- Queue for messages sent via Vercel dashboard (processed by local sync)

create table if not exists pending_sends (
  id                  uuid primary key default gen_random_uuid(),
  contact_id          uuid references contacts(id),
  dripify_contact_id  text not null default '',
  text                text not null,
  status              text default 'pending',  -- pending | sent | failed
  created_at          timestamptz default now(),
  sent_at             timestamptz,
  error_msg           text
);

-- Also add country column to contacts if missing
alter table contacts
  add column if not exists country text default '';
