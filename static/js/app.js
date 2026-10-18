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
    // 0. Initialize Theme & Auth
    initDarkMode();
    await checkCurrentUser();

    // 1. Fetch Universities
    const uniRes = await fetch('/api/universities');
    window.appState.allUniversities = await uniRes.json();

    // 2. Fetch User Profile
    const profRes = await fetch('/api/profile');
    const profile = await profRes.json();
    
    window.appState.currentLevel = profile.current_level || 'B2';
    if (!window.appState.currentUniversity) {
      window.appState.currentUniversity = profile.university || window.appState.allUniversities[0];
    }

    // 3. Render Initial State
    renderUniversityHeader();
    renderLevelSelector();
    setupTabNavigation();
    
    // 4. Load initial tab & student status
    switchTab('dashboard');
    loadStudentStatus();

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

async function loadWritingGuides(targetLevel = null) {
  const container = document.getElementById("writing-guides-container");
  const filterBar = document.getElementById("writing-filter-bar");
  if (!container) return;

  const currentLevel = window.appState?.currentLevel || 'B2';
  const activeLevel = targetLevel !== null ? targetLevel : currentLevel;

  // Render Writing Level Filter Bar
  if (filterBar) {
    const levels = ['A2', 'B1', 'B2', 'C1', 'C2'];
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
  if (badgeEl) badgeEl.innerText = `${lvl} (Hedef Kur)`;

  let module1 = {
    badge: `Use of English • ${lvl}`,
    badgeColor: "bg-indigo-100 text-indigo-700",
    title: "Temel Dilbilgisi & Cümle Kurma",
    desc: `${lvl} seviyesine uygun zamanlar, bağlaçlar, cümle kurma kuralları ve günlük soru kalıpları.`,
    category: "Use of English"
  };

  let module2 = {
    badge: `Okuma & Kelime • ${lvl}`,
    badgeColor: "bg-amber-100 text-amber-700",
    title: "Akademik Kelime & Okuma Testi",
    desc: `${lvl} seviyesinde kısa akademik ve günlük metinler üzerinden ana fikir ve kelime soruları.`,
    category: "Reading"
  };

  let module3 = {
    badge: `Dilbilgisi • ${lvl}`,
    badgeColor: "bg-emerald-100 text-emerald-700",
    title: "Grammar & Boşluk Doldurma",
    desc: `${lvl} seviyesine özel hazırlanmış çoktan seçmeli dilbilgisi ve boşluk tamamlama soruları.`,
    category: "Grammar"
  };

  if (['B1', 'B2'].includes(lvl)) {
    module1 = {
      badge: `Restatement • ${lvl}`,
      badgeColor: "bg-indigo-100 text-indigo-700",
      title: "Restatement (En Yakın Anlam) Atölyesi",
      desc: `${lvl} seviyesinde cümle paraphrase etme, eşanlamlı yapılar ve anlam bütünlüğü analizi.`,
      category: "Restatement"
    };
    module2 = {
      badge: `Akademik Okuma • ${lvl}`,
      badgeColor: "bg-amber-100 text-amber-700",
      title: "Akademik Reading & Çıkarım Testi",
      desc: `${lvl} sınav formatında makaleler üzerinden ana fikir, detay, yazar tutumu ve kelime soruları.`,
      category: "Reading"
    };
    module3 = {
      badge: `Cloze Test • ${lvl}`,
      badgeColor: "bg-emerald-100 text-emerald-700",
      title: "Grammar & Cloze Test Serisi",
      desc: `${lvl} hazırlık müfredatına uygun zamanlar, bağlaçlar ve paragraf içi boşluk doldurma.`,
      category: "Cloze Test"
    };
  } else if (['C1', 'C2'].includes(lvl)) {
    module1 = {
      badge: `İleri Düzey • ${lvl}`,
      badgeColor: "bg-purple-100 text-purple-700",
      title: "İleri Düzey Restatement & Text Analysis",
      desc: `Boğaziçi BUEPT ve ODTÜ EPE standardında karmaşık felsefi ve bilimsel cümle paraphrase testleri.`,
      category: "Restatement"
    };
    module2 = {
      badge: `Akademik Analiz • ${lvl}`,
      badgeColor: "bg-rose-100 text-rose-700",
      title: "Akademik Makale & Eleştirel Okuma",
      desc: `${lvl} seviyesinde yüksek lisans ve lisans muafiyetine yönelik akademik makale çıkarım soruları.`,
      category: "Reading"
    };
    module3 = {
      badge: `Sentence Completion • ${lvl}`,
      badgeColor: "bg-teal-100 text-teal-700",
      title: "Cümle & Paragraf Tamamlama Serisi",
      desc: `İleri düzey akademik geçiş bağlaçları, retorik akış ve paragraf tamamlama soruları.`,
      category: "Sentence Completion"
    };
  }

  container.innerHTML = `
    <!-- Full Mock Exam Card -->
    <div class="p-5 rounded-2xl border-2 border-blue-600 bg-blue-50/20 flex flex-col justify-between shadow-sm">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 bg-blue-600 text-white text-[11px] font-bold rounded-lg uppercase">Tam Deneme</span>
          <span class="px-2.5 py-0.5 bg-blue-100 text-blue-800 text-xs font-black rounded-lg">Seviye: ${lvl}</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">Resmi Muafiyet / ${lvl} Kur Bitirme Denemesi</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          ${lvl} müfredatına özel seçilmiş 15 soru, dinleme parçası ve yazma/konuşma sınav simülasyonu.
        </p>
      </div>
      <button onclick="startFullMockExam(null, '${lvl}')" class="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow transition flex items-center justify-center gap-1.5">
        <i data-lucide="play" class="w-3.5 h-3.5"></i> ${lvl} Deneme Sınavını Başlat
      </button>
    </div>

    <!-- Modül 1 -->
    <div class="p-5 rounded-2xl border border-slate-200 bg-white hover:border-slate-300 transition flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 ${module1.badgeColor} text-[11px] font-bold rounded-lg uppercase">${module1.badge}</span>
          <span class="text-xs text-slate-500 font-semibold">${lvl} Modülü</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">${module1.title}</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          ${module1.desc}
        </p>
      </div>
      <button onclick="startExamSimulation(null, '${lvl}', '${module1.category}')" class="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs rounded-xl transition">
        ${module1.category} Sorularını Çöz
      </button>
    </div>

    <!-- Modül 2 -->
    <div class="p-5 rounded-2xl border border-slate-200 bg-white hover:border-slate-300 transition flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 ${module2.badgeColor} text-[11px] font-bold rounded-lg uppercase">${module2.badge}</span>
          <span class="text-xs text-slate-500 font-semibold">${lvl} Modülü</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">${module2.title}</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          ${module2.desc}
        </p>
      </div>
      <button onclick="startExamSimulation(null, '${lvl}', '${module2.category}')" class="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs rounded-xl transition">
        ${module2.category} Sorularını Çöz
      </button>
    </div>

    <!-- Modül 3 -->
    <div class="p-5 rounded-2xl border border-slate-200 bg-white hover:border-slate-300 transition flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2.5 py-0.5 ${module3.badgeColor} text-[11px] font-bold rounded-lg uppercase">${module3.badge}</span>
          <span class="text-xs text-slate-500 font-semibold">${lvl} Modülü</span>
        </div>
        <h4 class="font-extrabold text-slate-800 text-base mb-1">${module3.title}</h4>
        <p class="text-xs text-slate-600 leading-relaxed mb-4">
          ${module3.desc}
        </p>
      </div>
      <button onclick="startExamSimulation(null, '${lvl}', '${module3.category}')" class="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs rounded-xl transition">
        ${module3.category} Sorularını Çöz
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

// --- Cloud Sync & Student Verification Module ---
async function syncCloudData() {
  const syncIcon = document.getElementById("sync-icon");
  if (syncIcon) syncIcon.classList.add("animate-spin");

  try {
    const res = await fetch('/api/sync/pull');
    const data = await res.json();

    if (window.appState.activeTab === 'dashboard') loadDashboardStats();
    else if (window.appState.activeTab === 'mistakes') loadMistakeVault();

    showNotification("✓ Bulut senkronizasyonu tamamlandı. Tüm verileriniz güncel!", "emerald");
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
    let user = stored ? JSON.parse(stored) : null;
    if (!user) {
      const res = await fetch("/api/auth/me?user_id=1");
      if (res.ok) user = await res.json();
    }
    if (user) {
      window.appState.currentUser = user;
      const nameEl = document.getElementById("header-user-name");
      if (nameEl) nameEl.innerText = (user.full_name || user.username || "Öğrenci").split(" ")[0];
    }
  } catch (e) {
    console.warn("checkCurrentUser error:", e);
  }
}

function openAuthModal() {
  const modal = document.getElementById("auth-modal");
  if (!modal) return;
  const user = window.appState.currentUser;
  const loggedInView = document.getElementById("auth-logged-in-view");
  const formsView = document.getElementById("auth-forms-view");

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
    if (titleEl) titleEl.innerText = "Öğrenci Girişi & Kayıt";
    switchAuthTab("login");
  }

  modal.classList.remove("hidden");
  if (window.lucide) window.lucide.createIcons();
}

function closeAuthModal() {
  const modal = document.getElementById("auth-modal");
  if (modal) modal.classList.add("hidden");
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
      btnLogin.className = "flex-1 py-1.5 rounded-xl bg-white dark:bg-slate-700 text-blue-700 dark:text-blue-400 shadow-sm transition font-bold";
    }
    if (btnReg) {
      btnReg.className = "flex-1 py-1.5 rounded-xl text-slate-500 hover:text-slate-800 transition font-bold";
    }
  } else {
    if (formLogin) formLogin.classList.add("hidden");
    if (formReg) formReg.classList.remove("hidden");
    if (btnLogin) {
      btnLogin.className = "flex-1 py-1.5 rounded-xl text-slate-500 hover:text-slate-800 transition font-bold";
    }
    if (btnReg) {
      btnReg.className = "flex-1 py-1.5 rounded-xl bg-white dark:bg-slate-700 text-blue-700 dark:text-blue-400 shadow-sm transition font-bold";
    }
  }
}

async function submitLogin() {
  const identInput = document.getElementById("login-identifier");
  const passInput = document.getElementById("login-password");
  const errEl = document.getElementById("login-error-msg");
  const identifier = identInput ? identInput.value.trim() : "";
  const password = passInput ? passInput.value.trim() : "";

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

    const nameEl = document.getElementById("header-user-name");
    if (nameEl) nameEl.innerText = (data.user.full_name || data.user.username).split(" ")[0];

    if (data.user.university) {
      window.appState.currentUniversity = data.user.university;
      renderUniversityHeader();
    }

    closeAuthModal();
    showNotification(`✓ Başarıyla giriş yapıldı. Hoş geldin, ${data.user.full_name}!`, "emerald");
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

    const nameEl = document.getElementById("header-user-name");
    if (nameEl) nameEl.innerText = (data.user.full_name || data.user.username).split(" ")[0];

    closeAuthModal();
    showNotification(`✓ Hesabınız oluşturuldu. Hoş geldin, ${data.user.full_name}!`, "emerald");
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
  const nameEl = document.getElementById("header-user-name");
  if (nameEl) nameEl.innerText = "Giriş Yap";
  closeAuthModal();
  showNotification("Oturumunuz kapatıldı.", "rose");
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
window.syncCloudData = syncCloudData;
window.openStudentVerifyModal = openStudentVerifyModal;
window.closeStudentVerifyModal = closeStudentVerifyModal;
window.submitStudentVerification = submitStudentVerification;
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




