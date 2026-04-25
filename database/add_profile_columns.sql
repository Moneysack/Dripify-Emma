-- Run once in Supabase SQL Editor
-- Adds LinkedIn profile fields to contacts

alter table contacts
  add column if not exists title        text default '',
  add column if not exists company_name text default '',
  add column if not exists location     text default '',
  add column if not exists linkedin_url text default '';
