-- Run once in Supabase SQL Editor to add avatar_url to contacts
alter table contacts add column if not exists avatar_url text default '';
