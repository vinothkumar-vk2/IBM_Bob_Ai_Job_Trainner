// Frontend Logic for AI Interview Trainer Agent

let currentPlan = null;
let currentQuestionIndex = 0;
let allQuestionsPool = [];

document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupResumeUpload();
  setupForm();
  setupSimulator();
  
  // Pre-load default state
  document.getElementById('profileForm').dispatchEvent(new Event('submit'));
});

// Setup Navigation Tabs
function setupTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabPanes.forEach(pane => pane.classList.remove('active'));

      button.classList.add('active');
      const targetId = button.getAttribute('data-tab');
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add('active');
    });
  });
}

// Resume Upload Handler
function setupResumeUpload() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('resumeFileInput');
  const filenameLabel = document.getElementById('uploadFilename');
  const skillsContainer = document.getElementById('skillsContainer');

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = 'var(--accent-cyan)';
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.style.borderColor = 'rgba(255, 255, 255, 0.15)';
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = 'rgba(255, 255, 255, 0.15)';
    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFileUpload(fileInput.files[0]);
    }
  });

  async function handleFileUpload(file) {
    filenameLabel.textContent = `Uploading: ${file.name}...`;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload-resume', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.status === 'success') {
        filenameLabel.textContent = `✅ Attached: ${file.name}`;
        skillsContainer.innerHTML = '';
        skillsContainer.classList.remove('hidden');

        if (data.skills_summary && data.skills_summary.length > 0) {
          data.skills_summary.forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'tag-badge';
            tag.textContent = skill;
            skillsContainer.appendChild(tag);
          });
        }
      } else {
        filenameLabel.textContent = `⚠️ Error: ${data.message || 'Upload failed'}`;
      }
    } catch (err) {
      filenameLabel.textContent = '⚠️ Upload failed';
    }
  }
}

// Plan Generation Form Submit
function setupForm() {
  const form = document.getElementById('profileForm');
  const btnText = document.getElementById('btnText');
  const btnSpinner = document.getElementById('btnSpinner');
  const submitBtn = document.getElementById('generatePlanBtn');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const profileName = document.getElementById('profileName').value;
    const jobRole = document.getElementById('jobRole').value;
    const expLevel = document.getElementById('expLevel').value;
    const targetCompany = document.getElementById('targetCompany').value;

    btnText.textContent = 'Generating with Watsonx & RAG...';
    btnSpinner.classList.remove('hidden');
    submitBtn.disabled = true;

    try {
      const res = await fetch('/api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile_name: profileName,
          job_role: jobRole,
          experience_level: expLevel,
          target_company: targetCompany
        })
      });

      const responseData = await res.json();
      if (responseData.status === 'success' && responseData.data) {
        currentPlan = responseData.data;
        renderInterviewPlan(currentPlan);
      }
    } catch (err) {
      console.error('Plan generation failed', err);
    } finally {
      btnText.textContent = '✨ Generate Prep Package';
      btnSpinner.classList.add('hidden');
      submitBtn.disabled = false;
    }
  });
}

// Render Received Interview Package
function renderInterviewPlan(plan) {
  // Update Hero Banner
  const overview = plan.candidate_overview || {};
  document.getElementById('bannerTitle').textContent = `Targeted Prep Plan for ${overview.profile_name || 'Candidate'}`;
  document.getElementById('bannerRole').textContent = `Role: ${overview.job_role || 'Software Engineer'} (${overview.experience_level || 'Mid'})`;

  // Render Technical Questions
  const techList = document.getElementById('techQuestionsList');
  techList.innerHTML = '';
  const techQuestions = plan.technical_questions || [];

  techQuestions.forEach((q, idx) => {
    const card = document.createElement('div');
    card.className = 'glass-panel question-card';
    card.innerHTML = `
      <div class="question-header">
        <span class="question-badge badge-tech">${q.category || 'Technical'}</span>
        <span class="question-badge badge-hard">${q.difficulty || 'Medium'}</span>
      </div>
      <h3 class="question-title">${q.question}</h3>
      <div class="question-why">🎯 <strong>Interviewer Focus:</strong> ${q.why_asked || 'Assesses core domain expertise'}</div>
      <ul class="key-points-list">
        ${(q.key_points_to_cover || []).map(p => `<li>${p}</li>`).join('')}
      </ul>
      <div class="model-answer-box">
        <div class="model-answer-header" onclick="this.nextElementSibling.classList.toggle('hidden')">💡 View Bar-Raiser Model Answer</div>
        <div class="model-answer-body hidden">${q.model_answer || 'Detailed structured answer.'}</div>
      </div>
    `;
    techList.appendChild(card);
  });

  // Render Behavioral STAR Questions
  const behList = document.getElementById('behavioralQuestionsList');
  behList.innerHTML = '';
  const behQuestions = plan.behavioral_questions || [];

  behQuestions.forEach((bq, idx) => {
    const card = document.createElement('div');
    card.className = 'glass-panel question-card';
    const star = bq.star_model_answer || {};
    card.innerHTML = `
      <div class="question-header">
        <span class="question-badge badge-star">${bq.category || 'Behavioral STAR'}</span>
      </div>
      <h3 class="question-title">${bq.question}</h3>
      <div class="question-why">🎯 <strong>Criteria:</strong> ${bq.evaluation_criteria || 'Leadership & STAR methodology'}</div>
      <div class="model-answer-box" style="margin-top: 10px;">
        <div class="model-answer-header" onclick="this.nextElementSibling.classList.toggle('hidden')">⭐ Detailed STAR Framework Response</div>
        <div class="model-answer-body hidden" style="font-size: 0.88rem;">
          <p><strong>Situation:</strong> ${star.situation || 'N/A'}</p>
          <p style="margin-top: 4px;"><strong>Task:</strong> ${star.task || 'N/A'}</p>
          <p style="margin-top: 4px;"><strong>Action:</strong> ${star.action || 'N/A'}</p>
          <p style="margin-top: 4px; color: var(--accent-emerald);"><strong>Result:</strong> ${star.result || 'N/A'}</p>
        </div>
      </div>
    `;
    behList.appendChild(card);
  });

  // Render Strategy Timeline
  const timelineList = document.getElementById('timelineList');
  timelineList.innerHTML = '';
  const roadmap = plan.strategy_roadmap || [];

  roadmap.forEach(item => {
    const tItem = document.createElement('div');
    tItem.className = 'glass-panel timeline-item';
    tItem.innerHTML = `
      <div class="timeline-dot"></div>
      <div class="timeline-phase">${item.phase}</div>
      <div class="timeline-focus">${item.focus}</div>
      <ul class="key-points-list">
        ${(item.action_items || []).map(act => `<li>${act}</li>`).join('')}
      </ul>
    `;
    timelineList.appendChild(tItem);
  });

  // Render HR Guidelines
  const hrList = document.getElementById('hrGuidelinesList');
  hrList.innerHTML = '';
  const hrItems = plan.hr_guidelines || [];

  hrItems.forEach(hr => {
    const card = document.createElement('div');
    card.className = 'glass-panel question-card';
    card.innerHTML = `
      <h3 class="question-title" style="color: var(--accent-amber); font-size: 1.05rem;">💼 ${hr.topic}</h3>
      <p class="model-answer-body" style="margin-top: 6px;">${hr.advice}</p>
    `;
    hrList.appendChild(card);
  });

  // Aggregate pool for Mock Simulator
  allQuestionsPool = [
    ...techQuestions.map(t => ({ question: t.question, category: 'Technical', model: t.model_answer })),
    ...behQuestions.map(b => ({ question: b.question, category: 'Behavioral', model: b.star_model_answer ? b.star_model_answer.action : '' }))
  ];
  currentQuestionIndex = 0;
  loadSimulatorQuestion();
}

// Setup Interactive Mock Simulator
function setupSimulator() {
  const nextBtn = document.getElementById('nextSimQuestionBtn');
  const evalForm = document.getElementById('evaluationForm');
  const evalResultCard = document.getElementById('evaluationResultCard');
  const evalBtnText = document.getElementById('evalBtnText');
  const evalBtnSpinner = document.getElementById('evalBtnSpinner');

  nextBtn.addEventListener('click', () => {
    if (allQuestionsPool.length > 0) {
      currentQuestionIndex = (currentQuestionIndex + 1) % allQuestionsPool.length;
      loadSimulatorQuestion();
      document.getElementById('simUserAnswer').value = '';
      evalResultCard.classList.add('hidden');
    }
  });

  evalForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userAnswer = document.getElementById('simUserAnswer').value.trim();
    if (!userAnswer) {
      alert('Please enter your response before submitting for evaluation.');
      return;
    }

    const currentQ = allQuestionsPool[currentQuestionIndex] || {
      question: document.getElementById('simQuestionText').textContent,
      category: 'Technical'
    };

    evalBtnText.textContent = 'Evaluating with AI...';
    evalBtnSpinner.classList.remove('hidden');

    try {
      const res = await fetch('/api/evaluate-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: currentQ.question,
          user_answer: userAnswer,
          question_category: currentQ.category,
          role: document.getElementById('jobRole').value
        })
      });

      const responseData = await res.json();
      if (responseData.status === 'success' && responseData.data) {
        displayEvaluationResult(responseData.data);
      }
    } catch (err) {
      console.error('Evaluation failed', err);
    } finally {
      evalBtnText.textContent = '📊 Submit Answer for AI Evaluation';
      evalBtnSpinner.classList.add('hidden');
    }
  });
}

function loadSimulatorQuestion() {
  if (allQuestionsPool.length === 0) return;
  const q = allQuestionsPool[currentQuestionIndex];
  document.getElementById('simCategory').textContent = q.category;
  document.getElementById('simQuestionText').textContent = q.question;
}

function displayEvaluationResult(feedback) {
  const card = document.getElementById('evaluationResultCard');
  card.classList.remove('hidden');

  document.getElementById('evalScoreValue').textContent = feedback.score || 85;
  document.getElementById('evalGradeText').textContent = feedback.grade || 'Hire';
  
  const strengthsList = document.getElementById('evalStrengthsList');
  strengthsList.innerHTML = '';
  (feedback.strengths || []).forEach(s => {
    const li = document.createElement('li');
    li.textContent = s;
    strengthsList.appendChild(li);
  });

  const weakList = document.getElementById('evalWeaknessesList');
  weakList.innerHTML = '';
  (feedback.weaknesses || []).forEach(w => {
    const li = document.createElement('li');
    li.textContent = w;
    weakList.appendChild(li);
  });

  document.getElementById('evalModelAnswer').textContent = feedback.model_answer || 'Practice articulating the technical trade-offs clearly.';

  card.scrollIntoView({ behavior: 'smooth' });
}
