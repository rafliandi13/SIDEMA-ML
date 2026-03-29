-- Create predictions table for anemia screening history
create extension if not exists pgcrypto;

create table if not exists public.predictions (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    method text not null check (method in ('nail', 'conjunctiva')),
    result_label text not null check (result_label in ('anemia_suspected', 'non_anemia')),
    confidence double precision not null check (confidence >= 0 and confidence <= 1),
    threshold double precision not null check (threshold >= 0 and threshold <= 1),
    model_version text not null,
    image_url text not null,
    file_key text not null,
    original_filename text not null,
    mime_type text not null,
    file_size bigint not null,
    quality_status text not null,
    quality_score double precision not null check (quality_score >= 0 and quality_score <= 1),
    notes text,
    created_at timestamptz not null default now()
);

create index if not exists idx_predictions_user_created_at
    on public.predictions (user_id, created_at desc);

create index if not exists idx_predictions_created_at
    on public.predictions (created_at desc);
