--
-- PostgreSQL database dump
--

\restrict 01QHHrD2Bl2JeKe1pXllTAMwvfI1lwkba08Mi0JfvyuyqkL5V4ZttcPEAhpn5KH

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: doniesdaily_clip_usage; Type: TABLE; Schema: ai_brain; Owner: postgres
--

CREATE TABLE ai_brain.doniesdaily_clip_usage (
    id integer NOT NULL,
    clip_name text NOT NULL,
    clip_path text NOT NULL,
    topic_key text NOT NULL,
    video_id text,
    used_at timestamp with time zone DEFAULT now()
);


ALTER TABLE ai_brain.doniesdaily_clip_usage OWNER TO postgres;

--
-- Name: doniesdaily_clip_usage_id_seq; Type: SEQUENCE; Schema: ai_brain; Owner: postgres
--

CREATE SEQUENCE ai_brain.doniesdaily_clip_usage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ai_brain.doniesdaily_clip_usage_id_seq OWNER TO postgres;

--
-- Name: doniesdaily_clip_usage_id_seq; Type: SEQUENCE OWNED BY; Schema: ai_brain; Owner: postgres
--

ALTER SEQUENCE ai_brain.doniesdaily_clip_usage_id_seq OWNED BY ai_brain.doniesdaily_clip_usage.id;


--
-- Name: doniesdaily_content_ideas; Type: TABLE; Schema: ai_brain; Owner: postgres
--

CREATE TABLE ai_brain.doniesdaily_content_ideas (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    topic_key text NOT NULL,
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


ALTER TABLE ai_brain.doniesdaily_content_ideas OWNER TO postgres;

--
-- Name: doniesdaily_learnings; Type: TABLE; Schema: ai_brain; Owner: postgres
--

CREATE TABLE ai_brain.doniesdaily_learnings (
    id integer NOT NULL,
    category text NOT NULL,
    rule_name text NOT NULL,
    directive text NOT NULL,
    rationale text NOT NULL,
    confidence_score numeric DEFAULT 0.5,
    status text DEFAULT 'active'::text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE ai_brain.doniesdaily_learnings OWNER TO postgres;

--
-- Name: doniesdaily_learnings_id_seq; Type: SEQUENCE; Schema: ai_brain; Owner: postgres
--

CREATE SEQUENCE ai_brain.doniesdaily_learnings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ai_brain.doniesdaily_learnings_id_seq OWNER TO postgres;

--
-- Name: doniesdaily_learnings_id_seq; Type: SEQUENCE OWNED BY; Schema: ai_brain; Owner: postgres
--

ALTER SEQUENCE ai_brain.doniesdaily_learnings_id_seq OWNED BY ai_brain.doniesdaily_learnings.id;


--
-- Name: doniesdaily_metrics_history; Type: TABLE; Schema: ai_brain; Owner: postgres
--

CREATE TABLE ai_brain.doniesdaily_metrics_history (
    id integer NOT NULL,
    video_id text NOT NULL,
    title text NOT NULL,
    snapshot_hours integer NOT NULL,
    views_count integer DEFAULT 0,
    likes_count integer DEFAULT 0,
    comments_count integer DEFAULT 0,
    duration_sec numeric,
    captured_at timestamp with time zone DEFAULT now(),
    stayed_to_watch_pct numeric(5,2) DEFAULT NULL::numeric,
    engaged_views integer,
    avg_view_duration_sec numeric(6,2) DEFAULT NULL::numeric,
    avg_view_pct numeric(6,2) DEFAULT NULL::numeric,
    subs_gained integer DEFAULT 0,
    end_retention_pct numeric(5,2) DEFAULT NULL::numeric,
    biggest_drop_sec numeric(6,2) DEFAULT NULL::numeric
);


ALTER TABLE ai_brain.doniesdaily_metrics_history OWNER TO postgres;

--
-- Name: doniesdaily_metrics_history_id_seq; Type: SEQUENCE; Schema: ai_brain; Owner: postgres
--

CREATE SEQUENCE ai_brain.doniesdaily_metrics_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ai_brain.doniesdaily_metrics_history_id_seq OWNER TO postgres;

--
-- Name: doniesdaily_metrics_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ai_brain; Owner: postgres
--

ALTER SEQUENCE ai_brain.doniesdaily_metrics_history_id_seq OWNED BY ai_brain.doniesdaily_metrics_history.id;


--
-- Name: doniesdaily_posts; Type: TABLE; Schema: ai_brain; Owner: postgres
--

CREATE TABLE ai_brain.doniesdaily_posts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    video_id text NOT NULL,
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
    stayed_to_watch_pct numeric(5,2) DEFAULT NULL::numeric,
    engaged_views integer,
    avg_view_duration_sec numeric(6,2) DEFAULT NULL::numeric,
    avg_view_pct numeric(6,2) DEFAULT NULL::numeric,
    subs_gained integer DEFAULT 0,
    end_retention_pct numeric(5,2) DEFAULT NULL::numeric,
    biggest_drop_sec numeric(6,2) DEFAULT NULL::numeric,
    retention_curve_json jsonb
);


ALTER TABLE ai_brain.doniesdaily_posts OWNER TO postgres;

--
-- Name: doniesdaily_production_queue; Type: TABLE; Schema: ai_brain; Owner: postgres
--

CREATE TABLE ai_brain.doniesdaily_production_queue (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    topic_key text NOT NULL,
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


ALTER TABLE ai_brain.doniesdaily_production_queue OWNER TO postgres;

--
-- Name: doniesdaily_sniper_logs; Type: TABLE; Schema: ai_brain; Owner: postgres
--

CREATE TABLE ai_brain.doniesdaily_sniper_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    video_id text NOT NULL,
    video_title text,
    channel_title text,
    comment_text text NOT NULL,
    comment_id text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE ai_brain.doniesdaily_sniper_logs OWNER TO postgres;

--
-- Name: doniesdaily_clip_usage id; Type: DEFAULT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_clip_usage ALTER COLUMN id SET DEFAULT nextval('ai_brain.doniesdaily_clip_usage_id_seq'::regclass);


--
-- Name: doniesdaily_learnings id; Type: DEFAULT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_learnings ALTER COLUMN id SET DEFAULT nextval('ai_brain.doniesdaily_learnings_id_seq'::regclass);


--
-- Name: doniesdaily_metrics_history id; Type: DEFAULT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_metrics_history ALTER COLUMN id SET DEFAULT nextval('ai_brain.doniesdaily_metrics_history_id_seq'::regclass);


--
-- Name: doniesdaily_clip_usage doniesdaily_clip_usage_pkey; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_clip_usage
    ADD CONSTRAINT doniesdaily_clip_usage_pkey PRIMARY KEY (id);


--
-- Name: doniesdaily_content_ideas doniesdaily_content_ideas_pkey; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_content_ideas
    ADD CONSTRAINT doniesdaily_content_ideas_pkey PRIMARY KEY (id);


--
-- Name: doniesdaily_content_ideas doniesdaily_content_ideas_topic_key_key; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_content_ideas
    ADD CONSTRAINT doniesdaily_content_ideas_topic_key_key UNIQUE (topic_key);


--
-- Name: doniesdaily_learnings doniesdaily_learnings_pkey; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_learnings
    ADD CONSTRAINT doniesdaily_learnings_pkey PRIMARY KEY (id);


--
-- Name: doniesdaily_learnings doniesdaily_learnings_rule_name_key; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_learnings
    ADD CONSTRAINT doniesdaily_learnings_rule_name_key UNIQUE (rule_name);


--
-- Name: doniesdaily_metrics_history doniesdaily_metrics_history_pkey; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_metrics_history
    ADD CONSTRAINT doniesdaily_metrics_history_pkey PRIMARY KEY (id);


--
-- Name: doniesdaily_posts doniesdaily_posts_pkey; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_posts
    ADD CONSTRAINT doniesdaily_posts_pkey PRIMARY KEY (id);


--
-- Name: doniesdaily_posts doniesdaily_posts_video_id_key; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_posts
    ADD CONSTRAINT doniesdaily_posts_video_id_key UNIQUE (video_id);


--
-- Name: doniesdaily_production_queue doniesdaily_production_queue_pkey; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_production_queue
    ADD CONSTRAINT doniesdaily_production_queue_pkey PRIMARY KEY (id);


--
-- Name: doniesdaily_production_queue doniesdaily_production_queue_topic_key_key; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_production_queue
    ADD CONSTRAINT doniesdaily_production_queue_topic_key_key UNIQUE (topic_key);


--
-- Name: doniesdaily_sniper_logs doniesdaily_sniper_logs_pkey; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_sniper_logs
    ADD CONSTRAINT doniesdaily_sniper_logs_pkey PRIMARY KEY (id);


--
-- Name: doniesdaily_sniper_logs uq_sniper_video; Type: CONSTRAINT; Schema: ai_brain; Owner: postgres
--

ALTER TABLE ONLY ai_brain.doniesdaily_sniper_logs
    ADD CONSTRAINT uq_sniper_video UNIQUE (video_id);


--
-- Name: idx_clip_usage_clip_name; Type: INDEX; Schema: ai_brain; Owner: postgres
--

CREATE INDEX idx_clip_usage_clip_name ON ai_brain.doniesdaily_clip_usage USING btree (clip_name);


--
-- Name: idx_clip_usage_used_at; Type: INDEX; Schema: ai_brain; Owner: postgres
--

CREATE INDEX idx_clip_usage_used_at ON ai_brain.doniesdaily_clip_usage USING btree (used_at);


--
-- Name: idx_doni_queue_stage; Type: INDEX; Schema: ai_brain; Owner: postgres
--

CREATE INDEX idx_doni_queue_stage ON ai_brain.doniesdaily_production_queue USING btree (current_stage);


--
-- Name: idx_doniesdaily_posted_at; Type: INDEX; Schema: ai_brain; Owner: postgres
--

CREATE INDEX idx_doniesdaily_posted_at ON ai_brain.doniesdaily_posts USING btree (posted_at DESC);


--
-- Name: idx_doniesdaily_video_id; Type: INDEX; Schema: ai_brain; Owner: postgres
--

CREATE INDEX idx_doniesdaily_video_id ON ai_brain.doniesdaily_posts USING btree (video_id);


--
-- Name: idx_learnings_category; Type: INDEX; Schema: ai_brain; Owner: postgres
--

CREATE INDEX idx_learnings_category ON ai_brain.doniesdaily_learnings USING btree (category);


--
-- Name: idx_learnings_status; Type: INDEX; Schema: ai_brain; Owner: postgres
--

CREATE INDEX idx_learnings_status ON ai_brain.doniesdaily_learnings USING btree (status);


--
-- Name: idx_metrics_captured_at; Type: INDEX; Schema: ai_brain; Owner: postgres
--

CREATE INDEX idx_metrics_captured_at ON ai_brain.doniesdaily_metrics_history USING btree (captured_at);


--
-- Name: idx_metrics_video_id; Type: INDEX; Schema: ai_brain; Owner: postgres
--

CREATE INDEX idx_metrics_video_id ON ai_brain.doniesdaily_metrics_history USING btree (video_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 01QHHrD2Bl2JeKe1pXllTAMwvfI1lwkba08Mi0JfvyuyqkL5V4ZttcPEAhpn5KH

