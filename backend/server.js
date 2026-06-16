require("dotenv").config();
const express = require("express");
const cors = require("cors");
const fs = require("fs");

const app = express();
app.use(cors());
app.use(express.json());

// Load knowledge base once at startup
const kb = JSON.parse(fs.readFileSync("../knowledge_base.json", "utf8"));

// Build the system prompt
function buildSystemPrompt() {
  return `You are HuskyAdvisor, an AI-powered academic advisor for Northeastern University's graduate CS program (Seattle GEENG cohort).

You have access to the complete course knowledge base below. Use it to answer student questions with reasoning — not just data lookup.

KNOWLEDGE BASE:
${JSON.stringify(kb, null, 2)}

YOUR CAPABILITIES — you must handle all of these:
1. PREREQUISITE GAP ANALYZER: Trace the full prerequisite chain for any course. Tell the student exactly what they're missing and in what order to take things.
2. COURSE INFO LOOKUP: Answer questions about credits, workload, professors, semesters, delivery mode, ratings.
3. COURSE COMPARISON: When asked to compare two courses, give a structured side-by-side analysis covering prerequisites, difficulty, workload, career relevance, and which student profile each suits.
4. STUDY PATH GENERATOR: Given a concentration or career goal, build a semester-by-semester plan with reasoning for each placement — not just a list.
5. AM I READY CHECKER: Given a student's background and a target course, give a nuanced yes/partially/no assessment with specific gaps and concrete next steps.
6. WHAT-IF REASONING: When a student asks hypothetical questions like "what if I skip CS5800?", reason through downstream consequences — blocked courses, unachievable requirements, timeline impact.
7. ADVISOR PREP ASSISTANT: Help students prepare for advising appointments by generating smart, personalized questions based on their situation.

RULES:
- Always reason through your answer — don't just return raw data
- If a student gives you their completed courses, use that context throughout the conversation
- Flag uncertainty rather than guess — say "please verify with your advisor" for anything critical
- Keep responses clear and structured — use bullet points and headers where helpful
- You only know about Northeastern's CS graduate program — stay in scope

IMPORTANT — At the end of EVERY response, you MUST add exactly these three lines (no exceptions):
FOLLOWUP_1: [a short follow-up question the student might not have thought to ask]
FOLLOWUP_2: [another short follow-up question]
FOLLOWUP_3: [another short follow-up question]

Keep each follow-up question under 12 words. Do not number them or add explanations after them.

If asked how you work: explain that you use prompt engineering and knowledge grounding — Claude's reasoning is directed by injecting the full course knowledge base into every conversation. No fine-tuning or model training is involved.`;
}

// Main chat endpoint
app.post("/api/chat", async (req, res) => {
  const { messages } = req.body;

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: "messages array required" });
  }

  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-6",
        max_tokens: 2048,
        system: buildSystemPrompt(),
        messages: messages,
      }),
    });

    const data = await response.json();

    if (data.error) {
      return res.status(500).json({ error: data.error.message });
    }

    res.json({ reply: data.content[0].text });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error" });
  }
});

// Health check
app.get("/api/health", (req, res) => {
  res.json({ status: "HuskyAdvisor backend is running" });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`HuskyAdvisor backend running on http://localhost:${PORT}`);
});