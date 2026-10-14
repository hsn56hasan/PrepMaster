// PrepMaster Main Application Logic

window.appState = {
  currentUniversity: null,
  currentLevel: 'B2',
  allUniversities: [],
  activeTab: 'dashboard'
};

document.addEventListener("DOMContentLoaded", async () => {
  await initApp();
});

async function initApp() {
  try {
    // 1. Fetch Universities
    const uniRes = await fetch('/api/universities');
    window.appState.allUniversities = await uniRes.json();

    // 2. Fetch User Profile
    const profRes = await fetch('/api/profile');
    const profile = await profRes.json();
    
    window.appState.currentLevel = profile.current_level || 'B2';
    window.appState.currentUniversity = profile.university || window.appState.allUniversities[0];

    // 3. Render Initial State
    renderUniversityHeader();
    renderLevelSelector();
    setupTabNavigation();
    
    // 4. Load initial tab
    switchTab('dashboard');

    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    console.error("Initialization error:", err);
  }
}

function renderUniversityHeader() {
  const uni = window.appState.currentUniversity;
  if (!uni) return;

  const titleEl = document.getElementById("header-uni-name");
  const badgeEl = document.getElementById("header-uni-badge");
  const examNameEl = document.getElementById("dashboard-exam-title");
  const passScoreEl = document.getElementById("dashboard-pass-score");
  const descEl = document.getElementById("dashboard-uni-desc");
  const sectionsEl = document.getElementById("dashboard-exam-sections");

  if (titleEl) titleEl.innerText = uni.short_name || uni.name;
  if (badgeEl) badgeEl.innerText = `${uni.short_name} Hazırlık`;
  if (examNameEl) examNameEl.innerText = uni.exam_name;
  if (passScoreEl) passScoreEl.innerText = `%${uni.passing_score} Baraj Puanı`;
  if (descEl) descEl.innerText = uni.description;

  // Render sections
  if (sectionsEl && uni.sections) {
    sectionsEl.innerHTML = uni.sections.map(sec => `
      <div class="p-4 bg-slate-50/80 rounded-2xl border border-slate-100 hover:border-slate-200 transition">
        <div class="flex items-center justify-between mb-1.5">
          <span class="text-sm font-bold text-slate-800">${sec.name}</span>
          <span class="text-xs font-semibold px-2 py-0.5 bg-blue-100 text-blue-700 rounded-md">
            Ağırlık: %${sec.weight_percent}
          </span>
        </div>
        <p class="text-xs text-slate-500 leading-relaxed">${sec.description}</p>
      </div>
    `).join('');
  }
}

function renderLevelSelector() {
  const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
  const container = document.getElementById("level-selector-pills");
  if (!container) return;

  container.innerHTML = levels.map(lvl => {
    const isSelected = lvl === window.appState.currentLevel;
    return `
      <button onclick="changeCurrentLevel('${lvl}')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition ${isSelected ? 'bg-blue-600 text-white shadow-md' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}">
        ${lvl}
      </button>
    `;
  }).join('');
}

async function changeCurrentLevel(lvl) {
  window.appState.currentLevel = lvl;
  renderLevelSelector();

  // Save profile to backend
  try {
    await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        university_id: window.appState.currentUniversity.id,
        current_level: lvl
      })
    });
  } catch (err) {
    console.error("Save profile error:", err);
  }

  // Refresh active tab content
  if (window.appState.activeTab === 'flashcards' && window.loadFlashcards) {
    window.loadFlashcards(lvl);
  } else if (window.appState.activeTab === 'practice') {
    loadPracticeQuestions();
  }
}

function setupTabNavigation() {
  const navBtns = document.querySelectorAll("[data-nav-tab]");
  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const tab = btn.getAttribute("data-nav-tab");
      switchTab(tab);
    });
  });
}

function switchTab(tabName) {
  window.appState.activeTab = tabName;

  // Toggle visible sections
  const tabs = ['dashboard', 'exams', 'listening', 'practice', 'flashcards', 'writing', 'analytics', 'mistakes'];
  tabs.forEach(t => {
    const el = document.getElementById(`tab-content-${t}`);
    if (el) {
      if (t === tabName) el.classList.remove("hidden");
      else el.classList.add("hidden");
    }
  });

  // Update nav button active styles
  document.querySelectorAll("[data-nav-tab]").forEach(btn => {
    const tab = btn.getAttribute("data-nav-tab");
    if (tab === tabName) {
      btn.classList.add("bg-blue-600", "text-white");
      btn.classList.remove("text-slate-600", "hover:bg-slate-100");
    } else {
      btn.classList.remove("bg-blue-600", "text-white");
      btn.classList.add("text-slate-600", "hover:bg-slate-100");
    }
  });

  // Execute tab-specific loaders
  if (tabName === 'dashboard') {
    loadDashboardStats();
  } else if (tabName === 'listening') {
    if (window.loadListeningHub) window.loadListeningHub();
  } else if (tabName === 'flashcards' && window.loadFlashcards) {
    window.loadFlashcards(window.appState.currentLevel);
  } else if (tabName === 'practice') {
    loadPracticeQuestions();
  } else if (tabName === 'writing') {
    if (window.initAIWritingEvaluator) window.initAIWritingEvaluator();
    loadWritingGuides();
  } else if (tabName === 'analytics') {
    loadAnalytics();
  } else if (tabName === 'mistakes') {
    loadMistakeVault();
  }

  if (window.lucide) window.lucide.createIcons();
}

async function loadDashboardStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();

    const streakEl = document.getElementById("stat-streak");
    const examsCountEl = document.getElementById("stat-exams-count");
    const avgScoreEl = document.getElementById("stat-avg-score");
    const vocabCountEl = document.getElementById("stat-vocab-count");
    const mistakesCountEl = document.getElementById("stat-mistakes-count");
    const mistakeNavBadge = document.getElementById("nav-mistakes-badge");
    const recentListEl = document.getElementById("dashboard-recent-exams");

    if (streakEl) streakEl.innerText = `${data.profile.streak_days || 1} Gün`;
    if (examsCountEl) examsCountEl.innerText = data.total_exams_taken;
    if (avgScoreEl) avgScoreEl.innerText = `%${data.average_exam_score}`;
    if (vocabCountEl) vocabCountEl.innerText = `${data.mastered_vocab} / ${data.total_vocab}`;
    
    const mCount = data.unresolved_mistakes || 0;
    if (mistakesCountEl) mistakesCountEl.innerText = mCount;
    if (mistakeNavBadge) {
      mistakeNavBadge.innerText = mCount;
      if (mCount > 0) mistakeNavBadge.classList.remove("hidden");
      else mistakeNavBadge.classList.add("hidden");
    }

    if (recentListEl) {
      if (!data.recent_exams || data.recent_exams.length === 0) {
        recentListEl.innerHTML = `<p class="text-xs text-slate-400 py-3">Henüz tamamlanan sınav denemesi bulunmuyor.</p>`;
      } else {
        recentListEl.innerHTML = data.recent_exams.map(e => `
          <div class="flex items-center justify-between p-3 bg-white rounded-xl border border-slate-100 text-xs">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full ${e.score >= 60 ? 'bg-emerald-500' : 'bg-rose-500'}"></span>
              <span class="font-bold text-slate-700 uppercase">${e.university_id}</span>
              <span class="text-slate-400">• ${e.level}</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="font-extrabold ${e.score >= 60 ? 'text-emerald-600' : 'text-slate-700'}">%${e.score}</span>
              <span class="text-slate-400">${new Date(e.created_at).toLocaleDateString('tr-TR')}</span>
            </div>
          </div>
        `).join('');
      }
    }
  } catch (err) {
    console.error("Dashboard stats error:", err);
  }
}

async function loadPracticeQuestions() {
  const container = document.getElementById("practice-questions-list");
  if (!container) return;

  const lvl = window.appState.currentLevel;
  const uni = window.appState.currentUniversity.id;

  try {
    const res = await fetch(`/api/questions?level=${lvl}`);
    const questions = await res.json();

    if (questions.length === 0) {
      container.innerHTML = `<p class="text-sm text-slate-500 py-6 text-center">Bu seviyede (${lvl}) henüz soru bulunamadı.</p>`;
      return;
    }

    container.innerHTML = questions.map((q, idx) => `
      <div class="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 text-xs font-bold bg-blue-100 text-blue-700 rounded-md">
              ${q.category}
            </span>
            <span class="px-2 py-0.5 text-xs font-semibold bg-slate-100 text-slate-600 rounded-md">
              ${q.level}
            </span>
          </div>
          <span class="text-xs text-slate-400 uppercase font-bold tracking-wider">${q.university_id}</span>
        </div>

        ${q.passage ? `
          <div class="p-4 bg-slate-50 rounded-xl text-xs text-slate-600 leading-relaxed mb-4 border border-slate-100 font-serif">
            ${q.passage}
          </div>
        ` : ''}

        <p class="text-sm font-semibold text-slate-800 mb-4 whitespace-pre-line">${q.question}</p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
          ${q.options.map(opt => `
            <div class="p-3 text-xs bg-slate-50 hover:bg-blue-50 border border-slate-200 rounded-xl flex items-center gap-2 cursor-default">
              <span class="font-bold text-slate-600">${opt.key})</span>
              <span class="text-slate-700">${opt.text}</span>
            </div>
          `).join('')}
        </div>

        <details class="text-xs group">
          <summary class="cursor-pointer font-bold text-blue-600 hover:text-blue-700 list-none flex items-center gap-1">
            <i data-lucide="help-circle" class="w-3.5 h-3.5"></i> Doğru Cevap ve Çözümü Gör
          </summary>
          <div class="mt-3 p-3.5 bg-emerald-50 rounded-xl border border-emerald-100 text-slate-700 leading-relaxed">
            <strong class="text-emerald-700 block mb-1">Doğru Cevap: ${q.correct_answer}</strong>
            ${q.explanation_tr}
          </div>
        </details>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    console.error("Practice load error:", err);
  }
}

async function loadWritingGuides() {
  const container = document.getElementById("writing-guides-container");
  if (!container) return;

  try {
    const res = await fetch('/api/writing-guides');
    const guides = await res.json();

    container.innerHTML = guides.map(g => `
      <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-6">
        <div>
          <h3 class="text-xl font-extrabold text-slate-800 mb-2">${g.title}</h3>
          <p class="text-xs text-slate-500 leading-relaxed">${g.description}</p>
        </div>

        <!-- Paragraf Yapısı -->
        <div class="space-y-3">
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400">İdeal Paragraf & Metin Yapısı</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            ${g.structure.map(st => `
              <div class="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                <span class="text-xs font-bold text-blue-700 block mb-2">${st.section}</span>
                <ul class="text-xs text-slate-600 space-y-1 list-disc list-inside">
                  ${st.elements.map(el => `<li>${el}</li>`).join('')}
                </ul>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Anahtar Bağlaçlar (Transitions) -->
        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Yüksek Puan Kazandıran Kalıplar & Bağlaçlar</h4>
          <div class="flex flex-wrap gap-2">
            ${g.key_transitions.map(tr => `
              <span class="px-3 py-1.5 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-xl border border-indigo-100">
                ${tr}
              </span>
            `).join('')}
          </div>
        </div>

        <!-- Örnek Konu & İpucu -->
        <div class="p-4 bg-amber-50/80 rounded-2xl border border-amber-200 text-xs text-amber-900 leading-relaxed">
          <span class="font-bold block text-amber-800 mb-1">Örnek Sınav Konusu:</span>
          "${g.sample_topic}"
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error("Writing guides error:", err);
  }
}

async function loadAnalytics() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    const historyRes = await fetch('/api/exam/history');
    const history = await historyRes.json();

    const historyTableBody = document.getElementById("analytics-history-table");
    if (historyTableBody) {
      if (history.length === 0) {
        historyTableBody.innerHTML = `<tr><td colspan="5" class="py-6 text-center text-xs text-slate-400">Kayıtlı sınav bulunamadı.</td></tr>`;
      } else {
        historyTableBody.innerHTML = history.map(h => `
          <tr class="border-b border-slate-100 text-xs hover:bg-slate-50">
            <td class="py-3.5 px-4 font-bold text-slate-800 uppercase">${h.university_id}</td>
            <td class="py-3.5 px-4 font-semibold text-slate-600">${h.level}</td>
            <td class="py-3.5 px-4">
              <span class="px-2.5 py-1 rounded-lg font-bold ${h.score >= 60 ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}">
                %${h.score}
              </span>
            </td>
            <td class="py-3.5 px-4 text-slate-600">${h.correct_count} / ${h.total_questions}</td>
            <td class="py-3.5 px-4 text-slate-400">${new Date(h.created_at).toLocaleString('tr-TR')}</td>
          </tr>
        `).join('');
      }
    }
  } catch (err) {
    console.error("Analytics load error:", err);
  }
}

// University Switcher Modal
function openUniversityModal() {
  const modal = document.getElementById("university-picker-modal");
  const list = document.getElementById("university-picker-list");
  if (!modal || !list) return;

  list.innerHTML = window.appState.allUniversities.map(u => {
    const isCurrent = u.id === window.appState.currentUniversity.id;
    return `
      <div onclick="selectUniversity('${u.id}')" class="p-4 rounded-2xl border-2 cursor-pointer transition flex items-center justify-between ${isCurrent ? 'border-blue-600 bg-blue-50/50' : 'border-slate-200 hover:border-slate-300 bg-white'}">
        <div>
          <div class="flex items-center gap-2">
            <h4 class="font-bold text-slate-800 text-sm">${u.name}</h4>
            <span class="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-bold rounded-md">${u.short_name}</span>
          </div>
          <p class="text-xs text-slate-500 mt-1">${u.exam_name} • Geçme Barajı: %${u.passing_score}</p>
        </div>
        <div class="w-6 h-6 rounded-full flex items-center justify-center ${isCurrent ? 'bg-blue-600 text-white' : 'border border-slate-300 text-transparent'}">
          ✓
        </div>
      </div>
    `;
  }).join('');

  modal.classList.remove("hidden");
}

function closeUniversityModal() {
  const modal = document.getElementById("university-picker-modal");
  if (modal) modal.classList.add("hidden");
}

async function selectUniversity(uniId) {
  const selected = window.appState.allUniversities.find(u => u.id === uniId);
  if (!selected) return;

  window.appState.currentUniversity = selected;
  renderUniversityHeader();
  closeUniversityModal();

  try {
    await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        university_id: selected.id,
        current_level: window.appState.currentLevel
      })
    });
  } catch (err) {
    console.error("Profile update error:", err);
  }

  if (window.appState.activeTab === 'practice') {
    loadPracticeQuestions();
  } else if (window.appState.activeTab === 'dashboard') {
    loadDashboardStats();
  }
}

// --- Mistake Vault Module ---
async function loadMistakeVault() {
  const container = document.getElementById("mistake-vault-list");
  const countBadge = document.getElementById("mistake-vault-count-badge");
  const emptyState = document.getElementById("mistake-vault-empty");
  if (!container) return;

  try {
    const res = await fetch('/api/mistakes');
    const mistakes = await res.json();

    if (countBadge) countBadge.innerText = `${mistakes.length} Yanlış Soru`;

    if (mistakes.length === 0) {
      container.innerHTML = '';
      if (emptyState) emptyState.classList.remove("hidden");
      return;
    }
    if (emptyState) emptyState.classList.add("hidden");

    container.innerHTML = mistakes.map((m, idx) => {
      const q = m.question_details;
      return `
        <div class="p-6 bg-white rounded-3xl border border-rose-100 shadow-sm hover:shadow-md transition">
          <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
            <div class="flex items-center gap-2">
              <span class="px-3 py-1 text-xs font-bold bg-rose-100 text-rose-700 rounded-lg">
                ${q.category || 'Soru'} • ${q.level || 'B2'}
              </span>
              <span class="px-2.5 py-1 text-xs font-bold bg-amber-50 text-amber-700 rounded-lg border border-amber-200">
                ${m.wrong_count} kez yanlış yapıldı
              </span>
              <span class="px-2 py-0.5 text-xs text-slate-500 uppercase font-semibold bg-slate-100 rounded-md">
                ${m.university_id}
              </span>
            </div>
            <span class="text-xs text-slate-400 font-mono">
              Son Hata: ${new Date(m.last_wrong_at).toLocaleDateString('tr-TR')}
            </span>
          </div>

          ${q.passage ? `
            <div class="p-4 bg-slate-50 rounded-2xl text-xs text-slate-600 leading-relaxed mb-4 border border-slate-100 font-serif">
              ${q.passage}
            </div>
          ` : ''}

          <p class="text-sm font-semibold text-slate-800 mb-4 whitespace-pre-line">${q.question}</p>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
            ${q.options.map(opt => {
              const isYourWrong = opt.key === m.last_wrong_answer;
              const isCorrect = opt.key === q.correct_answer;
              let borderClass = "border-slate-200 bg-slate-50";
              if (isYourWrong) borderClass = "border-rose-400 bg-rose-50/60 font-semibold";
              if (isCorrect) borderClass = "border-emerald-400 bg-emerald-50/60 font-bold";

              return `
                <div class="p-3 text-xs border rounded-xl flex items-center justify-between ${borderClass}">
                  <div class="flex items-center gap-2">
                    <span class="font-bold">${opt.key})</span>
                    <span>${opt.text}</span>
                  </div>
                  ${isYourWrong ? `<span class="text-[10px] text-rose-600 font-bold shrink-0">Senin Yanıtın</span>` : ''}
                  ${isCorrect ? `<span class="text-[10px] text-emerald-600 font-bold shrink-0">Doğru Cevap</span>` : ''}
                </div>
              `;
            }).join('')}
          </div>

          <div class="p-4 bg-blue-50/60 rounded-2xl border border-blue-100 text-xs text-slate-700 mb-4">
            <strong class="text-blue-800 block mb-1">Neden Yanıldınız? (Çözüm Analizi):</strong>
            ${q.explanation_tr || 'Açıklama mevcut değil.'}
          </div>

          <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
            <button onclick="resolveMistakeItem('${q.id}')" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-sm transition flex items-center gap-1.5">
              <i data-lucide="check-check" class="w-4 h-4"></i> Çözdüm (Hata Defterinden Çıkar)
            </button>
            <button onclick="deleteMistakeItem('${q.id}')" class="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition" title="Sil">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    console.error("Mistake vault load error:", err);
  }
}

async function resolveMistakeItem(questionId) {
  try {
    await fetch(`/api/mistakes/${questionId}/resolve`, { method: 'POST' });
    loadMistakeVault();
    loadDashboardStats();
  } catch (err) {
    console.error("Resolve mistake error:", err);
  }
}

async function deleteMistakeItem(questionId) {
  try {
    await fetch(`/api/mistakes/${questionId}`, { method: 'DELETE' });
    loadMistakeVault();
    loadDashboardStats();
  } catch (err) {
    console.error("Delete mistake error:", err);
  }
}

window.changeCurrentLevel = changeCurrentLevel;
window.switchTab = switchTab;
window.openUniversityModal = openUniversityModal;
window.closeUniversityModal = closeUniversityModal;
window.selectUniversity = selectUniversity;
window.loadDashboardStats = loadDashboardStats;
window.loadMistakeVault = loadMistakeVault;
window.resolveMistakeItem = resolveMistakeItem;
window.deleteMistakeItem = deleteMistakeItem;
