# HuskyAdvisor 🐾
### AI-Powered Academic Advising Chatbot for Northeastern MS Computer Science Program

**Built by:** Dhanush Murdur Hemanth  
**Program:** MS Artificial Intelligence, Northeastern University Seattle  
**Course:** Foundations of AI — CS5100 (GEENG Cohort, Summer 2026)  
**GitHub Repo:** https://github.com/5100-SEA-GEENG/final-project-husky-advisor

---

## What is HuskyAdvisor?

HuskyAdvisor is an AI-powered academic advising chatbot built specifically for students in Northeastern University's MS Computer Science program, covering all 5 concentration tracks: AI/ML, Systems, Data Science, Software Engineering, and Theory. Instead of waiting for an advising appointment to answer routine questions, students can get instant, reasoned answers about courses, prerequisites, study paths, and graduation planning.

The key difference from a static course catalog: HuskyAdvisor **reasons** across course data. It can answer questions like "What if I skip CS5800?" or "Build me a 6-semester AI/ML study path" — questions that require multi-step logic, not just data lookup.

---

## The Problem It Solves

A static course catalog can tell you what prerequisites CS6140 requires. But it cannot reason. HuskyAdvisor answers things like:

- "Given what I've completed, am I ready for CS6140?"
- "What if I skip CS5800 — what courses become blocked?"
- "Build me a semester-by-semester ML career path"
- "Help me prepare questions for my advisor meeting"

None of these are simple lookups — they require reasoning across multiple data points simultaneously.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Create React App) |
| Backend | Node.js + Express |
| AI Model | Claude Sonnet 4.6 (Anthropic API) |
| AI Technique | Prompt Engineering + Knowledge Grounding |
| Knowledge Base | `knowledge_base.json` — 30 MS CS courses |
| Fonts | Inter, DM Sans |

---

## How It Works

```
User types question
        ↓
React frontend sends message to Express backend
        ↓
Backend injects knowledge_base.json into Claude system prompt
        ↓
Claude reasons over 30 courses + user question
        ↓
Response returned with FOLLOWUP_1/2/3 structured output
        ↓
React parses follow-up buttons and renders response
```

### AI Approach: Prompt Engineering + Knowledge Grounding

HuskyAdvisor uses **prompt engineering at inference time** — not fine-tuning or RAG.

The entire `knowledge_base.json` (30 courses) is injected into Claude's system prompt on every API call. Claude then reasons over this grounded context to answer the user's question. This approach is appropriate because:

- 30 courses fit comfortably within Claude's context window
- Direct injection is more reliable than RAG for this scale
- No vector database or embedding infrastructure needed
- The AI reasons holistically across all courses simultaneously

The system prompt encodes 7 advising capabilities:
1. Course info lookup
2. Prerequisite gap analysis
3. Course comparison
4. Study path generation
5. Am I Ready checker
6. What-If reasoning
7. Advisor prep assistant

---

## Knowledge Base

`knowledge_base.json` contains 30 Northeastern MS CS courses. Each course includes:

| Field | Description |
|---|---|
| id | Course code (e.g. CS6140) |
| name | Course name |
| credits | Credit hours |
| tuition_cost | Cost per course |
| description | Course description |
| prerequisites | Required prior courses |
| tracks | Concentration track(s) |
| difficulty | 1–5 scale |
| workload_hrs_per_week | Weekly time commitment |
| career_tags | Target roles/companies |
| professor | Instructor name |
| semesters_offered | Fall/Spring/Summer availability |
| delivery_mode | In-person/Online/Hybrid |
| class_size | Enrollment size |
| student_rating | Student satisfaction score |
| grade_distribution | A/B/C/D/F percentages |
| coop_relevance | Co-op applicability |

> **Note on Data Sources:** Factual fields (course names, credits, prerequisites, professors, semesters offered) were sourced from the Northeastern University Graduate CS catalog. Additional fields such as difficulty ratings, workload estimates, student ratings, and grade distributions were synthesized using AI to enrich the knowledge base for demonstration purposes and do not represent official Northeastern data.

---

## Features

### 1. Course Info Lookup
Ask about any course — credits, professor, semesters offered, tuition cost, prerequisites, and more.
> *"How many credits is CS6140, who teaches it, and when is it offered?"*

### 2. Prerequisite Gap Analyzer
Given your completed courses, HuskyAdvisor traces the full prerequisite chain to your target course and identifies exactly what you're missing.
> *"I've completed CS5001 and CS5002. What do I need for CS6140?"*

### 3. Course Comparison
Side-by-side comparison of any two courses — difficulty, workload, grade distribution, career relevance, and who should take which.
> *"Compare CS5800 and CS6210 — which is harder and what careers do they lead to?"*

### 4. Study Path Generator
Builds a semester-by-semester plan based on your target track or career goal, respecting prerequisite ordering and workload balance.
> *"Build me a semester-by-semester study path for the AI/ML track"*

### 5. Am I Ready Checker
Checks your completed courses against the full prerequisite chain of a target course and tells you exactly what you're missing and why.
> *"I've done CS5001, CS5002, CS5008 and CS5800. Am I ready for CS6140?"*

### 6. What-If Reasoning
Analyzes downstream consequences of skipping or delaying a course — showing every course that becomes blocked.
> *"What if I skip CS5800 and go straight to CS6140?"*

### 7. Advisor Prep Assistant
Generates a personalized list of smart questions to bring to your advising appointment, based on your current course history.
> *"I've completed CS5001, CS5800 and INFO6105. Help me prepare for my advising appointment"*

---

## Follow-Up Question System

Every response includes 3 contextual follow-up buttons generated by the AI using structured output format (`FOLLOWUP_1`, `FOLLOWUP_2`, `FOLLOWUP_3`). These are parsed client-side with regex and rendered as clickable buttons — enabling natural multi-turn advising conversations.

---

## UI Features

- **My Profile sidebar** — checkboxes to select completed courses (loads into context)
- **Quick Actions sidebar** — one-click buttons for each feature
- **Course Catalog sidebar** — scrollable list of all 30 courses with track filters
- **Follow-up buttons** — contextual suggestions after every response
- **Full-screen layout** — clean white minimal theme with Inter/DM Sans fonts

---

## How to Run

### Prerequisites
- Node.js (v18+)
- npm
- Anthropic API key

### Setup

```bash
# Clone the repo
git clone https://github.com/5100-SEA-GEENG/final-project-husky-advisor
cd final-project-husky-advisor

# Install backend dependencies
cd backend
npm install

# Create .env file in backend/
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# Start the backend server
node server.js

# In a new terminal, install and start frontend
cd ../frontend
npm install
npm start
```

The app will open at `http://localhost:3000`

---

## Functional Testing — 15 Test Queries

All 15 queries were manually run and verified against the Northeastern MS CS course catalog.

| # | Query | Feature Tested | Result |
|---|---|---|---|
| 1 | How many credits is CS6140, who teaches it, when is it offered? | Course Info | ✅ Pass |
| 2 | Which courses are offered in Summer semester? | Semester Planning | ✅ Pass |
| 3 | I've completed CS5001 and CS5002. What do I need for CS6140? | Prereq Gap | ✅ Pass |
| 4 | What is the full prerequisite chain to reach CS6120 from scratch? | Deep Prereq Chain | ✅ Pass |
| 5 | Compare CS6140 and CS7150 | Course Comparison | ✅ Pass |
| 6 | Compare CS5800 and CS6210 — which is harder and what careers? | Course Comparison | ✅ Pass |
| 7 | Build me a semester-by-semester study path for the AI/ML track | Study Path | ✅ Pass |
| 8 | I want to work at Google as an ML engineer. What courses in what order? | Career Study Path | ✅ Pass |
| 9 | I've done CS5001, CS5002, CS5008 and CS5800. Am I ready for CS6140? | Am I Ready | ✅ Pass |
| 10 | I have a strong math background but no CS experience. Am I ready for CS5100? | Am I Ready | ✅ Pass |
| 11 | What if I skip CS5800 and go straight to CS6140? | What-If Reasoning | ✅ Pass |
| 12 | What happens if I take CS6140 and CS7150 in the same semester? | What-If / Workload | ✅ Pass |
| 13 | I've completed CS5001, CS5800 and INFO6105. Help me prepare for my advising appointment | Advisor Prep | ✅ Pass |
| 14 | I want to graduate in 2 semesters focusing on systems. What should I ask my advisor? | Advisor Prep | ✅ Pass |
| 15 | I've completed CS5001, CS5002, CS5008, CS5800 and INFO6105. How many courses do I have left to graduate? | Graduation Planning | ✅ Pass |

---

## Evaluation: HuskyAdvisor vs Manual Advising

To evaluate HuskyAdvisor's real-world value, the same 7 advising tasks were timed manually (using the Northeastern course catalog website) and compared against HuskyAdvisor response times.

| Task | Manual Time | HuskyAdvisor | Time Saved | Accuracy |
|---|---|---|---|---|
| Course Info Lookup | ~3 min | ~10 sec | 97% faster | ✅ Correct |
| Prerequisite Check | ~8 min | ~15 sec | 97% faster | ✅ Correct |
| Course Comparison | ~10 min | ~20 sec | 97% faster | ✅ Correct |
| Study Path Planning | ~25 min | ~30 sec | 98% faster | ✅ Correct |
| Am I Ready Check | ~10 min | ~15 sec | 97% faster | ✅ Correct |
| What-If Reasoning | ~15 min | ~20 sec | 98% faster | ✅ Correct |
| Advisor Prep | ~20 min | ~25 sec | 98% faster | ✅ Correct |

**Why manual is slow:**
- Prerequisite checking requires opening multiple catalog pages and tracing chains by hand
- Course comparison means switching between two browser tabs and manually noting differences
- Study path planning requires mapping prereqs on paper across multiple semesters
- What-if reasoning means tracing every downstream dependency manually — easily missed

**Why HuskyAdvisor is faster and better:**
- All 30 courses loaded in context — no page switching
- Multi-step reasoning happens instantly
- Personalized to your specific completed courses
- Never misses a downstream dependency
- Available 24/7, no appointment needed

---

## Limitations

- Knowledge base is limited to 30 courses — does not cover the full Northeastern catalog
- No memory between sessions — each conversation starts fresh
- Course data may become outdated if Northeastern changes offerings
- Cannot access real-time enrollment or seat availability
- Should not replace official academic advising for graduation audits

---

## Ethical Considerations

- **Accuracy:** HuskyAdvisor always reminds users to verify with their official advisor — it is a planning tool, not an official academic record system
- **Bias:** The knowledge base was manually curated and may reflect gaps or errors in course data
- **Over-reliance:** Students should use HuskyAdvisor as a starting point, not a final authority on graduation requirements
- **Data Privacy:** No student data is stored — conversations are stateless

---

## Project Structure

```
final-project-husky-advisor/
├── backend/
│   ├── server.js          # Express server + Claude API calls
│   ├── package.json
│   └── .env               # ANTHROPIC_API_KEY (not committed)
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   └── App.css        # Styling
│   └── package.json
├── knowledge_base.json    # 30 MS CS courses
└── README.md
```

---

## Future Work

- **Persistent Memory** — Add a database to remember a student's completed courses and conversation history across sessions, enabling truly personalized long-term advising without re-entering course history each visit
- **Suggested Questions Panel** — Add pre-set example query buttons below the follow-up suggestions so new students can explore all 7 features without typing
- **Full Catalog Coverage** — Expand the knowledge base beyond 30 courses to cover the complete Northeastern MS CS catalog
- **Real-Time Data** — Connect to Northeastern's live enrollment system to show seat availability and current semester offerings
- **RAG Architecture** — If the knowledge base grows beyond context window limits, migrate to a RAG system with vector database retrieval

---

## Acknowledgements

- Built using the [Anthropic Claude API](https://www.anthropic.com)
- Course data sourced from the [Northeastern University Graduate CS Catalog](https://catalog.northeastern.edu)
- Project developed for CS5100 Foundations of AI, Northeastern University Seattle, Summer 2026