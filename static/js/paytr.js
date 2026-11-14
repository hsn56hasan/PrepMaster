// PrepMaster — PayTR iFrame ödemesi
//
// Akış: telefon -> /api/payment/paytr/token (sunucu 'pending' sipariş açar) -> PayTR'nin
// güvenli sayfası bu pencerede açılır (kart bilgisi PrepMaster'a hiç gelmez) -> sunucuya
// sipariş durumu sorulur. Kilit YALNIZCA PayTR'nin sunucuya gönderdiği imzalı bildirimle
// açılır; tarayıcıdaki "başarılı" sayfası tek başına hiçbir şeyi açmaz.
(function () {
  const POLL_MS = 3000;
  const POLL_MAX_MS = 15 * 60 * 1000;
  let pollTimer = null;
  let pollStarted = 0;
  let activeOid = null;

  const $ = (id) => document.getElementById(id);

  async function getConfig() {
    if (window.appState && window.appState.config) return window.appState.config;
    try {
      const res = await fetch("/api/config");
      if (res.ok) {
        const cfg = await res.json();
        if (window.appState) window.appState.config = cfg;
        return cfg;
      }
    } catch (_) {}
    return {};
  }

  function show(id, visible) {
    const el = $(id);
    if (el) el.classList.toggle("hidden", !visible);
  }

  function setMsg(text, ok) {
    const el = $("paytr-msg");
    if (!el) return;
    if (!text) { el.classList.add("hidden"); return; }
    el.className = "p-3 rounded-xl text-xs font-semibold " +
      (ok ? "bg-emerald-50 border border-emerald-200 text-emerald-800" : "bg-rose-50 border border-rose-200 text-rose-700");
    el.innerText = text;
  }

  function stopPolling() {
    if (pollTimer) clearTimeout(pollTimer);
    pollTimer = null;
  }

  function resetPaytrView() {
    stopPolling();
    activeOid = null;
    show("paytr-step-phone", true);
    show("paytr-step-frame", false);
    show("paytr-step-done", false);
    const holder = $("paytr-frame-holder");
    if (holder) holder.innerHTML = "";
    const btn = $("btn-paytr-start");
    if (btn) btn.disabled = false;
    setMsg("");
  }

  function loadIframeResizer() {
    return new Promise((resolve) => {
      if (window.iFrameResize) return resolve();
      const s = document.createElement("script");
      s.src = "https://www.paytr.com/js/iframeResizer.min.js";
      s.onload = () => resolve();
      s.onerror = () => resolve(); // boyutlandırıcı olmadan da çalışır (sabit yükseklik)
      document.head.appendChild(s);
    });
  }

  async function checkOrder(oid) {
    const res = await fetch(`/api/payment/paytr/orders/${encodeURIComponent(oid)}`);
    if (!res.ok) return null;
    return res.json();
  }

  function onPaid(order) {
    stopPolling();
    try { sessionStorage.removeItem("pm_paytr_oid"); } catch (_) {}
    if (window.appState && window.appState.currentUser) {
      window.appState.currentUser.unlocked_universities = order.unlocked_universities || [];
      localStorage.setItem("auth_user", JSON.stringify(window.appState.currentUser));
    }
    show("paytr-step-frame", false);
    show("paytr-step-done", true);
    setMsg("");
    if (typeof showNotification === "function") {
      showNotification(`✓ ${String(order.university_id).toUpperCase()} paketi açıldı!`, "emerald");
    }
    if (window.lucide) window.lucide.createIcons();
  }

  function onFailed(text) {
    stopPolling();
    try { sessionStorage.removeItem("pm_paytr_oid"); } catch (_) {}
    show("paytr-step-frame", false);
    show("paytr-step-phone", true);
    const btn = $("btn-paytr-start");
    if (btn) btn.disabled = false;
    setMsg(text, false);
  }

  async function pollOnce() {
    if (!activeOid) return;
    try {
      const order = await checkOrder(activeOid);
      if (order && order.status === "success") return onPaid(order);
      if (order && (order.status === "failed" || order.status === "amount_mismatch")) {
        return onFailed("Ödeme tamamlanamadı; kartınızdan para çekilmedi. Tekrar deneyebilirsiniz.");
      }
    } catch (_) {}
    if (Date.now() - pollStarted > POLL_MAX_MS) {
      return onFailed("Ödeme sonucu alınamadı. Kartınızdan çekim yapıldıysa paket birkaç dakika içinde açılır; sayfayı yenileyin.");
    }
    pollTimer = setTimeout(pollOnce, POLL_MS);
  }

  window.startPaytrPayment = async function () {
    const uniId = window.currentPaywallTargetUniId;
    const phone = ($("paytr-phone")?.value || "").trim();
    if (!uniId) return;
    if (phone.replace(/\D/g, "").length < 10) {
      setMsg("Lütfen cep telefonunuzu girin (05XX XXX XX XX).", false);
      return;
    }
    const btn = $("btn-paytr-start");
    btn.disabled = true;
    setMsg("");
    try {
      const res = await fetch("/api/payment/paytr/token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ university_id: uniId, user_phone: phone }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const d = data.detail;
        throw new Error(Array.isArray(d) ? (d[0]?.msg || "Bilgileri kontrol edin.").replace(/^Value error, /, "") : (d || "Ödeme başlatılamadı."));
      }
      activeOid = data.merchant_oid;
      try { sessionStorage.setItem("pm_paytr_oid", activeOid); } catch (_) {}

      await loadIframeResizer();
      const holder = $("paytr-frame-holder");
      holder.innerHTML = "";
      const frame = document.createElement("iframe");
      frame.id = "paytriframe";
      frame.src = data.iframe_url;
      frame.setAttribute("frameborder", "0");
      frame.setAttribute("scrolling", "no");
      frame.style.width = "100%";
      frame.style.minHeight = "420px";
      frame.title = "PayTR güvenli ödeme";
      holder.appendChild(frame);
      if (window.iFrameResize) {
        try { window.iFrameResize({}, "#paytriframe"); } catch (_) {}
      }
      show("paytr-step-phone", false);
      show("paytr-step-frame", true);

      pollStarted = Date.now();
      pollTimer = setTimeout(pollOnce, POLL_MS);
    } catch (err) {
      btn.disabled = false;
      setMsg(err.message, false);
    }
  };

  // PayTR penceresi ödeme sonunda /odeme-sonuc sayfasını açar; o sayfa bize haber verir.
  window.addEventListener("message", (ev) => {
    if (ev.origin !== window.location.origin) return;
    if (!ev.data || ev.data.kaynak !== "prepmaster-odeme" || !activeOid) return;
    stopPolling();
    if (ev.data.durum === "basarili") {
      const msg = $("paytr-wait-msg");
      if (msg) msg.innerText = "Ödeme onayı bekleniyor…";
    }
    pollStarted = Date.now();
    pollOnce();
  });

  // Ödeme penceresi açılırken doğru görünümü seç
  const prevOpen = window.openUniversityPaywallModal;
  window.openUniversityPaywallModal = async function (targetUniId, onUnlockCallback = null) {
    if (prevOpen) prevOpen(targetUniId, onUnlockCallback);
    resetPaytrView();
    const cfg = await getConfig();
    const paytr = !!cfg.paytr_configured;
    const demo = !!cfg.demo_mode;
    // Gerçek ödeme açıksa kart formu (simülasyon) hiç gösterilmez
    show("paywall-view-card", !paytr && demo);
    show("paywall-view-paytr", paytr);
    show("paywall-view-unavailable", !paytr && !demo);
    if (window.lucide) window.lucide.createIcons();
  };

  const prevClose = window.closeUniversityPaywallModal;
  window.closeUniversityPaywallModal = function () {
    stopPolling();
    if (prevClose) prevClose();
  };

  // Ödeme pencere DIŞINDA tamamlandıysa (ör. 3D Secure sayfası tam ekrana geçtiyse) ana sayfaya
  // /?odeme=… ile dönülür: son siparişin durumunu sor ve sonucu bildir.
  async function resumeAfterRedirect() {
    const params = new URLSearchParams(location.search);
    if (!params.has("odeme")) return;
    history.replaceState(null, "", location.pathname);
    let oid = null;
    try { oid = sessionStorage.getItem("pm_paytr_oid"); } catch (_) {}
    if (!oid) return;
    for (let i = 0; i < 20; i++) {
      const order = await checkOrder(oid).catch(() => null);
      if (order && order.status === "success") {
        try { sessionStorage.removeItem("pm_paytr_oid"); } catch (_) {}
        if (typeof showNotification === "function") showNotification(`✓ ${String(order.university_id).toUpperCase()} paketi açıldı!`, "emerald");
        if (typeof reloadUserData === "function") reloadUserData();
        return;
      }
      if (order && order.status !== "pending") {
        try { sessionStorage.removeItem("pm_paytr_oid"); } catch (_) {}
        if (typeof showNotification === "function") showNotification("Ödeme tamamlanamadı; kartınızdan para çekilmedi.", "rose");
        return;
      }
      await new Promise((r) => setTimeout(r, POLL_MS));
    }
  }
  if (document.readyState === "complete") resumeAfterRedirect();
  else window.addEventListener("load", resumeAfterRedirect);
})();
