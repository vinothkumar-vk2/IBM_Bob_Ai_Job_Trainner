import os
import json
import re
from typing import Dict, Any, List, Optional
from file.get_file import File
from Rag_system.reg_system import RagSystem
from Rag_system.vec_db import VectorDB
from Ai.ai_config import generate_text_watsonx

class InterviewTrainerService:
    """Core RAG & AI Orchestrator for Problem Statement No.22 - Interview Trainer Agent."""

    def __init__(self):
        self.rag_system = RagSystem()
        self.vector_db = VectorDB(self.rag_system)
        self.file_handler = File()

    def ingest_resume(self, file_path: str) -> Dict[str, Any]:
        """Extracts text from an uploaded resume and indexes it into VectorDB."""
        resume_text = self.file_handler.read_file(file_path)
        self.vector_db.create_index(resume_text, source_label="candidate_resume")
        
        # Analyze profile summary
        skills_summary = self._extract_profile_highlights(resume_text)
        return {
            "characters_parsed": len(resume_text),
            "preview": resume_text[:300] + "..." if len(resume_text) > 300 else resume_text,
            "skills_summary": skills_summary
        }

    def _extract_profile_highlights(self, text: str) -> List[str]:
        """Heuristic and regex extraction of tech skills and keywords."""
        keywords = [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI", "Flask",
            "Docker", "Kubernetes", "AWS", "GCP", "Azure", "SQL", "PostgreSQL", "MongoDB",
            "Redis", "Kafka", "Machine Learning", "Deep Learning", "LLM", "RAG", "PyTorch",
            "TensorFlow", "CI/CD", "Git", "System Design", "Microservices", "Java", "C++"
        ]
        found = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE)]
        return found[:12]

    def generate_interview_plan(self, profile_name: str, experience_level: str, job_role: str, target_company: str = "Top Tier Tech", custom_notes: str = "") -> Dict[str, Any]:
        """Uses RAG to retrieve role standards and prompts Watsonx / AI to generate tailored questions, model answers, and preparation roadmap."""
        search_query = f"{job_role} {experience_level} technical questions behavioral STAR system design expectations"
        retrieved_docs = self.vector_db.search(search_query, top_k=4)
        
        context_str = "\n\n---\n\n".join([d["text"] for d in retrieved_docs])
        
        prompt = f"""You are an elite Senior Staff Interviewer and Career Coach. 
Generate a comprehensive, rigorous interview preparation package for the following candidate profile.

CANDIDATE PROFILE:
- Name: {profile_name}
- Target Job Role: {job_role}
- Experience Level: {experience_level}
- Target Company / Industry Tier: {target_company}
- Custom Focus / Notes: {custom_notes if custom_notes else 'None'}

RETRIEVED DOMAIN KNOWLEDGE & INTERVIEW STANDARDS:
{context_str}

OUTPUT INSTRUCTIONS:
Return a valid JSON object strictly matching this schema with high quality, in-depth technical accuracy:
{{
  "candidate_overview": {{
    "profile_name": "{profile_name}",
    "job_role": "{job_role}",
    "experience_level": "{experience_level}",
    "competency_focus": ["area1", "area2", "area3", "area4"]
  }},
  "strategy_roadmap": [
    {{"phase": "Day 1-2: Core Concepts", "focus": "Deep dive into fundamentals and architecture.", "action_items": ["item1", "item2"]}},
    {{"phase": "Day 3-4: System Design & Deep Dives", "focus": "Distributed patterns and scalability tradeoffs.", "action_items": ["item1", "item2"]}},
    {{"phase": "Day 5-6: Behavioral STAR Mastery", "focus": "Craft high-impact leadership stories.", "action_items": ["item1", "item2"]}},
    {{"phase": "Day 7: Mock Simulations", "focus": "Simulate live pressure and time constraints.", "action_items": ["item1", "item2"]}}
  ],
  "technical_questions": [
    {{
      "id": "tech_1",
      "category": "Core Architecture / Technical",
      "difficulty": "Medium-Hard",
      "question": "Detailed technical question targeting {job_role}?",
      "why_asked": "Explains interviewer intent and evaluation metric",
      "key_points_to_cover": ["Point A", "Point B", "Point C"],
      "model_answer": "Complete, articulate answer showcasing deep technical knowledge."
    }},
    {{
      "id": "tech_2",
      "category": "Scalability / System Design / Framework",
      "difficulty": "Hard",
      "question": "Advanced question on edge cases, scaling or data flow?",
      "why_asked": "Interviewer rationale",
      "key_points_to_cover": ["Point A", "Point B", "Point C"],
      "model_answer": "In-depth model response."
    }},
    {{
      "id": "tech_3",
      "category": "Practical Debugging / Best Practices",
      "difficulty": "Medium",
      "question": "Scenario on resolving production bottlenecks or concurrency?",
      "why_asked": "Interviewer rationale",
      "key_points_to_cover": ["Point A", "Point B"],
      "model_answer": "Structured model response."
    }}
  ],
  "behavioral_questions": [
    {{
      "id": "beh_1",
      "category": "Behavioral (STAR Method)",
      "question": "Tell me about a time when you faced conflicting project priorities or technical disagreement.",
      "evaluation_criteria": "Assesses communication, ownership, and emotional intelligence.",
      "star_model_answer": {{
        "situation": "Context and business constraints...",
        "task": "Specific responsibility you owned...",
        "action": "Concrete actions you drove...",
        "result": "Quantified business metrics and outcomes achieved..."
      }}
    }},
    {{
      "id": "beh_2",
      "category": "Failure & Resilience",
      "question": "Describe a major production bug or missed deadline. How did you manage it?",
      "evaluation_criteria": "Accountability, blameless post-mortem culture, and long-term fix.",
      "star_model_answer": {{
        "situation": "High-stakes incident scenario...",
        "task": "Restoring service and mitigating risk...",
        "action": "Immediate rollback, RCA, and guardrails implemented...",
        "result": "99.99% uptime restored, regression test suite created..."
      }}
    }}
  ],
  "hr_guidelines": [
    {{"topic": "Salary Negotiation", "advice": "Anchor compensation against market standards with clear total comp breakdown."}},
    {{"topic": "Reverse Questions", "advice": "Ask high-impact questions about team roadmap, tech debt, and 90-day success metrics."}},
    {{"topic": "Closing Strong", "advice": "Reiterate excitement, summarize key value-add, and ask for next steps timeline."}}
  ]
}}
IMPORTANT: Return ONLY valid JSON, without markdown backticks or commentary."""

        ai_response = generate_text_watsonx(prompt, max_tokens=2200)
        parsed_result = self._parse_json_safely(ai_response)

        if not parsed_result or "technical_questions" not in parsed_result:
            # Fallback structured response generated with domain knowledge
            parsed_result = self._generate_local_interview_plan(profile_name, experience_level, job_role, target_company)

        return parsed_result

    def evaluate_mock_answer(self, question: str, user_answer: str, question_category: str = "Technical", role: str = "Software Engineer") -> Dict[str, Any]:
        """Evaluates candidate's typed/spoken answer using RAG criteria and provides scoring & feedback."""
        if not user_answer.strip():
            return {
                "score": 0,
                "grade": "Incomplete",
                "feedback": "No answer provided. Please provide your response to receive detailed evaluation.",
                "strengths": [],
                "weaknesses": ["Empty submission"],
                "model_answer": "Provide a structured response covering key technical aspects.",
                "actionable_tips": ["Structure your answer with a high-level summary followed by technical specifics."]
            }

        retrieved_context = self.vector_db.search(f"{question} {role}", top_k=2)
        ctx_snippet = "\n".join([c["text"] for c in retrieved_context])

        prompt = f"""You are a Principal Bar Raiser interviewer at a premier technology company.
Evaluate the candidate's answer for the following question.

ROLE: {role}
CATEGORY: {question_category}
QUESTION: {question}

CANDIDATE'S ANSWER:
"{user_answer}"

REFERENCE CONTEXT / STANDARDS:
{ctx_snippet}

SCORING CRITERIA:
- Technical / Conceptual Accuracy & Depth (0-40)
- Structure & Communication Clarity (0-30)
- Problem Solving, Metrics & Practical Realism (0-30)

OUTPUT INSTRUCTIONS:
Return ONLY a valid JSON object matching this schema:
{{
  "score": 85,
  "grade": "Strong Hire / Hire / Lean Hire / No Hire",
  "criteria_breakdown": {{
    "technical_depth": 35,
    "clarity_and_structure": 26,
    "practical_metrics": 24
  }},
  "strengths": ["Strength point 1", "Strength point 2"],
  "weaknesses": ["Area for improvement 1", "Area for improvement 2"],
  "model_answer": "Exemplary model answer showcasing how a top 1% candidate answers this question.",
  "actionable_tips": [
    "Specific improvement tip 1",
    "Specific improvement tip 2"
  ]
}}
IMPORTANT: Output JSON ONLY, no extra text."""

        ai_response = generate_text_watsonx(prompt, max_tokens=1200)
        parsed = self._parse_json_safely(ai_response)

        if not parsed or "score" not in parsed:
            # Fallback heuristic evaluation
            word_count = len(user_answer.split())
            score = min(92, max(45, 50 + int(word_count * 0.4)))
            grade = "Strong Hire" if score >= 80 else ("Hire" if score >= 70 else "Needs Improvement")
            parsed = {
                "score": score,
                "grade": grade,
                "criteria_breakdown": {
                    "technical_depth": int(score * 0.4),
                    "clarity_and_structure": int(score * 0.3),
                    "practical_metrics": int(score * 0.3)
                },
                "strengths": [
                    "Directly addressed the core theme of the question",
                    "Good use of domain terminology and logical flow"
                ],
                "weaknesses": [
                    "Could incorporate more concrete performance metrics or scale estimates",
                    "Consider discussing edge cases or architectural tradeoffs"
                ],
                "model_answer": f"To answer '{question}' effectively, state the primary concept, detail the underlying mechanism, explain tradeoffs, and conclude with a real-world production example.",
                "actionable_tips": [
                    "Follow the STAR format for behavioral scenarios (Situation, Task, Action, Result).",
                    "Quantify your results (e.g., 'reduced latency by 35%', 'handled 50k RPS')."
                ]
            }

        return parsed

    def _parse_json_safely(self, text: str) -> Optional[Dict[str, Any]]:
        """Cleans AI markdown output and extracts valid JSON object."""
        if not text:
            return None
        try:
            cleaned = text.strip()
            # Strip markdown code blocks
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
                cleaned = re.sub(r"\s*```$", "", cleaned)
            
            # Find first { and last }
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start:end+1]
                return json.loads(cleaned)
        except Exception as e:
            print(f"[InterviewTrainerService] JSON parse error: {e}")
        return None

    def _generate_local_interview_plan(self, profile_name: str, experience_level: str, job_role: str, target_company: str) -> Dict[str, Any]:
        """Fallback rich template plan matching the specified role."""
        return {
            "candidate_overview": {
                "profile_name": profile_name,
                "job_role": job_role,
                "experience_level": experience_level,
                "competency_focus": ["System Design & Scale", "Algorithmic Efficiency", "STAR Leadership", "Cloud Reliability"]
            },
            "strategy_roadmap": [
                {"phase": "Day 1-2: Technical Foundations", "focus": "Review role-specific architecture, memory models, and concurrency.", "action_items": ["Review data structures & algorithmic complexity", "Draft 5 core technical concept summaries"]},
                {"phase": "Day 3-4: Distributed Systems & Scale", "focus": "Deep dive into caching, partitioning, and resilience patterns.", "action_items": ["Design 2 high-scale architectures (URL Shortener, E-commerce Checkout)", "Review CAP theorem & database indexing"]},
                {"phase": "Day 5-6: Behavioral STAR Mastery", "focus": "Formulate high-impact leadership stories highlighting ownership.", "action_items": ["Write down 4 STAR stories (Conflict, Outage, Mentorship, Innovation)", "Rehearse with 2-minute time constraints"]},
                {"phase": "Day 7: Live Mock Simulation", "focus": "Simulate live pressure, timing, and HR salary negotiation.", "action_items": ["Execute full mock interview round", "Review rubrics and refine pitch"]}
            ],
            "technical_questions": [
                {
                    "id": "tech_1",
                    "category": "Core Architecture",
                    "difficulty": "Medium-Hard",
                    "question": f"How do you design and optimize a high-throughput backend service in {job_role} to ensure low latency and zero downtime?",
                    "why_asked": "Assesses end-to-end understanding of concurrency, caching layers, and database query optimization.",
                    "key_points_to_cover": ["Connection pooling & asynchronous I/O", "Redis Cache-Aside pattern & TTL strategy", "Database indexing & connection scaling"],
                    "model_answer": "I approach high-throughput services by decoupling CPU-bound tasks via message queues (Kafka/RabbitMQ), using non-blocking I/O with connection pooling, implementing Redis caching with Cache-Aside strategy, and applying database read-replicas with proper B-Tree indexing."
                },
                {
                    "id": "tech_2",
                    "category": "Scalability & Resilience",
                    "difficulty": "Hard",
                    "question": "How do you handle distributed consistency and failure recovery when integrating third-party microservices?",
                    "why_asked": "Evaluates fault tolerance, idempotency, and distributed system design skills.",
                    "key_points_to_cover": ["Idempotency keys in headers", "Circuit Breaker pattern (Resilience4j / Envoy)", "Dead Letter Queues and exponential backoff retries"],
                    "model_answer": "I enforce idempotency via unique request tokens stored in distributed cache, wrap external RPCs in Circuit Breakers to prevent cascading timeouts, and route failed operations to Dead Letter Queues with exponential backoff and jitter."
                },
                {
                    "id": "tech_3",
                    "category": "System Design / Troubleshooting",
                    "difficulty": "Medium",
                    "question": "Walk me through how you investigate and resolve a sudden 10x spike in p99 API latency during peak production traffic.",
                    "why_asked": "Tests live triage instinct, observability tooling, and root-cause analysis methodology.",
                    "key_points_to_cover": ["Observability (APM traces, Grafana metrics, CPU/memory)", "Database slow query logs & lock contention", "Mitigation before root-cause (rate limiting / autoscaling)"],
                    "model_answer": "First, protect the system by scaling worker replicas or activating graceful degradation/rate limiting. Next, inspect APM distributed traces to isolate whether latency is in DB queries, external API dependencies, or GC thread pauses. Finally, apply targeted fix and conduct blameless post-mortem."
                }
            ],
            "behavioral_questions": [
                {
                    "id": "beh_1",
                    "category": "Conflict & Alignment",
                    "question": "Tell me about a time you strongly disagreed with a technical or product decision. How did you handle it?",
                    "evaluation_criteria": "Tests emotional intelligence, constructive communication, and 'Disagree and Commit' philosophy.",
                    "star_model_answer": {
                        "situation": "Our team was debating whether to build an in-house search engine vs adopting managed Elasticsearch under a tight 6-week timeline.",
                        "task": "I needed to evaluate the feasibility without alienating teammates or jeopardizing delivery.",
                        "action": "I constructed a lightweight 2-day proof-of-concept benchmark measuring latency and maintenance overhead. Presented the data objectively in an architectural review.",
                        "result": "The team unanimously agreed on the managed solution, saving 3 weeks of dev effort and meeting our launch SLA with zero downtime."
                    }
                },
                {
                    "id": "beh_2",
                    "category": "Ownership & Incident Response",
                    "question": "Describe an incident where a system failed under your watch. What was your immediate response and long-term fix?",
                    "evaluation_criteria": "Evaluates ownership, calm under pressure, and systematic blameless post-mortem process.",
                    "star_model_answer": {
                        "situation": "A schema migration caused a database lock spike, dropping checkout success rates by 25%.",
                        "task": "Restore checkout operations immediately and prevent future migration lockups.",
                        "action": "Rolled back the lock migration within 6 minutes, drained stuck queues, and later implemented zero-downtime online schema change tools (gh-ost/pt-online-schema-change).",
                        "result": "Restored 100% service availability in under 10 minutes and incorporated mandatory migration automated checks into our CI pipeline."
                    }
                }
            ],
            "hr_guidelines": [
                {"topic": "Compensation Negotiation", "advice": "Anchor compensation against market percentile data (e.g. Levels.fyi). Express enthusiasm while negotiating total compensation (Base + Equity + Signing Bonus)."},
                {"topic": "Reverse Questions to Ask", "advice": "Ask: 'What are the key engineering metrics your team uses to measure success?' and 'What is the biggest architectural transition planned for this year?'"},
                {"topic": "Executive Presence", "advice": "Communicate in top-down structured bullet points. Quantify impact with metrics, scale numbers, and percentages."}
            ]
        }


trainer_service = InterviewTrainerService()
service = trainer_service # For compatibility
