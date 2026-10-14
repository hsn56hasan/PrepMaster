// PrepMaster AI Writing & Essay Evaluator

const AI_ESSAY_PROMPTS = [
  {
    id: "boun_p1",
    university: "Boğaziçi BUEPT",
    title: "Artificial Intelligence in Medicine: Benefits vs. Ethical Dilemmas",
    promptText: "Some argue that autonomous AI diagnostics undermine human clinical care, while others claim their efficiency saves lives. Discuss both views and state your own opinion."
  },
  {
    id: "itu_p1",
    university: "İTÜ Proficiency",
    title: "Transition to Renewable Energy: Causes and Environmental Impacts",
    promptText: "Explain the fundamental causes driving the global shift from fossil fuels to renewable sources and analyze its potential impact on modern urban engineering."
  },
  {
    id: "metu_p1",
    university: "ODTÜ EPE",
    title: "Urban Architecture and Climate Change Adaptation",
    promptText: "To what extent can bioclimatic urban architecture and green roofs mitigate the severe effects of urban heat islands in developing megacities?"
  },
  {
    id: "custom",
    university: "Serbest Konu",
    title: "Kendi Belirlediğiniz Bir Konuda Essay Yazın",
    promptText: "Hazırlık sınavınızda çıkmasını beklediğiniz herhangi bir konuyu yazıp yapay zekaya puanlatabilirsiniz."
  }
];

function initAIWritingEvaluator() {
  const container = document.getElementById("ai-writing-evaluator-section");
  if (!container) return;

  container.innerHTML = `
    <div class="bg-gradient-to-br from-indigo-900 via-slate-900 to-blue-950 text-white rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
      <div class="max-w-2xl">
        <span class="px-3 py-1 bg-blue-500/30 text-blue-200 border border-blue-400/30 rounded-full text-xs font-bold uppercase tracking-wider inline-flex items-center gap-1.5 mb-3">
          <i data-lucide="sparkles" class="w-3.5 h-3.5 text-blue-300"></i> Yapay Zeka Destekli
        </span>
        <h2 class="text-2xl sm:text-3xl font-extrabold tracking-tight mb-2">
          Akıllı Essay Değerlendirici & Puanlama Motoru
        </h2>
        <p class="text-xs text-slate-300 leading-relaxed">
          Yazdığınız kompozisyonu (Opinion, Cause-Effect vb.) Boğaziçi, İTÜ ve ODTÜ muafiyet kriterlerine göre anında puanlatın; CEFR seviyenizi, kelime çeşitliliğinizi ve Türkçe düzeltme önerilerinizi görün.
        </p>
      </div>
    </div>

    <!-- Editör Alanı -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-6">
      <!-- Konu Seçici -->
      <div>
        <label class="block text-xs font-extrabold text-slate-700 uppercase tracking-wider mb-2">
          1. Hedef Sınav Konusu Seçin:
        </label>
        <select id="ai-essay-prompt-select" onchange="onSelectEssayPrompt(this.value)" class="w-full p-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-bold text-slate-700 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500">
          ${AI_ESSAY_PROMPTS.map(p => `
            <option value="${p.id}">[${p.university}] ${p.title}</option>
          `).join('')}
        </select>
        <p id="ai-essay-prompt-text" class="mt-2 text-xs text-slate-500 italic bg-blue-50/60 p-3 rounded-xl border border-blue-100">
          ${AI_ESSAY_PROMPTS[0].promptText}
        </p>
      </div>

      <!-- Essay Metin Editörü -->
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <label class="text-xs font-extrabold text-slate-700 uppercase tracking-wider">
            2. Kompozisyonunuzu Yazın (İdeal: 250 - 350 Kelime):
          </label>
          <div class="flex items-center gap-2">
            <span id="essay-word-count-badge" class="px-3 py-1 bg-slate-100 text-slate-600 font-mono text-xs font-bold rounded-lg border border-slate-200">
              0 / 250 kelime
            </span>
          </div>
        </div>

        <textarea id="ai-essay-input" oninput="updateEssayWordCount(this.value)" rows="12" class="w-full p-4 text-xs font-serif leading-relaxed text-slate-800 bg-slate-50 border border-slate-200 rounded-2xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder:text-slate-400" placeholder="Write your essay here with clear paragraphs (Introduction, Body 1, Body 2, Conclusion)..."></textarea>
      </div>

      <!-- Değerlendir Butonu -->
      <div class="flex items-center justify-between pt-2">
        <span class="text-xs text-slate-400">
          * Kompozisyonunuz akademik kriterlere (Task Achievement, Cohesion, Vocabulary, Grammar) göre taranır.
        </span>
        <button id="ai-eval-btn" onclick="submitEssayForEvaluation()" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-lg shadow-blue-500/25 transition flex items-center gap-2">
          <i data-lucide="cpu" class="w-4 h-4"></i> Yapay Zeka ile Analiz Et
        </button>
      </div>

      <!-- SONUÇ PANELİ -->
      <div id="ai-eval-results-container" class="hidden pt-6 border-t border-slate-200 space-y-6">
        <!-- JS renderAIEvaluationResults() -->
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function onSelectEssayPrompt(promptId) {
  const p = AI_ESSAY_PROMPTS.find(x => x.id === promptId);
  const el = document.getElementById("ai-essay-prompt-text");
  if (p && el) {
    el.innerText = p.promptText;
  }
}

function updateEssayWordCount(val) {
  const words = val.trim().match(/\b[A-Za-z0-9'-]+\b/g) || [];
  const badge = document.getElementById("essay-word-count-badge");
  if (badge) {
    badge.innerText = `${words.length} / 250 kelime`;
    if (words.length >= 250) {
      badge.className = "px-3 py-1 bg-emerald-50 text-emerald-700 font-mono text-xs font-bold rounded-lg border border-emerald-200";
    } else {
      badge.className = "px-3 py-1 bg-slate-100 text-slate-600 font-mono text-xs font-bold rounded-lg border border-slate-200";
    }
  }
}

async function submitEssayForEvaluation() {
  const inputEl = document.getElementById("ai-essay-input");
  const essayText = inputEl ? inputEl.value : "";
  const btn = document.getElementById("ai-eval-btn");
  const resultsContainer = document.getElementById("ai-eval-results-container");

  if (!essayText.trim()) {
    alert("Lütfen önce bir kompozisyon metni girin.");
    return;
  }

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Analiz Ediliyor...`;
  }

  try {
    const res = await fetch('/api/writing/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        essay: essayText,
        prompt: document.getElementById("ai-essay-prompt-text")?.innerText || "General Essay",
        university_id: window.appState.currentUniversity?.id || "itu",
        level: window.appState.currentLevel || "B2"
      })
    });

    const data = await res.json();
    renderAIEvaluationResults(data);
  } catch (err) {
    console.error("Evaluation error:", err);
    alert("Yapay zeka analizi sırasında bir hata oluştu.");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="cpu" class="w-4 h-4"></i> Yapay Zeka ile Analiz Et`;
      if (window.lucide) window.lucide.createIcons();
    }
  }
}

function renderAIEvaluationResults(data) {
  const container = document.getElementById("ai-eval-results-container");
  if (!container) return;

  container.classList.remove("hidden");

  const isPassed = data.is_passing;

  container.innerHTML = `
    <!-- Ana Skor Rozeti -->
    <div class="p-6 bg-gradient-to-r ${isPassed ? 'from-emerald-900 to-slate-900' : 'from-rose-900 to-slate-900'} text-white rounded-3xl shadow-lg flex flex-col sm:flex-row items-center justify-between gap-6">
      <div>
        <span class="px-3 py-1 rounded-full text-xs font-extrabold ${isPassed ? 'bg-emerald-500/30 text-emerald-300 border border-emerald-400/30' : 'bg-rose-500/30 text-rose-300 border border-rose-400/30'} uppercase">
          ${isPassed ? '✓ Muafiyet Barajını Geçti' : '⚠️ Barajın Altında Kaldı'}
        </span>
        <h3 class="text-2xl font-black mt-2">Genel Puan: ${data.overall_score} / 100</h3>
        <p class="text-xs text-slate-300 mt-1">
          Tahmini CEFR Seviyesi: <strong class="text-white">${data.estimated_cefr}</strong> • Kelime: ${data.word_count} • Paragraf: ${data.paragraph_count}
        </p>
      </div>

      <div class="text-center sm:text-right shrink-0">
        <div class="text-4xl font-black ${isPassed ? 'text-emerald-400' : 'text-rose-400'}">
          ${data.overall_score}
        </div>
        <span class="text-[11px] text-slate-400 uppercase tracking-widest font-bold">Toplam Not</span>
      </div>
    </div>

    <!-- 4 Temel Kriter Puan Dağılımı -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
        <span class="text-[10px] font-bold uppercase text-slate-400 block mb-1">Task Response</span>
        <span class="text-lg font-black text-slate-800">${data.task_achievement_score} / 25</span>
        <p class="text-[10px] text-slate-500 mt-1">Konuyu ele alış ve tez ifadesi</p>
      </div>

      <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
        <span class="text-[10px] font-bold uppercase text-slate-400 block mb-1">Cohesion & Coherence</span>
        <span class="text-lg font-black text-slate-800">${data.coherence_cohesion_score} / 25</span>
        <p class="text-[10px] text-slate-500 mt-1">Geçiş bağlaçları & akış</p>
      </div>

      <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
        <span class="text-[10px] font-bold uppercase text-slate-400 block mb-1">Lexical Resource</span>
        <span class="text-lg font-black text-slate-800">${data.lexical_resource_score} / 25</span>
        <p class="text-[10px] text-slate-500 mt-1">Akademik kelime dağarcığı</p>
      </div>

      <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
        <span class="text-[10px] font-bold uppercase text-slate-400 block mb-1">Grammar Range</span>
        <span class="text-lg font-black text-slate-800">${data.grammatical_range_score} / 25</span>
        <p class="text-[10px] text-slate-500 mt-1">Cümle çeşitliliği & yapılar</p>
      </div>
    </div>

    <!-- Tespit Edilen Geçiş Bağlaçları ve Akademik Kelimeler -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="p-4 bg-blue-50/70 border border-blue-200 rounded-2xl space-y-2">
        <h4 class="text-xs font-extrabold text-blue-900 flex items-center gap-1.5">
          <i data-lucide="link" class="w-3.5 h-3.5 text-blue-600"></i> Tespit Edilen Geçiş Bağlaçları (${data.detected_transitions.length})
        </h4>
        <div class="flex flex-wrap gap-1.5">
          ${data.detected_transitions.length ? data.detected_transitions.map(t => `
            <span class="px-2 py-0.5 bg-blue-100 text-blue-800 text-[11px] font-bold rounded-md">${t}</span>
          `).join('') : '<span class="text-xs text-slate-400">Hiç bağlaç tespit edilemedi.</span>'}
        </div>
      </div>

      <div class="p-4 bg-purple-50/70 border border-purple-200 rounded-2xl space-y-2">
        <h4 class="text-xs font-extrabold text-purple-900 flex items-center gap-1.5">
          <i data-lucide="book-open" class="w-3.5 h-3.5 text-purple-600"></i> Akademik Kelime Kullanımı (${data.detected_academic_words.length})
        </h4>
        <div class="flex flex-wrap gap-1.5">
          ${data.detected_academic_words.length ? data.detected_academic_words.map(w => `
            <span class="px-2 py-0.5 bg-purple-100 text-purple-800 text-[11px] font-bold rounded-md">${w}</span>
          `).join('') : '<span class="text-xs text-slate-400">Daha fazla akademik kelime kullanmalısınız.</span>'}
        </div>
      </div>
    </div>

    <!-- Güçlü Yönler & Geliştirme Tavsiyeleri -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="p-5 bg-emerald-50 border border-emerald-200 rounded-2xl space-y-2">
        <h4 class="text-xs font-extrabold text-emerald-900 flex items-center gap-1.5">
          <i data-lucide="check" class="w-4 h-4 text-emerald-600"></i> Güçlü Yönleriniz
        </h4>
        <ul class="text-xs text-emerald-800 space-y-1.5 list-disc list-inside">
          ${data.strengths_tr.map(s => `<li>${s}</li>`).join('')}
        </ul>
      </div>

      <div class="p-5 bg-amber-50 border border-amber-200 rounded-2xl space-y-2">
        <h4 class="text-xs font-extrabold text-amber-900 flex items-center gap-1.5">
          <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-600"></i> Geliştirilmesi Gereken Noktalar
        </h4>
        <ul class="text-xs text-amber-800 space-y-1.5 list-disc list-inside">
          ${data.improvements_tr.map(imp => `<li>${imp}</li>`).join('')}
        </ul>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

window.initAIWritingEvaluator = initAIWritingEvaluator;
window.onSelectEssayPrompt = onSelectEssayPrompt;
window.updateEssayWordCount = updateEssayWordCount;
window.submitEssayForEvaluation = submitEssayForEvaluation;
window.renderAIEvaluationResults = renderAIEvaluationResults;

