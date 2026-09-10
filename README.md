# ⚡ Interview Trainer Agent (Powered by RAG & IBM Watsonx.ai)

**Problem Statement No. 22 – Interview Trainer Agent**  
An enterprise-grade, AI-driven Interview Preparation and Simulation Agent powered by Retrieval-Augmented Generation (RAG) and IBM Watsonx.ai foundation models (`meta-llama/llama-3-3-70b-instruct`).

---

## 🌟 Key Features

1. **RAG-Powered Domain Question Retrieval**:
   - FAISS vector database indexed with role-specific questions, system design architectures, STAR behavioral scenarios, and HR recruiter standards.
2. **Dynamic Profile & Resume Parsing**:
   - Ingests resumes in PDF, DOCX, or TXT formats, extracts core technical skills, and contextualizes interview questions to candidate experience level.
3. **Structured Bar-Raiser Question Packages**:
   - **Technical Deep Dives**: Multi-tier difficulty questions with interviewer focus, key points to cover, and exemplary model answers.
   - **Behavioral STAR Masterclass**: Situation, Task, Action, and Result structured breakdowns for Amazon Leadership Principles & Top Tech culture fit.
   - **7-Day Personalized Roadmap**: Step-by-step preparation plan targeting specific candidate competencies.
   - **HR Strategy & Salary Negotiation**: Practical negotiation scripts and reverse questions for recruiters.
4. **Interactive Mock Interview Simulator**:
   - Real-time question progression, live candidate response input, and automated AI grading on technical accuracy, structure, metrics, and hiring grade.
5. **Modern Glassmorphic Web UI**:
   - Responsive dark-mode interface built with HTML5, CSS3, and modern JavaScript.

---

## 🚀 Getting Started

### 1. Environment Variables (`.env`)
Make sure your `.env` contains your IBM Watsonx credentials:
```env
IBM_CLOUD_API_KEY=your_api_key_here
PROJECT_ID=your_project_id_here
IBM_CLOUD_URL=https://us-south.ml.cloud.ibm.com
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Local Server
```bash
python main.py
```
Or with Uvicorn directly:
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Open in Browser
Visit **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
