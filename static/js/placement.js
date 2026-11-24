// PrepKampüs — Seviye Tespit Sınavı (web)
//
// Uyarlamalı akış: A1'den başlar, her kurda en fazla 4 soru sorulur. 3 doğruya ulaşan kur
// geçilmiş sayılır ve bir üst kura geçilir; kurda geçme ihtimali kalmayınca (ikinci yanlış)
// sınav biter. Önerilen çalışma kuru = geçilen en yüksek kurun bir üstü (C2'de C2).
// Mobil uygulamadaki PlacementEngine ile aynı kurallar.

(function () {
  const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];
  const PER_LEVEL = 4;
  const PASS_MARK = 3;
  const STORE_KEY = "prepkampus_placement";

  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // ---------------- Motor ----------------
  class PlacementEngine {
    constructor(pool) {
      this.queues = {};
      this.results = {};
      LEVELS.forEach((l) => {
        this.queues[l] = (pool[l] || []).slice(0, PER_LEVEL);
        this.results[l] = { level: l, correct: 0, answered: 0, passed: null };
      });
      this.levelIndex = 0;
      this.questionIndex = 0;
      this.finished = false;
      this._skipEmpty();
    }
    get currentLevel() { return LEVELS[this.levelIndex]; }
    get current() { return this.finished ? null : this.queues[this.currentLevel][this.questionIndex]; }
    get answeredCount() { return LEVELS.reduce((s, l) => s + this.results[l].answered, 0); }
    get correctCount() { return LEVELS.reduce((s, l) => s + this.results[l].correct, 0); }
    get maxQuestions() { return LEVELS.reduce((s, l) => s + this.queues[l].length, 0); }
    get masteredLevel() {
      let best = null;
      LEVELS.forEach((l) => { if (this.results[l].passed === true) best = l; });
      return best;
    }
    get recommendedLevel() {
      const m = this.masteredLevel;
      if (!m) return LEVELS[0];
      return LEVELS[Math.min(LEVELS.indexOf(m) + 1, LEVELS.length - 1)];
    }
    answer(key) {
      const q = this.current;
      if (!q) return false;
      const r = this.results[this.currentLevel];
      const ok = key === q.correct_answer;
      r.answered++;
      if (ok) r.correct++;
      const total = this.queues[this.currentLevel].length;
      const need = Math.min(PASS_MARK, total);
      const wrong = r.answered - r.correct;
      if (r.correct >= need) {
        r.passed = true;
        this.levelIndex++;
        this.questionIndex = 0;
        this._skipEmpty();
      } else if (wrong > total - need) {
        r.passed = false;
        this.finished = true;
      } else {
        this.questionIndex++;
      }
      return ok;
    }
    _skipEmpty() {
      while (this.levelIndex < LEVELS.length && this.queues[LEVELS[this.levelIndex]].length === 0) this.levelIndex++;
      if (this.levelIndex >= LEVELS.length) {
        this.levelIndex = LEVELS.length - 1;
        this.finished = true;
      }
    }
  }

  // ---------------- Kayıt ----------------
  function loadSaved() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY) || "null"); } catch (_) { return null; }
  }
  function saveResult(engine) {
    const data = { level: engine.recommendedLevel, mastered: engine.masteredLevel, date: new Date().toISOString() };
    try { localStorage.setItem(STORE_KEY, JSON.stringify(data)); } catch (_) {}
    return data;
  }

  // ---------------- Arayüz ----------------
  let engine = null;
  let applied = false;

  function modal() {
    let m = document.getElementById("placement-modal");
    if (!m) {
      m = document.createElement("div");
      m.id = "placement-modal";
      m.className = "hidden fixed inset-0 z-[65] bg-slate-900/70 backdrop-blur-sm p-3 sm:p-6 overflow-y-auto flex items-start sm:items-center justify-center";
      m.innerHTML = `
        <div class="w-full max-w-xl bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-700 my-auto">
          <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2 font-extrabold text-slate-800 dark:text-slate-100">
              <i data-lucide="gauge" class="w-5 h-5 text-blue-600"></i>
              <span>Seviye Tespit Sınavı</span>
            </div>
            <button type="button" onclick="closePlacementTest()" aria-label="Kapat" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800">
              <i data-lucide="x" class="w-5 h-5"></i>
            </button>
          </div>
          <div id="placement-body" class="p-5 sm:p-6"></div>
        </div>`;
      m.addEventListener("click", (e) => { if (e.target === m) closePlacementTest(); });
      document.body.appendChild(m);
    }
    return m;
  }

  function body() { return document.getElementById("placement-body"); }
  function icons() { if (window.lucide) window.lucide.createIcons(); }

  function renderIntro() {
    const rows = [
      ["list-ordered", "En fazla 24 soru, çoğu zaman çok daha az"],
      ["timer-off", "Süre sınırı yok, acele etme"],
      ["gift", "Ücretsiz; üyelik gerekmez"],
      ["graduation-cap", "Sonunda önerilen çalışma kurunu görürsün"],
    ];
    body().innerHTML = `
      <div class="text-center">
        <div class="mx-auto w-14 h-14 rounded-2xl bg-blue-50 dark:bg-blue-950 flex items-center justify-center mb-3">
          <i data-lucide="gauge" class="w-7 h-7 text-blue-600"></i>
        </div>
        <h3 class="text-xl font-black text-slate-800 dark:text-slate-100">Seviyeni 5 dakikada öğren</h3>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
          Sınav A1'den başlar ve sen doğru cevapladıkça zorlaşır. Her kurda en fazla ${PER_LEVEL} soru sorulur;
          ${PASS_MARK} doğru yapınca bir üst kura geçersin. Zorlandığın kurda sınav biter.
        </p>
      </div>
      <ul class="mt-5 space-y-2">
        ${rows.map(([ic, t]) => `
          <li class="flex items-center gap-2.5 text-sm text-slate-700 dark:text-slate-200">
            <i data-lucide="${ic}" class="w-4 h-4 text-blue-600 shrink-0"></i><span>${t}</span>
          </li>`).join("")}
      </ul>
      <button type="button" id="placement-begin" onclick="beginPlacementTest()" class="mt-6 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-sm rounded-2xl shadow transition flex items-center justify-center gap-2">
        <i data-lucide="play" class="w-4 h-4"></i><span>Sınava başla</span>
      </button>`;
    icons();
  }

  async function begin() {
    const btn = document.getElementById("placement-begin");
    if (btn) { btn.disabled = true; btn.querySelector("span").innerText = "Sorular hazırlanıyor..."; }
    let pool = {};
    try {
      const res = await fetch("/api/placement/questions");
      if (res.ok) pool = (await res.json()).questions || {};
    } catch (_) {}
    engine = new PlacementEngine(pool);
    applied = false;
    if (engine.finished) {
      if (engine.maxQuestions === 0) {
        body().innerHTML = `<p class="text-sm text-rose-600 font-bold text-center py-6">Sorular yüklenemedi. Bağlantını kontrol edip tekrar dene.</p>
          <button type="button" onclick="beginPlacementTest()" class="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-sm rounded-xl">Tekrar dene</button>`;
        return;
      }
      saveResult(engine);
      renderResult();
    } else {
      renderQuestion();
    }
  }

  function renderQuestion() {
    const q = engine.current;
    const r = engine.results[engine.currentLevel];
    const pct = engine.maxQuestions ? Math.round((engine.answeredCount / engine.maxQuestions) * 100) : 0;
    body().innerHTML = `
      <div class="flex items-center gap-2 mb-3">
        <span id="placement-level-badge" class="px-2.5 py-1 bg-blue-600 text-white text-xs font-black rounded-lg">Kur ${engine.currentLevel}</span>
        <span class="text-xs text-slate-500 dark:text-slate-400 font-semibold">Bu kurda soru ${r.answered + 1} • Toplam ${engine.answeredCount + 1}</span>
      </div>
      <div class="h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mb-5">
        <div class="h-full bg-blue-600 rounded-full transition-all" style="width:${pct}%"></div>
      </div>
      <p id="placement-question" class="text-[15px] leading-relaxed font-semibold text-slate-800 dark:text-slate-100 whitespace-pre-line mb-5">${esc(q.question)}</p>
      <div class="space-y-2.5">
        ${q.options.map((o) => `
          <button type="button" data-placement-opt="${esc(o.key)}" onclick="answerPlacementQuestion('${esc(o.key)}')"
            class="w-full text-left flex gap-3 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-slate-800 transition text-sm text-slate-700 dark:text-slate-200">
            <span class="font-black text-blue-600 shrink-0">${esc(o.key)})</span><span>${esc(o.text)}</span>
          </button>`).join("")}
      </div>`;
    icons();
  }

  function answer(key) {
    if (!engine || engine.finished) return;
    engine.answer(key);
    if (engine.finished) {
      saveResult(engine);
      renderResult();
      renderPlacementCard();
    } else {
      renderQuestion();
    }
  }

  function renderResult() {
    const mastered = engine.masteredLevel;
    const rec = engine.recommendedLevel;
    const current = window.appState?.currentLevel;
    const note = mastered === null
      ? "A1 sorularında zorlandın; temelden başlamak en iyisi."
      : mastered === "C2"
        ? "Tüm kurları geçtin! C2 ile pratiğe devam et."
        : `${mastered} kurunu geçtin, ${rec} kurunda zorlandın.`;
    const row = (r) => {
      const [icon, color, label] = r.passed === true
        ? ["circle-check", "text-emerald-600", "Geçti"]
        : r.passed === false ? ["circle-x", "text-rose-600", "Zorlandın"] : ["circle-minus", "text-slate-400", "Sorulmadı"];
      return `
        <div class="flex items-center gap-3 py-1.5 text-sm">
          <span class="w-8 font-black text-slate-800 dark:text-slate-100">${r.level}</span>
          <i data-lucide="${icon}" class="w-4 h-4 ${color}"></i>
          <span class="flex-1 ${color} font-semibold">${label}</span>
          ${r.answered ? `<span class="text-xs text-slate-400 font-bold">${r.correct}/${r.answered}</span>` : ""}
        </div>`;
    };
    const action = rec !== current && !applied
      ? `<button type="button" id="placement-apply" onclick="applyPlacementLevel()" class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-sm rounded-2xl shadow transition flex items-center justify-center gap-2">
           <i data-lucide="check" class="w-4 h-4"></i><span>Çalışma kurumu ${rec} yap</span>
         </button>`
      : `<div id="placement-level-set" class="p-3 rounded-2xl bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 text-sm font-bold text-center">Çalışma kurun ${rec}.</div>`;
    body().innerHTML = `
      <div class="rounded-3xl p-6 text-center text-white bg-gradient-to-br from-blue-900 to-indigo-950">
        <div class="text-xs text-blue-200 font-semibold">Önerilen çalışma kurun</div>
        <div id="placement-recommended" class="text-5xl font-black my-2">${rec}</div>
        <div class="text-sm">${note}</div>
        <div class="text-xs text-blue-200 mt-1">${engine.answeredCount} sorudan ${engine.correctCount} doğru</div>
      </div>
      <h4 class="mt-5 mb-1 text-sm font-extrabold text-slate-800 dark:text-slate-100">Kur kur sonuçların</h4>
      <div class="divide-y divide-slate-100 dark:divide-slate-800">${LEVELS.map((l) => row(engine.results[l])).join("")}</div>
      <div class="mt-5 space-y-2.5">
        ${action}
        <div class="grid grid-cols-2 gap-2.5">
          <button type="button" onclick="beginPlacementTest()" class="py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-100 font-bold text-sm rounded-xl">Tekrar çöz</button>
          <button type="button" onclick="closePlacementTest()" class="py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-100 font-bold text-sm rounded-xl">Kapat</button>
        </div>
      </div>`;
    icons();
  }

  async function applyLevel() {
    if (!engine) return;
    const rec = engine.recommendedLevel;
    applied = true;
    if (window.changeCurrentLevel) await window.changeCurrentLevel(rec);
    renderResult();
  }

  function open() {
    modal().classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    renderIntro();
  }

  function close() {
    const inProgress = engine && !engine.finished && engine.answeredCount > 0 &&
      !document.getElementById("placement-modal").classList.contains("hidden") &&
      document.getElementById("placement-question");
    if (inProgress && !confirm("Sınavdan çıkılsın mı? Cevapların kaydedilmeyecek.")) return;
    const m = document.getElementById("placement-modal");
    if (m) m.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    engine = null;
    renderPlacementCard();
  }

  // Panel kartı: çözülmediyse belirgin teklif, çözüldüyse kısa özet
  function renderPlacementCard() {
    const el = document.getElementById("placement-card");
    if (!el) return;
    const saved = loadSaved();
    if (saved && saved.level) {
      el.innerHTML = `
        <div id="placement-summary" class="flex items-center gap-3 px-4 py-3 rounded-2xl bg-blue-50 dark:bg-slate-800 border border-blue-100 dark:border-slate-700">
          <i data-lucide="gauge" class="w-5 h-5 text-blue-600 shrink-0"></i>
          <span class="flex-1 text-xs sm:text-sm font-bold text-blue-900 dark:text-slate-100">
            Seviye tespiti: ${saved.mastered ? `${esc(saved.mastered)} geçildi • ` : ""}önerilen kur ${esc(saved.level)}
          </span>
          <button type="button" onclick="openPlacementTest()" class="text-xs font-extrabold text-blue-700 dark:text-blue-300 hover:underline shrink-0">Tekrar çöz</button>
        </div>`;
    } else {
      el.innerHTML = `
        <div id="placement-offer" class="flex flex-col sm:flex-row sm:items-center gap-3 p-4 sm:p-5 rounded-3xl bg-white dark:bg-slate-900 border-2 border-blue-200 dark:border-blue-900 shadow-sm">
          <div class="w-11 h-11 rounded-2xl bg-blue-50 dark:bg-blue-950 flex items-center justify-center shrink-0">
            <i data-lucide="gauge" class="w-6 h-6 text-blue-600"></i>
          </div>
          <div class="flex-1">
            <div class="font-extrabold text-slate-800 dark:text-slate-100">Seviyeni bilmiyor musun?</div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">
              Seviye tespit sınavı A1'den C2'ye uyarlamalı ilerler (en fazla 24 soru, yaklaşık 5 dakika) ve sana uygun çalışma kurunu önerir.
            </p>
          </div>
          <button type="button" onclick="openPlacementTest()" class="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs rounded-xl shadow transition flex items-center justify-center gap-1.5 shrink-0">
            <i data-lucide="play" class="w-3.5 h-3.5"></i><span>Seviye tespit sınavına başla</span>
          </button>
        </div>`;
    }
    icons();
  }

  document.addEventListener("keydown", (e) => {
    const m = document.getElementById("placement-modal");
    if (e.key === "Escape" && m && !m.classList.contains("hidden")) close();
  });
  document.addEventListener("DOMContentLoaded", renderPlacementCard);

  window.PlacementEngine = PlacementEngine;
  window.openPlacementTest = open;
  window.closePlacementTest = close;
  window.beginPlacementTest = begin;
  window.answerPlacementQuestion = answer;
  window.applyPlacementLevel = applyLevel;
  window.renderPlacementCard = renderPlacementCard;
})();
