-- Run once in Supabase SQL Editor
-- Adds email, connections_count to contacts

alter table contacts
  add column if not exists email             text default '',
  add column if not exists connections_count text default '';
