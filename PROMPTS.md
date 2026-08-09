# AI Usage Log: The Interview Agent

This document contains a chronological log of the primary prompts provided to the AI agent during the development, debugging, and deployment phases of this project.

---

### Prompt 1: Initial Backend Bug & UI Refactor
> **Role & Context:** You are a Full-Stack Architect fixing a state machine bug in "The Interview Agent" and applying a strict dark-only UI standard. The interview completes immediately after turn 1 because the `plan` array length evaluates incorrectly, and the frontend currently uses a light theme.
> **Task:** Fix the SQLite JSON array parsing in the backend and refactor the Next.js Tailwind classes to a Cosmic Dark Mode aesthetic.
> **Requirements:**
> 1. Backend Fix (`app/api/interview.py` or `orchestrator.py`): Ensure `session.plan` is properly populated...

### Prompt 2: State Machine Backend Fix
> **Role & Context:** You are a Backend Architect fixing a critical state machine bug in "The Interview Agent". The interview completes immediately after turn 1 because the `plan` array length evaluates incorrectly. You are strictly forbidden from altering any Next.js frontend code, CSS, or UI layouts.
> **Task:** Fix the SQLite JSON array parsing and session initialization logic in the backend.

### Prompt 3: Data-Mapping Bug
> **Role & Context:** You are debugging a critical state machine and data-mapping bug in "The Interview Agent". The interview terminates immediately after the first user input because the session plan is empty. The UI is completely off-limits—do not touch any Next.js Tailwind classes, layouts, or CSS.
> **Task:** Fix the `candidateId` data mapping in the Next.js API call, and add a backend safety net for empty curriculum plans.

### Prompt 4: React Lifecycle & Chat Initialization
> **Role & Context:** You are a React/Next.js Logic Engineer finalizing the integration for "The Interview Agent". The UI design is locked. You are STRICTLY FORBIDDEN from altering any Tailwind classes, CSS files, HTML structures, or visual components.
> **Task:** Rewrite the React state and lifecycle hooks in the main chat component to properly initialize and maintain a session with the FastAPI backend.

### Prompt 5: State Machine & JSON Output
> **Role & Context:** You are a React/Next.js Logic Engineer fixing a broken state machine in "The Interview Agent". The UI design is locked. You are STRICTLY FORBIDDEN from altering any Tailwind classes, HTML structures, or visual elements.
> **Task:** Fix the candidate selection payload, remove hardcoded state, and parse the final JSON output.

### Prompt 6: Deep State-Management Debugging
> **Role & Context:** You are an Expert Full-Stack Engineer debugging a critical state-management and API integration failure in "The Interview Agent" (Next.js App Router frontend, FastAPI + SQLite backend). The backend logic and database work perfectly, but the frontend has a severe data disconnect that is causing the backend to instantly terminate the interview on the first turn.
> **Task:** Scan and fix the frontend API disconnect.

### Prompt 7: Major Architecture Overhaul (Supabase + Netlify)
> **Role & Context:** You are a Senior Full-Stack Architect overhauling "The Interview Agent". The project uses a Next.js App Router frontend and a FastAPI backend. You need to prepare the frontend for Netlify deployment, integrate a newly pulled Supabase data layer, and heavily rewrite the AI's system prompts to make the conversation feel organic and strictly grounded in the dataset.
> **Task:** 
> 1. Supabase Integration (Zero-Breakage Data Swap) - transition from local sqlite.db to Supabase PostgreSQL and Auth.

### Prompt 8: Initiating Deployment
> i want to deploy the frontend now in the netlify and the backend api server and everything in the render. so get on to your work and make sure everything stays intact and nothing breaks.

### Prompt 9: Addressing Render Errors
> look at this render error it is showing error

### Prompt 10: Addressing Netlify CVE Blocker
> The Netlify deploy errored, with the following guidance provided: The build is failing due to a critical security vulnerability in the version of Next.js being used. Netlify is blocking the deploy to protect the project.

### Prompt 11: End-to-End Testing Request
> okay now both myn frontend in netlify and backend in render are live. now how do i check if the project is in working condition or not and if it is then how do i start it

### Prompt 12: Diagnosing API Connectivity
> my render backend is not able to communicate with the netlify frontend. analyse the entire codebase and also there is another error when i open backend on chrome it shows detail not found.

### Prompt 13: Continuing Fixes
> continue work

### Prompt 14: API Connectivity (Round 2)
> still the same thing. it was working completely fine in the local but when i deployed it there are issues in integrating everything

### Prompt 15: Fixing the Missing UI Feedback Panel
> everything is working right now but the interview ended at the 5th question with message your interview is completed and that's it. no feedback,nothing else. when i re entered message it only said interview already completed

### Prompt 16: Log Generation
> generate prompts.md file for all the prompts i gave you in the given format

### Prompt 17: Fixing the UI Feedback Deployment
> the feedback did not come out from this. it only executed upto 5 questions then terminnated the interview with a message. solve this error asap. do not ask for any permission you are fully allowed to run commands
