// PrepKampüs — Konu Yolu
// Seviyeye göre sırayla açılan gündelik hayat dersleri. Her ders: kısa tanıtım, örnek konuşma ve 14 alıştırma
// (anlam seçme, eşleştirme, dinleme, cümle kurma, boşluk doldurma, yazma). Yanlışlar dersin
// sonuna geri gelir; 5 kalp biterse ders yeniden denenir. Sonuç sunucuya yazılır (yıldız + XP).
(function () {
  "use strict";

  const HEARTS = 5;
  const NODE_OFFSETS = [0, 46, 78, 46, 0, -46, -78, -46];
  const state = { overview: null, level: null, loading: false, lesson: null };

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const icons = () => { if (window.lucide) window.lucide.createIcons(); };
  const shuffle = (arr) => { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const sample = (arr, n) => shuffle(arr).slice(0, n);
  const notify = (msg, ok) => (typeof window.showNotification === "function" ? window.showNotification(msg, ok ? "emerald" : "rose") : alert(msg));

  // ---------------- Seslendirme ----------------
  const ttsOk = () => "speechSynthesis" in window && typeof SpeechSynthesisUtterance !== "undefined";
  function speak(text) {
    if (!ttsOk() || !text) return;
    try {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = "en-US";
      u.rate = 0.9;
      const v = window.speechSynthesis.getVoices().find((x) => /^en(-|_)/i.test(x.lang));
      if (v) u.voice = v;
      window.speechSynthesis.speak(u);
    } catch (_) { /* ses yoksa sessiz geç */ }
  }

  // ---------------- Yol (harita) ----------------
  async function loadPath(level) {
    const root = $("path-root");
    if (!root || state.loading) return;
    state.loading = true;
    if (!state.overview) root.innerHTML = `<div class="path-card p-10 text-center text-sm text-slate-500">Konu yolu yükleniyor…</div>`;
    try {
      const q = level ? `?level=${encodeURIComponent(level)}` : "";
      const res = await fetch(`/api/path/overview${q}`);
      if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || "Konu yolu yüklenemedi.");
      state.overview = await res.json();
      state.level = state.overview.selected_level;
      renderPath();
    } catch (e) {
      root.innerHTML = `<div class="path-card p-8 text-center"><p class="text-sm font-semibold text-rose-600">${esc(e.message)}</p>
        <button type="button" class="path-btn path-btn-ghost mt-4" onclick="loadLessonPath()">Tekrar dene</button></div>`;
    } finally {
      state.loading = false;
    }
  }

  function renderPath() {
    const ov = state.overview;
    const root = $("path-root");
    if (!ov || !root) return;
    const st = ov.stats;
    const pct = st.total ? Math.round((st.completed / st.total) * 100) : 0;
    const cur = ov.current_topic;

    const levelPills = ov.levels.map((l) => {
      const active = l.level === ov.selected_level;
      const lp = l.total ? Math.round((l.done / l.total) * 100) : 0;
      return `<button type="button" class="path-level ${active ? "is-active" : ""} ${l.unlocked ? "" : "is-locked"}"
          data-path-level="${l.level}" title="${esc(l.title)} · ${l.done}/${l.total}">
          <span class="font-extrabold">${l.level}</span>
          ${l.unlocked ? `<span class="path-level-bar"><span style="width:${lp}%"></span></span>` : `<i data-lucide="lock" class="w-3 h-3"></i>`}
        </button>`;
    }).join("");

    const selected = ov.levels.find((l) => l.level === ov.selected_level) || { title: "", done: 0, total: 0, unlocked: true };

    const units = ov.units.map((u) => {
      const nodes = u.topics.map((t, i) => nodeHtml(t, i, t.id === cur)).join("");
      const reviewCls = u.review_unlocked ? (u.review_stars ? "is-done" : "is-open") : "is-locked";
      return `<section class="path-unit">
          <header class="path-unit-head">
            <div class="min-w-0">
              <div class="text-[11px] font-bold uppercase tracking-wider opacity-80">${ov.selected_level} · Ünite ${u.index}</div>
              <h3 class="text-lg font-extrabold leading-tight truncate">${esc(u.title_tr)}</h3>
            </div>
            <div class="shrink-0 text-right">
              <div class="text-xs font-bold opacity-90">${u.done}/${u.total} ders</div>
              <div class="path-unit-bar"><span style="width:${u.total ? Math.round((u.done / u.total) * 100) : 0}%"></span></div>
            </div>
          </header>
          <div class="path-track">
            ${nodes}
            <div class="path-node-wrap" style="--x:0px">
              <button type="button" class="path-review ${reviewCls}" data-path-unit="${u.id}" ${u.review_unlocked ? "" : 'aria-disabled="true"'}
                title="${u.review_unlocked ? "Ünite tekrarı" : "Ünitedeki bütün dersleri bitirince açılır"}">
                <i data-lucide="${u.review_unlocked ? "trophy" : "lock"}" class="w-6 h-6"></i>
              </button>
              <div class="path-node-label">Ünite tekrarı${u.review_stars ? ` <span class="text-amber-500">${"★".repeat(u.review_stars)}</span>` : ""}</div>
            </div>
          </div>
        </section>`;
    }).join("");

    root.innerHTML = `
      <div class="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_320px] gap-5 items-start">
        <div class="space-y-5 min-w-0">
          <div class="path-hero">
            <div class="relative z-10 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
              <div class="min-w-0">
                <div class="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider bg-white/15 border border-white/20 rounded-full px-2.5 py-1">
                  <i data-lucide="route" class="w-3.5 h-3.5"></i> Konu Yolu
                </div>
                <h2 class="mt-2 text-2xl sm:text-3xl font-extrabold leading-tight">Gündelik İngilizceyi adım adım öğren</h2>
                <p class="mt-1 text-sm text-white/80 max-w-xl">Her ders kısa bir anlatım, örnek bir konuşma ve 14 alıştırmadan oluşur. Bir dersi bitirince sıradaki açılır; yanlışların dersin sonunda tekrar karşına çıkar.</p>
              </div>
              ${cur ? `<button type="button" class="path-btn path-btn-light shrink-0" data-path-topic="${cur}">
                  <i data-lucide="play" class="w-4 h-4"></i> Kaldığın yerden devam</button>` : ""}
            </div>
          </div>

          <div class="path-card p-3 sm:p-4">
            <div class="flex items-center justify-between gap-3 mb-3">
              <div>
                <div class="text-sm font-extrabold text-slate-900 dark:text-white">${esc(selected.level || ov.selected_level)} · ${esc(selected.title)}</div>
                <div class="text-xs text-slate-500">${selected.done}/${selected.total} ders tamamlandı</div>
              </div>
              <button type="button" class="path-btn path-btn-ghost" data-path-review ${st.review_available ? "" : "disabled"}>
                <i data-lucide="refresh-cw" class="w-4 h-4"></i> Karışık tekrar
              </button>
            </div>
            <div class="path-levels" role="tablist" aria-label="Seviyeler">${levelPills}</div>
          </div>

          ${selected.unlocked ? units : lockedLevelHtml(ov, selected)}
        </div>

        <aside class="space-y-4">
          <div class="path-card p-4">
            <div class="grid grid-cols-2 gap-2.5">
              ${statTile("zap", "text-amber-500", "Toplam XP", st.xp_total)}
              ${statTile("check-circle-2", "text-emerald-600", "Biten ders", `${st.completed}<span class="text-sm text-slate-400 font-bold">/${st.total}</span>`)}
              ${statTile("star", "text-amber-500", "Kusursuz", st.perfect)}
              ${statTile("percent", "text-emerald-600", "Yol", `%${pct}`)}
            </div>
          </div>
          <div class="path-card p-4">
            <h4 class="text-sm font-extrabold text-slate-900 dark:text-white mb-3">Nasıl çalışır?</h4>
            <ul class="space-y-2.5 text-xs text-slate-600 dark:text-slate-300">
              <li class="flex gap-2.5"><i data-lucide="heart" class="w-4 h-4 text-rose-500 shrink-0"></i><span>Her derste <b>5 kalbin</b> var. Yanlış cevap bir kalp götürür; biterse dersi baştan denersin, bekleme yok.</span></li>
              <li class="flex gap-2.5"><i data-lucide="star" class="w-4 h-4 text-amber-500 shrink-0"></i><span>İlk denemede doğru oranına göre yıldız: <b>%90+ üç</b>, %70+ iki, %50+ bir.</span></li>
              <li class="flex gap-2.5"><i data-lucide="zap" class="w-4 h-4 text-amber-500 shrink-0"></i><span>Ders 10 XP, kusursuz ders +5, ünite tekrarı 20 XP. Çözdüğün alıştırmalar günlük görevine de sayılır.</span></li>
              <li class="flex gap-2.5"><i data-lucide="unlock" class="w-4 h-4 text-emerald-600 shrink-0"></i><span>Seviye tespitindeki kurun ve altı açıktır. Üst seviye, bir önceki seviyenin <b>%80'i</b> bitince açılır.</span></li>
            </ul>
          </div>
        </aside>
      </div>`;
    icons();
  }

  function statTile(icon, color, label, value) {
    return `<div class="kpi-tile">
        <div class="flex items-center gap-1.5 text-[11px] font-semibold text-slate-500"><i data-lucide="${icon}" class="w-3.5 h-3.5 ${color}"></i>${label}</div>
        <div class="mt-1 text-xl font-extrabold text-slate-900 dark:text-white">${value}</div>
      </div>`;
  }

  function lockedLevelHtml(ov, selected) {
    const idx = ov.levels.findIndex((l) => l.level === selected.level);
    const prev = idx > 0 ? ov.levels[idx - 1] : null;
    const need = prev ? Math.ceil(prev.total * 0.8) : 0;
    return `<div class="path-card p-8 text-center">
        <div class="w-14 h-14 mx-auto rounded-2xl bg-slate-100 dark:bg-slate-700 flex items-center justify-center"><i data-lucide="lock" class="w-6 h-6 text-slate-500"></i></div>
        <h3 class="mt-3 text-lg font-extrabold text-slate-900 dark:text-white">${esc(selected.level)} henüz kilitli</h3>
        <p class="mt-1 text-sm text-slate-500 max-w-md mx-auto">${prev ? `Açmak için ${esc(prev.level)} seviyesinde en az <b>${need}</b> ders bitir (şu an ${prev.done}/${prev.total}).` : ""}
          Seviye tespitine girersen kurun ve altındaki seviyeler hemen açılır.</p>
        <div class="mt-4 flex flex-wrap justify-center gap-2">
          ${prev ? `<button type="button" class="path-btn path-btn-primary" data-path-level="${prev.level}">${esc(prev.level)} seviyesine git</button>` : ""}
          <button type="button" class="path-btn path-btn-ghost" onclick="openPlacementTest && openPlacementTest()">Seviye tespiti</button>
        </div>
      </div>`;
  }

  function nodeHtml(t, i, isCurrent) {
    const x = NODE_OFFSETS[i % NODE_OFFSETS.length];
    const stars = [1, 2, 3].map((n) => `<span class="${n <= t.stars ? "is-on" : ""}">★</span>`).join("");
    const icon = t.status === "locked" ? "lock" : (t.status === "done" && t.stars >= 3 ? "crown" : t.icon || "book-open");
    return `<div class="path-node-wrap ${isCurrent ? "has-bubble" : ""}" style="--x:${x}px">
        ${isCurrent ? `<div class="path-bubble">BAŞLA</div>` : ""}
        <button type="button" class="path-node is-${t.status} ${isCurrent ? "is-current" : ""}" data-path-topic="${t.id}"
          ${t.status === "locked" ? 'aria-disabled="true"' : ""} aria-label="${esc(t.title_tr)}${t.status === "locked" ? " (kilitli)" : ""}">
          <i data-lucide="${icon}" class="w-7 h-7"></i>
        </button>
        ${t.status === "done" ? `<div class="path-stars">${stars}</div>` : ""}
        <div class="path-node-label">${esc(t.title_tr)}</div>
      </div>`;
  }

  // Tıklamalar tek yerden
  document.addEventListener("click", (ev) => {
    const lvBtn = ev.target.closest("[data-path-level]");
    if (lvBtn && $("path-root") && $("path-root").contains(lvBtn)) {
      loadPath(lvBtn.getAttribute("data-path-level"));
      return;
    }
    const topicBtn = ev.target.closest("[data-path-topic]");
    if (topicBtn && $("path-root") && $("path-root").contains(topicBtn)) {
      if (topicBtn.getAttribute("aria-disabled") === "true") {
        notify("Bu ders kilitli. Önce sıradaki dersi bitir.", false);
        return;
      }
      openLesson("topic", topicBtn.getAttribute("data-path-topic"));
      return;
    }
    const unitBtn = ev.target.closest("[data-path-unit]");
    if (unitBtn && $("path-root") && $("path-root").contains(unitBtn)) {
      if (unitBtn.getAttribute("aria-disabled") === "true") {
        notify("Ünite tekrarı, ünitedeki bütün dersleri bitirince açılır.", false);
        return;
      }
      openLesson("unit", unitBtn.getAttribute("data-path-unit"));
      return;
    }
    const reviewBtn = ev.target.closest("[data-path-review]");
    if (reviewBtn && !reviewBtn.disabled) openLesson("review", state.level);
  });

  // ---------------- Alıştırma üretimi ----------------
  function vocabChoice(item, pool, dir) {
    const others = sample(pool.filter((v) => v.en !== item.en), 3);
    if (dir === "en-tr") {
      return { type: "choice", prompt: "Bu kelimenin anlamı ne?", display: item.en, speak: item.en,
        options: shuffle([item.tr, ...others.map((o) => o.tr)]), answer: item.tr };
    }
    return { type: "choice", prompt: "Bunun İngilizcesi hangisi?", display: item.tr,
      options: shuffle([item.en, ...others.map((o) => o.en)]), answer: item.en, speakAnswer: true };
  }

  function listenEx(item, pool) {
    const others = sample(pool.filter((v) => v.en !== item.en), 3);
    return { type: "listen", prompt: "Duyduğun kelimeyi seç", speak: item.en,
      options: shuffle([item.en, ...others.map((o) => o.en)]), answer: item.en };
  }

  function matchEx(items) {
    return { type: "match", prompt: "Eşleri bul", pairs: items.map((v) => ({ en: v.en, tr: v.tr })) };
  }

  function orderEx(phrase, vocabPool, level) {
    const words = phrase.en.trim().split(/\s+/);
    let extra = [];
    if (!/^A/.test(level || "")) {
      const lower = words.map((w) => w.toLowerCase().replace(/[.,!?]/g, ""));
      extra = sample(vocabPool.filter((v) => !/\s/.test(v.en) && !lower.includes(v.en.toLowerCase())), 2).map((v) => v.en);
    }
    const tokens = shuffle([...words, ...extra]).map((w, i) => ({ id: i, w }));
    return { type: "order", prompt: "Cümleyi İngilizce kur", display: phrase.tr, tokens, answer: words.join(" "), speak: phrase.en };
  }

  function quizEx(q) {
    return { type: "quiz", prompt: "Boşluğu doldur", q: q.q, options: shuffle(q.options.map((o, i) => ({ t: o, i }))),
      answer: q.answer, explain: q.explain_tr, full: q.q.replace("___", q.options[q.answer]) };
  }

  function phraseChoice(phrase, phrases) {
    const others = sample(phrases.filter((p) => p.en !== phrase.en), 3);
    return { type: "choice", prompt: "Bu cümle ne anlama geliyor?", display: phrase.en, speak: phrase.en, long: true,
      options: shuffle([phrase.tr, ...others.map((o) => o.tr)]), answer: phrase.tr };
  }

  function typeEx(item) {
    return { type: "type", prompt: "İngilizcesini yaz", display: item.tr, answer: item.en, speak: item.en };
  }

  // Konuşmayı tamamla: diyalogdaki bir B cevabını, önceki satırlara bakarak seç
  function dialogueEx(dialogue, otherReplies) {
    if (!Array.isArray(dialogue) || dialogue.length < 2) return null;
    const bIdx = dialogue.map((l, i) => (l.who === "B" && i > 0 ? i : -1)).filter((i) => i > 0);
    if (!bIdx.length) return null;
    const i = bIdx[Math.floor(Math.random() * bIdx.length)];
    const answer = dialogue[i].en;
    const pool = [...new Set(otherReplies.filter((t) => t && t !== answer))];
    const options = shuffle([answer, ...sample(pool, 3)]);
    if (options.length < 3) return null;
    return { type: "dialogue", prompt: "Konuşmayı tamamla", context: dialogue.slice(Math.max(0, i - 3), i),
      options, answer, speak: answer, tr: dialogue[i].tr };
  }

  function buildExercises(bundle) {
    const topics = bundle.topics || [];
    const level = bundle.level || "";
    const vocab = topics.flatMap((t) => t.vocab || []);
    const phrases = topics.flatMap((t) => t.phrases || []);
    const quiz = topics.flatMap((t) => t.quiz || []);
    const dialogues = topics.map((t) => (t.speaking && t.speaking.dialogue) || []).filter((d) => d.length);
    const replies = dialogues.flatMap((d) => d.filter((l) => l.who === "B").map((l) => l.en));
    const replyPool = replies.length >= 4 ? replies : [...replies, ...phrases.map((p) => p.en)];
    const tts = ttsOk();
    const ex = [];
    if (topics.length === 1) {
      const v = shuffle(vocab), ph = shuffle(phrases), qz = shuffle(quiz);
      ex.push(vocabChoice(v[0], vocab, "en-tr"), vocabChoice(v[1], vocab, "en-tr"), vocabChoice(v[2], vocab, "tr-en"));
      ex.push(matchEx(v.slice(3, 8)));
      ex.push(tts ? listenEx(v[4], vocab) : vocabChoice(v[4], vocab, "en-tr"));
      ex.push(orderEx(ph[0], vocab, level), quizEx(qz[0]), quizEx(qz[1]));
      ex.push(phraseChoice(ph[1], phrases), dialogueEx(dialogues[0], replyPool), typeEx(v[5]), orderEx(ph[2], vocab, level));
      ex.push(quizEx(qz[2]), quizEx(qz[3]));
    } else {
      const v = shuffle(vocab), ph = shuffle(phrases), qz = shuffle(quiz), dl = shuffle(dialogues);
      ex.push(vocabChoice(v[0], vocab, "en-tr"), vocabChoice(v[1], vocab, "tr-en"), vocabChoice(v[2], vocab, "en-tr"));
      ex.push(matchEx(v.slice(3, 8)));
      ex.push(tts ? listenEx(v[8], vocab) : vocabChoice(v[8], vocab, "tr-en"));
      ex.push(orderEx(ph[0], vocab, level), quizEx(qz[0]), dialogueEx(dl[0], replyPool), quizEx(qz[1]), phraseChoice(ph[1], phrases));
      ex.push(typeEx(v[9]), quizEx(qz[2]), dialogueEx(dl[1], replyPool), orderEx(ph[2], vocab, level), quizEx(qz[3]), typeEx(v[10]), quizEx(qz[4]));
    }
    return ex.filter(Boolean).map((e, i) => Object.assign(e, { key: i }));
  }

  // Örnek konuşma ve konuşma görevleri (ders girişinde)
  function speakingHtml(sp) {
    if (!sp || !Array.isArray(sp.dialogue) || !sp.dialogue.length) return "";
    const lines = sp.dialogue.map((l) => `
        <div class="lesson-bubble-row ${l.who === "B" ? "is-b" : ""}">
          <span class="lesson-who" aria-hidden="true">${esc(l.who)}</span>
          <button type="button" class="lesson-bubble" data-speak="${esc(l.en)}">
            <span class="block font-semibold text-slate-900 dark:text-white">${esc(l.en)}</span>
            <span class="block text-xs text-slate-500 mt-0.5">${esc(l.tr)}</span>
          </button>
        </div>`).join("");
    const prompts = (sp.prompts || []).map((p, i) => `
        <div class="lesson-prompt">
          <div class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Konuşma görevi ${i + 1}</div>
          <p class="mt-1 font-bold text-slate-900 dark:text-white">${esc(p.q_en)}</p>
          <p class="text-xs text-slate-500">${esc(p.q_tr)}</p>
          <div class="mt-2 flex flex-wrap gap-1.5">${(p.useful || []).map((u) => `<button type="button" class="lesson-chip" data-speak="${esc(u)}">${esc(u)}</button>`).join("")}</div>
          <details class="mt-2">
            <summary class="text-xs font-bold text-emerald-700 dark:text-emerald-400 cursor-pointer select-none">Örnek cevabı göster</summary>
            <button type="button" class="mt-2 w-full text-left text-sm text-slate-700 dark:text-slate-200 lesson-model" data-speak="${esc(p.model)}">
              <i data-lucide="volume-2" class="w-4 h-4 text-emerald-600 inline -mt-0.5 mr-1"></i>${esc(p.model)}</button>
          </details>
          <p class="mt-2 text-[11px] text-slate-500">Önce kendin sesli cevapla, sonra örnek cevabı dinleyip karşılaştır.</p>
        </div>`).join("");
    return `
        <div class="mt-5 flex items-center justify-between gap-2">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500">Örnek konuşma</h3>
          ${ttsOk() ? `<button type="button" class="path-btn path-btn-ghost !py-1.5 !px-3 !text-xs" data-speak-all><i data-lucide="play" class="w-3.5 h-3.5"></i> Tümünü dinle</button>` : ""}
        </div>
        <div class="lesson-dialogue mt-2" data-dialogue='${esc(JSON.stringify(sp.dialogue.map((l) => l.en)))}'>${lines}</div>
        ${prompts ? `<h3 class="mt-5 mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">Sesli pratik</h3><div class="space-y-3">${prompts}</div>` : ""}`;
  }

  function speakAll(texts) {
    if (!ttsOk() || !texts.length) return;
    try {
      window.speechSynthesis.cancel();
      const v = window.speechSynthesis.getVoices().filter((x) => /^en(-|_)/i.test(x.lang));
      texts.forEach((t, i) => {
        const u = new SpeechSynthesisUtterance(t);
        u.lang = "en-US"; u.rate = 0.9;
        if (v.length) u.voice = v[i % 2 && v.length > 1 ? 1 : 0]; // A ve B farklı ses (varsa)
        window.speechSynthesis.speak(u);
      });
    } catch (_) {}
  }

  // ---------------- Ders akışı ----------------
  async function openLesson(kind, id) {
    let url;
    if (kind === "topic") url = `/api/path/topic/${encodeURIComponent(id)}`;
    else if (kind === "unit") url = `/api/path/unit/${encodeURIComponent(id)}`;
    else url = `/api/path/review${id ? `?level=${encodeURIComponent(id)}` : ""}`;
    try {
      const res = await fetch(url);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Ders açılamadı.");
      startLesson(kind, data);
    } catch (e) {
      notify(e.message, false);
    }
  }

  function overlay() {
    let el = $("lesson-overlay");
    if (!el) {
      el = document.createElement("div");
      el.id = "lesson-overlay";
      el.className = "lesson-overlay hidden";
      el.setAttribute("role", "dialog");
      el.setAttribute("aria-modal", "true");
      document.body.appendChild(el);
    }
    return el;
  }

  function startLesson(kind, bundle) {
    const queue = buildExercises(bundle);
    state.lesson = {
      kind, bundle, nodeId: kind === "review" ? `review-${(bundle.level || "all").toLowerCase()}` : bundle.id,
      queue, total: queue.length, done: 0, firstWrong: new Set(), hearts: HEARTS,
      current: null, phase: "intro", selection: null, matchState: null, orderPicked: [],
    };
    const el = overlay();
    el.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    renderIntro();
  }

  function closeLesson(force) {
    const L = state.lesson;
    if (!force && L && L.phase === "exercise" && L.done > 0 && !confirm("Dersten çıkarsan ilerlemen kaydedilmez. Çıkmak istiyor musun?")) return;
    try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (_) {}
    state.lesson = null;
    const el = $("lesson-overlay");
    if (el) { el.classList.add("hidden"); el.innerHTML = ""; }
    document.body.classList.remove("overflow-hidden");
  }

  function topBar() {
    const L = state.lesson;
    const pct = Math.round((L.done / L.total) * 100);
    const hearts = Array.from({ length: HEARTS }, (_, i) =>
      `<i data-lucide="heart" class="w-5 h-5 ${i < L.hearts ? "text-rose-500 fill-rose-500" : "text-slate-300 dark:text-slate-600"}"></i>`).join("");
    return `<div class="lesson-top">
        <button type="button" class="lesson-icon-btn" data-lesson-close aria-label="Dersi kapat"><i data-lucide="x" class="w-5 h-5"></i></button>
        <div class="lesson-progress" aria-label="İlerleme %${pct}"><span style="width:${pct}%"></span></div>
        <div class="flex items-center gap-0.5 shrink-0" aria-label="${L.hearts} kalp">${hearts}</div>
      </div>`;
  }

  function renderIntro() {
    const L = state.lesson;
    const b = L.bundle;
    const el = overlay();
    let body;
    if (L.kind === "topic") {
      const t = b.topics[0];
      const vocab = t.vocab.map((v) => `<button type="button" class="lesson-vocab" data-speak="${esc(v.en)}">
          <span class="min-w-0"><span class="block font-bold text-slate-900 dark:text-white truncate">${esc(v.en)}</span>
          <span class="block text-xs text-slate-500 truncate">${esc(v.tr)}</span></span>
          ${ttsOk() ? `<i data-lucide="volume-2" class="w-4 h-4 text-emerald-600 shrink-0"></i>` : ""}</button>`).join("");
      body = `
        <div class="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">${esc(b.level)} · ${esc(b.unit_title || "")}</div>
        <h2 class="mt-1 text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">${esc(t.title_tr)}</h2>
        <div class="text-sm text-slate-500">${esc(t.title_en)}</div>
        <p class="mt-3 text-sm text-slate-700 dark:text-slate-300">${esc(t.intro_tr)}</p>
        <h3 class="mt-5 mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">Bu dersin kelimeleri</h3>
        <div class="grid grid-cols-2 gap-2">${vocab}</div>
        <div class="lesson-tip mt-5">
          <div class="flex items-center gap-1.5 text-xs font-extrabold text-emerald-800 dark:text-emerald-300"><i data-lucide="lightbulb" class="w-4 h-4"></i> İpucu</div>
          <p class="mt-1 text-sm text-slate-700 dark:text-slate-200">${esc(t.tip_tr)}</p>
          <button type="button" class="mt-2 text-left text-sm" data-speak="${esc(t.tip_example.en)}">
            <span class="font-bold text-slate-900 dark:text-white">${esc(t.tip_example.en)}</span>
            <span class="block text-xs text-slate-500">${esc(t.tip_example.tr)}</span>
          </button>
        </div>
        ${speakingHtml(t.speaking)}`;
    } else {
      const names = b.topics.map((t) => `<li class="flex items-center gap-2"><i data-lucide="${esc(t.icon || "book-open")}" class="w-4 h-4 text-emerald-600"></i>${esc(t.title_tr)}</li>`).join("");
      body = `
        <div class="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">${esc(b.level || "")} · ${L.kind === "unit" ? "Ünite tekrarı" : "Karışık tekrar"}</div>
        <h2 class="mt-1 text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">${esc(b.title_tr)}</h2>
        <p class="mt-3 text-sm text-slate-700 dark:text-slate-300">${L.total} alıştırma, bu konulardan karışık geliyor:</p>
        <ul class="mt-3 space-y-2 text-sm text-slate-700 dark:text-slate-200">${names}</ul>`;
    }
    el.innerHTML = `
      <div class="lesson-shell">
        <div class="lesson-top">
          <button type="button" class="lesson-icon-btn" data-lesson-close aria-label="Kapat"><i data-lucide="x" class="w-5 h-5"></i></button>
          <div class="flex-1"></div>
        </div>
        <div class="lesson-body"><div class="lesson-inner">${body}</div></div>
        <div class="lesson-foot"><div class="lesson-foot-inner">
          <div class="text-xs text-slate-500">${L.total} alıştırma · ${HEARTS} kalp</div>
          <button type="button" class="path-btn path-btn-primary lesson-main-btn" data-lesson-start>Derse başla</button>
        </div></div>
      </div>`;
    icons();
    const startBtn = el.querySelector("[data-lesson-start]");
    if (startBtn) startBtn.focus();
  }

  function nextExercise() {
    const L = state.lesson;
    if (!L) return;
    if (!L.queue.length) return finishLesson();
    L.current = L.queue.shift();
    L.phase = "exercise";
    L.selection = null;
    L.orderPicked = [];
    L.matchState = L.current.type === "match"
      ? { left: shuffle(L.current.pairs.map((p) => p.en)), right: shuffle(L.current.pairs.map((p) => p.tr)), done: new Set(), pick: null, misses: 0 }
      : null;
    renderExercise();
    if (L.current.type === "listen") setTimeout(() => speak(L.current.speak), 250);
  }

  function renderExercise() {
    const L = state.lesson;
    const ex = L.current;
    const el = overlay();
    let main = "";
    if (ex.type === "choice" || ex.type === "listen") {
      const head = ex.type === "listen"
        ? `<div class="flex justify-center gap-3 my-4">
            <button type="button" class="lesson-sound" data-speak="${esc(ex.speak)}" aria-label="Dinle"><i data-lucide="volume-2" class="w-8 h-8"></i></button>
            <button type="button" class="lesson-sound is-slow" data-speak-slow="${esc(ex.speak)}" aria-label="Yavaş dinle"><i data-lucide="snail" class="w-6 h-6"></i></button>
          </div>`
        : `<div class="lesson-display ${ex.long ? "is-long" : ""}">
            ${ex.speak ? `<button type="button" class="lesson-mini-sound" data-speak="${esc(ex.speak)}" aria-label="Dinle"><i data-lucide="volume-2" class="w-4 h-4"></i></button>` : ""}
            <span>${esc(ex.display)}</span></div>`;
      main = `${head}<div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">${ex.options.map((o, i) =>
        `<button type="button" class="lesson-option" data-opt="${esc(o)}"><span class="lesson-key">${i + 1}</span><span>${esc(o)}</span></button>`).join("")}</div>`;
    } else if (ex.type === "dialogue") {
      const ctx = ex.context.map((l) => `
        <div class="lesson-bubble-row ${l.who === "B" ? "is-b" : ""}">
          <span class="lesson-who" aria-hidden="true">${esc(l.who)}</span>
          <button type="button" class="lesson-bubble" data-speak="${esc(l.en)}"><span class="block font-semibold text-slate-900 dark:text-white">${esc(l.en)}</span></button>
        </div>`).join("");
      main = `<div class="lesson-dialogue my-4">${ctx}
          <div class="lesson-bubble-row is-b"><span class="lesson-who" aria-hidden="true">B</span><div class="lesson-bubble is-empty">…</div></div>
        </div>
        <div class="grid grid-cols-1 gap-2.5">${ex.options.map((o, i) =>
          `<button type="button" class="lesson-option" data-opt="${esc(o)}"><span class="lesson-key">${i + 1}</span><span>${esc(o)}</span></button>`).join("")}</div>`;
    } else if (ex.type === "quiz") {
      const parts = ex.q.split("___");
      main = `<div class="lesson-display is-long"><span>${esc(parts[0])}<span class="lesson-blank">____</span>${esc(parts[1] || "")}</span></div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">${ex.options.map((o, i) =>
          `<button type="button" class="lesson-option" data-opt="${o.i}"><span class="lesson-key">${i + 1}</span><span>${esc(o.t)}</span></button>`).join("")}</div>`;
    } else if (ex.type === "match") {
      const m = L.matchState;
      const col = (arr, side) => arr.map((w) => {
        const pair = L.current.pairs.find((p) => (side === "en" ? p.en : p.tr) === w);
        const done = m.done.has(pair.en);
        return `<button type="button" class="lesson-match ${done ? "is-done" : ""} ${m.pick && m.pick.side === side && m.pick.w === w ? "is-picked" : ""}"
          data-match-side="${side}" data-match-w="${esc(w)}" ${done ? "disabled" : ""}>${esc(w)}</button>`;
      }).join("");
      main = `<div class="grid grid-cols-2 gap-2.5 mt-2"><div class="space-y-2.5">${col(m.left, "en")}</div><div class="space-y-2.5">${col(m.right, "tr")}</div></div>`;
    } else if (ex.type === "order") {
      const picked = L.orderPicked.map((id) => ex.tokens.find((t) => t.id === id));
      main = `<div class="lesson-display is-long"><span>${esc(ex.display)}</span></div>
        <div class="lesson-answer-line" aria-label="Cevabın">${picked.map((t) => `<button type="button" class="lesson-token" data-token-out="${t.id}">${esc(t.w)}</button>`).join("") || '<span class="text-xs text-slate-400">Kelimelere sırayla dokun</span>'}</div>
        <div class="lesson-bank">${ex.tokens.map((t) => `<button type="button" class="lesson-token ${L.orderPicked.includes(t.id) ? "is-used" : ""}" data-token-in="${t.id}" ${L.orderPicked.includes(t.id) ? "disabled" : ""}>${esc(t.w)}</button>`).join("")}</div>`;
    } else if (ex.type === "type") {
      main = `<div class="lesson-display"><span>${esc(ex.display)}</span></div>
        <input id="lesson-type-input" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" class="lesson-input" placeholder="İngilizcesini yaz…" aria-label="Cevap">`;
    }

    el.innerHTML = `
      <div class="lesson-shell">
        ${topBar()}
        <div class="lesson-body"><div class="lesson-inner">
          <h2 class="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">${esc(ex.prompt)}</h2>
          ${main}
        </div></div>
        <div class="lesson-foot" id="lesson-foot"><div class="lesson-foot-inner">
          <button type="button" class="path-btn path-btn-ghost" data-lesson-skip>Atla</button>
          <button type="button" class="path-btn path-btn-primary lesson-main-btn" data-lesson-check ${ex.type === "match" ? "hidden" : ""} disabled>Kontrol et</button>
        </div></div>
      </div>`;
    icons();
    const inp = $("lesson-type-input");
    if (inp) {
      inp.focus();
      inp.addEventListener("input", () => { L.selection = inp.value; setCheckEnabled(!!inp.value.trim()); });
    }
  }

  function setCheckEnabled(on) {
    const b = overlay().querySelector("[data-lesson-check]");
    if (b) b.disabled = !on;
  }

  const norm = (s) => String(s || "").toLowerCase().replace(/[’']/g, "'").replace(/[.,!?;:"]/g, "").replace(/\s+/g, " ").trim();
  const stripArticle = (s) => s.replace(/^(to|a|an|the) /, "");
  function lev(a, b) {
    const m = a.length, n = b.length;
    if (Math.abs(m - n) > 1) return 2;
    const d = Array.from({ length: m + 1 }, (_, i) => [i, ...Array(n).fill(0)]);
    for (let j = 1; j <= n; j++) d[0][j] = j;
    for (let i = 1; i <= m; i++) for (let j = 1; j <= n; j++)
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    return d[m][n];
  }

  function checkAnswer() {
    const L = state.lesson;
    const ex = L.current;
    if (!L || L.phase !== "exercise") return;
    let ok = false, typo = false, correctText = "";
    if (ex.type === "choice" || ex.type === "listen" || ex.type === "dialogue") {
      ok = L.selection === ex.answer; correctText = ex.type === "dialogue" && ex.tr ? `${ex.answer} (${ex.tr})` : ex.answer;
    } else if (ex.type === "quiz") {
      ok = Number(L.selection) === ex.answer; correctText = ex.full;
    } else if (ex.type === "order") {
      const built = L.orderPicked.map((id) => ex.tokens.find((t) => t.id === id).w).join(" ");
      ok = norm(built) === norm(ex.answer); correctText = ex.answer;
    } else if (ex.type === "type") {
      const a = stripArticle(norm(L.selection)), b = stripArticle(norm(ex.answer));
      ok = a === b;
      if (!ok && b.length >= 5 && lev(a, b) <= 1) { ok = true; typo = true; }
      correctText = ex.answer;
    }
    showFeedback(ok, correctText, typo);
  }

  function showFeedback(ok, correctText, typo) {
    const L = state.lesson;
    const ex = L.current;
    L.phase = "feedback";
    if (!ok) {
      if (!L.firstWrong.has(ex.key)) L.firstWrong.add(ex.key);
      L.hearts -= 1;
      // Yanlış alıştırma dersin sonunda, seçenekleri karıştırılmış olarak yeniden gelir
      const again = Object.assign({}, ex);
      if (Array.isArray(ex.options)) again.options = shuffle(ex.options);
      if (Array.isArray(ex.tokens)) again.tokens = shuffle(ex.tokens);
      L.queue.push(again);
    } else {
      L.done += 1;
    }
    if (ex.type === "choice" && ex.speakAnswer && ok) speak(ex.answer);
    else if (ex.speak && ok && ex.type !== "listen") speak(ex.speak);

    // Seçenekleri renklendir
    overlay().querySelectorAll(".lesson-option").forEach((b) => {
      const val = b.getAttribute("data-opt");
      const right = ex.type === "quiz" ? Number(val) === ex.answer : val === ex.answer;
      if (right) b.classList.add("is-right");
      else if (val === String(L.selection)) b.classList.add("is-wrong");
      b.disabled = true;
    });
    const inp = $("lesson-type-input");
    if (inp) inp.disabled = true;

    const foot = $("lesson-foot");
    const heartsGone = L.hearts <= 0;
    foot.className = `lesson-foot ${ok ? "is-right" : "is-wrong"}`;
    foot.innerHTML = `<div class="lesson-foot-inner">
        <div class="min-w-0 flex items-start gap-3">
          <span class="lesson-feedback-icon"><i data-lucide="${ok ? "check" : "x"}" class="w-6 h-6"></i></span>
          <div class="min-w-0">
            <div class="text-lg font-extrabold">${ok ? (typo ? "Doğru, küçük bir yazım hatası var" : pick(["Harika!", "Aynen böyle!", "Çok iyi!", "Doğru!"])) : "Doğru cevap:"}</div>
            ${!ok || typo ? `<div class="text-sm font-semibold break-words">${esc(correctText)}</div>` : ""}
            ${ex.type === "quiz" && ex.explain ? `<div class="text-xs mt-1 opacity-90">${esc(ex.explain)}</div>` : ""}
          </div>
        </div>
        <button type="button" class="path-btn ${ok ? "path-btn-primary" : "path-btn-danger"} lesson-main-btn shrink-0" data-lesson-next>${heartsGone ? "Bitir" : "Devam"}</button>
      </div>`;
    // Üst çubuğu güncelle
    const top = overlay().querySelector(".lesson-top");
    if (top) top.outerHTML = topBar();
    icons();
    const nb = foot.querySelector("[data-lesson-next]");
    if (nb) nb.focus();
  }

  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

  function afterFeedback() {
    const L = state.lesson;
    if (!L) return;
    if (L.hearts <= 0) return renderOutOfHearts();
    nextExercise();
  }

  function renderOutOfHearts() {
    const L = state.lesson;
    L.phase = "end";
    overlay().innerHTML = `
      <div class="lesson-shell">
        <div class="lesson-body"><div class="lesson-inner text-center pt-10">
          <div class="w-20 h-20 mx-auto rounded-full bg-rose-50 dark:bg-rose-500/10 flex items-center justify-center"><i data-lucide="heart-crack" class="w-10 h-10 text-rose-500"></i></div>
          <h2 class="mt-4 text-2xl font-extrabold text-slate-900 dark:text-white">Kalplerin bitti</h2>
          <p class="mt-2 text-sm text-slate-600 dark:text-slate-300 max-w-sm mx-auto">Sorun değil, bekleme süresi yok. Kelimelere bir kez daha göz atıp dersi baştan dene.</p>
        </div></div>
        <div class="lesson-foot"><div class="lesson-foot-inner">
          <button type="button" class="path-btn path-btn-ghost" data-lesson-close-force>Yola dön</button>
          <button type="button" class="path-btn path-btn-primary lesson-main-btn" data-lesson-retry>Tekrar dene</button>
        </div></div>
      </div>`;
    icons();
  }

  async function finishLesson() {
    const L = state.lesson;
    L.phase = "end";
    const correct = L.total - L.firstWrong.size;
    const el = overlay();
    el.innerHTML = `<div class="lesson-shell"><div class="lesson-body"><div class="lesson-inner text-center pt-16 text-sm text-slate-500">Sonuç kaydediliyor…</div></div></div>`;
    let r = null, errMsg = "";
    try {
      const res = await fetch("/api/path/result", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_id: L.nodeId, correct, total: L.total }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Sonuç kaydedilemedi.");
      r = data;
    } catch (e) {
      errMsg = e.message;
    }
    const pct = Math.round((correct / L.total) * 100);
    const stars = r ? r.stars : (pct >= 90 ? 3 : pct >= 70 ? 2 : pct >= 50 ? 1 : 0);
    const starRow = [1, 2, 3].map((n) => `<span class="lesson-big-star ${n <= stars ? "is-on" : ""}" style="--d:${n * 120}ms">★</span>`).join("");
    const next = r && r.next_topic;
    el.innerHTML = `
      <div class="lesson-shell">
        <div class="lesson-body"><div class="lesson-inner text-center pt-8">
          <div class="lesson-stars-row">${starRow}</div>
          <h2 class="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white">${stars ? (pct === 100 ? "Kusursuz!" : "Ders tamamlandı!") : "Az kaldı!"}</h2>
          <p class="mt-1 text-sm text-slate-500">${stars ? (r && r.first_completion && L.kind === "topic" ? "Sıradaki ders açıldı." : "Bilgini tazeledin.") : "Geçmek için ilk denemede en az %50 doğru gerekiyor."}</p>
          <div class="mt-6 grid grid-cols-3 gap-2.5 max-w-sm mx-auto">
            <div class="kpi-tile"><div class="text-[11px] font-semibold text-slate-500">Doğruluk</div><div class="text-xl font-extrabold text-slate-900 dark:text-white">%${pct}</div></div>
            <div class="kpi-tile"><div class="text-[11px] font-semibold text-slate-500">XP</div><div class="text-xl font-extrabold text-amber-500">+${r ? r.xp_gained : 0}</div></div>
            <div class="kpi-tile"><div class="text-[11px] font-semibold text-slate-500">Kalp</div><div class="text-xl font-extrabold text-rose-500">${L.hearts}</div></div>
          </div>
          ${errMsg ? `<p class="mt-4 text-sm font-semibold text-rose-600">${esc(errMsg)}</p>` : ""}
        </div></div>
        <div class="lesson-foot"><div class="lesson-foot-inner">
          <button type="button" class="path-btn path-btn-ghost" data-lesson-close-force>Yola dön</button>
          ${next ? `<button type="button" class="path-btn path-btn-primary lesson-main-btn" data-lesson-goto="${next}">Sonraki ders</button>`
                 : `<button type="button" class="path-btn path-btn-primary lesson-main-btn" data-lesson-retry>${stars ? "Tekrar çöz" : "Tekrar dene"}</button>`}
        </div></div>
      </div>`;
    icons();
    if (stars) speak(pick(["Well done!", "Great job!", "Excellent!"]));
    // Yolu arka planda yenile
    loadPath(state.level);
    if (typeof window.loadDashboardStats === "function" && window.appState && window.appState.activeTab === "dashboard") window.loadDashboardStats();
  }

  // Ders içi tıklamalar
  document.addEventListener("click", (ev) => {
    const el = $("lesson-overlay");
    if (!el || el.classList.contains("hidden") || !el.contains(ev.target)) return;
    const L = state.lesson;
    const t = ev.target;
    const all = t.closest("[data-speak-all]");
    if (all) {
      const d = el.querySelector(".lesson-dialogue[data-dialogue]");
      try { speakAll(JSON.parse(d.getAttribute("data-dialogue"))); } catch (_) {}
      return;
    }
    const sp = t.closest("[data-speak]");
    if (sp) { speak(sp.getAttribute("data-speak")); if (!t.closest(".lesson-option")) return; }
    const slow = t.closest("[data-speak-slow]");
    if (slow) {
      if (ttsOk()) { window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(slow.getAttribute("data-speak-slow")); u.lang = "en-US"; u.rate = 0.55; window.speechSynthesis.speak(u); }
      return;
    }
    if (t.closest("[data-lesson-close]")) return closeLesson(false);
    if (t.closest("[data-lesson-close-force]")) return closeLesson(true);
    if (t.closest("[data-lesson-start]")) return nextExercise();
    if (t.closest("[data-lesson-retry]")) { const { kind, bundle } = L; return startLesson(kind, bundle); }
    const go = t.closest("[data-lesson-goto]");
    if (go) { closeLesson(true); return openLesson("topic", go.getAttribute("data-lesson-goto")); }
    if (!L) return;
    if (t.closest("[data-lesson-next]")) return afterFeedback();
    if (t.closest("[data-lesson-check]")) return checkAnswer();
    if (t.closest("[data-lesson-skip]") && L.phase === "exercise") return showFeedback(false, answerText(L.current), false);

    if (L.phase !== "exercise") return;
    const opt = t.closest(".lesson-option");
    if (opt) {
      el.querySelectorAll(".lesson-option").forEach((b) => b.classList.toggle("is-selected", b === opt));
      L.selection = opt.getAttribute("data-opt");
      if (L.current.type === "listen") speak(L.selection);
      setCheckEnabled(true);
      return;
    }
    const tin = t.closest("[data-token-in]");
    if (tin) { L.orderPicked.push(Number(tin.getAttribute("data-token-in"))); renderOrderOnly(); return; }
    const tout = t.closest("[data-token-out]");
    if (tout) { const id = Number(tout.getAttribute("data-token-out")); L.orderPicked = L.orderPicked.filter((x) => x !== id); renderOrderOnly(); return; }
    const mb = t.closest("[data-match-side]");
    if (mb) return handleMatch(mb.getAttribute("data-match-side"), mb.getAttribute("data-match-w"));
  });

  function answerText(ex) {
    if (ex.type === "quiz") return ex.full;
    if (ex.type === "match") return ex.pairs.map((p) => `${p.en} = ${p.tr}`).join(" · ");
    return ex.answer;
  }

  function renderOrderOnly() {
    const L = state.lesson;
    const ex = L.current;
    const el = overlay();
    const line = el.querySelector(".lesson-answer-line");
    const bank = el.querySelector(".lesson-bank");
    const picked = L.orderPicked.map((id) => ex.tokens.find((t) => t.id === id));
    line.innerHTML = picked.map((t) => `<button type="button" class="lesson-token" data-token-out="${t.id}">${esc(t.w)}</button>`).join("") || '<span class="text-xs text-slate-400">Kelimelere sırayla dokun</span>';
    bank.querySelectorAll("[data-token-in]").forEach((b) => {
      const used = L.orderPicked.includes(Number(b.getAttribute("data-token-in")));
      b.classList.toggle("is-used", used);
      b.disabled = used;
    });
    setCheckEnabled(L.orderPicked.length > 0);
  }

  function handleMatch(side, w) {
    const L = state.lesson;
    const m = L.matchState;
    if (side === "en") speak(w);
    if (!m.pick || m.pick.side === side) {
      m.pick = { side, w };
      renderExercise();
      return;
    }
    const en = side === "en" ? w : m.pick.w;
    const tr = side === "tr" ? w : m.pick.w;
    const pair = L.current.pairs.find((p) => p.en === en);
    m.pick = null;
    if (pair && pair.tr === tr) {
      m.done.add(en);
      renderExercise();
      if (m.done.size === L.current.pairs.length) {
        // Eşleştirmede yanlış dokunuş kalp götürmez; 1'den fazla hata ilk deneme doğrusunu bozar
        L.phase = "exercise";
        if (m.misses > 1) L.firstWrong.add(L.current.key);
        L.done += 1;
        L.phase = "feedback";
        const foot = $("lesson-foot");
        foot.className = "lesson-foot is-right";
        foot.innerHTML = `<div class="lesson-foot-inner">
            <div class="flex items-center gap-3"><span class="lesson-feedback-icon"><i data-lucide="check" class="w-6 h-6"></i></span>
            <div class="text-lg font-extrabold">${m.misses ? "Tamamlandı" : "Hepsi doğru!"}</div></div>
            <button type="button" class="path-btn path-btn-primary lesson-main-btn" data-lesson-next>Devam</button></div>`;
        const top = overlay().querySelector(".lesson-top");
        if (top) top.outerHTML = topBar();
        icons();
        foot.querySelector("[data-lesson-next]").focus();
      }
    } else {
      m.misses += 1;
      renderExercise();
      overlay().querySelectorAll(`[data-match-w="${CSS.escape(w)}"]`).forEach((b) => { b.classList.add("is-shake"); });
    }
  }

  // Klavye: 1–4 seçenek, Enter kontrol/devam, Esc kapat
  document.addEventListener("keydown", (ev) => {
    const el = $("lesson-overlay");
    if (!el || el.classList.contains("hidden") || !state.lesson) return;
    const L = state.lesson;
    if (ev.key === "Escape") { ev.preventDefault(); return closeLesson(false); }
    if (ev.key === "Enter") {
      const b = el.querySelector("[data-lesson-next], [data-lesson-start], [data-lesson-check]:not([disabled]):not([hidden])");
      if (b && document.activeElement !== b) { ev.preventDefault(); b.click(); }
      return;
    }
    if (L.phase === "exercise" && /^[1-4]$/.test(ev.key) && document.activeElement && document.activeElement.id !== "lesson-type-input") {
      const opts = el.querySelectorAll(".lesson-option");
      const o = opts[Number(ev.key) - 1];
      if (o) { ev.preventDefault(); o.click(); }
    }
  });

  window.loadLessonPath = loadPath;
  window.openLessonNode = openLesson;
})();
