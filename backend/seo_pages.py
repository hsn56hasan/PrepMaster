"""
PrepKampüs SEO & Google Dizinleme Modülü:
- /robots.txt
- /sitemap.xml
- /sinavlar (26 üniversite İngilizce hazırlık & muafiyet sınav rehberi)
- /universite/{uni_id} (her üniversite için özgün, sunucu taraflı HTML + JSON-LD sayfası)
"""

import html as _html
import json
import os
from typing import Any, Dict, List
from fastapi import Request

DEFAULT_PUBLIC_URL = "https://prepkampus.com"

# Öğrencilerin üniversite kısaltması yanında sık aradığı alternatif sınav adları
_EXTRA_SEARCH_TERMS: Dict[str, str] = {
    "itu": "İTÜ Proficiency, İTÜ İngilizce Hazırlık Atlama, İTÜ YDY, İTÜ Stage 1 Stage 2",
    "metu": "ODTÜ EPE, METU EPE, ODTÜ İngilizce Yeterlik Sınavı, ODTÜ Hazırlık Muafiyet",
    "boun": "Boğaziçi BUEPT, BÜEPT, Boğaziçi İngilizce Yeterlik, BUEPT Writing Reading Listening",
    "bilkent": "Bilkent PAE, Bilkent COPE, Bilkent Hazırlık Atlama Sınavı, Bilkent Stage",
    "ytu": "YTÜ İYS, Yıldız Teknik İngilizce Yeterlik Sınavı, YTÜ Hazırlık Muafiyet",
    "koc": "Koç KUEPE, KUEPE Hazırlık, Koç Üniversitesi İngilizce Muafiyet",
    "sabanci": "Sabancı ELAE, ELAE Stage 1 Stage 2, Sabancı Üniversitesi Hazırlık Atlama",
    "ozyegin": "Özyeğin TRACE, ÖzÜ TRACE Sınavı, Özyeğin İngilizce Yeterlik",
    "bahcesehir": "BAU Proficiency, Bahçeşehir Üniversitesi İngilizce Muafiyet Sınavı",
    "tobb": "TOBB ETÜ İYS, TOBB Ekonomi Hazırlık Atlama Sınavı",
    "hacettepe": "Hacettepe YDYO Muafiyet, Hacettepe İngilizce Düzey Belirleme",
    "ankara": "Ankara Üniversitesi Hazırlık Muafiyet, AÜ YDYO İngilizce Sınavı",
    "gazi": "Gazi Üniversitesi YDYO Muafiyet, Gazi Hazırlık Atlama Sınavı",
    "ege": "Ege Üniversitesi YDYO Yeterlik, Ege İngilizce Muafiyet Sınavı",
    "marmara": "Marmara Üniversitesi YDYO Muafiyet, Marmara İngilizce Yeterlik",
    "istanbul": "İstanbul Üniversitesi YDYO Muafiyet, İÜ İngilizce Hazırlık Atlama",
    "cerrahpasa": "İÜC YDYO İngilizce Yeterlik, Cerrahpaşa Hazırlık Muafiyet",
    "dokuz_eylul": "DEÜ YDYO Muafiyet, Dokuz Eylül İngilizce Yeterlik Sınavı",
    "iyte": "İYTE YDYO İngilizce Muafiyet, İzmir Yüksek Teknoloji Hazırlık Atlama",
    "anadolu": "Anadolu Üniversitesi YDYO İngilizce Yeterlik Sınavı",
    "eskisehir_teknik": "ESTÜ YDYO Hazırlık Muafiyet, Eskişehir Teknik İngilizce Sınavı",
    "gebze_teknik": "GTÜ Yabancı Diller Muafiyet, Gebze Teknik İngilizce Sınavı",
    "akdeniz": "Akdeniz Üniversitesi YDYO Hazırlık Muafiyet Sınavı",
    "cukurova": "Çukurova YADYO İngilizce Muafiyet Sınavı",
    "uludag": "Bursa Uludağ YDYO İngilizce Yeterlik Sınavı",
    "yeditepe": "Yeditepe Proficiency, Yeditepe Hazırlık Atlama Sınavı",
    "general": "Üniversite İngilizce Hazırlık A1 A2 B1 B2 C1 C2 Genel Kur Denemeleri",
}


def resolve_site_url(request: Request) -> str:
    """Özel SITE_URL env varsa onu, yoksa canlı host başlığını döner."""
    env_url = os.getenv("SITE_URL", "").strip().rstrip("/")
    if env_url:
        return env_url
    host = (request.headers.get("x-forwarded-host") or request.headers.get("host") or "").split(",")[0].strip()
    if host and not any(local in host for local in ("localhost", "127.0.0.1", "testserver")):
        proto = (request.headers.get("x-forwarded-proto") or request.url.scheme or "https").split(",")[0].strip()
        return f"{proto}://{host}".rstrip("/")
    return DEFAULT_PUBLIC_URL


def get_google_verification_meta() -> str:
    code = os.getenv("GOOGLE_SITE_VERIFICATION", "").strip()
    if not code:
        return ""
    return f'<meta name="google-site-verification" content="{_html.escape(code)}" />'


def build_robots_txt(site_url: str) -> str:
    base = site_url.rstrip("/")
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Allow: /sinavlar\n"
        "Allow: /universite/\n"
        "Allow: /kvkk\n"
        "Disallow: /admin\n"
        "Disallow: /api/\n"
        "Disallow: /odeme-sonuc\n"
        "Disallow: /*?uni=\n"
        "Disallow: /*&tab=register\n\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )


def build_sitemap_xml(site_url: str, universities: List[Dict[str, Any]]) -> str:
    base = site_url.rstrip("/")
    urls = [
        (f"{base}/", "weekly", "1.0"),
        (f"{base}/sinavlar", "weekly", "0.9"),
        (f"{base}/kvkk", "monthly", "0.4"),
    ]
    for uni in universities:
        uid = uni.get("id", "")
        if not uid:
            continue
        prio = "0.7" if uid == "general" else "0.85"
        urls.append((f"{base}/universite/{_html.escape(uid)}", "weekly", prio))

    items = "\n".join(
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <changefreq>{freq}</changefreq>\n"
        f"    <priority>{prio}</priority>\n"
        f"  </url>"
        for loc, freq, prio in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{items}\n"
        "</urlset>\n"
    )


def compute_counts_by_uni(
    questions: List[Dict[str, Any]],
    listening: List[Dict[str, Any]],
    speaking: List[Dict[str, Any]],
) -> Dict[str, Dict[str, int]]:
    counts: Dict[str, Dict[str, int]] = {}
    for q in questions:
        uid = q.get("university_id", "general")
        counts.setdefault(uid, {"questions": 0, "listening": 0, "speaking": 0})["questions"] += 1
    for item in listening:
        uid = item.get("university_id", "general")
        counts.setdefault(uid, {"questions": 0, "listening": 0, "speaking": 0})["listening"] += 1
    for item in speaking:
        uid = item.get("university_id", "general")
        counts.setdefault(uid, {"questions": 0, "listening": 0, "speaking": 0})["speaking"] += 1
    return counts


_PAGE_CSS = """
:root{color-scheme:light}
*{box-sizing:border-box}
body{margin:0;font-family:'Plus Jakarta Sans',system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#eef8f3;color:#0f172a;line-height:1.6}
a{color:#047857;text-decoration:none}
a:hover{text-decoration:underline}
.topbar{background:linear-gradient(135deg,#0f172a,#064e3b 60%,#065f46);color:#fff;padding:18px 20px}
.container{max-width:1100px;margin:0 auto;padding:0 18px}
.nav{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px}
.brand{display:flex;align-items:center;gap:10px;color:#fff;font-weight:800;font-size:18px}
.navlinks{display:flex;flex-wrap:wrap;gap:14px;font-size:13px;font-weight:700}
.navlinks a{color:#cbd5e1}
.navlinks a:hover{color:#fff}
.btn{display:inline-block;background:#059669;color:#fff;font-weight:700;font-size:13px;padding:10px 18px;border-radius:12px;border:0}
.btn:hover{background:#047857;text-decoration:none}
.btn-outline{display:inline-block;background:#fff;color:#064e3b;border:1px solid #cbd5e1;font-weight:700;font-size:13px;padding:9px 16px;border-radius:12px}
.hero{padding:28px 0 12px}
.badge{display:inline-block;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;background:#d1fae5;color:#065f46;padding:4px 10px;border-radius:999px}
h1{font-size:28px;line-height:1.25;margin:10px 0 8px}
h2{font-size:20px;margin:26px 0 12px;color:#0f172a}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:18px 0}
.stat{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:14px 16px}
.stat .lbl{font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase}
.stat .val{font-size:20px;font-weight:800;color:#0f172a;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:16px 0 28px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:18px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;gap:10px}
.card h3{margin:0;font-size:16px;color:#0f172a}
.meta{font-size:12px;color:#475569}
.pills{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
.pill{font-size:11px;font-weight:700;background:#f1f5f9;color:#334155;padding:3px 9px;border-radius:999px}
.section-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.tips{background:#ecfdf5;border:1px solid #a7f3d0;border-radius:18px;padding:18px 22px}
.tips li{margin-bottom:6px;font-size:14px;color:#1e293b}
.faq-item{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:14px 18px;margin-bottom:10px}
.faq-item h3{margin:0 0 6px;font-size:15px}
.footer{border-top:1px solid #e2e8f0;padding:24px 0 36px;margin-top:32px;font-size:12px;color:#64748b}
@media(max-width:640px){h1{font-size:22px}}
"""


def render_exams_hub_html(
    site_url: str,
    universities: List[Dict[str, Any]],
    counts_by_uni: Dict[str, Dict[str, int]],
) -> str:
    base = site_url.rstrip("/")
    canonical = f"{base}/sinavlar"
    total_q = sum(c["questions"] for c in counts_by_uni.values())
    total_l = sum(c["listening"] for c in counts_by_uni.values())
    total_s = sum(c["speaking"] for c in counts_by_uni.values())
    uni_only = [u for u in universities if u.get("id") != "general"]
    ordered = uni_only + [u for u in universities if u.get("id") == "general"]

    ld_items = [
        {
            "@type": "ListItem",
            "position": idx + 1,
            "name": f"{u.get('short_name', '')} — {u.get('exam_name', '')}",
            "url": f"{base}/universite/{u['id']}",
        }
        for idx, u in enumerate(ordered)
    ]
    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "Türkiye Üniversiteleri İngilizce Hazırlık Muafiyet Sınavları",
            "numberOfItems": len(ld_items),
            "itemListElement": ld_items,
        },
        ensure_ascii=False,
    )

    cards_html = []
    for u in ordered:
        uid = _html.escape(u.get("id", ""))
        name = _html.escape(u.get("name", ""))
        short = _html.escape(u.get("short_name", ""))
        exam = _html.escape(u.get("exam_name", ""))
        desc = _html.escape(u.get("description", ""))
        c = counts_by_uni.get(u.get("id", ""), {"questions": 0, "listening": 0, "speaking": 0})
        cards_html.append(
            f'<article class="card">'
            f'<div>'
            f'<span class="badge">{short}</span>'
            f'<h3 style="margin-top:8px"><a href="/universite/{uid}">{name} — {exam}</a></h3>'
            f'<p class="meta" style="margin:6px 0">{desc}</p>'
            f'<div class="pills">'
            f'<span class="pill">Geçme: {int(u.get("passing_score", 60))}</span>'
            f'<span class="pill">Süre: {int(u.get("duration_minutes", 120))} dk</span>'
            f'<span class="pill">{c["questions"]} Soru</span>'
            f'<span class="pill">{c["listening"]} Listening</span>'
            f'<span class="pill">{c["speaking"]} Speaking</span>'
            f'</div>'
            f'</div>'
            f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">'
            f'<a class="btn" href="/universite/{uid}">Sınav Rehberi</a>'
            f'<a class="btn-outline" href="/?uni={uid}&tab=register" rel="nofollow">Ücretsiz Başla</a>'
            f'</div>'
            f'</article>'
        )

    title = "26 Üniversite İngilizce Hazırlık & Muafiyet (Proficiency) Sınav Rehberi | PrepKampüs"
    description = (
        f"İTÜ Proficiency, Boğaziçi BUEPT, ODTÜ EPE, Bilkent PAE, YTÜ İYS, Koç KUEPE, Sabancı ELAE ve "
        f"26 üniversite hazırlık muafiyet sınavları için {total_q} soru, {total_l} listening ve {total_s} speaking denemesi."
    )
    verif = get_google_verification_meta()

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_html.escape(title)}</title>
  <meta name="description" content="{_html.escape(description)}" />
  <meta name="robots" content="index, follow" />
  {verif}
  <link rel="canonical" href="{_html.escape(canonical)}" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="tr_TR" />
  <meta property="og:site_name" content="PrepKampüs" />
  <meta property="og:title" content="{_html.escape(title)}" />
  <meta property="og:description" content="{_html.escape(description)}" />
  <meta property="og:url" content="{_html.escape(canonical)}" />
  <meta property="og:image" content="{base}/static/img/logo-512.png?v=2" />
  <link rel="icon" type="image/png" sizes="96x96" href="/static/img/favicon-96x96.png?v=3" />
  <link rel="icon" type="image/png" sizes="48x48" href="/static/img/favicon-48x48.png?v=3" />
  <link rel="icon" type="image/svg+xml" href="/static/img/logo.svg?v=3" />
  <link rel="shortcut icon" href="/favicon.ico?v=3" />
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet" />
  <style>{_PAGE_CSS}</style>
  <script type="application/ld+json">{json_ld}</script>
</head>
<body>
  <header class="topbar">
    <div class="container nav">
      <a class="brand" href="/" style="display:inline-flex;align-items:center;gap:10px"><img src="/static/img/logo.png?v=2" alt="PrepKampüs" width="32" height="32" style="border-radius:8px;vertical-align:middle" />PrepKampüs — İngilizce Hazırlık &amp; Muafiyet</a>
      <nav class="navlinks">
        <a href="/">Ana Platform</a>
        <a href="/sinavlar">26 Üniversite Rehberi</a>
        <a href="/kvkk">KVKK &amp; Destek</a>
      </nav>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <span class="badge">26 Üniversite • A1–C2 Kur &amp; Muafiyet Hazırlığı</span>
      <h1>Türkiye Üniversiteleri İngilizce Hazırlık Muafiyet (Proficiency) Sınavları</h1>
      <p style="color:#475569;max-width:820px;font-size:15px">
        Hedeflediğiniz üniversitenin İngilizce yeterlik ve hazırlık atlama sınav formatını, geçme notunu,
        bölüm ağırlıklarını ve çalışma ipuçlarını inceleyin. E-Devlet öğrenci belgenizi doğrulayarak kendi
        üniversitenizin tüm denemelerini <strong>ücretsiz</strong> çözebilirsiniz.
      </p>
      <div class="stats">
        <div class="stat"><div class="lbl">Üniversite Sayısı</div><div class="val">{len(uni_only)} Üniversite</div></div>
        <div class="stat"><div class="lbl">Toplam Soru Bankası</div><div class="val">{total_q} Soru</div></div>
        <div class="stat"><div class="lbl">Listening Sınavı</div><div class="val">{total_l} Ders</div></div>
        <div class="stat"><div class="lbl">Speaking Görevi</div><div class="val">{total_s} Simülasyon</div></div>
      </div>
    </section>

    <section class="grid">
      {"".join(cards_html)}
    </section>

    <footer class="footer">
      <strong>PrepKampüs (PrepKampus • prepkampus.com)</strong> • Resmi İletişim: destek@prepkampus.com • Tel: 0539 838 18 87 •
      <a href="/kvkk">KVKK &amp; Hukuki Belgeler</a> • <a href="/">Giriş Yap / Kayıt Ol</a>
    </footer>
  </main>
</body>
</html>"""


def render_university_seo_html(
    site_url: str,
    uni: Dict[str, Any],
    all_unis: List[Dict[str, Any]],
    uni_counts: Dict[str, int],
) -> str:
    base = site_url.rstrip("/")
    uid = uni.get("id", "")
    canonical = f"{base}/universite/{uid}"
    name = uni.get("name", "")
    short = uni.get("short_name", "")
    exam = uni.get("exam_name", "")
    desc = uni.get("description", "")
    passing = int(uni.get("passing_score", 60))
    duration = int(uni.get("duration_minutes", 120))
    official_q = int(uni.get("total_questions", 60))
    q_cnt = uni_counts.get("questions", 0)
    l_cnt = uni_counts.get("listening", 0)
    s_cnt = uni_counts.get("speaking", 0)
    extra_kw = _EXTRA_SEARCH_TERMS.get(uid, f"{short} {exam}, {name} hazırlık muafiyet")

    title = f"{short} {exam} Hazırlık, Geçme Notu & Denemeler | PrepKampüs"
    meta_desc = (
        f"{name} ({short}) {exam}: geçme notu {passing}, sınav süresi {duration} dk. "
        f"PrepKampüs'te {q_cnt} soru, {l_cnt} listening ve {s_cnt} speaking denemesiyle ücretsiz hazırlan."
    )

    sections = uni.get("sections", [])
    sections_html = "".join(
        f'<div class="card">'
        f'<div>'
        f'<span class="badge">Ağırlık: %{int(s.get("weight_percent", 0))}</span>'
        f'<h3 style="margin-top:8px">{_html.escape(s.get("name", ""))}</h3>'
        f'<p class="meta" style="margin:6px 0">{_html.escape(s.get("description", ""))}</p>'
        f'</div>'
        f'<div class="pill" style="align-self:flex-start">{int(s.get("questions_count", 0))} Soru / Görev</div>'
        f'</div>'
        for s in sections
    )

    tips = uni.get("tips", [])
    tips_html = "".join(f"<li>{_html.escape(t)}</li>" for t in tips)

    faqs = [
        (
            f"{name} ({short}) {exam} geçme notu kaçtır?",
            f"{name} {exam} için hedef geçme puanı 100 üzerinden {passing} olarak belirtilmiştir; toplam süre yaklaşık {duration} dakikadır.",
        ),
        (
            f"PrepKampüs'te {short} için kaç adet deneme içeriği var?",
            f"PrepKampüs üzerinde {name} formatına özel {q_cnt} çoktan seçmeli kur sorusu (A1–C2), {l_cnt} akademik listening ve {s_cnt} speaking simülasyonu yer alır.",
        ),
        (
            f"{short} hazırlık paketini ücretsiz açabilir miyim?",
            f"Evet. {name} öğrencisiyseniz E-Devlet öğrenci belgenizi veya .edu.tr okul e-postanızı doğrulayarak kendi üniversitenizin tüm içeriklerini ücretsiz kullanabilirsiniz.",
        ),
    ]
    faq_html = "".join(
        f'<div class="faq-item"><h3>{_html.escape(q)}</h3><p style="margin:0;font-size:14px;color:#475569">{_html.escape(a)}</p></div>'
        for q, a in faqs
    )

    other_links = " • ".join(
        f'<a href="/universite/{_html.escape(o["id"])}">{_html.escape(o["short_name"])} ({_html.escape(o["exam_name"])})</a>'
        for o in all_unis
        if o.get("id") and o.get("id") != uid
    )

    ld_graph = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Course",
                    "name": f"{name} — {exam} Hazırlık Programı",
                    "description": meta_desc,
                    "provider": {
                        "@type": "EducationalOrganization",
                        "name": "PrepKampüs",
                        "alternateName": ["PrepKampus", "prepkampus", "Prep Kampüs", "Prep Kampus", "PerpKampus", "prepkampus.com"],
                        "url": base,
                    },
                    "inLanguage": ["tr", "en"],
                    "url": canonical,
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a},
                        }
                        for q, a in faqs
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )
    verif = get_google_verification_meta()

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_html.escape(title)}</title>
  <meta name="description" content="{_html.escape(meta_desc)}" />
  <meta name="keywords" content="{_html.escape(extra_kw)}" />
  <meta name="robots" content="index, follow" />
  {verif}
  <link rel="canonical" href="{_html.escape(canonical)}" />
  <meta property="og:type" content="article" />
  <meta property="og:locale" content="tr_TR" />
  <meta property="og:site_name" content="PrepKampüs" />
  <meta property="og:title" content="{_html.escape(title)}" />
  <meta property="og:description" content="{_html.escape(meta_desc)}" />
  <meta property="og:url" content="{_html.escape(canonical)}" />
  <meta property="og:image" content="{base}/static/img/logo-512.png?v=2" />
  <link rel="icon" type="image/png" sizes="96x96" href="/static/img/favicon-96x96.png?v=3" />
  <link rel="icon" type="image/png" sizes="48x48" href="/static/img/favicon-48x48.png?v=3" />
  <link rel="icon" type="image/svg+xml" href="/static/img/logo.svg?v=3" />
  <link rel="shortcut icon" href="/favicon.ico?v=3" />
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet" />
  <style>{_PAGE_CSS}</style>
  <script type="application/ld+json">{ld_graph}</script>
</head>
<body>
  <header class="topbar">
    <div class="container nav">
      <a class="brand" href="/" style="display:inline-flex;align-items:center;gap:10px"><img src="/static/img/logo.png?v=2" alt="PrepKampüs" width="32" height="32" style="border-radius:8px;vertical-align:middle" />PrepKampüs — İngilizce Hazırlık &amp; Muafiyet</a>
      <nav class="navlinks">
        <a href="/">Ana Platform</a>
        <a href="/sinavlar">Tüm 26 Üniversite</a>
        <a href="/kvkk">KVKK &amp; Destek</a>
      </nav>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <div style="font-size:12px;color:#64748b;margin-bottom:8px">
        <a href="/">Ana Sayfa</a> / <a href="/sinavlar">Sınavlar</a> / <span>{_html.escape(short)}</span>
      </div>
      <span class="badge">{_html.escape(short)} Muafiyet Rehberi</span>
      <h1>{_html.escape(name)} ({_html.escape(short)}) — {_html.escape(exam)}</h1>
      <p style="color:#475569;max-width:820px;font-size:15px">{_html.escape(desc)}</p>

      <div style="display:flex;gap:10px;flex-wrap:wrap;margin:16px 0">
        <a class="btn" href="/?uni={_html.escape(uid)}&tab=register" rel="nofollow">{_html.escape(short)} İçin Ücretsiz Kayıt Ol</a>
        <a class="btn-outline" href="/sinavlar">Diğer Üniversiteleri Gör</a>
      </div>

      <div class="stats">
        <div class="stat"><div class="lbl">Geçme Notu</div><div class="val">{passing} / 100</div></div>
        <div class="stat"><div class="lbl">Sınav Süresi</div><div class="val">{duration} Dk</div></div>
        <div class="stat"><div class="lbl">Resmi Sınav Yapısı</div><div class="val">{official_q} Soru</div></div>
        <div class="stat"><div class="lbl">PrepKampüs Havuzu</div><div class="val">{q_cnt} Soru • {l_cnt}L • {s_cnt}S</div></div>
      </div>
    </section>

    <h2>Sınav Bölümleri ve Puan Ağırlıkları</h2>
    <section class="section-list">
      {sections_html}
    </section>

    <h2>{_html.escape(short)} Hazırlık &amp; Muafiyet İpuçları</h2>
    <section class="tips">
      <ul style="margin:0;padding-left:18px">{tips_html}</ul>
    </section>

    <h2>Sıkça Sorulan Sorular ({_html.escape(short)})</h2>
    <section>
      {faq_html}
    </section>

    <h2>Diğer Üniversite Muafiyet Sınavları</h2>
    <p style="font-size:13px;line-height:1.9;color:#334155">{other_links}</p>

    <footer class="footer">
      <strong>PrepKampüs (PrepKampus • prepkampus.com)</strong> • İlgili aramalar: {_html.escape(extra_kw)} •
      Resmi Destek: destek@prepkampus.com • 0539 838 18 87 • <a href="/kvkk">KVKK</a>
    </footer>
  </main>
</body>
</html>"""
