// Site duyurusu: yönetici panelinden açılan şerit (metin yalnızca textContent ile basılır).
// Kapatma tercihi yalnızca bu tarayıcı oturumunda (sessionStorage) tutulur.
(function () {
  const TONES = {
    info: "background:#0369a1;color:#fff",
    success: "background:#047857;color:#fff",
    warning: "background:#f59e0b;color:#1c1917",
  };

  function keyFor(a) {
    return "pk_ann_closed:" + (a.text || "").slice(0, 120);
  }

  async function showAnnouncement() {
    let a;
    try {
      const res = await fetch("/api/site/announcement", { cache: "no-store" });
      if (!res.ok) return;
      a = await res.json();
    } catch (_) {
      return;
    }
    if (!a || !a.enabled || !a.text) return;
    try {
      if (sessionStorage.getItem(keyFor(a))) return;
    } catch (_) {}

    const bar = document.createElement("div");
    bar.id = "site-announcement";
    bar.setAttribute("role", "status");
    // Sayfanın üstündeki sabit menüleri kapatmasın diye altta, ortada yüzen şerit olarak gösterilir.
    const cookie = document.getElementById("cookie-notice");
    const cookieRect = cookie ? cookie.getBoundingClientRect() : null;
    const cookieH = cookieRect && cookieRect.height > 0 ? cookieRect.height + 12 : 0;
    bar.style.cssText = (TONES[a.tone] || TONES.info) +
      `;position:fixed;left:50%;bottom:${16 + cookieH}px;transform:translateX(-50%);width:min(760px,calc(100% - 24px));z-index:80;` +
      "display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:6px 12px;padding:11px 44px 11px 18px;border-radius:14px;" +
      "box-shadow:0 12px 32px rgba(0,0,0,.28);font:600 13px/1.4 'Plus Jakarta Sans',sans-serif;text-align:center";
    const text = document.createElement("span");
    text.textContent = a.text;
    bar.appendChild(text);
    if (a.link_url && (a.link_url.startsWith("https://") || (a.link_url.startsWith("/") && !a.link_url.startsWith("//")))) {
      const link = document.createElement("a");
      link.href = a.link_url;
      link.textContent = (a.link_text || "Ayrıntılar") + " →";
      link.style.cssText = "color:inherit;text-decoration:underline;font-weight:800;white-space:nowrap";
      if (a.link_url.startsWith("https://")) {
        link.target = "_blank";
        link.rel = "noopener";
      }
      bar.appendChild(link);
    }
    const close = document.createElement("button");
    close.type = "button";
    close.setAttribute("aria-label", "Duyuruyu kapat");
    close.textContent = "×";
    close.style.cssText = "position:absolute;right:10px;top:50%;transform:translateY(-50%);background:transparent;border:0;color:inherit;font-size:20px;line-height:1;cursor:pointer;padding:4px 8px";
    close.onclick = () => {
      bar.remove();
      try { sessionStorage.setItem(keyFor(a), "1"); } catch (_) {}
    };
    bar.appendChild(close);
    document.body.appendChild(bar);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", showAnnouncement);
  else showAnnouncement();
})();
