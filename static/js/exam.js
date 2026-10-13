// Exam & Practice Simulation Engine for PrepMaster (with Time Management & Mistake Vault integration)

let activeExamState = {
  questions: [],
  currentIndex: 0,
  userAnswers: {}, // questionId -> optionKey
  questionTimes: {}, // questionId -> seconds spent
  lastQuestionEnterTime: null,
  flaggedQuestions: new Set(),
  timerInterval: null,
  secondsRemaining: 0,
  totalSeconds: 0,
  universityId: null,
  level: null,
  isMistakeExam: false,
  isFinished: false
};

function trackQuestionTimeLeave() {
  if (!activeExamState.lastQuestionEnterTime) return;
  const currentQ = activeExamState.questions[activeExamState.currentIndex];
  if (!currentQ) return;
  const elapsed = Math.max(1, Math.round((Date.now() - activeExamState.lastQuestionEnterTime) / 1000));
  activeExamState.questionTimes[currentQ.id] = (activeExamState.questionTimes[currentQ.id] || 0) + elapsed;
}

function trackQuestionTimeEnter() {
  activeExamState.lastQuestionEnterTime = Date.now();
}

async function startExamSimulation(universityId = null, level = null, category = null) {
  const uniId = universityId || window.appState.currentUniversity.id;
  const targetLevel = level || window.appState.currentLevel;

  try {
    let url = `/api/questions?university_id=${uniId}`;
    if (targetLevel && targetLevel !== 'all') {
      url += `&level=${targetLevel}`;
    }
    if (category && category !== 'all') {
      url += `&category=${category}`;
    }

    const res = await fetch(url);
    const questions = await res.json();

    if (!questions || questions.length === 0) {
      alert("Bu filtreye uygun soru bulunamadı. Lütfen seviye veya filtre seçimini değiştirin.");
      return;
    }

    launchExamWithQuestions(questions, uniId, targetLevel, false);

  } catch (err) {
    console.error("Exam start error:", err);
    alert("Sınav yüklenirken bir hata oluştu.");
  }
}

async function startMistakeExam() {
  try {
    const res = await fetch('/api/mistakes');
    const mistakes = await res.json();

    if (!mistakes || mistakes.length === 0) {
      alert("Tebrikler! Hata defterinizde çözülmemiş yanlış soru bulunmuyor.");
      return;
    }

    const questions = mistakes.map(m => m.question_details);
    const uniId = window.appState.currentUniversity.id;
    const level = window.appState.currentLevel;

    launchExamWithQuestions(questions, uniId, level, true);

  } catch (err) {
    console.error("Mistake exam error:", err);
    alert("Hata defteri sınavı başlatılamadı.");
  }
}

function launchExamWithQuestions(questions, uniId, targetLevel, isMistake = false) {
  activeExamState.questions = questions;
  activeExamState.currentIndex = 0;
  activeExamState.userAnswers = {};
  activeExamState.questionTimes = {};
  activeExamState.flaggedQuestions = new Set();
  activeExamState.universityId = uniId;
  activeExamState.level = targetLevel;
  activeExamState.isMistakeExam = isMistake;
  activeExamState.isFinished = false;

  // Soru başına 90 sn süre
  activeExamState.totalSeconds = Math.max(questions.length * 90, 180);
  activeExamState.secondsRemaining = activeExamState.totalSeconds;

  showExamInterface();
  startTimer();
  trackQuestionTimeEnter();
  renderCurrentQuestion();
  renderQuestionPalette();
}

function showExamInterface() {
  document.getElementById("main-content-area").classList.add("hidden");
  document.getElementById("exam-simulation-area").classList.remove("hidden");
  document.getElementById("exam-results-modal").classList.add("hidden");
}

function exitExamInterface() {
  trackQuestionTimeLeave();
  if (activeExamState.timerInterval) {
    clearInterval(activeExamState.timerInterval);
  }
  document.getElementById("exam-simulation-area").classList.add("hidden");
  document.getElementById("exam-results-modal").classList.add("hidden");
  document.getElementById("main-content-area").classList.remove("hidden");
  if (window.loadDashboardStats) window.loadDashboardStats();
  if (window.loadMistakeVault) window.loadMistakeVault();
}

function startTimer() {
  if (activeExamState.timerInterval) clearInterval(activeExamState.timerInterval);
  updateTimerDisplay();

  activeExamState.timerInterval = setInterval(() => {
    activeExamState.secondsRemaining--;
    updateTimerDisplay();

    if (activeExamState.secondsRemaining <= 0) {
      clearInterval(activeExamState.timerInterval);
      alert("Süre doldu! Sınavınız otomatik olarak teslim ediliyor.");
      finishExam();
    }
  }, 1000);
}

function updateTimerDisplay() {
  const timerEl = document.getElementById("exam-timer-display");
  if (!timerEl) return;

  const mins = Math.floor(activeExamState.secondsRemaining / 60);
  const secs = activeExamState.secondsRemaining % 60;
  timerEl.innerText = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

  if (activeExamState.secondsRemaining < 180) {
    timerEl.classList.add("timer-urgent");
  } else {
    timerEl.classList.remove("timer-urgent");
  }
}

function renderCurrentQuestion() {
  const q = activeExamState.questions[activeExamState.currentIndex];
  if (!q) return;

  const container = document.getElementById("exam-question-card");
  if (!container) return;

  const currentAns = activeExamState.userAnswers[q.id];
  const isFlagged = activeExamState.flaggedQuestions.has(q.id);
  const spentSoFar = activeExamState.questionTimes[q.id] || 0;

  container.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
      <div class="flex items-center gap-2 sm:gap-3 flex-wrap">
        <span class="px-3 py-1 bg-blue-100 text-blue-700 font-bold text-xs rounded-lg uppercase">
          Soru ${activeExamState.currentIndex + 1} / ${activeExamState.questions.length}
        </span>
        ${activeExamState.isMistakeExam ? `
          <span class="px-2.5 py-1 bg-rose-100 text-rose-700 text-xs font-bold rounded-lg flex items-center gap-1">
            <i data-lucide="shield-alert" class="w-3.5 h-3.5"></i> Hata Defteri Tekrarı
          </span>
        ` : ''}
        <span class="px-2.5 py-0.5 bg-slate-100 text-slate-600 text-xs font-semibold rounded-md">
          ${q.category || 'Use of English'}
        </span>
        <span class="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-xs font-bold rounded-md">
          ${q.level || 'B2'}
        </span>
      </div>

      <div class="flex items-center gap-2">
        <span class="text-xs text-slate-400 font-mono hidden sm:inline" title="Bu soruda geçen süre">
          ⏱️ ~${spentSoFar}s
        </span>
        <button onclick="toggleFlagQuestion('${q.id}')" class="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition ${isFlagged ? 'bg-amber-50 text-amber-600 border-amber-300' : 'text-slate-400 hover:text-slate-600 border-slate-200'}">
          <i data-lucide="bookmark" class="w-4 h-4 ${isFlagged ? 'fill-amber-500' : ''}"></i>
          ${isFlagged ? 'İşaretlendi' : 'İşaretle'}
        </button>
      </div>
    </div>

    ${q.passage ? `
      <div class="mb-6 p-5 bg-slate-50 border border-slate-200 rounded-2xl text-slate-700 text-sm leading-relaxed font-serif">
        <div class="text-xs font-bold tracking-wider uppercase text-slate-400 mb-2 font-sans">Okuma Parçası (Reading Passage)</div>
        ${q.passage}
      </div>
    ` : ''}

    <div class="text-base font-semibold text-slate-800 leading-relaxed mb-6 whitespace-pre-line">
      ${q.question}
    </div>

    <!-- Seçenekler -->
    <div class="space-y-3">
      ${q.options.map(opt => {
        const isSelected = currentAns === opt.key;
        return `
          <div onclick="selectExamOption('${q.id}', '${opt.key}')" class="p-4 rounded-xl border-2 cursor-pointer transition flex items-start gap-4 ${isSelected ? 'border-blue-600 bg-blue-50/50 shadow-sm' : 'border-slate-200 hover:border-slate-300 bg-white'}">
            <span class="w-7 h-7 shrink-0 rounded-lg font-bold text-xs flex items-center justify-center ${isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'}">
              ${opt.key}
            </span>
            <div class="text-sm ${isSelected ? 'text-blue-950 font-medium' : 'text-slate-700'} pt-0.5">
              ${opt.text}
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function selectExamOption(questionId, optionKey) {
  activeExamState.userAnswers[questionId] = optionKey;
  renderCurrentQuestion();
  renderQuestionPalette();
}

function toggleFlagQuestion(questionId) {
  if (activeExamState.flaggedQuestions.has(questionId)) {
    activeExamState.flaggedQuestions.delete(questionId);
  } else {
    activeExamState.flaggedQuestions.add(questionId);
  }
  renderCurrentQuestion();
  renderQuestionPalette();
}

function renderQuestionPalette() {
  const container = document.getElementById("exam-question-palette");
  if (!container) return;

  container.innerHTML = activeExamState.questions.map((q, idx) => {
    const isCurrent = idx === activeExamState.currentIndex;
    const isAnswered = activeExamState.userAnswers[q.id] !== undefined;
    const isFlagged = activeExamState.flaggedQuestions.has(q.id);

    let btnClass = "border text-slate-600 bg-white hover:bg-slate-50";
    if (isAnswered) {
      btnClass = "bg-blue-600 text-white border-blue-600 font-bold";
    }
    if (isFlagged) {
      btnClass += " ring-2 ring-amber-400";
    }
    if (isCurrent) {
      btnClass += " ring-2 ring-offset-2 ring-blue-500 scale-105";
    }

    return `
      <button onclick="jumpToExamQuestion(${idx})" class="w-9 h-9 rounded-lg text-xs font-medium transition flex items-center justify-center ${btnClass}">
        ${idx + 1}
      </button>
    `;
  }).join('');
}

function jumpToExamQuestion(index) {
  trackQuestionTimeLeave();
  activeExamState.currentIndex = index;
  trackQuestionTimeEnter();
  renderCurrentQuestion();
  renderQuestionPalette();
}

function nextExamQuestion() {
  if (activeExamState.currentIndex < activeExamState.questions.length - 1) {
    trackQuestionTimeLeave();
    activeExamState.currentIndex++;
    trackQuestionTimeEnter();
    renderCurrentQuestion();
    renderQuestionPalette();
  }
}

function prevExamQuestion() {
  if (activeExamState.currentIndex > 0) {
    trackQuestionTimeLeave();
    activeExamState.currentIndex--;
    trackQuestionTimeEnter();
    renderCurrentQuestion();
    renderQuestionPalette();
  }
}

async function finishExam() {
  trackQuestionTimeLeave();
  if (activeExamState.timerInterval) clearInterval(activeExamState.timerInterval);

  const durationSpent = activeExamState.totalSeconds - activeExamState.secondsRemaining;

  try {
    const res = await fetch('/api/exam/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        university_id: activeExamState.universityId,
        level: activeExamState.level,
        duration_seconds: durationSpent,
        answers: activeExamState.userAnswers,
        question_times: activeExamState.questionTimes,
        is_mistake_practice: activeExamState.isMistakeExam
      })
    });

    const result = await res.json();
    showExamResults(result);

  } catch (err) {
    console.error("Exam submit error:", err);
    alert("Sınav sonuçları kaydedilirken hata oluştu.");
  }
}

function showExamResults(result) {
  const modal = document.getElementById("exam-results-modal");
  if (!modal) return;

  const currentUni = window.appState.currentUniversity || { passing_score: 60, name: "Hazırlık Sınavı" };
  const isPassed = result.score >= currentUni.passing_score;
  const tAnalytics = result.time_analytics || {};

  modal.classList.remove("hidden");

  modal.innerHTML = `
    <div class="bg-white rounded-3xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl p-6 sm:p-8 border border-slate-100">
      
      <!-- Başlık ve Sonuç Kartı -->
      <div class="text-center pb-6 border-b border-slate-100">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center ${isPassed ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'}">
          <i data-lucide="${isPassed ? 'award' : 'alert-circle'}" class="w-8 h-8"></i>
        </div>
        <h2 class="text-2xl font-bold text-slate-800">${isPassed ? 'Tebrikler, Muafiyet Barajını Geçtiniz!' : 'Sınav Tamamlandı'}</h2>
        <p class="text-sm text-slate-500 mt-1">${currentUni.name} • Hedef Baraj Notu: %${currentUni.passing_score}</p>
        
        <div class="grid grid-cols-3 gap-3 sm:gap-4 mt-6 max-w-md mx-auto">
          <div class="p-3 bg-slate-50 rounded-2xl border border-slate-100">
            <div class="text-2xl font-extrabold text-blue-600">%${result.score}</div>
            <div class="text-xs text-slate-400 mt-0.5">Başarı Oranı</div>
          </div>
          <div class="p-3 bg-emerald-50 rounded-2xl border border-emerald-100">
            <div class="text-2xl font-extrabold text-emerald-600">${result.correct_count}</div>
            <div class="text-xs text-emerald-600 mt-0.5">Doğru</div>
          </div>
          <div class="p-3 bg-rose-50 rounded-2xl border border-rose-100">
            <div class="text-2xl font-extrabold text-rose-600">${result.wrong_count}</div>
            <div class="text-xs text-rose-600 mt-0.5">Yanlış / Boş</div>
          </div>
        </div>
      </div>

      <!-- Soru Başına Süre & Zaman Yönetimi Analitiği -->
      <div class="py-6 border-b border-slate-100">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
            <i data-lucide="clock" class="w-4 h-4 text-amber-500"></i> Zaman Yönetimi & Hız Analizi
          </h3>
          <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">
            Toplam Süre: ${Math.floor(result.duration_seconds / 60)} dk ${result.duration_seconds % 60} sn
          </span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="p-3.5 bg-amber-50/60 rounded-2xl border border-amber-200/80">
            <span class="text-xs text-amber-800 font-semibold block mb-1">Ortalama Soru Süresi</span>
            <div class="text-xl font-extrabold text-amber-900">${tAnalytics.avg_time_per_question || 0} sn / soru</div>
            <span class="text-[10px] text-amber-700">İdeal: 60-90 sn</span>
          </div>

          <div class="p-3.5 bg-blue-50/60 rounded-2xl border border-blue-200/80">
            <span class="text-xs text-blue-800 font-semibold block mb-1">En Hızlı Yanıt</span>
            <div class="text-xl font-extrabold text-blue-900">${tAnalytics.fastest_question ? `${tAnalytics.fastest_question.seconds} sn` : '-'}</div>
            <span class="text-[10px] text-blue-700">Hızlı ve kendinden emin</span>
          </div>

          <div class="p-3.5 ${tAnalytics.time_traps_count > 0 ? 'bg-rose-50/60 border-rose-200/80' : 'bg-emerald-50/60 border-emerald-200/80'} rounded-2xl border">
            <span class="text-xs ${tAnalytics.time_traps_count > 0 ? 'text-rose-800' : 'text-emerald-800'} font-semibold block mb-1">Zaman Tuzakları (>90 sn)</span>
            <div class="text-xl font-extrabold ${tAnalytics.time_traps_count > 0 ? 'text-rose-900' : 'text-emerald-900'}">${tAnalytics.time_traps_count || 0} Soru</div>
            <span class="text-[10px] ${tAnalytics.time_traps_count > 0 ? 'text-rose-700' : 'text-emerald-700'}">${tAnalytics.time_traps_count > 0 ? 'Aşırı vakit harcanan sorular' : 'Zaman yönetimi harika!'}</span>
          </div>
        </div>
      </div>

      <!-- Detaylı Soru İncelemesi & Çözüm Açıklamaları -->
      <div class="py-6 space-y-6">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-bold text-slate-800 flex items-center gap-2">
            <i data-lucide="file-check" class="w-5 h-5 text-blue-600"></i> Detaylı Çözüm Açıklamaları
          </h3>
          ${result.wrong_count > 0 ? `
            <span class="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-200">
              📌 ${result.wrong_count} Yanlış Hata Defterine Kaydedildi
            </span>
          ` : ''}
        </div>

        ${result.details.map((d, index) => {
          const isTimeTrap = d.time_spent >= 90;
          return `
            <div class="p-5 rounded-2xl border ${d.is_correct ? 'border-emerald-200 bg-emerald-50/20' : 'border-rose-200 bg-rose-50/20'}">
              <div class="flex items-center justify-between mb-2 flex-wrap gap-2">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-bold ${d.is_correct ? 'text-emerald-700' : 'text-rose-700'}">
                    Soru ${index + 1} (${d.category}) - ${d.is_correct ? 'DOĞRU' : 'YANLIŞ'}
                  </span>
                  <span class="px-2 py-0.5 rounded text-[11px] font-mono font-bold ${isTimeTrap ? 'bg-amber-100 text-amber-800 border border-amber-300' : 'bg-slate-100 text-slate-600'}">
                    ⏱️ ${d.time_spent} sn ${isTimeTrap ? '⚠️ Zaman Tuzağı' : ''}
                  </span>
                </div>
                <span class="text-xs text-slate-500">
                  Cevabınız: <strong>${d.chosen_answer || 'Boş'}</strong> | Doğru Cevap: <strong class="text-emerald-600">${d.correct_answer}</strong>
                </span>
              </div>
              <p class="text-sm text-slate-800 font-medium mb-3 whitespace-pre-line">${d.question_text}</p>
              
              <div class="p-3.5 bg-white rounded-xl border border-slate-200/80 text-xs text-slate-600 leading-relaxed">
                <strong class="text-blue-700 block mb-1 flex items-center gap-1">
                  <i data-lucide="lightbulb" class="w-3.5 h-3.5"></i> Neden ${d.correct_answer}? (Detaylı Açıklama):
                </strong>
                ${d.explanation_tr || 'Açıklama mevcut değil.'}
              </div>
            </div>
          `;
        }).join('')}
      </div>

      <!-- Butonlar -->
      <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
        ${result.wrong_count > 0 ? `
          <button onclick="exitExamInterface(); switchTab('mistakes');" class="px-4 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold rounded-xl text-xs border border-rose-200 transition flex items-center gap-1.5">
            <i data-lucide="shield-alert" class="w-4 h-4"></i> Hata Defterime Git
          </button>
        ` : `<div></div>`}

        <button onclick="exitExamInterface()" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm shadow transition">
          Tamamla ve Dashboard'a Dön
        </button>
      </div>

    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

window.startExamSimulation = startExamSimulation;
window.startMistakeExam = startMistakeExam;
window.selectExamOption = selectExamOption;
window.toggleFlagQuestion = toggleFlagQuestion;
window.jumpToExamQuestion = jumpToExamQuestion;
window.nextExamQuestion = nextExamQuestion;
window.prevExamQuestion = prevExamQuestion;
window.finishExam = finishExam;
window.exitExamInterface = exitExamInterface;
