"""Interview Knowledge Base containing role-specific questions, behavioral STAR questions,
industry expectations, system design topics, and HR evaluation rubrics."""

INTERVIEW_KNOWLEDGE = [
    # Full Stack & Frontend Developer
    {
        "role": "Full Stack Developer",
        "category": "Technical - Frontend",
        "experience_level": "Mid-Senior",
        "topic": "React / Modern Frontend Architecture & Performance",
        "content": """Topic: Frontend Performance & State Architecture
Key Questions:
1. How does the React Fiber reconciliation algorithm work, and how does Concurrent Mode improve responsiveness?
2. Compare Redux Toolkit, Zustand, and React Context API for enterprise-scale state management. When would Context cause unnecessary re-renders?
3. How do you optimize Core Web Vitals (LCP, FID/INP, CLS) in a Next.js / React application?
4. Explain Micro-frontends architecture: Module Federation vs iframe-based isolation.
Model Answer Outline:
- Explain Virtual DOM diffing (heuristics, O(n) complexity, keys, Fiber tree dual-buffering).
- Discuss memoization (useMemo, useCallback, React.memo), code splitting (lazy/Suspense), image optimization (AVIF/WebP), and server-side rendering (SSR/SSG).
Industry Expectations:
- Clear understanding of browser rendering pipeline (parse, layout, paint, composite).
- Clean code principles, TypeScript safety, accessibility (WCAG 2.1 AA), and robust automated testing (Jest, React Testing Library, Playwright)."""
    },
    {
        "role": "Full Stack Developer",
        "category": "Technical - Backend",
        "experience_level": "Mid-Senior",
        "topic": "Node.js / Python REST & Microservices Architecture",
        "content": """Topic: Scalable Backend Services & API Design
Key Questions:
1. How does the Node.js Event Loop (Libuv) handle asynchronous non-blocking I/O across phases (timers, I/O polling, check/setImmediate)?
2. How do you design idempotent RESTful APIs and handle distributed transactions (Saga pattern vs 2PC)?
3. How do you implement Redis caching strategies (Cache-Aside, Write-Through, Write-Behind) and mitigate cache stampedes?
4. Compare SQL (PostgreSQL indexing, B-Trees, transaction isolation levels) vs NoSQL (MongoDB, DynamoDB sharding).
Model Answer Outline:
- Detail Event Loop phases, worker threads for CPU-bound tasks.
- For idempotency: Idempotency-Keys in headers, database unique constraints, atomic operations.
Industry Expectations:
- Thorough knowledge of API security (JWT expiration, OAuth2.0, CSRF, CORS, Rate Limiting).
- Observability and instrumentation (OpenTelemetry, Prometheus, structured logging)."""
    },

    # AI / Machine Learning / Data Science
    {
        "role": "AI / ML Engineer",
        "category": "Technical - GenAI & Deep Learning",
        "experience_level": "Mid-Senior",
        "topic": "Retrieval-Augmented Generation (RAG) & Large Language Models",
        "content": """Topic: RAG Systems, Vector Databases, and LLM Finetuning
Key Questions:
1. Explain the architectural differences between dense retrieval (e.g. BGE, OpenAI, SentenceTransformers) and sparse retrieval (BM25). How does hybrid search combine them with Reciprocal Rank Fusion (RRF)?
2. How do you handle chunking strategies (semantic chunking, parent-document retrieval, recursive character splitting) and handle hallucination in production RAG?
3. Explain Transformer self-attention mechanism: Why do we divide by sqrt(d_k) in Scaled Dot-Product Attention?
4. What is LoRA (Low-Rank Adaptation) and QLoRA, and how do they reduce memory footprint during fine-tuning?
Model Answer Outline:
- Scaled attention formula: Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V. Normalization prevents gradient vanishing in softmax for large dimensions.
- RAG evaluation frameworks: Ragas (faithfulness, answer relevancy, context precision/recall), TruLens.
Industry Expectations:
- Ability to deploy LLMs with vLLM/TGI, quantify latency (TTFT, tokens/sec), and implement guardrails/moderation."""
    },
    {
        "role": "Data Scientist",
        "category": "Technical - Statistics & Modeling",
        "experience_level": "Mid-Senior",
        "topic": "Predictive Modeling, Feature Engineering, and A/B Testing",
        "content": """Topic: Machine Learning Lifecycle & Experimentation
Key Questions:
1. How do you diagnose and fix data leakage in high-dimensional tabular datasets?
2. Explain the Bias-Variance tradeoff and how regularization (L1 Lasso vs L2 Ridge) impacts feature selection.
3. How do you design a statistically rigorous A/B test with sample size calculation, p-value correction (Bonferroni), and minimum detectable effect (MDE)?
4. How do you evaluate imbalanced classification models (ROC-AUC vs PR-AUC, F1-Macro)?
Model Answer Outline:
- Use PR-AUC when true negatives vastly outnumber positives (e.g., fraud detection).
- Explain cross-validation with stratification and out-of-time validation splits."""
    },

    # Cloud & DevOps / SRE
    {
        "role": "DevOps / Cloud Engineer",
        "category": "Technical - Infrastructure & CI/CD",
        "experience_level": "Mid-Senior",
        "topic": "Kubernetes, Terraform, and Cloud Reliability",
        "content": """Topic: Cloud Infrastructure, Orchestration, and Zero-Downtime Deployments
Key Questions:
1. Explain Kubernetes Pod lifecycle, readiness vs liveness probes, and Horizontal Pod Autoscaling (HPA) metrics.
2. How do you implement Canary and Blue-Green deployment strategies using ArgoCD or Istio Service Mesh?
3. How does Terraform manage state locking with AWS S3 + DynamoDB or HashiCorp Cloud, and how do you handle state drift?
4. How do you architect a multi-region disaster recovery (RTO/RPO) with active-passive vs active-active database replication?
Model Answer Outline:
- Liveness restart pod on deadlock; Readiness stops routing ingress traffic during warm-up.
- Terraform state: stores mapped real-world resource IDs, state locking prevents concurrent apply collisions."""
    },

    # System Design & Architecture
    {
        "role": "Software Architect / Senior Engineer",
        "category": "System Design",
        "experience_level": "Senior / Lead",
        "topic": "High-Scale Distributed Systems",
        "content": """Topic: Distributed Systems Architecture (e.g., URL Shortener, Uber/Ride Sharing, Real-Time Messaging)
Key Questions:
1. Design a globally distributed URL shortening service (like Bit.ly) handling 100M new URLs/day and 10B reads/month.
2. How do you handle concurrency, distributed locking (Redlock), and database partitioning (Consistent Hashing)?
3. Compare message brokers: Apache Kafka (log-based, partition ordering, consumer groups) vs RabbitMQ (AMQP, queue-based, exchange routing).
4. Explain CAP Theorem and PACELC: How does Cassandra achieve high write availability with tunable consistency?
Model Answer Outline:
- Step 1: Requirements (Functional & Non-functional).
- Step 2: Back-of-the-envelope estimation (QPS: ~4000 read QPS, Storage: 100M * 500B * 365 * 5yr ~ 90TB).
- Step 3: High-level design (API Gateway, Rate Limiter, Load Balancers, Web Servers, Distributed ID Generator - Snowflake, Base62 encoding, Redis Cache, Database cluster).
- Step 4: Deep dive into bottlenecks, replication lag, CDN caching."""
    },

    # Behavioral & Leadership (STAR Method)
    {
        "role": "All Roles",
        "category": "Behavioral - Leadership & Culture",
        "experience_level": "All Levels",
        "topic": "STAR Method Behavioral Scenarios & Conflict Resolution",
        "content": """Topic: Behavioral Interview Questions (Amazon Leadership Principles, Google Googlyness, Top Tech Standards)
Key Questions:
1. "Tell me about a time you had a technical disagreement with a senior engineer or product manager. How did you resolve it?" (Disagree and Commit / Ownership)
2. "Describe a project that failed or missed a critical deadline. What went wrong, what was your accountability, and what did you learn?" (Customer Obsession / Resilience)
3. "Give an example of how you mentored a junior engineer or improved your team's engineering velocity." (Earn Trust / Bias for Action)
4. "Tell me about a high-pressure production outage you resolved under tight SLA constraints." (Deliver Results / Dive Deep)
STAR Response Structure Formula:
- **Situation**: Context, company, scope, and specific business constraint (15% of time).
- **Task**: The exact goal or challenge you were personally responsible for solving (15% of time).
- **Action**: Concrete technical/leadership actions YOU took (tools chosen, discussions led, architectural decisions) (50% of time).
- **Result**: Quantifiable business impact (e.g., reduced latency by 45%, saved $20k/mo cloud spend, zero downtime) and retro reflection (20% of time)."""
    },

    # HR & Recruiter Guidelines
    {
        "role": "All Roles",
        "category": "HR Guidelines & Salary Negotiation",
        "experience_level": "All Levels",
        "topic": "HR Screening, Cultural Fit, and Compensation Strategy",
        "content": """Topic: HR Round Guidelines & Recruiter Etiquette
Key Questions & Strategies:
1. "Why are you looking to leave your current company and why our company?"
   - Rule: Never speak negatively about past employers. Frame in terms of career growth, desire for higher scale, alignment with company mission and technology stack.
2. "What are your salary expectations?"
   - Strategy: Research Level.fyi / Glassdoor bands. Anchor politely: "Based on the market rate for Senior Engineers in this domain and the responsibilities of this role, I am targeting in the range of X to Y, though total compensation and growth opportunities are my primary priority."
3. "Do you have any questions for us?" (Critical to ask 2-3 thoughtful questions):
   - "How does the engineering team measure success for this role in the first 90 days?"
   - "What is the biggest technical hurdle the team is currently tackling this quarter?"
   - "How does the team balance technical debt refactoring with product feature velocity?"""
    }
]
