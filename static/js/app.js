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

// Sunucudaki profili uygular. Giriş yoksa varsayılanlarla devam eder.
async function applyServerProfile() {
  let profile = null;
  if (window.appState.currentUser) {
    try {
      const profRes = await fetch('/api/profile');
      if (profRes.ok) profile = await profRes.json();
    } catch (_) {}
  }
  window.appState.currentLevel = (profile && profile.current_level) || window.appState.currentLevel || 'B2';
  const uniId = profile && profile.university_id;
  window.appState.currentUniversity =
    window.appState.allUniversities.find(u => u.id === uniId) ||
    window.appState.currentUniversity ||
    window.appState.allUniversities[0];
  if (profile && window.appState.currentUser) {
    // Kilit bilgisi (unlocked_universities, verified_university, verification_status) da güncel kalsın
    Object.assign(window.appState.currentUser, {
      university_id: profile.university_id || window.appState.currentUser.university_id,
      student_number: profile.student_number || window.appState.currentUser.student_number,
      is_verified_student: profile.is_verified_student,
      unlocked_universities: profile.unlocked_universities,
      verified_university: profile.verified_university,
      verification_status: profile.verification_status,
      streak_days: profile.streak_days,
    });
    localStorage.setItem("auth_user", JSON.stringify(window.appState.currentUser));
  }
}

// Giriş, kayıt ve "eşitle" sonrası: bu öğrencinin verisini sunucudan yeniden yükler.
// Telefonda yapılanlar (kelime, Hata Kasası, denemeler, seçili okul/seviye) böylece web'e gelir.
async function reloadUserData() {
  await applyServerProfile();
  renderUniversityHeader();
  renderLevelSelector();
  switchTab(window.appState.activeTab || 'dashboard');
  loadStudentStatus();
}

function setAppShellVisible(visible) {
  const headerEl = document.getElementById("app-top-navbar");
  const mainEl = document.getElementById("main-content-area");
  const mobileNavEl = document.getElementById("mobile-bottom-nav");

  if (visible) {
    headerEl?.classList.remove("hidden");
    mainEl?.classList.remove("hidden");
    mobileNavEl?.classList.remove("hidden");
  } else {
    headerEl?.classList.add("hidden");
    mainEl?.classList.add("hidden");
    mobileNavEl?.classList.add("hidden");
  }
}

async function initApp() {
  try {
    // 0. Initialize Theme & Auth
    initDarkMode();
    await checkCurrentUser();
    loadPublicConfig();

    // 1. Fetch Universities
    const uniRes = await fetch('/api/universities');
    window.appState.allUniversities = await uniRes.json();

    // 2. Kullanıcının sunucudaki profili (seçili üniversite/seviye mobil ile ortaktır)
    await applyServerProfile();

    // 3. Render Initial State
    renderUniversityHeader();
    renderLevelSelector();
    setupTabNavigation();

    // 4. Giriş ve Belge Doğrulama Kapısı (Arkada sistem gözükmesin)
    if (!window.appState.currentUser) {
      setAppShellVisible(false);
      openAuthModal(true);
    } else if (
      window.appState.currentUser.verification_status !== 'verified' &&
      !window.appState.currentUser.is_verified_student
    ) {
      setAppShellVisible(false);
      document.getElementById("auth-modal")?.classList.add("hidden");
      openDocScanModal(true);
    } else {
      document.getElementById("auth-modal")?.classList.add("hidden");
      setAppShellVisible(true);
      switchTab('dashboard');
      loadStudentStatus();
    }

    initDocDropZone();
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

  // Dynamically refresh the currently active tab content for the new level
  refreshActiveTabContent(lvl);
}

function refreshActiveTabContent(lvl) {
  const currentLvl = lvl || window.appState.currentLevel;
  const activeTab = window.appState.activeTab;

  if (activeTab === 'flashcards' && window.loadFlashcards) {
    window.loadFlashcards(currentLvl);
  } else if (activeTab === 'practice') {
    loadPracticeQuestions();
  } else if (activeTab === 'listening' && window.loadListeningHub) {
    window.loadListeningHub(currentLvl);
  } else if (activeTab === 'speaking' && window.loadSpeakingHub) {
    window.loadSpeakingHub(currentLvl);
  } else if (activeTab === 'writing') {
    loadWritingGuides(currentLvl);
  } else if (activeTab === 'exams') {
    renderExamsTab(currentLvl);
  } else if (activeTab === 'dashboard') {
    loadDashboardStats();
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
  const currentLvl = window.appState.currentLevel;

  // Toggle visible sections
  const tabs = ['dashboard', 'exams', 'listening', 'speaking', 'practice', 'flashcards', 'writing', 'analytics', 'mistakes'];
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

  // Execute tab-specific loaders with active level parameter
  if (tabName === 'dashboard') {
    loadDashboardStats();
  } else if (tabName === 'exams') {
    renderExamsTab(currentLvl);
  } else if (tabName === 'listening') {
    if (window.loadListeningHub) window.loadListeningHub(currentLvl);
  } else if (tabName === 'speaking') {
    if (window.loadSpeakingHub) window.loadSpeakingHub(currentLvl);
  } else if (tabName === 'flashcards' && window.loadFlashcards) {
    window.loadFlashcards(currentLvl);
  } else if (tabName === 'practice') {
    loadPracticeQuestions();
  } else if (tabName === 'writing') {
    if (window.initAIWritingEvaluator) window.initAIWritingEvaluator();
    loadWritingGuides(currentLvl);
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
    if (!res.ok) return;  // giriş yok: kartlar varsayılan hâlinde kalır
    const data = await res.json();

    const streakEl = document.getElementById("stat-streak");
    const examsCountEl = document.getElementById("stat-exams-count");
    const avgScoreEl = document.getElementById("stat-avg-score");
    const vocabCountEl = document.getElementById("stat-vocab-count");
    const mistakesCountEl = document.getElementById("stat-mistakes-count");
    const mistakeNavBadge = document.getElementById("nav-mistakes-badge");
    const recentListEl = document.getElementById("dashboard-recent-exams");

    if (streakEl) streakEl.innerText = `${data.profile.streak_days ?? 0} Gün`;
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

// ---------------- İNTERAKTİF KUR ALIŞTIRMALARI & SORU BANKASI ----------------
const practiceState = {
  category: "all",
  pool: "school_only", // "school_only" (Sadece Seçili Okulun 36 Sorusu), "school_plus_general", "all_unlocked"
  levelScope: "current", // "current" (Seçili Kur) veya "all_levels" (Okulun Tüm 36 Sorusu)
  answers: {}, // { [questionId]: selectedKey }
  questionsById: {}
};

function updatePracticeScoreUI() {
  const counterEl = document.getElementById("practice-score-counter");
  if (!counterEl) return;
  const entries = Object.entries(practiceState.answers);
  const totalSolved = entries.length;
  let correctCount = 0;
  for (const [qid, selectedKey] of entries) {
    const q = practiceState.questionsById[qid];
    if (q && q.correct_answer === selectedKey) {
      correctCount++;
    }
  }
  counterEl.innerText = `${correctCount} / ${totalSolved} Doğru`;
}

function resetPracticeSession() {
  practiceState.answers = {};
  updatePracticeScoreUI();
  loadPracticeQuestions();
  showNotification("✓ Alıştırma yanıtları ve skor sayacı sıfırlandı.", "blue");
}

function setPracticeCategory(cat) {
  practiceState.category = cat;
  loadPracticeQuestions();
}

function setPracticePool(poolMode) {
  practiceState.pool = poolMode;
  loadPracticeQuestions();
}

function setPracticeLevelScope(scopeMode) {
  practiceState.levelScope = scopeMode;
  loadPracticeQuestions();
}

async function selectPracticeOption(questionId, selectedKey) {
  const q = practiceState.questionsById[questionId];
  if (!q) return;

  practiceState.answers[questionId] = selectedKey;
  updatePracticeScoreUI();

  // Sadece ilgili soru kartını veya listeyi anında güncelle
  renderPracticeQuestionList(window._lastPracticeFiltered || []);

  // Yanıtı sunucuya ilet (yanlışsa Hata Defterine ekler, doğruysa çözer)
  try {
    await fetch("/api/practice/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: String(q.id), chosen_answer: selectedKey })
    });
  } catch (_) {}
}

function renderPracticeQuestionList(filteredQuestions) {
  const container = document.getElementById("practice-questions-list");
  if (!container) return;

  const badgeEl = document.getElementById("practice-count-badge");
  if (badgeEl) badgeEl.innerText = `${filteredQuestions.length} Soru`;

  if (filteredQuestions.length === 0) {
    container.innerHTML = `
      <div class="p-8 text-center bg-slate-50 rounded-2xl border border-slate-200/80">
        <p class="text-sm font-bold text-slate-600 mb-2">Bu filtrede (${window.appState.currentLevel} • ${practiceState.category}) soru bulunamadı.</p>
        <button onclick="setPracticeCategory('all'); setPracticePool('all');" class="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-xl hover:bg-blue-700 transition">
          Tüm Kategorileri Göster
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = filteredQuestions.map((q, idx) => {
    const chosen = practiceState.answers[q.id];
    const isAnswered = Boolean(chosen);
    const isCorrect = isAnswered && chosen === q.correct_answer;

    return `
      <div class="p-6 bg-white rounded-2xl border ${isAnswered ? (isCorrect ? 'border-emerald-300 bg-emerald-50/10' : 'border-rose-300 bg-rose-50/10') : 'border-slate-200/80'} shadow-sm hover:shadow-md transition">
        <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 text-xs font-extrabold bg-slate-900 text-white rounded-md">
              #${idx + 1}
            </span>
            <span class="px-2.5 py-0.5 text-xs font-bold bg-blue-100 text-blue-700 rounded-md">
              ${q.category}
            </span>
            <span class="px-2 py-0.5 text-xs font-semibold bg-slate-100 text-slate-600 rounded-md">
              ${q.level}
            </span>
            ${isAnswered ? (
              isCorrect
                ? `<span class="px-2.5 py-0.5 text-xs font-black bg-emerald-100 text-emerald-700 rounded-full">✓ Doğru Çözüldü</span>`
                : `<span class="px-2.5 py-0.5 text-xs font-black bg-rose-100 text-rose-700 rounded-full">✗ Yanlış (Hata Defterine Eklendi)</span>`
            ) : ''}
          </div>
          <span class="text-xs text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-md uppercase font-extrabold tracking-wider border border-indigo-100">${q.university_id}</span>
        </div>

        ${q.passage ? `
          <div class="p-4 bg-slate-50 rounded-xl text-xs text-slate-600 leading-relaxed mb-4 border border-slate-100 font-serif">
            ${q.passage}
          </div>
        ` : ''}

        <p class="text-sm font-semibold text-slate-800 mb-4 whitespace-pre-line">${q.question}</p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-4">
          ${q.options.map(opt => {
            let btnClass = "bg-slate-50 hover:bg-blue-50/80 border-slate-200 hover:border-blue-300 text-slate-700";
            let badgeHtml = "";
            if (isAnswered) {
              if (opt.key === q.correct_answer) {
                btnClass = "bg-emerald-50 border-emerald-400 text-emerald-900 font-bold ring-1 ring-emerald-400";
                badgeHtml = `<span class="ml-auto text-[11px] font-black text-emerald-700">✓ Doğru</span>`;
              } else if (opt.key === chosen) {
                btnClass = "bg-rose-50 border-rose-400 text-rose-900 font-bold ring-1 ring-rose-400";
                badgeHtml = `<span class="ml-auto text-[11px] font-black text-rose-700">✗ Seçiminiz</span>`;
              } else {
                btnClass = "bg-slate-50/60 border-slate-200 text-slate-400 opacity-75";
              }
            }
            return `
              <button type="button" onclick="selectPracticeOption('${q.id}', '${opt.key}')" class="p-3 text-xs border rounded-xl flex items-center gap-2.5 text-left transition cursor-pointer ${btnClass}">
                <span class="w-6 h-6 shrink-0 rounded-lg ${isAnswered && opt.key === q.correct_answer ? 'bg-emerald-600 text-white' : (isAnswered && opt.key === chosen ? 'bg-rose-600 text-white' : 'bg-white border border-slate-200 text-slate-700')} font-extrabold flex items-center justify-center text-[11px]">${opt.key}</span>
                <span class="flex-1">${opt.text}</span>
                ${badgeHtml}
              </button>
            `;
          }).join('')}
        </div>

        <details class="text-xs group" ${isAnswered ? 'open' : ''}>
          <summary class="cursor-pointer font-bold text-blue-600 hover:text-blue-700 list-none flex items-center gap-1">
            <i data-lucide="help-circle" class="w-3.5 h-3.5"></i> Doğru Cevap ve Çözümü Gör
          </summary>
          <div class="mt-3 p-3.5 bg-emerald-50 rounded-xl border border-emerald-200 text-slate-700 leading-relaxed">
            <strong class="text-emerald-800 block mb-1">Doğru Cevap: ${q.correct_answer}</strong>
            ${q.explanation_tr}
          </div>
        </details>
      </div>
    `;
  }).join('');

  if (window.lucide) window.lucide.createIcons();
}

async function loadPracticeQuestions() {
  const container = document.getElementById("practice-questions-list");
  if (!container) return;

  const lvl = window.appState.currentLevel || "B2";
  const uniObj = window.appState.currentUniversity || { id: "itu", short_name: "İTÜ", name: "İstanbul Teknik Üniversitesi" };
  const uni = uniObj.id || "itu";
  const shortName = uniObj.short_name || uni.toUpperCase();

  try {
    let url = `/api/questions`;
    const params = new URLSearchParams();
    if (practiceState.levelScope === "current") {
      params.set("level", lvl);
    }
    if (practiceState.pool === "school_only" && uni !== "general") {
      params.set("university_id", uni);
      params.set("strict_uni", "true");
    } else if (practiceState.pool === "school_plus_general" && uni !== "general") {
      params.set("university_id", uni);
    }

    let res = await fetch(`${url}?${params.toString()}`);
    if (res.status === 403) {
      // Kilitli üniversite ise açık olan genel havuz sorularına düş
      const fallbackParams = new URLSearchParams();
      if (practiceState.levelScope === "current") fallbackParams.set("level", lvl);
      res = await fetch(`/api/questions?${fallbackParams.toString()}`);
    }
    const poolFiltered = await res.json();

    for (const q of poolFiltered) {
      practiceState.questionsById[q.id] = q;
    }

    // Kategori sayılarını hesapla
    const catCounts = { all: poolFiltered.length };
    for (const q of poolFiltered) {
      catCounts[q.category] = (catCounts[q.category] || 0) + 1;
    }

    const categories = [
      { key: "all", label: "Tümü" },
      { key: "Grammar", label: "Grammar" },
      { key: "Vocabulary", label: "Vocabulary" },
      { key: "Reading", label: "Reading" },
      { key: "Restatement", label: "Restatement" },
      { key: "Cloze Test", label: "Cloze Test" },
      { key: "Sentence Completion", label: "Sentence Comp." },
      { key: "Paragraph Completion", label: "Paragraph Comp." },
      { key: "Dialogue", label: "Dialogue" }
    ];

    const catBar = document.getElementById("practice-category-bar");
    if (catBar) {
      catBar.innerHTML = `
        <div class="flex flex-wrap items-center gap-1.5">
          ${categories.map(c => {
            const count = catCounts[c.key] || 0;
            if (c.key !== "all" && count === 0) return "";
            const active = practiceState.category === c.key;
            return `
              <button type="button" onclick="setPracticeCategory('${c.key}')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${active ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'}">
                <span>${c.label}</span>
                <span class="text-[10px] px-1.5 py-0.2 rounded-full ${active ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-500'} font-extrabold">${count}</span>
              </button>
            `;
          }).join("")}
        </div>

        <div class="flex flex-wrap items-center gap-1.5">
          <div class="flex items-center gap-1 bg-white p-1 rounded-xl border border-slate-200 text-[11px] font-bold">
            <button type="button" onclick="setPracticePool('school_only'); setPracticeLevelScope('current');" class="px-2.5 py-1 rounded-lg transition ${practiceState.pool === 'school_only' && practiceState.levelScope === 'current' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'}">
              Sadece ${shortName} (${lvl} • 30 Soru)
            </button>
            <button type="button" onclick="setPracticePool('school_only'); setPracticeLevelScope('all_levels');" class="px-2.5 py-1 rounded-lg transition ${practiceState.pool === 'school_only' && practiceState.levelScope === 'all_levels' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'}">
              ${shortName} Tüm Kurlar (180 Soru)
            </button>
            <button type="button" onclick="setPracticePool('school_plus_general'); setPracticeLevelScope('current');" class="px-2.5 py-1 rounded-lg transition ${practiceState.pool === 'school_plus_general' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'}">
              ${shortName} + Genel Havuz
            </button>
          </div>
        </div>
      `;
    }

    const finalFiltered = practiceState.category === "all"
      ? poolFiltered
      : poolFiltered.filter(q => q.category === practiceState.category);

    window._lastPracticeFiltered = finalFiltered;
    updatePracticeScoreUI();
    renderPracticeQuestionList(finalFiltered);
  } catch (err) {
    console.error("Practice load error:", err);
  }
}

window.selectPracticeOption = selectPracticeOption;
window.setPracticeCategory = setPracticeCategory;
window.setPracticePool = setPracticePool;
window.setPracticeLevelScope = setPracticeLevelScope;
window.resetPracticeSession = resetPracticeSession;

async function loadWritingGuides(targetLevel = null) {
  const container = document.getElementById("writing-guides-container");
  const filterBar = document.getElementById("writing-filter-bar");
  if (!container) return;

  const currentLevel = window.appState?.currentLevel || 'B2';
  const activeLevel = targetLevel !== null ? targetLevel : currentLevel;

  // Render Writing Level Filter Bar
  if (filterBar) {
    const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
    filterBar.innerHTML = `
      <span class="text-xs font-bold text-slate-500 mr-2 flex items-center gap-1">
        <i data-lucide="filter" class="w-3.5 h-3.5"></i> Essay & Yazma Kuru:
      </span>
      ${levels.map(lvl => {
        const isSelected = activeLevel === lvl;
        return `
          <button onclick="loadWritingGuides('${lvl}')" class="px-3 py-1 rounded-xl text-xs font-bold transition ${isSelected ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-200 border border-slate-200'}">
            ${lvl} ${lvl === currentLevel ? '★' : ''}
          </button>
        `;
      }).join('')}
      <button onclick="loadWritingGuides('all')" class="px-3 py-1 rounded-xl text-xs font-bold transition ${activeLevel === 'all' ? 'bg-slate-800 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-200 border border-slate-200'}">
        Tüm Kurlar
      </button>
    `;
  }

  try {
    const url = activeLevel && activeLevel !== 'all' ? `/api/writing-guides?level=${activeLevel}` : '/api/writing-guides';
    const res = await fetch(url);
    const guides = await res.json();

    if (!guides || guides.length === 0) {
      container.innerHTML = `
        <div class="p-8 text-center bg-white rounded-3xl border border-slate-200">
          <p class="text-sm font-bold text-slate-700 mb-2">${activeLevel} seviyesinde yazma rehberi bulunamadı.</p>
          <button onclick="loadWritingGuides('all')" class="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-xl hover:bg-blue-700 transition">
            Tüm Rehberleri Görüntüle
          </button>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    container.innerHTML = guides.map(g => `
      <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-6">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2.5 py-0.5 bg-blue-100 text-blue-800 rounded-md text-xs font-black">
                ${g.level || 'B2'}
              </span>
              <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">
                Akademik Kompozisyon Formatı
              </span>
            </div>
            <h3 class="text-xl font-extrabold text-slate-800 mb-1">${g.title}</h3>
            <p class="text-xs text-slate-500 leading-relaxed">${g.description}</p>
          </div>
          ${g.model_band_score ? `
            <span class="px-3.5 py-1.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-xl text-xs font-black shrink-0">
              Model Band: ${g.model_band_score} / 100
            </span>
          ` : ''}
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
          ${g.band_score_tip ? `<p class="mt-2 text-amber-800 font-semibold">💡 İpucu: ${g.band_score_tip}</p>` : ''}
        </div>

        <!-- MODEL ESSAY & EXEMPLAR ACCORDION -->
        ${g.model_essay ? `
          <div class="pt-2 border-t border-slate-100">
            <details class="group bg-slate-50 rounded-2xl border border-slate-200 p-4 transition">
              <summary class="flex items-center justify-between cursor-pointer font-bold text-xs text-slate-800 select-none">
                <span class="flex items-center gap-2 text-blue-900">
                  <i data-lucide="book-open" class="w-4 h-4 text-blue-600"></i>
                  Band ${g.model_band_score || 90}+ Örnek Model Essay & Hata Analizini İncele
                </span>
                <span class="text-xs text-blue-600 group-open:rotate-180 transition-transform">▼</span>
              </summary>

              <div class="mt-4 pt-4 border-t border-slate-200 space-y-4">
                <div class="p-4 bg-white rounded-xl border border-slate-200 text-xs text-slate-800 font-serif leading-relaxed whitespace-pre-line">
                  ${g.model_essay}
                </div>

                ${g.annotated_strengths && g.annotated_strengths.length > 0 ? `
                  <div class="p-3.5 bg-emerald-50 rounded-xl border border-emerald-200 text-xs text-emerald-900 space-y-1">
                    <strong class="text-emerald-800 block mb-1">✓ Neden Yüksek Puan Aldı? (Güçlü Yönler):</strong>
                    ${g.annotated_strengths.map(s => `<div>• ${s}</div>`).join('')}
                  </div>
                ` : ''}

                ${g.common_pitfalls && g.common_pitfalls.length > 0 ? `
                  <div class="p-3.5 bg-rose-50 rounded-xl border border-rose-200 text-xs text-rose-900 space-y-1">
                    <strong class="text-rose-800 block mb-1">⚠ Sık Yapılan Hatalar (Puan Kırdıran Noktalar):</strong>
                    ${g.common_pitfalls.map(p => `<div>• ${p}</div>`).join('')}
                  </div>
                ` : ''}
              </div>
            </details>
          </div>
        ` : ''}
      </div>
    `).join('');
    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    console.error("Writing guides error:", err);
  }
}

function renderExamsTab(targetLevel = null) {
  const container = document.getElementById("exams-cards-container");
  const badgeEl = document.getElementById("exams-active-level-badge");
  if (!container) return;

  const lvl = (targetLevel || window.appState.currentLevel || "B2").toUpperCase();
  const u = window.appState.currentUniversity || {
    id: "itu",
    name: "İstanbul Teknik Üniversitesi",
    short_name: "İTÜ",
    exam_name: "İTÜ Proficiency",
    passing_score: 60,
    duration_minutes: 150,
    sections: []
  };

  if (badgeEl) badgeEl.innerText = `${u.short_name || u.id.toUpperCase()} • ${lvl} Kuru`;

  const sectionBadgesHtml = (u.sections || []).map(sec => `
    <span class="px-2.5 py-1 bg-white/10 border border-white/15 rounded-xl text-[11px] font-bold text-slate-100">
      ${sec.title} (%${sec.weight})
    </span>
  `).join('');

  container.innerHTML = `
    <!-- Seçili Üniversite Özel Paket Özeti Banner -->
    <div class="col-span-full p-6 rounded-3xl bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-lg border border-blue-500/20 space-y-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <div class="flex items-center gap-2 mb-1.5 flex-wrap">
            <span class="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 rounded-full text-[11px] font-black uppercase">
              ${u.short_name} Özel Sınav Havuzu
            </span>
            <span class="px-2.5 py-0.5 bg-blue-500/20 text-blue-200 border border-blue-400/30 rounded-full text-[11px] font-bold">
              Geçme Barajı: %${u.passing_score || 60} • Süre: ${u.duration_minutes || 120} dk
            </span>
          </div>
          <h3 class="text-lg sm:text-xl font-black text-white">${u.name} — ${u.exam_name} Paketi</h3>
          <p class="text-xs text-slate-300 mt-1">${u.description || `${u.name} hazırlık muafiyet sınav formatına birebir uyumlu özgün soru ve deneme paketi.`}</p>
        </div>

        <div class="grid grid-cols-3 gap-2 shrink-0 text-center">
          <div class="p-2.5 bg-white/10 rounded-2xl border border-white/10">
            <div class="text-base font-black text-emerald-400">180</div>
            <div class="text-[10px] text-slate-300 font-bold">Özgün Soru</div>
          </div>
          <div class="p-2.5 bg-white/10 rounded-2xl border border-white/10">
            <div class="text-base font-black text-blue-300">24</div>
            <div class="text-[10px] text-slate-300 font-bold">Listening Ders</div>
          </div>
          <div class="p-2.5 bg-white/10 rounded-2xl border border-white/10">
            <div class="text-base font-black text-purple-300">24</div>
            <div class="text-[10px] text-slate-300 font-bold">Speaking Görev</div>
          </div>
        </div>
      </div>

      ${sectionBadgesHtml ? `
        <div class="pt-3 border-t border-white/10 flex items-center gap-2 flex-wrap">
          <span class="text-[11px] font-bold text-slate-400">Resmi Sınav Bölümleri:</span>
          ${sectionBadgesHtml}
        </div>
      ` : ''}
    </div>

    <!-- 1. Tam Muafiyet / Kur Sınavı (${lvl} • 30 Soru) -->
    <div class="p-5 rounded-2xl border-2 border-blue-600 bg-blue-50/20 flex flex-col justify-between shadow-sm">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 bg-blue-600 text-white text-[11px] font-bold rounded-lg uppercase">${u.short_name} Tam Kur Sınavı</span>
          <span class="px-2.5 py-0.5 bg-blue-100 text-blue-800 text-xs font-black rounded-lg">${lvl} • 30 Soru</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">${u.short_name} (${u.exam_name}) • ${lvl} Kur & Muafiyet Sınavı (30 Soru)</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          Tamamı ${u.name} ${lvl} kuru özel havuzundan seçilen <strong>30 özgün soru</strong>, ${u.short_name} akademik dinleme dersi ve konuşma/yazma simülasyonu.
        </p>
      </div>
      <button onclick="startFullMockExam('${u.id}', '${lvl}')" class="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow transition flex items-center justify-center gap-1.5">
        <i data-lucide="play" class="w-3.5 h-3.5"></i> ${u.short_name} ${lvl} 30 Soruluk Sınavı Başlat
      </button>
    </div>

    <!-- 2. Okulun Tüm 180 Özgün Sorusunu Kapsayan Büyük Maraton -->
    <div class="p-5 rounded-2xl border-2 border-indigo-600 bg-indigo-50/20 flex flex-col justify-between shadow-sm">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 bg-indigo-600 text-white text-[11px] font-bold rounded-lg uppercase">Tam Paket Maratonu</span>
          <span class="px-2.5 py-0.5 bg-indigo-100 text-indigo-800 text-xs font-black rounded-lg">180 Özgün Soru</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">${u.short_name} Özel Soru Bankası Tam Maraton (A1–C2)</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          ${u.name} için özel hazırlanmış 180 özgün sorunun tamamını (her kurda 30 soru: Grammar, Vocab, Reading, Restatement, Cloze, Sentence Comp.) çözün.
        </p>
      </div>
      <button onclick="startExamSimulation('${u.id}', 'all', 'all', true)" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow transition flex items-center justify-center gap-1.5">
        <i data-lucide="award" class="w-3.5 h-3.5"></i> ${u.short_name} 180 Soruluk Tam Maratonu Başlat
      </button>
    </div>

    <!-- 3. Seçili Kur (${lvl}) 30 Soruluk Kur Bitirme Sınavı -->
    <div class="p-5 rounded-2xl border border-slate-200 bg-white hover:border-blue-300 transition flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 bg-emerald-100 text-emerald-800 text-[11px] font-bold rounded-lg uppercase">${u.short_name} • ${lvl} Kuru</span>
          <span class="text-xs text-slate-500 font-semibold">30 Özgün Soru</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">${u.short_name} ${lvl} Kur Bitirme Sınavı (30 Soru)</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          Sadece ${u.name} ${lvl} kuru için hazırlanmış 30 özgün soruyu (5 Grammar, 5 Vocab, 5 Reading, 5 Restatement, 5 Cloze, 5 Sentence Comp.) içerir.
        </p>
      </div>
      <button onclick="startExamSimulation('${u.id}', '${lvl}', 'all', true)" class="w-full py-2.5 bg-slate-100 hover:bg-emerald-600 hover:text-white text-slate-800 font-bold text-xs rounded-xl transition">
        ${u.short_name} ${lvl} Kur Sınavını Çöz (30 Soru)
      </button>
    </div>

    <!-- 4. Reading & Makale Analizi Modülü (30 Soru) -->
    <div class="p-5 rounded-2xl border border-slate-200 bg-white hover:border-blue-300 transition flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 bg-amber-100 text-amber-800 text-[11px] font-bold rounded-lg uppercase">${u.short_name} • Reading</span>
          <span class="text-xs text-slate-500 font-semibold">30 Özgün Soru</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">${u.short_name} Akademik Reading Sınavı (30 Soru)</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          ${u.name} (${u.exam_name}) akademik araştırma bültenleri ve makale parçaları üzerinden 30 özgün okuma-anlama sorusu.
        </p>
      </div>
      <button onclick="startExamSimulation('${u.id}', 'all', 'Reading', true)" class="w-full py-2.5 bg-slate-100 hover:bg-amber-600 hover:text-white text-slate-800 font-bold text-xs rounded-xl transition">
        ${u.short_name} 30 Reading Sorusunu Çöz
      </button>
    </div>

    <!-- 5. Restatement (Yakın Anlam) Sınavı (30 Soru) -->
    <div class="p-5 rounded-2xl border border-slate-200 bg-white hover:border-blue-300 transition flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 bg-purple-100 text-purple-800 text-[11px] font-bold rounded-lg uppercase">${u.short_name} • Restatement</span>
          <span class="text-xs text-slate-500 font-semibold">30 Özgün Soru</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">${u.short_name} Restatement Sınavı (30 Soru)</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          ${u.exam_name} sınavında en çok puan getiren 30 özgün paraphrase ve cümle yeniden ifade etme sorusu.
        </p>
      </div>
      <button onclick="startExamSimulation('${u.id}', 'all', 'Restatement', true)" class="w-full py-2.5 bg-slate-100 hover:bg-purple-600 hover:text-white text-slate-800 font-bold text-xs rounded-xl transition">
        ${u.short_name} 30 Restatement Sorusunu Çöz
      </button>
    </div>

    <!-- 6. Use of English (Grammar) Sınavı (30 Soru) -->
    <div class="p-5 rounded-2xl border border-slate-200 bg-white hover:border-blue-300 transition flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 bg-rose-100 text-rose-800 text-[11px] font-bold rounded-lg uppercase">${u.short_name} • Grammar</span>
          <span class="text-xs text-slate-500 font-semibold">30 Özgün Soru</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">${u.short_name} Akademik Grammar Sınavı (30 Soru)</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          ${u.name} hazırlık müfredatına özel 30 özgün akademik dilbilgisi ve yapı sorusu.
        </p>
      </div>
      <button onclick="startExamSimulation('${u.id}', 'all', 'Grammar', true)" class="w-full py-2.5 bg-slate-100 hover:bg-rose-600 hover:text-white text-slate-800 font-bold text-xs rounded-xl transition">
        ${u.short_name} 30 Grammar Sorusunu Çöz
      </button>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
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

  const user = window.appState.currentUser;
  const verifiedUni = user?.verified_university || null;  // yalnızca belgeyle doğrulanan okul ücretsiz
  const unlocked = user?.unlocked_universities || ['general'];

  list.innerHTML = window.appState.allUniversities.map(u => {
    const isCurrent = u.id === window.appState.currentUniversity.id;
    const isFreeOrUnlocked = u.id === 'general' || u.id === verifiedUni || unlocked.includes(u.id);

    return `
      <div onclick="selectUniversity('${u.id}')" class="p-4 rounded-2xl border-2 cursor-pointer transition flex items-center justify-between ${isCurrent ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-900/20' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-800'}">
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <h4 class="font-bold text-slate-800 dark:text-white text-sm">${u.name}</h4>
            <span class="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-bold rounded-md">${u.short_name}</span>
            ${u.id === verifiedUni ? '<span class="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-[10px] font-extrabold rounded-md">Öğrenci Okulunuz (Ücretsiz)</span>' : ''}
            ${!isFreeOrUnlocked ? '<span class="px-2 py-0.5 bg-amber-100 text-amber-800 text-[10px] font-extrabold rounded-md flex items-center gap-1">🔒 50 TL Üyelik</span>' : ''}
          </div>
          <p class="text-xs text-slate-500 mt-1">${u.exam_name} • Geçme Barajı: %${u.passing_score}</p>
        </div>
        <div class="flex items-center gap-2">
          ${!isFreeOrUnlocked ? '<span class="text-xs font-black text-amber-600">50 TL</span>' : ''}
          <div class="w-6 h-6 rounded-full flex items-center justify-center ${isCurrent ? 'bg-blue-600 text-white' : 'border border-slate-300 text-transparent'}">
            ✓
          </div>
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

  const user = window.appState.currentUser;
  const verifiedUni = user?.verified_university || null;
  const unlocked = user?.unlocked_universities || ['general'];
  const hasAccess = uniId === 'general' || uniId === verifiedUni || unlocked.includes(uniId);

  if (!hasAccess) {
    closeUniversityModal();
    if (window.openUniversityPaywallModal) {
      window.openUniversityPaywallModal(uniId, () => {
        selectUniversity(uniId);
      });
    }
    return;
  }

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
  } else if (window.appState.activeTab === 'exams') {
    renderExamsTab();
  } else if (window.appState.activeTab === 'listening' && window.loadListeningHub) {
    window.loadListeningHub('all');
  } else if (window.appState.activeTab === 'speaking' && window.loadSpeakingHub) {
    window.loadSpeakingHub('all');
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

// --- Cloud Sync & Student Verification Module ---
async function syncCloudData() {
  const syncIcon = document.getElementById("sync-icon");
  if (syncIcon) syncIcon.classList.add("animate-spin");

  try {
    const res = await fetch('/api/sync/pull');
    if (!res.ok) throw new Error("sync " + res.status);
    await reloadUserData();

    showNotification("✓ Telefonla eşitlendi. Tüm verileriniz güncel!", "emerald");
  } catch (err) {
    console.error("Cloud sync error:", err);
    showNotification("Senkronizasyon sırasında hata oluştu.", "rose");
  } finally {
    if (syncIcon) syncIcon.classList.remove("animate-spin");
  }
}

function showNotification(msg, color) {
  const toast = document.createElement("div");
  toast.className = `fixed bottom-6 right-6 z-50 px-5 py-3 ${color === 'emerald' ? 'bg-emerald-600' : 'bg-rose-600'} text-white font-bold text-xs rounded-2xl shadow-xl transition`;
  toast.innerText = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function openStudentVerifyModal() {
  const modal = document.getElementById("student-verify-modal");
  if (modal) modal.classList.remove("hidden");
}

function closeStudentVerifyModal() {
  const modal = document.getElementById("student-verify-modal");
  if (modal) modal.classList.add("hidden");
}

let otpTimerInterval = null;
let currentOtpEmail = "";

async function requestStudentOtp() {
  const emailInput = document.getElementById("verify-edu-email");
  const numberInput = document.getElementById("verify-student-number");
  const statusMsg = document.getElementById("verify-status-msg");
  const email = emailInput ? emailInput.value.trim() : "";
  const studentNumber = numberInput ? numberInput.value.trim() : "";

  if (!email || !email.includes("@")) {
    if (statusMsg) {
      statusMsg.className = "p-3 rounded-xl text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 block";
      statusMsg.innerText = "Lütfen geçerli bir üniversite e-posta adresi (.edu.tr) girin.";
    }
    return;
  }

  currentOtpEmail = email;

  try {
    const res = await fetch('/api/student/request-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, student_number: studentNumber })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Kod gönderilemedi.");
    }

    document.getElementById("verify-step-input")?.classList.add("hidden");
    document.getElementById("verify-step-otp")?.classList.remove("hidden");
    const sentLabel = document.getElementById("otp-sent-email-label");
    if (sentLabel) sentLabel.innerText = `${email} adresine gönderilen 6 haneli kodu girin.`;

    const otpInput = document.getElementById("verify-otp-code");
    if (otpInput) {
      otpInput.value = "";
      otpInput.focus();
    }

    startOtpCountdown(60);
    showNotification("✓ 6 haneli doğrulama kodu gönderildi!", "emerald");
  } catch (err) {
    if (statusMsg) {
      statusMsg.className = "p-3 rounded-xl text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 block";
      statusMsg.innerText = err.message;
    }
  }
}

function startOtpCountdown(seconds) {
  if (otpTimerInterval) clearInterval(otpTimerInterval);
  let remaining = seconds;
  const display = document.getElementById("otp-timer-display");
  const resendBtn = document.getElementById("btn-resend-otp");
  if (resendBtn) resendBtn.disabled = true;

  if (display) display.innerText = `Kalan Süre: ${remaining}s`;

  otpTimerInterval = setInterval(() => {
    remaining--;
    if (display) display.innerText = `Kalan Süre: ${remaining}s`;
    if (remaining <= 0) {
      clearInterval(otpTimerInterval);
      if (display) display.innerText = "Süre doldu";
      if (resendBtn) resendBtn.disabled = false;
    }
  }, 1000);
}

function resendStudentOtp() {
  requestStudentOtp();
}

async function submitStudentOtp() {
  const otpInput = document.getElementById("verify-otp-code");
  const statusMsg = document.getElementById("verify-status-msg");
  const code = otpInput ? otpInput.value.trim() : "";

  if (!code || code.length !== 6) {
    if (statusMsg) {
      statusMsg.className = "p-3 rounded-xl text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 block";
      statusMsg.innerText = "Lütfen 6 haneli doğrulama kodunu eksiksiz girin.";
    }
    return;
  }

  try {
    const res = await fetch('/api/student/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: currentOtpEmail, otp_code: code })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Kod doğrulanamadı.");
    }

    if (otpTimerInterval) clearInterval(otpTimerInterval);

    if (statusMsg) {
      statusMsg.className = "p-3 rounded-xl text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 block";
      statusMsg.innerText = data.message || "Öğrenci hesabınız başarıyla doğrulandı!";
    }

    showNotification("✓ Öğrenci hesabı doğrulandı!", "emerald");

    setTimeout(() => {
      closeStudentVerifyModal();
      loadStudentStatus();
      document.getElementById("verify-step-input")?.classList.remove("hidden");
      document.getElementById("verify-step-otp")?.classList.add("hidden");
    }, 1500);
  } catch (err) {
    if (statusMsg) {
      statusMsg.className = "p-3 rounded-xl text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 block";
      statusMsg.innerText = err.message;
    }
  }
}

async function loadStudentStatus() {
  try {
    const res = await fetch('/api/student/status');
    const data = await res.json();
    const badgeText = document.getElementById("header-verification-text");
    const badgeEl = document.getElementById("header-verification-badge");

    if (badgeText && badgeEl) {
      if (data.is_verified_student) {
        badgeText.innerText = "Doğrulanmış Öğrenci";
        badgeEl.className = "hidden sm:flex items-center gap-1.5 px-3 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-bold transition";
      } else {
        badgeText.innerText = "Öğrenci Doğrula";
        badgeEl.className = "hidden sm:flex items-center gap-1.5 px-3 py-2 bg-amber-50 text-amber-700 border border-amber-200 rounded-xl text-xs font-bold transition";
      }
    }
  } catch (e) {
    console.warn("Student status load error:", e);
  }
}

async function openPrintableReportModal() {
  const modal = document.getElementById("printable-report-modal");
  const content = document.getElementById("printable-report-content");
  if (!modal || !content) return;

  content.innerHTML = `<div class="p-8 text-center text-slate-400">Akademik gelişim raporu ve karne hazırlanıyor...</div>`;
  modal.classList.remove("hidden");

  try {
    const res = await fetch('/api/report/summary');
    const data = await res.json();

    content.innerHTML = `
      <div class="print-card bg-white p-8 rounded-3xl border border-slate-200 shadow-xl space-y-6 max-w-2xl mx-auto">
        <!-- Rapor Başlığı -->
        <div class="flex items-center justify-between pb-4 border-b-2 border-slate-900">
          <div>
            <div class="flex items-center gap-2">
              <span class="font-extrabold text-xl text-blue-900">PrepMaster</span>
              <span class="text-xs uppercase font-bold px-2 py-0.5 bg-blue-50 text-blue-800 rounded">Akademik Karne</span>
            </div>
            <h2 class="text-base font-bold text-slate-700 mt-1">${data.target_university.name} Hazırlık Muafiyet Karnesi</h2>
          </div>
          <div class="text-right text-xs text-slate-400">
            <div>Tarih: ${data.generated_at}</div>
            <div class="font-bold text-slate-600">Öğrenci No: ${data.student_profile.student_number || '040220199'}</div>
          </div>
        </div>

        <!-- Özet Skorlar -->
        <div class="grid grid-cols-3 gap-4 text-center">
          <div class="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <span class="text-xs text-slate-400 font-bold block">Ortalama Skor</span>
            <span class="text-2xl font-black text-blue-900">%${data.average_score}</span>
            <span class="text-[10px] text-slate-500">Baraj: %${data.passing_score}</span>
          </div>
          <div class="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <span class="text-xs text-slate-400 font-bold block">Çözülen Sınavlar</span>
            <span class="text-2xl font-black text-slate-800">${data.total_exams_taken}</span>
            <span class="text-[10px] text-slate-500">Tamamlanan Deneme</span>
          </div>
          <div class="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <span class="text-xs text-slate-400 font-bold block">Öğrenilen AWL</span>
            <span class="text-2xl font-black text-indigo-700">${data.mastered_vocabulary_count} / ${data.total_vocabulary_count}</span>
            <span class="text-[10px] text-slate-500">Akademik Kelime</span>
          </div>
        </div>

        <!-- Muafiyet Hazırlık Durumu -->
        <div class="p-4 rounded-2xl border ${data.readiness_color === 'emerald' ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-amber-50 border-amber-200 text-amber-900'}">
          <div class="flex items-center gap-2 font-extrabold text-sm mb-1">
            <span>Muafiyet Durumu:</span>
            <span>${data.readiness_status}</span>
          </div>
          <p class="text-xs opacity-90 leading-relaxed">
            Hata defterinizde toplam ${data.unresolved_mistakes_count} çözülmemiş soru bulunmaktadır.
          </p>
        </div>

        <!-- Kategori Dağılımı -->
        <div>
          <h4 class="text-xs font-bold uppercase text-slate-400 tracking-wider mb-2">Hata Dağılımı & Zayıf Konular:</h4>
          <div class="flex flex-wrap gap-2">
            ${Object.keys(data.mistakes_by_category).length > 0 ? 
              Object.entries(data.mistakes_by_category).map(([cat, cnt]) => `
                <span class="px-3 py-1 bg-rose-50 text-rose-700 border border-rose-200 rounded-xl text-xs font-bold">
                  ${cat}: ${cnt} Yanlış
                </span>
              `).join('') : '<span class="text-xs text-emerald-600 font-bold">Harika! Hata havuzunuz temiz.</span>'}
          </div>
        </div>

        <!-- Aksiyon Butonları -->
        <div class="pt-4 border-t border-slate-100 flex items-center justify-between no-print">
          <button onclick="closePrintableReportModal()" class="px-4 py-2 text-slate-500 hover:bg-slate-100 rounded-xl text-xs font-bold">
            Kapat
          </button>
          <button onclick="window.print()" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow flex items-center gap-1.5">
            <i data-lucide="printer" class="w-4 h-4"></i> PDF Olarak Kaydet / Yazdır
          </button>
        </div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    console.error("Report load error:", err);
  }
}

function closePrintableReportModal() {
  const modal = document.getElementById("printable-report-modal");
  if (modal) modal.classList.add("hidden");
}

// --- DARK MODE (THEME) CONTROLLER ---
function initDarkMode() {
  const saved = localStorage.getItem("prepmaster_theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const isDark = saved === "dark" || (!saved && prefersDark);
  if (isDark) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
  updateThemeIcon(isDark);
}

function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle("dark");
  localStorage.setItem("prepmaster_theme", isDark ? "dark" : "light");
  updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
  const btn = document.getElementById("header-theme-btn");
  if (!btn) return;
  btn.innerHTML = `<i data-lucide="${isDark ? 'sun' : 'moon'}" class="w-4 h-4 ${isDark ? 'text-amber-400' : 'text-slate-700'}" id="theme-icon"></i>`;
  if (window.lucide) window.lucide.createIcons();
}

// --- USER AUTHENTICATION & SESSION MANAGEMENT ---
async function checkCurrentUser() {
  try {
    const stored = localStorage.getItem("auth_user");
    // Token'sız kayıtlı kullanıcı sunucu tarafından tanınmaz; yeniden giriş gerekir.
    if (stored && !localStorage.getItem("prepmaster_token")) {
      localStorage.removeItem("auth_user");
    } else if (stored) {
      const user = JSON.parse(stored);
      window.appState.currentUser = user;
      const nameEl = document.getElementById("header-user-name");
      if (nameEl) nameEl.innerText = (user.full_name || user.username || "Öğrenci").split(" ")[0];
      return user;
    }
    window.appState.currentUser = null;
    return null;
  } catch (e) {
    console.warn("checkCurrentUser error:", e);
    window.appState.currentUser = null;
    return null;
  }
}

function openAuthModal(isMandatory = false) {
  const modal = document.getElementById("auth-modal");
  if (!modal) return;
  const user = window.appState.currentUser;
  const loggedInView = document.getElementById("auth-logged-in-view");
  const formsView = document.getElementById("auth-forms-view");
  const closeBtn = document.getElementById("btn-close-auth-modal") || modal.querySelector('button[onclick="closeAuthModal()"]');
  const brandHeader = document.getElementById("auth-gate-brand-header");

  if (isMandatory || !user) {
    modal.setAttribute("data-mandatory", "true");
    setAppShellVisible(false);
    modal.className = "fixed inset-0 z-50 bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 p-4 overflow-y-auto flex flex-col items-center justify-center";
    if (closeBtn) closeBtn.classList.add("hidden");
    if (brandHeader) brandHeader.classList.remove("hidden");
  } else {
    modal.removeAttribute("data-mandatory");
    modal.className = "fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto flex flex-col items-center justify-center";
    if (closeBtn) closeBtn.classList.remove("hidden");
    if (brandHeader) brandHeader.classList.add("hidden");
  }

  if (user && user.id) {
    if (loggedInView) loggedInView.classList.remove("hidden");
    if (formsView) formsView.classList.add("hidden");
    const titleEl = document.getElementById("auth-modal-title");
    if (titleEl) titleEl.innerText = "Öğrenci Profili";

    const fName = document.getElementById("profile-full-name");
    const uName = document.getElementById("profile-username");
    const email = document.getElementById("profile-email");
    const uniName = document.getElementById("profile-uni-name");
    const sNum = document.getElementById("profile-student-number");
    const verifEl = document.getElementById("profile-verification-status");

    if (fName) fName.innerText = user.full_name || "-";
    if (uName) uName.innerText = user.username || "-";
    if (email) email.innerText = user.email || "-";
    if (uniName) uniName.innerText = user.university ? user.university.name : (user.university_id ? user.university_id.toUpperCase() : "-");
    if (sNum) sNum.innerText = user.student_number || "-";

    const isVerified = user.is_verified_student === 1 || user.verification_status === "verified";
    if (verifEl) {
      verifEl.innerText = isVerified ? "✓ Doğrulanmış Öğrenci" : "⚠️ Doğrulanmadı";
      verifEl.className = isVerified ? "text-xs font-extrabold text-emerald-600" : "text-xs font-bold text-amber-600";
    }
  } else {
    if (loggedInView) loggedInView.classList.add("hidden");
    if (formsView) formsView.classList.remove("hidden");
    const titleEl = document.getElementById("auth-modal-title");
    if (titleEl) titleEl.innerText = "Öğrenci Giriş Kapısı";
    switchAuthTab("login");
  }

  modal.classList.remove("hidden");
  if (window.lucide) window.lucide.createIcons();
}

function closeAuthModal() {
  const modal = document.getElementById("auth-modal");
  if (!modal) return;
  if (modal.getAttribute("data-mandatory") === "true" && !window.appState.currentUser) {
    showNotification("Lütfen devam etmek için giriş yapın veya kayıt olun.", "amber");
    return;
  }
  modal.classList.add("hidden");
}

function switchAuthTab(tab) {
  const btnLogin = document.getElementById("tab-btn-login");
  const btnReg = document.getElementById("tab-btn-register");
  const formLogin = document.getElementById("form-login");
  const formReg = document.getElementById("form-register");

  if (tab === "login") {
    if (formLogin) formLogin.classList.remove("hidden");
    if (formReg) formReg.classList.add("hidden");
    if (btnLogin) {
      btnLogin.className = "flex-1 py-2 rounded-xl bg-white dark:bg-slate-700 text-blue-700 dark:text-blue-400 shadow-sm transition font-bold";
    }
    if (btnReg) {
      btnReg.className = "flex-1 py-2 rounded-xl text-slate-500 hover:text-slate-800 transition font-bold";
    }
  } else {
    if (formLogin) formLogin.classList.add("hidden");
    if (formReg) formReg.classList.remove("hidden");
    if (btnLogin) {
      btnLogin.className = "flex-1 py-2 rounded-xl text-slate-500 hover:text-slate-800 transition font-bold";
    }
    if (btnReg) {
      btnReg.className = "flex-1 py-2 rounded-xl bg-white dark:bg-slate-700 text-blue-700 dark:text-blue-400 shadow-sm transition font-bold";
    }
  }
}

async function submitLogin() {
  const identInput = document.getElementById("login-identifier");
  const passInput = document.getElementById("login-password");
  const errEl = document.getElementById("login-error-msg");
  const identifier = identInput ? identInput.value.trim() : "";
  const password = passInput ? passInput.value.trim() : "";

  if (errEl) errEl.classList.add("hidden");

  if (!identifier || !password) {
    if (errEl) {
      errEl.innerText = "Lütfen kullanıcı adı/e-posta ve şifrenizi girin.";
      errEl.classList.remove("hidden");
    }
    return;
  }

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Giriş başarısız.");
    }

    window.appState.currentUser = data.user;
    localStorage.setItem("auth_user", JSON.stringify(data.user));
    if (data.token) localStorage.setItem("prepmaster_token", data.token);

    const nameEl = document.getElementById("header-user-name");
    if (nameEl) nameEl.innerText = (data.user.full_name || data.user.username).split(" ")[0];

    if (data.user.university) {
      window.appState.currentUniversity = data.user.university;
      renderUniversityHeader();
    }

    const modal = document.getElementById("auth-modal");
    if (modal) modal.removeAttribute("data-mandatory");
    closeAuthModal();

    const isVerified = data.user.verification_status === "verified" || data.user.is_verified_student === 1;
    if (!isVerified) {
      // Önce belge doğrulama ekranı tam ekran olarak açılır (arkada sistem gözükmez)
      setAppShellVisible(false);
      openDocScanModal(true);
      showNotification(`Hoş geldin, ${data.user.full_name}! Üniversiteni ücretsiz açmak için öğrenci belgeni doğrula.`, "blue");
    } else {
      setAppShellVisible(true);
      await reloadUserData();
      showNotification(`✓ Başarıyla giriş yapıldı. Hoş geldin, ${data.user.full_name}!`, "emerald");
    }
  } catch (err) {
    if (errEl) {
      errEl.innerText = err.message;
      errEl.classList.remove("hidden");
    }
  }
}

async function submitRegister() {
  const fullName = (document.getElementById("reg-fullname")?.value || "").trim();
  const username = (document.getElementById("reg-username")?.value || "").trim();
  const email = (document.getElementById("reg-email")?.value || "").trim();
  const universityId = document.getElementById("reg-university")?.value || "itu";
  const studentNumber = (document.getElementById("reg-student-num")?.value || "").trim();
  const password = (document.getElementById("reg-password")?.value || "").trim();
  const errEl = document.getElementById("register-error-msg");

  if (errEl) errEl.classList.add("hidden");

  if (!fullName || !username || !email || !password) {
    if (errEl) {
      errEl.innerText = "Lütfen zorunlu alanları (Ad Soyad, Kullanıcı Adı, E-Posta, Şifre) doldurun.";
      errEl.classList.remove("hidden");
    }
    return;
  }

  try {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: fullName,
        username: username,
        email: email,
        university_id: universityId,
        student_number: studentNumber,
        password: password
      })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Kayıt işlemi başarısız.");
    }

    window.appState.currentUser = data.user;
    localStorage.setItem("auth_user", JSON.stringify(data.user));
    if (data.token) localStorage.setItem("prepmaster_token", data.token);

    const nameEl = document.getElementById("header-user-name");
    if (nameEl) nameEl.innerText = (data.user.full_name || data.user.username).split(" ")[0];

    const modal = document.getElementById("auth-modal");
    if (modal) modal.removeAttribute("data-mandatory");
    closeAuthModal();

    // Kayıt sonrası doğrudan tam ekran Belge Doğrulama Merkezine geç (arkada sistem gözükmez)
    setAppShellVisible(false);
    openDocScanModal(true);
    showNotification(`✓ Hesabınız oluşturuldu! Şimdi öğrenci belgenizi doğrulayarak okulunuzu ücretsiz açın.`, "emerald");
  } catch (err) {
    if (errEl) {
      errEl.innerText = err.message;
      errEl.classList.remove("hidden");
    }
  }
}

function logoutUser() {
  window.appState.currentUser = null;
  localStorage.removeItem("auth_user");
  localStorage.removeItem("prepmaster_token");
  setAppShellVisible(false);
  window.location.reload();
}

window.setAppShellVisible = setAppShellVisible;
window.changeCurrentLevel = changeCurrentLevel;
window.switchTab = switchTab;
window.openUniversityModal = openUniversityModal;
window.closeUniversityModal = closeUniversityModal;
window.selectUniversity = selectUniversity;
window.loadDashboardStats = loadDashboardStats;
window.loadMistakeVault = loadMistakeVault;
window.resolveMistakeItem = resolveMistakeItem;
window.deleteMistakeItem = deleteMistakeItem;
window.syncCloudData = syncCloudData;
window.openStudentVerifyModal = openStudentVerifyModal;
window.closeStudentVerifyModal = closeStudentVerifyModal;
window.loadStudentStatus = loadStudentStatus;
window.openPrintableReportModal = openPrintableReportModal;
window.closePrintableReportModal = closePrintableReportModal;

// Dark mode and Auth exports
window.initDarkMode = initDarkMode;
window.toggleDarkMode = toggleDarkMode;
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.switchAuthTab = switchAuthTab;
window.submitLogin = submitLogin;
window.submitRegister = submitRegister;
window.logoutUser = logoutUser;
window.requestStudentOtp = requestStudentOtp;
window.resendStudentOtp = resendStudentOtp;
window.submitStudentOtp = submitStudentOtp;


// ================= ÖĞRENCİ BELGESİ TARAMA ALGORİTMASI & OTOMATİK EŞLEME =================
let selectedDocFile = null;
let cachedSampleDocs = null;

function initDocDropZone() {
  const dropZone = document.getElementById("doc-drop-zone");
  if (!dropZone || dropZone.dataset.bound === "true") return;
  dropZone.dataset.bound = "true";

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("border-blue-500", "bg-blue-50/60");
  });
  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("border-blue-500", "bg-blue-50/60");
  });
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("border-blue-500", "bg-blue-50/60");
    const file = e.dataTransfer?.files?.[0];
    if (file) {
      applySelectedDocFile(file);
    }
  });
}

function applySelectedDocFile(file) {
  selectedDocFile = file;
  const label = document.getElementById("doc-upload-label");
  const card = document.getElementById("doc-selected-file-card");
  const nameEl = document.getElementById("doc-selected-file-name");
  const metaEl = document.getElementById("doc-selected-file-meta");

  const sizeKb = Math.max(1, Math.round(file.size / 1024));
  if (label) {
    label.innerText = `Seçilen Belge: ${file.name} (${sizeKb} KB)`;
  }
  if (card) card.classList.remove("hidden");
  if (nameEl) nameEl.innerText = file.name;
  if (metaEl) metaEl.innerText = `${sizeKb} KB • YÖK / E-Devlet Belge Analizine Hazır`;
}

function openDocScanModal(isInitial = false) {
  const modal = document.getElementById("student-doc-scan-modal");
  if (!modal) return;

  const closeBtn = document.getElementById("btn-close-doc-scan");
  const skipFooter = document.getElementById("doc-scan-skip-footer");

  if (isInitial) {
    modal.setAttribute("data-initial-onboarding", "true");
    setAppShellVisible(false);
    modal.className = "fixed inset-0 z-50 bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 p-4 overflow-y-auto flex items-center justify-center";
    if (closeBtn) closeBtn.classList.add("hidden");
    if (skipFooter) skipFooter.classList.remove("hidden");
  } else {
    modal.removeAttribute("data-initial-onboarding");
    modal.className = "fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-sm p-4 overflow-y-auto flex items-center justify-center";
    if (closeBtn) closeBtn.classList.remove("hidden");
    if (skipFooter) skipFooter.classList.add("hidden");
  }

  modal.classList.remove("hidden");
  switchDocScanTab("upload");
  const msgEl = document.getElementById("doc-scan-result-msg");
  if (msgEl) msgEl.classList.add("hidden");
  initDocDropZone();
  if (window.lucide) window.lucide.createIcons();
}

function closeDocScanModal() {
  const modal = document.getElementById("student-doc-scan-modal");
  if (!modal) return;
  const wasInitial = modal.getAttribute("data-initial-onboarding") === "true";
  modal.removeAttribute("data-initial-onboarding");
  modal.classList.add("hidden");

  if (wasInitial && window.appState.currentUser) {
    setAppShellVisible(true);
    reloadUserData();
  }
}

function skipDocScanAndEnterPlatform() {
  const modal = document.getElementById("student-doc-scan-modal");
  if (modal) {
    modal.removeAttribute("data-initial-onboarding");
    modal.classList.add("hidden");
  }
  setAppShellVisible(true);
  reloadUserData();
  showNotification("Genel hazırlık havuzu açıldı. Öğrenci belgenizi istediğiniz zaman üst menüden doğrulayabilirsiniz.", "blue");
}

function enterPlatformAfterVerification() {
  const modal = document.getElementById("student-doc-scan-modal");
  if (modal) {
    modal.removeAttribute("data-initial-onboarding");
    modal.classList.add("hidden");
  }
  setAppShellVisible(true);
  reloadUserData();
}

function switchDocScanTab(tab) {
  const btnUp = document.getElementById("tab-btn-doc-upload");
  const btnTxt = document.getElementById("tab-btn-doc-text");
  const btnSmp = document.getElementById("tab-btn-doc-samples");

  const viewUp = document.getElementById("doc-scan-view-upload");
  const viewTxt = document.getElementById("doc-scan-view-text");
  const viewSmp = document.getElementById("doc-scan-view-samples");

  [viewUp, viewTxt, viewSmp].forEach(v => v?.classList.add("hidden"));
  const inactiveClass = "py-2 px-2 rounded-xl text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition flex items-center justify-center gap-1.5 font-bold";
  const activeClass = "py-2 px-2 rounded-xl bg-white dark:bg-slate-800 text-blue-700 dark:text-blue-400 shadow-sm transition flex items-center justify-center gap-1.5 font-bold";

  [btnUp, btnTxt, btnSmp].forEach(b => {
    if (b) b.className = inactiveClass;
  });

  if (tab === "upload") {
    viewUp?.classList.remove("hidden");
    if (btnUp) btnUp.className = activeClass;
  } else if (tab === "text") {
    viewTxt?.classList.remove("hidden");
    if (btnTxt) btnTxt.className = activeClass;
    const textInput = document.getElementById("doc-scan-text-input");
    if (textInput) analyzeDocTextLive(textInput.value);
  } else if (tab === "samples") {
    viewSmp?.classList.remove("hidden");
    if (btnSmp) btnSmp.className = activeClass;
  }
  if (window.lucide) window.lucide.createIcons();
}

function handleDocFileSelect(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  applySelectedDocFile(file);
}

function _setLiveBadge(id, label, passed) {
  const el = document.getElementById(id);
  if (!el) return;
  if (passed) {
    el.className = "px-2 py-1 rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold flex items-center gap-1";
    el.innerHTML = `<span>✓</span> <span>${label}</span>`;
  } else {
    el.className = "px-2 py-1 rounded-lg bg-slate-200/70 text-slate-500 font-semibold flex items-center gap-1";
    el.innerHTML = `<span>○</span> <span>${label}</span>`;
  }
}

function analyzeDocTextLive(rawText) {
  const t = (rawText || "")
    .replace(/İ/g, "i")
    .replace(/I/g, "ı")
    .replace(/Ğ/g, "ğ")
    .replace(/Ü/g, "ü")
    .replace(/Ş/g, "ş")
    .replace(/Ö/g, "ö")
    .replace(/Ç/g, "ç")
    .toLowerCase();

  const uniKeywords = [
    "istanbul teknik", "itü", "boğaziçi", "bogazici", "orta doğu teknik", "odtü",
    "bilkent", "yıldız teknik", "hacettepe", "ankara üniversitesi", "gazi üniversitesi",
    "ege üniversitesi", "koç üniversitesi", "sabancı üniversitesi",
    "marmara üniversitesi", "istanbul üniversitesi", "cerrahpaşa", "dokuz eylül",
    "izmir yüksek teknoloji", "iyte", "anadolu üniversitesi", "eskişehir teknik",
    "gebze teknik", "akdeniz üniversitesi", "çukurova üniversitesi", "uludağ üniversitesi",
    "özyeğin üniversitesi", "bahçeşehir üniversitesi", "yeditepe üniversitesi",
    "tobb ekonomi", "tobb etü"
  ];
  const hasUni = uniKeywords.some(k => t.includes(k));
  const hasBarcode = /(?:yök|yok|tr|edevlet|belge)[\-][a-z0-9\-]{5,24}|barkod\s*(?:no|kodu|numarası)?\s*[:\-]?\s*[a-z0-9\-]{6,25}/i.test(t);
  const hasStuNo = /\b[0-9]{7,11}\b/.test(t) || /öğrenci\s*(?:numarası|no)\s*[:\-]?\s*[0-9]{6,12}/i.test(t);
  const hasOfficial = ["yükseköğretim", "e-devlet", "öğrenci belgesi", "rektörlüğü", "aktif öğrenci", "yabancı diller"].some(k => t.includes(k));

  _setLiveBadge("live-check-uni", "Üniversite", hasUni);
  _setLiveBadge("live-check-barcode", "YÖK Barkod", hasBarcode);
  _setLiveBadge("live-check-stuno", "Öğrenci No", hasStuNo);
  _setLiveBadge("live-check-official", "Resmi Başlık", hasOfficial);
}

async function _fetchSampleDocText(sampleKey) {
  try {
    if (!cachedSampleDocs) {
      const res = await fetch("/api/student/sample-documents");
      if (res.ok) {
        cachedSampleDocs = await res.json();
      }
    }
    if (cachedSampleDocs && cachedSampleDocs[sampleKey]?.content) {
      return cachedSampleDocs[sampleKey].content;
    }
  } catch (e) {
    console.warn("Sample doc fetch warning:", e);
  }
  return `T.C. YÜKSEKÖĞRETİM KURULU BAŞKANLIĞI\nE-DEVLET KAPISI ÖĞRENCİ BELGESİ\nBarkod: YÖK-${sampleKey.toUpperCase()}98451203\nÜniversite: İSTANBUL TEKNİK ÜNİVERSİTESİ\nÖğrenci Numarası: 150240789\nÖğrencilik Durumu: Aktif Öğrenci`;
}

async function fillSampleTextForCurrentUni() {
  const uniId = window.appState.currentUser?.university_id || window.appState.currentUniversity?.id || "itu";
  const key = (uniId && uniId !== "general") ? uniId : "itu";
  const sampleText = await _fetchSampleDocText(key);
  const textInput = document.getElementById("doc-scan-text-input");
  if (textInput) {
    textInput.value = sampleText;
    analyzeDocTextLive(sampleText);
  }
}

async function submitDocFileUpload() {
  if (!selectedDocFile) {
    showNotification("Lütfen önce taranacak bir PDF veya belge dosyası seçin.", "amber");
    return;
  }

  const loadingEl = document.getElementById("doc-scan-loading");
  const msgEl = document.getElementById("doc-scan-result-msg");
  if (loadingEl) loadingEl.classList.remove("hidden");
  if (msgEl) msgEl.classList.add("hidden");

  const formData = new FormData();
  formData.append("file", selectedDocFile);
  const userId = window.appState.currentUser?.id || 1;
  formData.append("user_id", userId);

  try {
    const res = await fetch("/api/student/upload-document", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (loadingEl) loadingEl.classList.add("hidden");

    if (!res.ok) {
      throw new Error(data.detail || "Belge taranamadı.");
    }

    handleScanSuccess(data);
  } catch (err) {
    if (loadingEl) loadingEl.classList.add("hidden");
    if (msgEl) {
      msgEl.className = "p-4 rounded-2xl text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200";
      msgEl.innerText = "Doğrulama Hatası: " + err.message;
      msgEl.classList.remove("hidden");
    }
  }
}

async function submitDocTextScan() {
  const textInput = document.getElementById("doc-scan-text-input");
  const text = (textInput?.value || "").trim();
  if (text.length < 15) {
    showNotification("Lütfen E-Devlet belgenizden kopyaladığınız metni veya barkod bilgisini yapıştırın.", "amber");
    return;
  }

  const loadingEl = document.getElementById("doc-scan-loading");
  const msgEl = document.getElementById("doc-scan-result-msg");
  if (loadingEl) loadingEl.classList.remove("hidden");
  if (msgEl) msgEl.classList.add("hidden");

  try {
    const userId = window.appState.currentUser?.id || 1;
    const res = await fetch("/api/student/scan-document", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, document_text: text })
    });
    const data = await res.json();
    if (loadingEl) loadingEl.classList.add("hidden");

    if (!res.ok) {
      throw new Error(data.detail || "Belge metni çözümlenemedi.");
    }

    handleScanSuccess(data);
  } catch (err) {
    if (loadingEl) loadingEl.classList.add("hidden");
    if (msgEl) {
      msgEl.className = "p-4 rounded-2xl text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200";
      msgEl.innerText = "Doğrulama Hatası: " + err.message;
      msgEl.classList.remove("hidden");
    }
  }
}

async function scanSampleDoc(sampleKey) {
  const loadingEl = document.getElementById("doc-scan-loading");
  const msgEl = document.getElementById("doc-scan-result-msg");
  if (loadingEl) loadingEl.classList.remove("hidden");
  if (msgEl) msgEl.classList.add("hidden");

  try {
    const userId = window.appState.currentUser?.id || 1;
    const isDemo = window.appState.config?.demo_mode !== false;

    let res;
    if (isDemo) {
      res = await fetch("/api/student/scan-document", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, sample_key: sampleKey })
      });
    }

    // Canlı ortamda (DEMO_MODE=false) örnek belge metnini çekip gerçek metin tarayıcıdan geçirir
    if (!isDemo || (res && res.status === 503)) {
      const sampleText = await _fetchSampleDocText(sampleKey);
      const textInput = document.getElementById("doc-scan-text-input");
      if (textInput) {
        textInput.value = sampleText;
        analyzeDocTextLive(sampleText);
      }
      res = await fetch("/api/student/scan-document", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, document_text: sampleText })
      });
    }

    const data = await res.json();
    if (loadingEl) loadingEl.classList.add("hidden");

    if (!res.ok) {
      throw new Error(data.detail || "Örnek belge işlenemedi.");
    }

    handleScanSuccess(data);
  } catch (err) {
    if (loadingEl) loadingEl.classList.add("hidden");
    if (msgEl) {
      msgEl.className = "p-4 rounded-2xl text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200";
      msgEl.innerText = "Doğrulama Hatası: " + err.message;
      msgEl.classList.remove("hidden");
    }
  }
}

function handleScanSuccess(data) {
  const msgEl = document.getElementById("doc-scan-result-msg");
  if (msgEl) {
    msgEl.className = "p-4 rounded-2xl text-xs bg-emerald-50 text-emerald-900 border-2 border-emerald-300 space-y-3 shadow-sm";
    msgEl.innerHTML = `
      <div class="flex items-center justify-between border-b border-emerald-200 pb-2.5">
        <div class="flex items-center gap-2">
          <span class="w-7 h-7 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-black text-sm">✓</span>
          <div>
            <div class="font-black text-sm text-emerald-950">E-Devlet Öğrenci Belgesi Onaylandı!</div>
            <div class="text-[11px] text-emerald-700">YÖK Barkod & Kurum Doğrulaması Başarılı</div>
          </div>
        </div>
        <span class="text-[10px] font-black uppercase px-2.5 py-1 bg-emerald-200/80 text-emerald-900 rounded-full">Doğrulandı</span>
      </div>

      <div class="grid grid-cols-2 gap-2 bg-white/90 p-3 rounded-xl border border-emerald-200/80 text-[11px]">
        <div>
          <span class="text-slate-400 block font-bold">Üniversite:</span>
          <span class="font-extrabold text-slate-800">${data.matched_university_name || "-"}</span>
        </div>
        <div>
          <span class="text-slate-400 block font-bold">Öğrenci Adı:</span>
          <span class="font-extrabold text-slate-800">${data.student_name || window.appState.currentUser?.full_name || "Aktif Öğrenci"}</span>
        </div>
        <div>
          <span class="text-slate-400 block font-bold">Öğrenci Numarası:</span>
          <span class="font-mono font-bold text-slate-800">${data.student_number || "-"}</span>
        </div>
        <div>
          <span class="text-slate-400 block font-bold">E-Devlet Barkod:</span>
          <span class="font-mono font-bold text-indigo-700">${data.document_barcode || "-"}</span>
        </div>
        <div class="col-span-2 pt-1 border-t border-slate-100">
          <span class="text-slate-400 font-bold">Birim / Program: </span>
          <span class="font-bold text-slate-700">${data.faculty || "Yabancı Diller Yüksekokulu"} • ${data.department || "İngilizce Hazırlık"}</span>
        </div>
      </div>

      <div class="p-2.5 bg-emerald-100/80 rounded-xl text-emerald-900 font-bold text-[11px] flex items-center justify-between">
        <span>🎁 ${data.matched_university_name} hazırlık paketi ÜCRETSİZ tanımlandı!</span>
      </div>

      <button type="button" onclick="enterPlatformAfterVerification()" class="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-black text-xs rounded-xl shadow-lg shadow-emerald-500/25 transition flex items-center justify-center gap-2">
        <span>Hazırlık Platformuna Giriş Yap →</span>
      </button>
    `;
    msgEl.classList.remove("hidden");
  }

  // Update App State & LocalStorage
  if (window.appState.currentUser) {
    window.appState.currentUser.verified_university = data.matched_university_id;
    window.appState.currentUser.university_id = data.matched_university_id;
    window.appState.currentUser.is_verified_student = 1;
    window.appState.currentUser.verification_status = "verified";
    window.appState.currentUser.student_number = data.student_number;
    window.appState.currentUser.unlocked_universities = data.unlocked_universities || [data.matched_university_id, "general"];
    localStorage.setItem("auth_user", JSON.stringify(window.appState.currentUser));
  }

  // Automatically switch active university to matched school
  const matchedUni = window.appState.allUniversities.find(u => u.id === data.matched_university_id) || data.university;
  if (matchedUni) {
    window.appState.currentUniversity = matchedUni;
    renderUniversityHeader();
  }

  loadStudentStatus();
  showNotification(`✓ ${data.matched_university_name} hesabınıza otomatik tanımlandı!`, "emerald");

  setTimeout(() => {
    enterPlatformAfterVerification();
    if (window.appState.activeTab === "exams") renderExamsTab();
    else if (window.appState.activeTab === "dashboard") loadDashboardStats();
  }, 2600);
}

window.analyzeDocTextLive = analyzeDocTextLive;
window.fillSampleTextForCurrentUni = fillSampleTextForCurrentUni;
window.skipDocScanAndEnterPlatform = skipDocScanAndEnterPlatform;
window.enterPlatformAfterVerification = enterPlatformAfterVerification;

// ================= 50 TL ÜNİVERSİTE ÜYELİK & PAYWALL MODAL LOGIC =================
let pendingUnlockCallback = null;
let currentPaywallTargetUniId = null;

function openUniversityPaywallModal(targetUniId, onUnlockCallback = null) {
  currentPaywallTargetUniId = targetUniId;
  pendingUnlockCallback = onUnlockCallback;

  const modal = document.getElementById("university-paywall-modal");
  if (!modal) return;

  const targetUni = window.appState.allUniversities.find(u => u.id === targetUniId);
  const user = window.appState.currentUser;
  const verifiedId = user?.verified_university || null;
  const userUni = verifiedId ? window.appState.allUniversities.find(u => u.id === verifiedId) : null;

  const badgeEl = document.getElementById("paywall-user-uni-badge");
  const targetNameEl = document.getElementById("paywall-target-uni-name");
  const statusMsg = document.getElementById("paywall-status-msg");

  if (badgeEl) badgeEl.innerText = userUni ? `${userUni.name} (Ücretsiz)` : "Öğrenci belgesi doğrulanmadı";
  if (targetNameEl) targetNameEl.innerText = targetUni ? `${targetUni.name} (${targetUni.exam_name})` : targetUniId.toUpperCase();
  if (statusMsg) statusMsg.classList.add("hidden");

  modal.classList.remove("hidden");
  if (window.lucide) window.lucide.createIcons();
}

function closeUniversityPaywallModal() {
  const modal = document.getElementById("university-paywall-modal");
  if (modal) modal.classList.add("hidden");
  currentPaywallTargetUniId = null;
  pendingUnlockCallback = null;
}

async function submitUniversityUnlockPayment() {
  if (!currentPaywallTargetUniId) return;

  const cardHolder = (document.getElementById("paywall-card-holder")?.value || "Öğrenci").trim();
  const cardNumber = (document.getElementById("paywall-card-number")?.value || "4242 4242 4242 4242").trim();
  const btn = document.getElementById("btn-submit-paywall-unlock");
  const statusMsg = document.getElementById("paywall-status-msg");

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin inline-block mr-2">⏳</span> Ödeme Alınıyor (50 TL)...`;
  }

  try {
    const userId = window.appState.currentUser?.id || 1;
    const res = await fetch("/api/membership/unlock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        university_id: currentPaywallTargetUniId,
        card_holder: cardHolder,
        card_number: cardNumber
      })
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Ödeme işlemi gerçekleştirilemedi.");
    }

    // Success! Update unlocked universities in user profile
    if (window.appState.currentUser) {
      window.appState.currentUser.unlocked_universities = data.unlocked_universities || [];
      localStorage.setItem("auth_user", JSON.stringify(window.appState.currentUser));
    }

    if (statusMsg) {
      statusMsg.className = "p-3 rounded-xl text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200";
      statusMsg.innerText = `✓ Başarılı! 50 TL tahsil edildi. ${currentPaywallTargetUniId.toUpperCase()} sınavları açıldı.`;
      statusMsg.classList.remove("hidden");
    }

    showNotification(`✓ ${currentPaywallTargetUniId.toUpperCase()} sınav paketi 50 TL karşılığında açıldı!`, "emerald");

    const callback = pendingUnlockCallback;
    setTimeout(() => {
      closeUniversityPaywallModal();
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="credit-card" class="w-4 h-4"></i> 50 TL ile Kilidi Aç ve Başla`;
      }
      if (callback) callback();
    }, 1200);

  } catch (err) {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="credit-card" class="w-4 h-4"></i> 50 TL ile Kilidi Aç ve Başla`;
    }
    if (statusMsg) {
      statusMsg.className = "p-3 rounded-xl text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200";
      statusMsg.innerText = "Ödeme Hatası: " + err.message;
      statusMsg.classList.remove("hidden");
    }
  }
}

// Window Exports
window.openDocScanModal = openDocScanModal;
window.closeDocScanModal = closeDocScanModal;
window.switchDocScanTab = switchDocScanTab;
window.handleDocFileSelect = handleDocFileSelect;
window.submitDocFileUpload = submitDocFileUpload;
window.submitDocTextScan = submitDocTextScan;
window.scanSampleDoc = scanSampleDoc;
window.openUniversityPaywallModal = openUniversityPaywallModal;
window.closeUniversityPaywallModal = closeUniversityPaywallModal;
window.submitUniversityUnlockPayment = submitUniversityUnlockPayment;

// ---------------- ŞİFREMİ UNUTTUM ----------------
// Kod yalnızca e-postayla gelir; sunucu, adres kayıtlı olsun olmasın aynı yanıtı verir.
async function loadPublicConfig() {
  try {
    const res = await fetch('/api/config');
    if (!res.ok) return;
    const cfg = await res.json();
    window.appState.config = cfg;
    const btn = document.getElementById("btn-forgot-password");
    if (btn) btn.classList.toggle("hidden", !cfg.password_reset_available);
  } catch (_) {}
}

function setForgotMsg(text, ok) {
  const el = document.getElementById("forgot-msg");
  if (!el) return;
  if (!text) { el.classList.add("hidden"); return; }
  el.className = "p-2.5 rounded-xl text-xs font-semibold " +
    (ok ? "bg-emerald-50 border border-emerald-200 text-emerald-800" : "bg-rose-50 border border-rose-200 text-rose-700");
  el.innerText = text;
}

function showForgotStep(step) {
  document.getElementById("forgot-step-email").classList.toggle("hidden", step !== "email");
  document.getElementById("forgot-step-code").classList.toggle("hidden", step !== "code");
  setForgotMsg("");
}

function openForgotPassword() {
  const loginId = (document.getElementById("login-identifier")?.value || "").trim();
  const emailEl = document.getElementById("forgot-email");
  if (emailEl && loginId.includes("@")) emailEl.value = loginId;
  showForgotStep("email");
  document.getElementById("forgot-modal").classList.remove("hidden");
  if (window.lucide) window.lucide.createIcons();
  setTimeout(() => emailEl && emailEl.focus(), 50);
}

function closeForgotPassword() {
  document.getElementById("forgot-modal").classList.add("hidden");
}

async function submitForgotEmail() {
  const email = (document.getElementById("forgot-email").value || "").trim();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    setForgotMsg("Lütfen geçerli bir e-posta adresi girin.", false);
    return;
  }
  const btn = document.getElementById("btn-forgot-send");
  btn.disabled = true;
  try {
    const res = await fetch('/api/auth/forgot-password', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || "Kod gönderilemedi.");
    window.appState.forgotEmail = email;
    showForgotStep("code");
    document.getElementById("forgot-sent-msg").innerText = data.message ||
      "Bu e-posta adresiyle kayıtlı bir hesap varsa 6 haneli bir kod gönderildi.";
    setTimeout(() => document.getElementById("forgot-code").focus(), 50);
  } catch (err) {
    setForgotMsg(err.message, false);
  } finally {
    btn.disabled = false;
  }
}

async function submitForgotReset() {
  const email = window.appState.forgotEmail || (document.getElementById("forgot-email").value || "").trim();
  const code = (document.getElementById("forgot-code").value || "").replace(/\D/g, "");
  const p1 = document.getElementById("forgot-new-password").value || "";
  const p2 = document.getElementById("forgot-new-password2").value || "";
  if (code.length !== 6) return setForgotMsg("Kod 6 haneli olmalı.", false);
  if (p1.length < 6) return setForgotMsg("Yeni şifre en az 6 karakter olmalı.", false);
  if (p1 !== p2) return setForgotMsg("Şifreler aynı değil.", false);

  const btn = document.getElementById("btn-forgot-reset");
  btn.disabled = true;
  try {
    const res = await fetch('/api/auth/reset-password', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, reset_code: code, new_password: p1 })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || "Şifre değiştirilemedi.");
    setForgotMsg("✓ Şifreniz değişti. Yeni şifrenizle giriş yapabilirsiniz.", true);
    const idEl = document.getElementById("login-identifier");
    if (idEl) idEl.value = email;
    ["forgot-code", "forgot-new-password", "forgot-new-password2"].forEach(id => { document.getElementById(id).value = ""; });
    setTimeout(closeForgotPassword, 1600);
  } catch (err) {
    setForgotMsg(err.message, false);
  } finally {
    btn.disabled = false;
  }
}

window.openForgotPassword = openForgotPassword;
window.closeForgotPassword = closeForgotPassword;
window.submitForgotEmail = submitForgotEmail;
window.submitForgotReset = submitForgotReset;
window.showForgotStep = showForgotStep;

// ---------------- MOBİL UYGULAMA (ANDROID APK & PWA) MERKEZİ ----------------
let deferredPwaPrompt = null;

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPwaPrompt = e;
});

async function openApkDownloadModal() {
  const modal = document.getElementById("apk-download-modal");
  if (!modal) return;
  modal.classList.remove("hidden");

  try {
    const res = await fetch("/api/mobile-app/info");
    if (res.ok) {
      const info = await res.json();
      const sizeEl = document.getElementById("apk-modal-size-badge");
      const verEl = document.getElementById("apk-modal-version-badge");
      if (sizeEl && info.size_mb) sizeEl.innerText = `${info.size_mb} MB`;
      if (verEl && info.version) verEl.innerText = `v${info.version}`;
    }
  } catch (_) {}

  if (window.lucide) window.lucide.createIcons();
}

function closeApkDownloadModal() {
  const modal = document.getElementById("apk-download-modal");
  if (modal) modal.classList.add("hidden");
}

function trackApkDownloadClick() {
  showNotification("📱 PrepMaster Android APK (18.3 MB) indiriliyor...", "emerald");
}

async function copyApkDownloadLink() {
  const fullUrl = `${window.location.origin}/api/download/apk`;
  try {
    await navigator.clipboard.writeText(fullUrl);
    showNotification("✓ APK indirme bağlantısı panoya kopyalandı! Telefonunuza gönderebilirsiniz.", "emerald");
  } catch (_) {
    prompt("APK İndirme Bağlantısını Kopyalayın:", fullUrl);
  }
}

async function installWebAppPWA() {
  if (deferredPwaPrompt) {
    deferredPwaPrompt.prompt();
    const { outcome } = await deferredPwaPrompt.userChoice;
    deferredPwaPrompt = null;
    if (outcome === "accepted") {
      showNotification("✓ PrepMaster ana ekranınıza eklendi!", "emerald");
      closeApkDownloadModal();
    }
  } else {
    showNotification(
      "Tarayıcınızın sağ üst (Chrome: ⋮) veya alt (Safari: Paylaş ↑) menüsünden 'Ana Ekrana Ekle' seçeneğine dokunarak uygulama olarak kurabilirsiniz.",
      "blue"
    );
  }
}

window.openApkDownloadModal = openApkDownloadModal;
window.closeApkDownloadModal = closeApkDownloadModal;
window.trackApkDownloadClick = trackApkDownloadClick;
window.copyApkDownloadLink = copyApkDownloadLink;
window.installWebAppPWA = installWebAppPWA;
