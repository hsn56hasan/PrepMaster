// PrepMaster Speaking & Interview Simulator

window.speakingState = {
  tasks: [],
  currentTask: null,
  phase: 'idle', // 'idle', 'prep', 'speaking', 'result'
  prepSecondsLeft: 0,
  speakSecondsLeft: 0,
  timerInterval: null,
  recognition: null,
  transcript: '',
  isRecording: false,
  durationElapsed: 0
};

async function loadSpeakingHub(targetLevel = null) {
  const container = document.getElementById("speaking-tasks-list");
  const filterBar = document.getElementById("speaking-filter-bar");
  if (!container) return;

  const currentLevel = window.appState?.currentLevel || 'B2';
  const activeLevel = targetLevel !== null ? targetLevel : currentLevel;

  // Render Level Filter Bar
  if (filterBar) {
    const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
    filterBar.innerHTML = `
      <span class="text-xs font-bold text-slate-500 mr-2 flex items-center gap-1">
        <i data-lucide="filter" class="w-3.5 h-3.5"></i> Mülakat Kuru:
      </span>
      ${levels.map(lvl => {
        const isSelected = activeLevel === lvl;
        return `
          <button onclick="loadSpeakingHub('${lvl}')" class="px-3 py-1 rounded-xl text-xs font-bold transition ${isSelected ? 'bg-indigo-600 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-200 border border-slate-200'}">
            ${lvl} ${lvl === currentLevel ? '★' : ''}
          </button>
        `;
      }).join('')}
      <button onclick="loadSpeakingHub('all')" class="px-3 py-1 rounded-xl text-xs font-bold transition ${activeLevel === 'all' ? 'bg-slate-800 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-200 border border-slate-200'}">
        Tüm Kurlar
      </button>
    `;
  }

  container.innerHTML = `
    <div class="col-span-full p-8 text-center text-slate-400">
      <i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-600"></i>
      ${activeLevel === 'all' ? 'Tüm' : activeLevel} seviyesi konuşma görevleri yükleniyor...
    </div>
  `;
  if (window.lucide) window.lucide.createIcons();

  try {
    const url = activeLevel && activeLevel !== 'all' ? `/api/speaking?level=${activeLevel}` : '/api/speaking';
    const res = await fetch(url);
    const tasks = await res.json();
    window.speakingState.tasks = tasks;

    if (!tasks || tasks.length === 0) {
      container.innerHTML = `
        <div class="col-span-full p-8 text-center bg-white rounded-3xl border border-slate-200">
          <p class="text-sm font-bold text-slate-700 mb-2">${activeLevel} seviyesinde mülakat görevi bulunamadı.</p>
          <button onclick="loadSpeakingHub('all')" class="px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded-xl hover:bg-indigo-700 transition">
            Tüm Mülakatları Görüntüle
          </button>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    container.innerHTML = tasks.map(t => `
      <div class="bg-white rounded-3xl p-6 border border-slate-200/80 hover:border-indigo-400 hover:shadow-md transition flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <span class="px-2.5 py-1 text-[11px] font-extrabold rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200">
              🎙️ Sözlü Mülakat
            </span>
            <span class="px-2.5 py-0.5 bg-indigo-50 text-indigo-700 border border-indigo-100 rounded-lg text-xs font-black">
              ${t.level}
            </span>
          </div>

          <h3 class="text-base font-extrabold text-slate-800 mb-1 leading-snug">${t.title}</h3>
          <p class="text-xs font-bold text-indigo-600 mb-2">${t.target_university}</p>
          <p class="text-xs text-slate-500 leading-relaxed mb-4">${t.instructions_tr}</p>

          <div class="p-3 bg-slate-50 rounded-xl border border-slate-100 mb-4 text-xs text-slate-600 italic">
            "${t.prompt_en}"
          </div>
        </div>

        <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
          <span class="text-xs text-slate-400 flex items-center gap-1 font-medium">
            <i data-lucide="clock" class="w-3.5 h-3.5"></i> Hazırlık: ${t.prep_time_seconds}s • Konuşma: ${t.speak_time_seconds}s
          </span>
          <button onclick="startSpeakingTask('${t.id}')" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5 shadow-sm shadow-indigo-500/20">
            <i data-lucide="mic" class="w-3.5 h-3.5"></i> Mülakata Başla
          </button>
        </div>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    console.error("Load speaking hub error:", err);
    container.innerHTML = `<p class="col-span-full text-xs text-rose-500 text-center">Konuşma görevleri yüklenemedi.</p>`;
  }
}

function startSpeakingTask(taskId) {
  const task = window.speakingState.tasks.find(t => t.id === taskId);
  if (!task) return;

  window.speakingState.currentTask = task;
  window.speakingState.transcript = '';
  window.speakingState.durationElapsed = 0;

  // Show runner modal or view
  const runner = document.getElementById("speaking-runner-view");
  const hub = document.getElementById("speaking-hub-view");
  if (runner) runner.classList.remove("hidden");
  if (hub) hub.classList.add("hidden");

  startPrepPhase();
}

function startPrepPhase() {
  const task = window.speakingState.currentTask;
  window.speakingState.phase = 'prep';
  window.speakingState.prepSecondsLeft = task.prep_time_seconds;

  renderSpeakingRunnerUI();

  if (window.speakingState.timerInterval) clearInterval(window.speakingState.timerInterval);

  window.speakingState.timerInterval = setInterval(() => {
    window.speakingState.prepSecondsLeft--;
    updateSpeakingTimerUI();

    if (window.speakingState.prepSecondsLeft <= 0) {
      clearInterval(window.speakingState.timerInterval);
      startRecordingPhase();
    }
  }, 1000);
}

function startRecordingPhase() {
  if (window.speakingState.timerInterval) clearInterval(window.speakingState.timerInterval);

  const task = window.speakingState.currentTask;
  window.speakingState.phase = 'speaking';
  window.speakingState.speakSecondsLeft = task.speak_time_seconds;
  window.speakingState.isRecording = true;
  window.speakingState.durationElapsed = 0;

  renderSpeakingRunnerUI();

  // Initialize Speech Recognition if supported
  initSpeechRecognition();

  window.speakingState.timerInterval = setInterval(() => {
    window.speakingState.speakSecondsLeft--;
    window.speakingState.durationElapsed++;
    updateSpeakingTimerUI();

    if (window.speakingState.speakSecondsLeft <= 0) {
      finishSpeakingRecording();
    }
  }, 1000);
}

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn("SpeechRecognition not supported in this browser.");
    return;
  }

  try {
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
      let finalTranscript = '';
      for (let i = 0; i < event.results.length; i++) {
        finalTranscript += event.results[i][0].transcript + ' ';
      }
      window.speakingState.transcript = finalTranscript.trim();
      const txtArea = document.getElementById("speaking-live-transcript");
      if (txtArea) txtArea.value = window.speakingState.transcript;
    };

    recognition.onerror = (e) => {
      console.warn("Speech recognition error:", e);
    };

    recognition.start();
    window.speakingState.recognition = recognition;
  } catch (e) {
    console.error("Speech recognition startup error:", e);
  }
}

function finishSpeakingRecording() {
  if (window.speakingState.timerInterval) clearInterval(window.speakingState.timerInterval);
  window.speakingState.isRecording = false;

  if (window.speakingState.recognition) {
    try { window.speakingState.recognition.stop(); } catch (_) {}
  }

  // Get transcript from textarea in case user edited it
  const txtArea = document.getElementById("speaking-live-transcript");
  if (txtArea && txtArea.value.trim().length > 0) {
    window.speakingState.transcript = txtArea.value.trim();
  }

  evaluateSpeakingTranscript();
}

async function evaluateSpeakingTranscript() {
  const task = window.speakingState.currentTask;
  const transcript = window.speakingState.transcript || "No transcript recorded.";
  const duration = Math.max(window.speakingState.durationElapsed, 15);

  const resultsContainer = document.getElementById("speaking-results-container");
  if (resultsContainer) {
    resultsContainer.innerHTML = `
      <div class="p-8 text-center text-slate-500">
        <i data-lucide="loader-2" class="w-8 h-8 animate-spin mx-auto mb-3 text-indigo-600"></i>
        <p class="font-bold">Yapay Zeka Mülakat Analizi Yapılıyor...</p>
        <p class="text-xs text-slate-400 mt-1">Akıcılık, kelime çeşitliliği, gramer ve soruya odaklanma puanlanıyor.</p>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
  }

  window.speakingState.phase = 'result';
  renderSpeakingRunnerUI();

  try {
    const res = await fetch('/api/speaking/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript: transcript,
        task_id: task.id,
        duration_seconds: duration
      })
    });

    const data = await res.json();
    renderSpeakingEvaluationResult(data);
  } catch (err) {
    console.error("Speaking evaluation error:", err);
  }
}

function renderSpeakingRunnerUI() {
  const task = window.speakingState.currentTask;
  if (!task) return;

  const titleEl = document.getElementById("speaking-runner-title");
  const promptEl = document.getElementById("speaking-runner-prompt");
  const guidingEl = document.getElementById("speaking-guiding-questions");
  const vocabEl = document.getElementById("speaking-key-vocab");

  if (titleEl) titleEl.innerText = `${task.target_university} - ${task.title}`;
  if (promptEl) promptEl.innerText = task.prompt_en;

  if (guidingEl && task.guiding_questions) {
    guidingEl.innerHTML = task.guiding_questions.map(q => `
      <li class="flex items-start gap-2">
        <i data-lucide="chevron-right" class="w-3.5 h-3.5 text-indigo-500 shrink-0 mt-0.5"></i>
        <span>${q}</span>
      </li>
    `).join('');
  }

  if (vocabEl && task.key_vocabulary) {
    vocabEl.innerHTML = task.key_vocabulary.map(v => `
      <span class="px-2.5 py-1 bg-indigo-50 text-indigo-700 text-xs font-semibold rounded-lg border border-indigo-100">
        ${v}
      </span>
    `).join('');
  }

  const prepBox = document.getElementById("speaking-prep-box");
  const recordBox = document.getElementById("speaking-record-box");
  const resultBox = document.getElementById("speaking-results-container");

  if (window.speakingState.phase === 'prep') {
    if (prepBox) prepBox.classList.remove("hidden");
    if (recordBox) recordBox.classList.add("hidden");
    if (resultBox) resultBox.classList.add("hidden");
  } else if (window.speakingState.phase === 'speaking') {
    if (prepBox) prepBox.classList.add("hidden");
    if (recordBox) recordBox.classList.remove("hidden");
    if (resultBox) resultBox.classList.add("hidden");
  } else if (window.speakingState.phase === 'result') {
    if (prepBox) prepBox.classList.add("hidden");
    if (recordBox) recordBox.classList.add("hidden");
    if (resultBox) resultBox.classList.remove("hidden");
  }

  updateSpeakingTimerUI();
  if (window.lucide) window.lucide.createIcons();
}

function updateSpeakingTimerUI() {
  const timerBadge = document.getElementById("speaking-timer-badge");
  if (!timerBadge) return;

  if (window.speakingState.phase === 'prep') {
    timerBadge.innerText = `⏳ Hazırlık: ${window.speakingState.prepSecondsLeft}s`;
    timerBadge.className = "px-3 py-1 bg-amber-100 text-amber-800 border border-amber-300 rounded-full text-xs font-bold";
  } else if (window.speakingState.phase === 'speaking') {
    timerBadge.innerText = `🔴 Konuşun: ${window.speakingState.speakSecondsLeft}s`;
    timerBadge.className = "px-3 py-1 bg-rose-100 text-rose-700 border border-rose-300 rounded-full text-xs font-bold animate-pulse";
  }
}

function renderSpeakingEvaluationResult(data) {
  const container = document.getElementById("speaking-results-container");
  if (!container) return;

  const task = window.speakingState.currentTask;

  container.innerHTML = `
    <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-lg space-y-6">
      
      <!-- Başlık & Genel Skor -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-4">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Mülakat Değerlendirme Karnesi</span>
          <h3 class="text-xl font-extrabold text-slate-800">${task.target_university}</h3>
          <p class="text-xs text-slate-500 mt-1">Süre: ${window.speakingState.durationElapsed}s • Kelime: ${data.word_count} • Hız: ${data.speaking_rate_wpm} WPM</p>
        </div>

        <div class="flex items-center gap-3">
          <div class="text-right">
            <div class="text-3xl font-black ${data.is_passing ? 'text-emerald-600' : 'text-amber-600'}">
              %${data.overall_score}
            </div>
            <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full ${data.is_passing ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
              ${data.is_passing ? 'MUAFİYET BAŞARILI' : 'GELİŞTİRİLMELİ'}
            </span>
          </div>
          <div class="px-3.5 py-2 bg-indigo-50 border border-indigo-200 rounded-2xl text-center">
            <span class="text-[10px] uppercase font-bold text-indigo-500 block">CEFR</span>
            <span class="text-sm font-extrabold text-indigo-700">${data.cefr_level.split(' ')[0]}</span>
          </div>
        </div>
      </div>

      <!-- 4 Temel Kriter Puanları -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-100 text-center">
          <span class="text-[11px] font-bold text-slate-400 block mb-1">Akıcılık (Fluency)</span>
          <span class="text-lg font-black text-slate-800">${data.scores.fluency_and_coherence} / 25</span>
        </div>
        <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-100 text-center">
          <span class="text-[11px] font-bold text-slate-400 block mb-1">Kelime (Lexical)</span>
          <span class="text-lg font-black text-slate-800">${data.scores.lexical_resource} / 25</span>
        </div>
        <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-100 text-center">
          <span class="text-[11px] font-bold text-slate-400 block mb-1">Gramer (Grammar)</span>
          <span class="text-lg font-black text-slate-800">${data.scores.grammatical_range} / 25</span>
        </div>
        <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-100 text-center">
          <span class="text-[11px] font-bold text-slate-400 block mb-1">Görev Başarısı</span>
          <span class="text-lg font-black text-slate-800">${data.scores.task_achievement} / 25</span>
        </div>
      </div>

      <!-- Güçlü Yönler & Geliştirilmesi Gerekenler -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl space-y-2">
          <h4 class="text-xs font-extrabold text-emerald-900 flex items-center gap-1.5">
            <i data-lucide="check" class="w-4 h-4 text-emerald-600"></i> Güçlü Yönleriniz
          </h4>
          <ul class="text-xs text-emerald-800 space-y-1 list-disc list-inside">
            ${data.strengths_tr.map(s => `<li>${s}</li>`).join('')}
          </ul>
        </div>

        <div class="p-4 bg-amber-50 border border-amber-200 rounded-2xl space-y-2">
          <h4 class="text-xs font-extrabold text-amber-900 flex items-center gap-1.5">
            <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-600"></i> Geliştirme Tavsiyeleri
          </h4>
          <ul class="text-xs text-amber-800 space-y-1 list-disc list-inside">
            ${data.improvements_tr.map(i => `<li>${i}</li>`).join('')}
          </ul>
        </div>
      </div>

      <!-- Öğrenci Transkripti & Model Cevap -->
      <div class="space-y-3">
        <details class="text-xs bg-slate-50 p-4 rounded-2xl border border-slate-200">
          <summary class="cursor-pointer font-bold text-indigo-600 hover:text-indigo-700 list-none flex items-center justify-between">
            <span>🎙️ Sizin Konuşma Metniniz (Transcript)</span>
            <span class="text-slate-400">Göster / Gizle</span>
          </summary>
          <p class="mt-3 text-slate-700 leading-relaxed italic bg-white p-3 rounded-xl border border-slate-100">
            "${window.speakingState.transcript}"
          </p>
        </details>

        <details class="text-xs bg-indigo-50/60 p-4 rounded-2xl border border-indigo-200">
          <summary class="cursor-pointer font-bold text-indigo-700 hover:text-indigo-800 list-none flex items-center justify-between">
            <span>⭐ Örnek C1 Model Konuşma (Examiner Model Answer)</span>
            <span class="text-indigo-400">İncele</span>
          </summary>
          <p class="mt-3 text-indigo-950 leading-relaxed bg-white p-3.5 rounded-xl border border-indigo-100">
            "${data.model_transcript}"
          </p>
        </details>
      </div>

      <!-- Aksiyon Butonları -->
      <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
        <button onclick="exitSpeakingRunner()" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition">
          Mülakat Listesine Dön
        </button>
        <button onclick="startPrepPhase()" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl transition flex items-center gap-1.5 shadow-md shadow-indigo-500/20">
          <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i> Yeniden Dene
        </button>
      </div>

    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function exitSpeakingRunner() {
  if (window.speakingState.timerInterval) clearInterval(window.speakingState.timerInterval);
  if (window.speakingState.recognition) {
    try { window.speakingState.recognition.stop(); } catch (_) {}
  }

  const runner = document.getElementById("speaking-runner-view");
  const hub = document.getElementById("speaking-hub-view");
  if (runner) runner.classList.add("hidden");
  if (hub) hub.classList.remove("hidden");

  loadSpeakingHub();
}

// Window exports
window.loadSpeakingHub = loadSpeakingHub;
window.startSpeakingTask = startSpeakingTask;
window.startPrepPhase = startPrepPhase;
window.startRecordingPhase = startRecordingPhase;
window.finishSpeakingRecording = finishSpeakingRecording;
window.exitSpeakingRunner = exitSpeakingRunner;
