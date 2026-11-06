-- ==============================================================================
-- DONIES VIRGIN — DATABASE SCHEMA DDL
-- Complete PostgreSQL schema for Virgin instance isolated state.
-- Guarantees 100% table-level and row-level separation from Donies Daily.
-- ==============================================================================

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- 1. Clip Usage (Anti-fatigue tracker)
CREATE TABLE IF NOT EXISTS ai_brain.virgin_clip_usage (
    id SERIAL PRIMARY KEY,
    clip_name text NOT NULL,
    clip_path text NOT NULL,
    topic_key text NOT NULL,
    video_id text,
    used_at timestamp with time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_virgin_clip_usage_clip_name ON ai_brain.virgin_clip_usage (clip_name);
CREATE INDEX IF NOT EXISTS idx_virgin_clip_usage_used_at ON ai_brain.virgin_clip_usage (used_at);

-- 2. Content Ideas Backlog
CREATE TABLE IF NOT EXISTS ai_brain.virgin_content_ideas (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    topic_key text NOT NULL UNIQUE,
    title text NOT NULL,
    hook_banner text NOT NULL,
    hook_vocal text NOT NULL,
    full_script text NOT NULL,
    scene_breakdown jsonb,
    flow_prompts jsonb,
    sound_fx jsonb,
    status text DEFAULT 'ready'::text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    hook_subtitle text
);

-- 3. Dynamic Learnings & Rules Database (Starts empty / fresh for Virgin Channel)
CREATE TABLE IF NOT EXISTS ai_brain.virgin_learnings (
    id SERIAL PRIMARY KEY,
    category text NOT NULL,
    rule_name text NOT NULL UNIQUE,
    directive text NOT NULL,
    rationale text NOT NULL,
    confidence_score numeric DEFAULT 0.5,
    status text DEFAULT 'active'::text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_virgin_learnings_category ON ai_brain.virgin_learnings (category);
CREATE INDEX IF NOT EXISTS idx_virgin_learnings_status ON ai_brain.virgin_learnings (status);

-- 4. Metrics History & Retention Forensics
CREATE TABLE IF NOT EXISTS ai_brain.virgin_metrics_history (
    id SERIAL PRIMARY KEY,
    video_id text NOT NULL,
    title text NOT NULL,
    snapshot_hours integer NOT NULL,
    views_count integer DEFAULT 0,
    likes_count integer DEFAULT 0,
    comments_count integer DEFAULT 0,
    duration_sec numeric,
    captured_at timestamp with time zone DEFAULT now(),
    stayed_to_watch_pct numeric(5,2),
    engaged_views integer,
    avg_view_duration_sec numeric(6,2),
    avg_view_pct numeric(6,2),
    subs_gained integer DEFAULT 0,
    end_retention_pct numeric(5,2),
    biggest_drop_sec numeric(6,2)
);
CREATE INDEX IF NOT EXISTS idx_virgin_metrics_video_id ON ai_brain.virgin_metrics_history (video_id);
CREATE INDEX IF NOT EXISTS idx_virgin_metrics_captured_at ON ai_brain.virgin_metrics_history (captured_at);

-- 5. Published Posts & YouTube Performance History
CREATE TABLE IF NOT EXISTS ai_brain.virgin_posts (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    video_id text NOT NULL UNIQUE,
    title text NOT NULL,
    hook text,
    story_text text,
    banner_title text,
    tags text[],
    duration_sec numeric(6,2),
    clips_used text[],
    privacy_status text DEFAULT 'public'::text,
    short_url text NOT NULL,
    posted_at timestamp with time zone DEFAULT now(),
    views_count integer DEFAULT 0,
    likes_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    stayed_to_watch_pct numeric(5,2),
    engaged_views integer,
    avg_view_duration_sec numeric(6,2),
    avg_view_pct numeric(6,2),
    subs_gained integer DEFAULT 0,
    end_retention_pct numeric(5,2),
    biggest_drop_sec numeric(6,2),
    retention_curve_json jsonb
);
CREATE INDEX IF NOT EXISTS idx_virgin_posts_posted_at ON ai_brain.virgin_posts (posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_virgin_posts_video_id ON ai_brain.virgin_posts (video_id);

-- 6. Production State Queue
CREATE TABLE IF NOT EXISTS ai_brain.virgin_production_queue (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    topic_key text NOT NULL UNIQUE,
    title text NOT NULL,
    current_stage ai_brain.production_stage DEFAULT 'IDEA_SELECTED'::ai_brain.production_stage NOT NULL,
    audio_path text,
    caption_path text,
    background_video_path text,
    rendered_master_path text,
    youtube_video_id text,
    qc_report jsonb DEFAULT '{}'::jsonb,
    error_message text,
    retry_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_virgin_queue_stage ON ai_brain.virgin_production_queue (current_stage);

-- 7. Comment Sniper Logs
CREATE TABLE IF NOT EXISTS ai_brain.virgin_sniper_logs (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    video_id text NOT NULL UNIQUE,
    video_title text,
    channel_title text,
    comment_text text NOT NULL,
    comment_id text,
    created_at timestamp with time zone DEFAULT now()
);
