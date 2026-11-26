// PrepKampüs Yönetim Paneli — sekmeler: genel bakış, öğrenciler, siparişler, destek, KVKK & izinler,
// içerik (soru bankası), site duyurusu, yönetici kayıtları ve sistem.
// admin.html içindeki esc(), adminFetch(), showAdminToast(), getUniLabel() fonksiyonlarını kullanır.
(function () {
  const TABS = ["overview", "students", "orders", "support", "consents", "content", "announcement", "audit", "system"];
  const ORDER_STATUS = {
    success: ["Başarılı", "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"],
    pending: ["Bekliyor", "bg-amber-500/15 text-amber-300 border-amber-500/30"],
    failed: ["Başarısız", "bg-rose-500/15 text-rose-300 border-rose-500/30"],
    amount_mismatch: ["Tutar uyuşmazlığı", "bg-rose-500/15 text-rose-300 border-rose-500/30"],
  };
  const TICKET_STATUS = { open: "Açık", in_progress: "İşlemde", answered: "Cevaplandı", closed: "Kapandı" };
  const AUDIT_LABELS = {
    student_access: "Öğrenci erişimi güncellendi",
    student_password_reset: "Öğrenci şifresi değiştirildi",
    student_delete: "Öğrenci silindi",
    ticket_update: "Destek talebi güncellendi",
    announcement_update: "Site duyurusu güncellendi",
    question_update: "Soru düzeltildi/gizlendi",
    export_students: "Öğrenci listesi indirildi",
    export_marketing_consents: "Ticari ileti onay listesi indirildi",
    export_orders: "Sipariş listesi indirildi",
    backup_download: "Veritabanı yedeği indirildi",
  };
  let currentTab = "overview";
  let contentState = { items: [], categories: [] };

  const $ = (id) => document.getElementById(id);
  const fmtDate = (v) => (v ? new Date(String(v).replace(" ", "T") + (String(v).length <= 19 ? "Z" : "")).toLocaleString("tr-TR", { dateStyle: "short", timeStyle: "short" }) : "-");
  const tl = (n) => `${Number(n || 0).toLocaleString("tr-TR", { minimumFractionDigits: 0, maximumFractionDigits: 2 })} TL`;
  const card = (label, value, sub = "", color = "text-white") => `
    <div class="p-4 bg-slate-900 border border-slate-800 rounded-2xl">
      <div class="text-slate-400 text-xs font-semibold mb-1">${esc(label)}</div>
      <div class="text-2xl font-black ${color}">${esc(value)}</div>
      ${sub ? `<div class="text-[11px] text-slate-500 mt-0.5">${esc(sub)}</div>` : ""}
    </div>`;
  const empty = (cols, text) => `<tr><td colspan="${cols}" class="py-8 text-center text-slate-500 font-semibold">${esc(text)}</td></tr>`;

  async function getJson(url) {
    const res = await adminFetch(url);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "İstek başarısız.");
    return data;
  }

  async function sendJson(url, method, body) {
    const res = await adminFetch(url, { method, body: JSON.stringify(body) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const d = data.detail;
      throw new Error(typeof d === "string" ? d : Array.isArray(d) ? d.map((x) => x.msg).join(", ") : "Kaydedilemedi.");
    }
    return data;
  }

  // Yetki başlığı gerektiği için CSV'ler bağlantıyla değil, istekle indirilir.
  async function downloadAdminFile(url, fallbackName) {
    try {
      const res = await adminFetch(url);
      if (!res.ok) throw new Error("İndirilemedi.");
      const blob = await res.blob();
      const m = (res.headers.get("content-disposition") || "").match(/filename="?([^";]+)"?/);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = m ? m[1] : fallbackName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 5000);
      showAdminToast("✓ Dosya indirildi.");
    } catch (err) {
      showAdminToast("Hata: " + err.message, "rose");
    }
  }

  function adminShowTab(name) {
    if (!TABS.includes(name)) name = "overview";
    currentTab = name;
    document.querySelectorAll("[data-admin-tab]").forEach((s) => s.classList.toggle("hidden", s.dataset.adminTab !== name));
    document.querySelectorAll("[data-admin-nav]").forEach((b) => {
      const on = b.dataset.adminNav === name;
      b.className = `px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 whitespace-nowrap ${on ? "bg-indigo-600 text-white shadow" : "text-slate-300 hover:bg-slate-800"}`;
    });
    if (location.hash !== "#" + name) history.replaceState(null, "", "#" + name);
    const loaders = {
      overview: loadOverview, orders: loadOrders, support: loadSupport, consents: loadConsents,
      content: loadContent, announcement: loadAnnouncement, audit: loadAudit,
    };
    if (loaders[name]) loaders[name]().catch((e) => showAdminToast("Hata: " + e.message, "rose"));
    if (window.lucide) window.lucide.createIcons();
  }

  // ---------------- Genel bakış ----------------
  async function loadOverview() {
    const d = await getJson("/api/admin/overview");
    const u = d.users, r = d.revenue, o = d.orders, t = d.tickets, l = d.learning, c = d.content, s = d.system;
    $("ov-kpis").innerHTML = [
      card("Toplam öğrenci", u.total, `Son 7 gün +${u.new_7d} • Son 30 gün +${u.new_30d}`),
      card("Aktif öğrenci", u.active_today, `Bugün • Son 7 gün ${u.active_7d}`, "text-emerald-400"),
      card("Belgesi doğrulanan", u.verified, `Seviye tespiti yapan ${u.placement_done}`, "text-sky-400"),
      card("Toplam gelir", tl(r.total_try), `Son 30 gün ${tl(r.last_30d_try)} • ${r.paying_users} ödeyen öğrenci`, "text-teal-400"),
      card("Siparişler", o.success, `Başarılı • bekleyen ${o.pending} • başarısız ${o.failed + o.amount_mismatch}`, "text-indigo-300"),
      card("Açık destek talebi", t.open + t.in_progress, `Cevaplanan ${t.answered} • kapanan ${t.closed}`, (t.open + t.in_progress) ? "text-amber-400" : "text-white"),
      card("Çözülen deneme", l.exams, `Son 7 günde ${l.questions_answered_7d} soru cevaplandı`),
      card("Ticari ileti onayı", u.marketing_consent, "Kampanya e-postası gönderilebilecek öğrenci", "text-fuchsia-300"),
    ].join("");

    const maxSign = Math.max(1, ...d.daily.map((x) => x.signups));
    $("ov-chart").innerHTML = d.daily.map((x) => `
      <div class="flex-1 flex flex-col items-center gap-1 min-w-0" title="${esc(x.day)}: ${x.signups} kayıt, ${x.sales} satış">
        <div class="text-[10px] text-slate-400">${x.signups || ""}</div>
        <div class="w-full rounded-t-md bg-indigo-500/70" style="height:${Math.round((x.signups / maxSign) * 110) + 2}px"></div>
        <div class="text-[9px] text-emerald-400 h-3">${x.sales ? x.sales + " satış" : ""}</div>
        <div class="text-[9px] text-slate-500">${esc(x.day.slice(8, 10))}.${esc(x.day.slice(5, 7))}</div>
      </div>`).join("");

    $("ov-unis").innerHTML = (d.top_universities || []).map((x) => `
      <div class="flex items-center justify-between py-1.5 border-b border-slate-800/70 text-xs">
        <span class="font-bold text-slate-200">${esc(getUniLabel(x.university_id))}</span><span class="text-slate-400">${esc(x.n)} öğrenci</span>
      </div>`).join("") || `<div class="text-xs text-slate-500">Henüz kayıt yok.</div>`;

    $("ov-content").innerHTML = [
      ["Soru bankası", `${c.questions.toLocaleString("tr-TR")} soru (${c.questions_live.toLocaleString("tr-TR")} yayında)`],
      ["Konu Yolu", `${c.lessons} ders`], ["Kelime kartı", c.vocabulary], ["Dinleme", c.listening],
      ["Konuşma görevi", c.speaking], ["Writing rehberi", c.writing_guides], ["Üniversite", c.universities],
    ].map(([k, v]) => `<div class="flex justify-between py-1.5 border-b border-slate-800/70 text-xs"><span class="text-slate-400">${esc(k)}</span><span class="font-bold text-slate-200">${esc(v)}</span></div>`).join("");

    const flag = (ok, yes, no) => `<span class="px-2 py-0.5 rounded-md text-[11px] font-bold ${ok ? "bg-emerald-500/15 text-emerald-300" : "bg-amber-500/15 text-amber-300"}">${ok ? yes : no}</span>`;
    $("ov-system").innerHTML = `
      <div class="flex justify-between py-1.5 text-xs"><span class="text-slate-400">PayTR ödeme</span>${flag(s.paytr_configured, "Bağlı", "Yapılandırılmadı")}</div>
      <div class="flex justify-between py-1.5 text-xs"><span class="text-slate-400">E-posta gönderimi</span>${flag(s.email_configured, "Aktif", "Anahtar bekleniyor")}</div>
      <div class="flex justify-between py-1.5 text-xs"><span class="text-slate-400">Ortam</span>${flag(s.production && !s.demo_mode, "Canlı", s.demo_mode ? "Demo modu" : "Geliştirme")}</div>`;
  }

  // ---------------- Siparişler ----------------
  async function loadOrders() {
    const p = new URLSearchParams();
    if ($("orders-status").value) p.set("status", $("orders-status").value);
    if ($("orders-search").value.trim()) p.set("search", $("orders-search").value.trim());
    const d = await getJson("/api/admin/orders?" + p);
    const rows = d.orders || [];
    const total = rows.filter((x) => x.status === "success").reduce((a, x) => a + x.amount_try, 0);
    $("orders-summary").textContent = `${rows.length} sipariş • listelenen başarılı tutar ${tl(total)}`;
    $("orders-tbody").innerHTML = rows.length ? rows.map((x) => {
      const [label, cls] = ORDER_STATUS[x.status] || [x.status, "bg-slate-800 text-slate-300 border-slate-700"];
      return `<tr class="hover:bg-slate-800/40">
        <td class="py-3 px-4 font-mono text-[11px] text-slate-300">${esc(x.merchant_oid)}<div class="text-[10px] text-slate-500">${esc(fmtDate(x.created_at))}</div></td>
        <td class="py-3 px-4">${x.user_id ? `<button class="font-bold text-indigo-300 hover:underline" onclick="openStudentDetail(${Number(x.user_id)})">${esc(x.full_name || "Öğrenci #" + x.user_id)}</button>` : "-"}<div class="text-[11px] text-slate-400">${esc(x.email || "")}</div></td>
        <td class="py-3 px-4 font-bold text-slate-200">${esc(getUniLabel(x.university_id))}</td>
        <td class="py-3 px-4 font-black text-white">${esc(tl(x.amount_try))}</td>
        <td class="py-3 px-4"><span class="px-2.5 py-1 rounded-lg border text-[11px] font-bold ${cls}">${esc(label)}</span>${x.failed_reason ? `<div class="text-[10px] text-rose-300 mt-1 max-w-[220px]">${esc(x.failed_reason)}</div>` : ""}</td>
      </tr>`;
    }).join("") : empty(5, "Bu filtreye uygun sipariş yok.");
  }

  // ---------------- Destek ----------------
  async function loadSupport() {
    const st = $("support-status").value;
    const d = await getJson("/api/admin/tickets" + (st ? "?status=" + encodeURIComponent(st) : ""));
    const rows = d.tickets || [];
    $("support-count").textContent = `${rows.length} talep`;
    $("support-list").innerHTML = rows.length ? rows.map((t) => `
      <div class="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-3">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div class="text-xs font-black text-white">#${esc(t.id)} • ${esc(t.full_name || "Ziyaretçi")} ${t.user_id ? `<button class="ml-1 text-indigo-300 hover:underline font-bold" onclick="openStudentDetail(${Number(t.user_id)})">öğrenci #${esc(t.user_id)}</button>` : ""}</div>
            <div class="text-[11px] text-slate-400">${esc(t.email || "-")}${t.phone ? " • " + esc(t.phone) : ""} • ${esc(fmtDate(t.created_at))}</div>
          </div>
          <span class="px-2.5 py-1 bg-blue-500/15 text-blue-300 border border-blue-500/30 rounded-lg font-bold text-[11px]">${esc(t.category || "Genel")}</span>
        </div>
        <div class="text-xs text-slate-200 whitespace-pre-wrap break-words bg-slate-950/60 border border-slate-800 rounded-xl p-3">${esc(t.message || "")}</div>
        <div class="flex flex-col md:flex-row gap-2 md:items-start">
          <select id="ticket-status-${t.id}" class="px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 font-bold">
            ${Object.entries(TICKET_STATUS).map(([k, v]) => `<option value="${k}" ${t.status === k ? "selected" : ""}>${v}</option>`).join("")}
          </select>
          <textarea id="ticket-note-${t.id}" rows="2" maxlength="2000" placeholder="Yönetici notu (öğrenciye gösterilmez): ne yapıldı, nasıl cevaplandı..." class="flex-1 p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white">${esc(t.admin_note || "")}</textarea>
          <div class="flex gap-2">
            ${t.email ? `<a href="mailto:${esc(t.email)}?subject=${encodeURIComponent("PrepKampüs destek talebiniz #" + t.id)}" class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-bold">E-posta yaz</a>` : ""}
            <button onclick="saveTicket(${Number(t.id)})" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black">Kaydet</button>
          </div>
        </div>
        ${t.updated_at ? `<div class="text-[10px] text-slate-500">Son güncelleme: ${esc(fmtDate(t.updated_at))}</div>` : ""}
      </div>`).join("") : `<div class="p-8 text-center text-xs text-slate-500 bg-slate-900 border border-slate-800 rounded-2xl">Bu durumda destek talebi yok.</div>`;
  }

  async function saveTicket(id) {
    try {
      await sendJson(`/api/admin/tickets/${id}`, "PATCH", { status: $(`ticket-status-${id}`).value, admin_note: $(`ticket-note-${id}`).value });
      showAdminToast("✓ Destek talebi güncellendi.");
      loadSupport();
    } catch (err) {
      showAdminToast("Hata: " + err.message, "rose");
    }
  }

  // ---------------- KVKK & izinler ----------------
  const DOC_LABELS = {
    kullanici_sozlesmesi: "Kullanıcı Sözleşmesi", aydinlatma_metni: "KVKK Aydınlatma Metni", ticari_ileti: "Ticari İleti Onayı",
    acik_riza: "Açık Rıza (eski kayıtlar)", on_bilgilendirme: "Ön Bilgilendirme", mesafeli_satis: "Mesafeli Satış Sözleşmesi",
  };
  const ACTION_LABELS = { accepted: "Kabul", acknowledged: "Okundu", granted: "Onay verildi", withdrawn: "Geri çekildi", declined: "Reddedildi" };

  async function loadConsents() {
    const d = await getJson("/api/admin/consents");
    $("consents-marketing-count").textContent = d.marketing_count;
    $("consents-summary").innerHTML = (d.by_document || []).length ? d.by_document.map((x) => `
      <tr class="hover:bg-slate-800/40"><td class="py-2.5 px-4 font-bold text-slate-200">${esc(DOC_LABELS[x.doc_key] || x.doc_key)}</td>
      <td class="py-2.5 px-4 text-slate-300">${esc(ACTION_LABELS[x.action] || x.action)}</td>
      <td class="py-2.5 px-4 font-black text-white">${esc(x.n)}</td><td class="py-2.5 px-4 text-slate-400">${esc(fmtDate(x.last_at))}</td></tr>`).join("") : empty(4, "Henüz onay kaydı yok.");
    $("consents-marketing").innerHTML = (d.marketing || []).length ? d.marketing.map((x) => `
      <tr class="hover:bg-slate-800/40"><td class="py-2 px-4"><button class="font-bold text-indigo-300 hover:underline" onclick="openStudentDetail(${Number(x.id)})">${esc(x.full_name || "#" + x.id)}</button></td>
      <td class="py-2 px-4 text-slate-300">${esc(x.email)}</td><td class="py-2 px-4 text-slate-400">${esc(fmtDate(x.marketing_consent_at))}</td></tr>`).join("") : empty(3, "Ticari ileti onayı veren öğrenci yok.");
  }

  // ---------------- İçerik (soru bankası) ----------------
  async function loadContent() {
    const p = new URLSearchParams({ limit: "40" });
    [["content-search", "search"], ["content-category", "category"], ["content-level", "level"], ["content-uni", "university_id"], ["content-state", "state"]]
      .forEach(([id, key]) => { const v = ($(id).value || "").trim(); if (v) p.set(key, v); });
    const d = await getJson("/api/admin/questions?" + p);
    contentState.items = d.questions || [];
    const catSel = $("content-category");
    if (catSel.options.length <= 1) {
      catSel.innerHTML = `<option value="">Tüm kategoriler</option>` + d.categories.map(([c, n]) => `<option value="${esc(c)}">${esc(c)} (${n})</option>`).join("");
    }
    const levels = ["A1", "A2", "B1", "B2", "C1", "C2"];
    $("content-matrix").innerHTML = `
      <thead><tr class="text-[11px] text-slate-400 uppercase"><th class="py-2 px-3 text-left">Kategori</th>${levels.map((l) => `<th class="py-2 px-3">${l}</th>`).join("")}<th class="py-2 px-3">Toplam</th></tr></thead>
      <tbody class="divide-y divide-slate-800/80">${d.categories.map(([cat, n]) => `<tr><td class="py-1.5 px-3 font-bold text-slate-200 text-left">${esc(cat)}</td>${levels.map((l) => `<td class="py-1.5 px-3 text-center text-slate-300">${esc((d.matrix[cat] || {})[l] || 0)}</td>`).join("")}<td class="py-1.5 px-3 text-center font-black text-white">${esc(n)}</td></tr>`).join("")}</tbody>`;
    $("content-stats").textContent = `${d.total} sonuç • gizlenen ${d.hidden_count} • düzeltilen ${d.edited_count}`;
    $("content-list").innerHTML = contentState.items.length ? contentState.items.map((q, i) => {
      const ov = q._override || {};
      return `<div class="p-4 bg-slate-900 border ${ov.hidden ? "border-rose-800/70 opacity-70" : "border-slate-800"} rounded-2xl space-y-2">
        <div class="flex flex-wrap items-center gap-1.5 text-[11px]">
          <span class="font-mono text-slate-400">${esc(q.id)}</span>
          <span class="px-2 py-0.5 rounded-md bg-indigo-500/15 text-indigo-300 font-bold">${esc(q.category)}</span>
          <span class="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 font-bold">${esc(q.level)}</span>
          <span class="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 font-bold">${esc(getUniLabel(q.university_id))}</span>
          ${ov.hidden ? `<span class="px-2 py-0.5 rounded-md bg-rose-500/20 text-rose-300 font-bold">Gizli</span>` : ""}
          ${ov.patch && Object.keys(ov.patch).length ? `<span class="px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-300 font-bold">Düzeltildi</span>` : ""}
          ${ov.note ? `<span class="text-slate-500">Not: ${esc(ov.note)}</span>` : ""}
        </div>
        <div class="text-xs text-slate-100 whitespace-pre-wrap">${esc(q.question)}</div>
        <div class="grid sm:grid-cols-2 gap-1.5">${(q.options || []).map((o) => `<div class="text-[11px] px-2.5 py-1.5 rounded-lg ${o.key === q.correct_answer ? "bg-emerald-500/15 text-emerald-200 border border-emerald-500/30 font-bold" : "bg-slate-800/70 text-slate-300"}">${esc(o.key)}) ${esc(o.text)}</div>`).join("")}</div>
        ${q.explanation_tr ? `<div class="text-[11px] text-slate-400"><strong class="text-slate-300">Çözüm:</strong> ${esc(q.explanation_tr)}</div>` : ""}
        <div class="flex gap-2 pt-1">
          <button onclick="openQuestionEditor(${i})" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-[11px] font-black">Düzenle</button>
          <button onclick="toggleQuestionHidden(${i})" class="px-3 py-1.5 ${ov.hidden ? "bg-emerald-600/20 text-emerald-300 border-emerald-500/30" : "bg-rose-950/60 text-rose-300 border-rose-800/60"} border rounded-xl text-[11px] font-bold">${ov.hidden ? "Yeniden yayınla" : "Yayından kaldır"}</button>
        </div>
      </div>`;
    }).join("") : `<div class="p-8 text-center text-xs text-slate-500 bg-slate-900 border border-slate-800 rounded-2xl">Aramaya uygun soru bulunamadı.</div>`;
  }

  function questionPayload(q, hidden) {
    return {
      hidden, question: q.question, options: q.options, correct_answer: q.correct_answer,
      explanation_tr: q.explanation_tr || "", explanation_en: q.explanation_en || "", note: (q._override || {}).note || "",
    };
  }

  async function toggleQuestionHidden(i) {
    const q = contentState.items[i];
    const hide = !(q._override || {}).hidden;
    if (hide && !confirm(`${q.id} sorusu öğrencilerden gizlensin mi? İstediğiniz zaman yeniden yayınlayabilirsiniz.`)) return;
    try {
      await sendJson(`/api/admin/questions/${encodeURIComponent(q.id)}`, "PUT", questionPayload(q, hide));
      showAdminToast(hide ? "✓ Soru yayından kaldırıldı." : "✓ Soru yeniden yayında.");
      loadContent();
    } catch (err) {
      showAdminToast("Hata: " + err.message, "rose");
    }
  }

  let editingIndex = null;
  function openQuestionEditor(i) {
    editingIndex = i;
    const q = contentState.items[i];
    $("qe-title").textContent = `${q.id} • ${q.category} • ${q.level}`;
    $("qe-question").value = q.question || "";
    $("qe-options").innerHTML = (q.options || []).map((o, k) => `
      <label class="flex items-center gap-2"><span class="w-6 text-xs font-black text-slate-300">${esc(o.key)})</span>
      <input data-key="${esc(o.key)}" value="${esc(o.text)}" class="qe-opt flex-1 p-2 bg-slate-800 border border-slate-700 rounded-lg text-xs text-white"></label>`).join("");
    $("qe-answer").innerHTML = (q.options || []).map((o) => `<option value="${esc(o.key)}" ${o.key === q.correct_answer ? "selected" : ""}>${esc(o.key)}</option>`).join("");
    $("qe-exp-tr").value = q.explanation_tr || "";
    $("qe-exp-en").value = q.explanation_en || "";
    $("qe-note").value = (q._override || {}).note || "";
    $("qe-hidden").checked = !!(q._override || {}).hidden;
    $("qe-original").classList.toggle("hidden", !q._original);
    $("qe-msg").classList.add("hidden");
    $("question-edit-modal").classList.remove("hidden");
  }

  function closeQuestionEditor() {
    $("question-edit-modal").classList.add("hidden");
    editingIndex = null;
  }

  async function saveQuestionEdit(restoreOriginal = false) {
    const q = contentState.items[editingIndex];
    let body;
    if (restoreOriginal) {
      if (!confirm("Bu sorudaki tüm düzeltmeler silinsin ve soru orijinal haline dönsün mü?")) return;
      body = { ...questionPayload(q._original || q, false), note: "" };
    } else {
      body = {
        hidden: $("qe-hidden").checked, question: $("qe-question").value,
        options: [...document.querySelectorAll(".qe-opt")].map((el) => ({ key: el.dataset.key, text: el.value })),
        correct_answer: $("qe-answer").value, explanation_tr: $("qe-exp-tr").value, explanation_en: $("qe-exp-en").value,
        note: $("qe-note").value,
      };
    }
    try {
      await sendJson(`/api/admin/questions/${encodeURIComponent(q.id)}`, "PUT", body);
      showAdminToast(restoreOriginal ? "✓ Soru orijinal haline döndü." : "✓ Soru kaydedildi; öğrencilere hemen yansıdı.");
      closeQuestionEditor();
      loadContent();
    } catch (err) {
      $("qe-msg").textContent = err.message;
      $("qe-msg").classList.remove("hidden");
    }
  }

  // ---------------- Site duyurusu ----------------
  async function loadAnnouncement() {
    const a = await getJson("/api/admin/announcement");
    $("ann-enabled").checked = !!a.enabled;
    $("ann-text").value = a.text || "";
    $("ann-tone").value = a.tone || "info";
    $("ann-link-url").value = a.link_url || "";
    $("ann-link-text").value = a.link_text || "";
    renderAnnouncementPreview();
  }

  function renderAnnouncementPreview() {
    const tones = { info: "bg-sky-600", success: "bg-emerald-600", warning: "bg-amber-500 text-slate-900" };
    const el = $("ann-preview");
    const text = $("ann-text").value.trim();
    el.className = `px-4 py-2.5 rounded-xl text-xs font-bold text-white ${tones[$("ann-tone").value] || tones.info}`;
    el.innerHTML = text ? `${esc(text)} ${$("ann-link-url").value.trim() ? `<u class="ml-1">${esc($("ann-link-text").value.trim() || "Ayrıntılar")} →</u>` : ""}` : "Duyuru metni yazın...";
    $("ann-state").textContent = $("ann-enabled").checked ? "Sitede gösteriliyor" : "Kapalı";
  }

  async function saveAnnouncement() {
    try {
      await sendJson("/api/admin/announcement", "PUT", {
        enabled: $("ann-enabled").checked, text: $("ann-text").value, tone: $("ann-tone").value,
        link_url: $("ann-link-url").value.trim(), link_text: $("ann-link-text").value.trim(),
      });
      showAdminToast($("ann-enabled").checked ? "✓ Duyuru yayında." : "✓ Duyuru kapatıldı.");
      renderAnnouncementPreview();
    } catch (err) {
      showAdminToast("Hata: " + err.message, "rose");
    }
  }

  // ---------------- Yönetici kayıtları ----------------
  async function loadAudit() {
    const d = await getJson("/api/admin/audit-log?limit=300");
    $("audit-tbody").innerHTML = (d.entries || []).length ? d.entries.map((e) => `
      <tr class="hover:bg-slate-800/40"><td class="py-2.5 px-4 text-slate-400 whitespace-nowrap">${esc(fmtDate(e.created_at))}</td>
      <td class="py-2.5 px-4 font-bold text-slate-200">${esc(AUDIT_LABELS[e.action] || e.action)}</td>
      <td class="py-2.5 px-4 font-mono text-slate-300">${esc(e.target || "-")}</td>
      <td class="py-2.5 px-4 text-slate-400 max-w-md break-words">${esc(e.detail || "")}</td>
      <td class="py-2.5 px-4 text-slate-500">${esc(e.admin || "")}<div class="text-[10px]">${esc(e.ip || "")}</div></td></tr>`).join("") : empty(5, "Henüz yönetici işlemi kaydı yok.");
  }

  // ---------------- Öğrenci ayrıntısı ----------------
  async function openStudentDetail(userId) {
    const modal = $("student-detail-modal");
    $("sd-body").innerHTML = `<div class="py-10 text-center text-xs text-slate-400">Yükleniyor...</div>`;
    modal.classList.remove("hidden");
    try {
      const d = await getJson(`/api/admin/students/${Number(userId)}`);
      const u = d.user, a = d.activity || {};
      $("sd-title").textContent = `${u.full_name || u.username} (#${u.id})`;
      const row = (k, v) => `<div class="flex justify-between gap-3 py-1.5 border-b border-slate-800/70 text-xs"><span class="text-slate-400">${esc(k)}</span><span class="font-semibold text-slate-200 text-right break-all">${esc(v ?? "-")}</span></div>`;
      const table = (title, rows, cols, map) => `
        <div class="space-y-2"><h4 class="text-xs font-black text-white">${esc(title)} <span class="text-slate-500 font-bold">(${rows.length})</span></h4>
        ${rows.length ? `<div class="overflow-x-auto"><table class="w-full text-[11px]"><thead><tr class="text-slate-500 text-left">${cols.map((c) => `<th class="py-1 pr-3">${esc(c)}</th>`).join("")}</tr></thead>
        <tbody class="divide-y divide-slate-800/70">${rows.map((r) => `<tr>${map(r).map((v) => `<td class="py-1.5 pr-3 text-slate-300">${esc(v ?? "-")}</td>`).join("")}</tr>`).join("")}</tbody></table></div>` : `<div class="text-[11px] text-slate-500">Kayıt yok.</div>`}</div>`;
      $("sd-body").innerHTML = `
        <div class="grid md:grid-cols-2 gap-5">
          <div>${row("E-posta", u.email)}${row("Kullanıcı adı", "@" + u.username)}${row("Ana okul", getUniLabel(u.university_id))}${row("Öğrenci no", u.student_number)}
            ${row("Belge doğrulama", u.is_verified_student ? "Doğrulandı (" + getUniLabel(u.verified_university) + ")" : "Doğrulanmadı")}
            ${row("Açık okullar", (u.unlocked_universities || []).filter((x) => x !== "general").map(getUniLabel).join(", ") || "Yalnızca genel havuz")}
            ${row("Kur / seviye tespiti", `${u.current_level || "-"} / ${u.placement_level || "yapılmadı"}`)}${row("Kayıt", fmtDate(u.created_at))}${row("Son aktiflik", fmtDate(u.last_active))}</div>
          <div>${row("Çalıştığı gün", a.days)}${row("Cevapladığı soru", `${a.answered} (doğru ${a.correct})`)}${row("Kelime tekrarı", a.vocab)}
            ${row("Konu Yolu", `${a.lessons_completed} ders • ${a.lesson_xp} XP`)}${row("Hata Kasası (açık)", a.open_mistakes)}${row("Seri", `${u.streak_days || 0} gün`)}
            ${row("Sözleşme onayı", fmtDate(u.terms_accepted_at))}${row("Aydınlatma okundu", fmtDate(u.privacy_notice_ack_at))}
            ${row("Ticari ileti onayı", u.marketing_consent ? "Var (" + fmtDate(u.marketing_consent_at) + ")" : "Yok")}</div>
        </div>
        ${table("Siparişler", d.orders, ["Sipariş", "Okul", "Tutar", "Durum", "Tarih"], (r) => [r.merchant_oid, getUniLabel(r.university_id), tl((r.total_amount_kurus || r.amount_kurus) / 100), (ORDER_STATUS[r.status] || [r.status])[0], fmtDate(r.created_at)])}
        ${table("Denemeler (son 20)", d.exams, ["Okul", "Kur", "Puan", "Doğru", "Tarih"], (r) => [getUniLabel(r.university_id), r.level, r.score, `${r.correct_count}/${r.total_questions}`, fmtDate(r.created_at)])}
        ${table("Onay geçmişi (KVKK ispat kaydı)", d.consents, ["Metin", "Sürüm", "İşlem", "Kanal", "Tarih"], (r) => [DOC_LABELS[r.doc_key] || r.doc_key, r.doc_version, ACTION_LABELS[r.action] || r.action, r.channel, fmtDate(r.created_at)])}
        ${table("Belge doğrulama kayıtları", d.verifications, ["Okul", "Tür", "Durum", "Not", "Tarih"], (r) => [getUniLabel(r.university_id), r.verification_type, r.verification_status, r.notes, fmtDate(r.verified_at)])}
        ${table("Destek talepleri", d.tickets, ["#", "Kategori", "Durum", "Mesaj", "Tarih"], (r) => [r.id, r.category, TICKET_STATUS[r.status] || r.status, (r.message || "").slice(0, 80), fmtDate(r.created_at)])}`;
    } catch (err) {
      $("sd-body").innerHTML = `<div class="py-10 text-center text-xs text-rose-300">${esc(err.message)}</div>`;
    }
  }

  function closeStudentDetail() {
    $("student-detail-modal").classList.add("hidden");
  }

  Object.assign(window, {
    adminShowTab, saveTicket, loadOrders, loadSupport, loadContent, toggleQuestionHidden, openQuestionEditor,
    closeQuestionEditor, saveQuestionEdit, renderAnnouncementPreview, saveAnnouncement, openStudentDetail,
    closeStudentDetail, downloadAdminFile, adminCurrentTab: () => currentTab,
  });

  window.addEventListener("DOMContentLoaded", () => {
    const fromHash = (location.hash || "").slice(1);
    if (getAdminToken()) adminShowTab(TABS.includes(fromHash) ? fromHash : "overview");
  });
})();
