-- Run this in Supabase SQL Editor (once, after schema.sql)
create table if not exists messages (
    id              uuid primary key default uuid_generate_v4(),
    contact_id      uuid not null references contacts(id) on delete cascade,
    direction       text not null check (direction in ('incoming','outgoing')),
    text            text not null,
    dripify_msg_id  text,
    sent_to_dripify boolean default false,
    created_at      timestamptz default now()
);

create index if not exists messages_contact_idx on messages(contact_id, created_at);
