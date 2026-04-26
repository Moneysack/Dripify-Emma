-- Run once in Supabase SQL editor

alter table contacts
  add column if not exists dripify_lead_id   text    default '',
  add column if not exists phone             text    default '',
  add column if not exists website           text    default '',
  add column if not exists industry          text    default '',
  add column if not exists top_skill         text    default '',
  add column if not exists time_in_role      text    default '',
  add column if not exists is_premium        boolean default false,
  add column if not exists responded         boolean default false,
  add column if not exists company_employees integer default 0,
  add column if not exists campaign_name     text    default '',
  add column if not exists campaign_status   text    default '',
  add column if not exists campaign_step     text    default '',
  add column if not exists linkedin_public_id text   default '';
