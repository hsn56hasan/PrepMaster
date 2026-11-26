// PrepKampüs — girişsiz ziyaretçinin gördüğü premium tanıtım sayfası (#pk-landing).
// Okul şeridi ve okul seçici /api/universities verisinden kurulur; bağlantı yoksa yerleşik liste kullanılır.
// Giriş paneli app.js'deki landingGo()/closeAuthSheet() ile açılıp kapanır.
(function () {
  "use strict";

  const FALLBACK = [
    ["itu", "İTÜ", "İTÜ Proficiency Sınavı", 60, 150, 60], ["metu", "ODTÜ", "İYS / EPE (İngilizce Yeterlik Sınavı)", 60, 145, 46],
    ["boun", "Boğaziçi", "BUEPT", 60, 210, 50], ["bilkent", "Bilkent", "PAE (Proficiency in Academic English)", 60, 180, 55],
    ["ytu", "YTÜ", "YTÜ İYS (İngilizce Yeterlik Sınavı)", 60, 150, 60], ["hacettepe", "Hacettepe", "YDYO Muafiyet ve Düzey Belirleme Sınavı", 65, 160, 70],
    ["koc", "Koç Üni", "KUEPE (Koç University English Proficiency Exam)", 65, 180, 55], ["sabanci", "Sabancı", "ELAE (English Language Assessment Exam)", 65, 190, 50],
  ];

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  let schools = FALLBACK;

  function renderMarquee() {
    const track = $("pk-marquee");
    if (!track) return;
    const names = schools.map((s) => s[1]);
    track.innerHTML = [...names, ...names]
      .map((n, i) => `<span${i >= names.length ? ' aria-hidden="true"' : ""}>${esc(n)}</span>`).join("");
  }

  function showSchool(i) {
    const s = schools[i];
    if (!s) return;
    const list = $("pk-school-list");
    if (list) list.querySelectorAll(".pk-school-chip").forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.i) === i)));
    $("pk-sc-short").textContent = s[1];
    $("pk-sc-exam").textContent = s[2];
    $("pk-sc-q").textContent = s[5];
    $("pk-sc-d").textContent = s[4];
    $("pk-sc-p").textContent = s[3];
    const cta = $("pk-sc-cta");
    if (cta && cta.firstChild) cta.firstChild.textContent = `${s[1]} hazırlığına başla `;
  }

  function renderSchools() {
    const list = $("pk-school-list");
    if (!list) return;
    list.innerHTML = schools
      .map((s, i) => `<button type="button" class="pk-school-chip" data-i="${i}" aria-pressed="${i === 0}">${esc(s[1])}</button>`).join("");
    showSchool(0);
  }

  async function loadSchools() {
    try {
      const res = await fetch("/api/universities");
      if (!res.ok) return;
      const data = await res.json();
      const list = (Array.isArray(data) ? data : data.universities || [])
        .filter((u) => u && u.id && u.id !== "general")
        .map((u) => [u.id, u.short_name || u.name, u.exam_name || u.name, u.passing_score, u.duration_minutes, u.total_questions]);
      if (list.length) {
        schools = list;
        renderMarquee();
        renderSchools();
      }
    } catch (_) { /* yerleşik liste kalır */ }
  }

  function initReveal(root) {
    // İlk ekran (hero) gözlemci beklemeden görünür; gerisi kaydırdıkça belirir
    root.querySelectorAll(".pk-hero .pk-reveal").forEach((el) => el.classList.add("is-in"));
    const els = root.querySelectorAll(".pk-reveal:not(.is-in)");
    if (!("IntersectionObserver" in window)) { els.forEach((el) => el.classList.add("is-in")); return; }
    const scroller = $("auth-modal");
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { root: scroller, rootMargin: "0px 0px -8% 0px" });
    els.forEach((el) => io.observe(el));
  }

  function init() {
    const root = $("pk-landing");
    if (!root) return;
    renderMarquee();
    renderSchools();
    loadSchools();
    initReveal(root);

    const modal = $("auth-modal");
    const nav = $("pk-nav");
    if (modal && nav) {
      const onScroll = () => nav.classList.toggle("is-scrolled", modal.scrollTop > 8);
      modal.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }

    root.addEventListener("click", (e) => {
      const chip = e.target.closest(".pk-school-chip");
      if (chip) { showSchool(Number(chip.dataset.i)); return; }
      const link = e.target.closest("a[data-pk-scroll]");
      if (link) {
        const target = document.querySelector(link.getAttribute("href"));
        if (target) { e.preventDefault(); target.scrollIntoView({ behavior: "smooth", block: "start" }); }
      }
    });

    if (window.lucide) window.lucide.createIcons();
  }

  // Çerez/yerel depolama bilgilendirmesi: yalnızca zorunlu depolama kullanıldığı için tek düğmeli bilgi bandı
  const COOKIE_NOTICE_VERSION = "2026-11-25";
  function initCookieNotice() {
    const box = $("cookie-notice");
    if (!box) return;
    let seen = null;
    try { seen = localStorage.getItem("pk_cookie_notice"); } catch (_) {}
    if (seen === COOKIE_NOTICE_VERSION) return;
    box.classList.remove("hidden");
    const ok = $("cookie-notice-ok");
    if (ok) ok.addEventListener("click", () => {
      try { localStorage.setItem("pk_cookie_notice", COOKIE_NOTICE_VERSION); } catch (_) {}
      box.classList.add("hidden");
    });
  }

  function boot() { init(); initCookieNotice(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
