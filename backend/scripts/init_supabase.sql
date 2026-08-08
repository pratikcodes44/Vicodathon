-- Supabase Database Initialization
-- Execute this script in the Supabase SQL Editor

-- 1. Candidates Table
CREATE TABLE IF NOT EXISTS public.candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    avatar_url TEXT,
    status TEXT DEFAULT 'Active'
);

-- 2. Interview Sessions Table
CREATE TABLE IF NOT EXISTS public.interview_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES public.candidates(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed'
    current_turn INT DEFAULT 1
);

-- 3. Chat Messages Table
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.interview_sessions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    sender TEXT NOT NULL, -- 'interviewer', 'candidate', 'system'
    content TEXT NOT NULL
);

-- 4. Scorecards Table
CREATE TABLE IF NOT EXISTS public.scorecards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.interview_sessions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    overall_score INT NOT NULL,
    communication_score FLOAT,
    technical_score FLOAT,
    problem_solving_score FLOAT,
    detailed_feedback JSONB NOT NULL
);

-- Enable Row Level Security (RLS) but allow all operations for now (or manage via Service Role)
ALTER TABLE public.candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interview_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scorecards ENABLE ROW LEVEL SECURITY;

-- Allow anon read/insert for hackathon speed (In production, restrict to authenticated users)
CREATE POLICY "Allow public read access" ON public.candidates FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON public.interview_sessions FOR SELECT USING (true);
CREATE POLICY "Allow public insert access" ON public.interview_sessions FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update access" ON public.interview_sessions FOR UPDATE USING (true);
CREATE POLICY "Allow public read access" ON public.chat_messages FOR SELECT USING (true);
CREATE POLICY "Allow public insert access" ON public.chat_messages FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public read access" ON public.scorecards FOR SELECT USING (true);
CREATE POLICY "Allow public insert access" ON public.scorecards FOR INSERT WITH CHECK (true);

-- Seed Initial Candidates
INSERT INTO public.candidates (name, role, status) VALUES 
('Diane Foster', 'AI Engineer', 'Active'),
('Gerald Combs', 'DevOps Engineer', 'Scheduled'),
('Michael Lee', 'UX Designer', 'Scheduled'),
('Sarah Chen', 'Frontend Developer', 'Scheduled');
