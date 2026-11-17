"""
E-posta gönderimi (şifre sıfırlama, öğrenci .edu.tr doğrulama kodları,
hoş geldin bildirimi, üniversite paket açılışı ve Destek/KVKK bildirimleri).

Desteklenen 3 altyapı (.env / Railway Variables ile seçilir):
  1) Resend (HTTPS API - Railway Free/Hobby/Pro tüm planlarda çalışır):
       RESEND_API_KEY=re_...
  2) Brevo (HTTPS API - Özel alan adı olmadan Gmail/kişisel adres doğrulamalı,
     günde 300 ücretsiz e-posta; tüm Railway planlarında çalışır):
       BREVO_API_KEY=xkeysib-...
  3) SMTP (Kendi sunucunuz veya Railway Pro plan):
       SMTP_HOST=smtp.gmail.com (veya smtp.zoho.eu)
       SMTP_PORT=465
       SMTP_USER=...
       SMTP_PASSWORD=<Uygulama Şifresi>

Ortak gönderici adresi:
       EMAIL_FROM="PrepMaster <prepmasteryonetici@gmail.com>"
Destek bildirim alıcısı:
       SUPPORT_NOTIFY_EMAIL=prepmasteryonetici@gmail.com
"""
import html as _html
import logging
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, parseaddr
from typing import Any, Dict, List, Optional

try:
    import env_loader  # noqa: F401  (.env'i yükler)
except ImportError:
    from backend import env_loader  # noqa: F401

log = logging.getLogger("prepmaster.email")

_LAST_DELIVERY_STATUS: Dict[str, Any] = {}


def _cfg() -> Dict[str, Any]:
    return {
        "from": os.getenv("EMAIL_FROM", "").strip(),
        "smtp_host": os.getenv("SMTP_HOST", "").strip(),
        "smtp_port": int(os.getenv("SMTP_PORT", "465") or 465),
        "smtp_user": os.getenv("SMTP_USER", "").strip(),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "resend_key": os.getenv("RESEND_API_KEY", "").strip(),
        "brevo_key": os.getenv("BREVO_API_KEY", "").strip(),
        "support_notify_email": os.getenv("SUPPORT_NOTIFY_EMAIL", "prepmasteryonetici@gmail.com").strip() or "prepmasteryonetici@gmail.com",
    }


def email_provider() -> str:
    c = _cfg()
    if not c["from"]:
        return ""
    if c["resend_key"]:
        return "resend"
    if c["brevo_key"]:
        return "brevo"
    if c["smtp_host"] and c["smtp_user"] and c["smtp_password"]:
        return "smtp"
    return ""


def email_configured() -> bool:
    return bool(email_provider())


def get_email_status() -> Dict[str, Any]:
    """Yönetici paneli için gizli anahtar içermeyen durum özeti."""
    c = _cfg()
    provider = email_provider()
    return {
        "configured": bool(provider),
        "provider": provider or "none",
        "from_address": c["from"] or None,
        "support_notify_email": c["support_notify_email"],
        "has_resend_key": bool(c["resend_key"]),
        "has_brevo_key": bool(c["brevo_key"]),
        "has_smtp_credentials": bool(c["smtp_host"] and c["smtp_user"] and c["smtp_password"]),
        "smtp_host": c["smtp_host"] or None,
        "smtp_port": c["smtp_port"] if c["smtp_host"] else None,
        "last_delivery": dict(_LAST_DELIVERY_STATUS) if _LAST_DELIVERY_STATUS else None,
    }


def _record_delivery(ok: bool, provider: str, to: str, subject: str, error: str = "") -> Dict[str, Any]:
    result = {
        "success": ok,
        "provider": provider or "none",
        "to": to,
        "subject": subject,
        "error": error,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _LAST_DELIVERY_STATUS.clear()
    _LAST_DELIVERY_STATUS.update(result)
    return result


# ------------------------------------------------------------------ günlük bütçe
# Brevo ücretsiz planı günde 300 e-posta. Kötüye kullanımda (ör. destek formuna seri
# gönderim, başkası adına kayıt) bu kota dolarsa şifre sıfırlama ve doğrulama kodları da
# gitmez. Bu yüzden e-postalar iki önceliğe ayrılır:
#   - "kritik"  (şifre sıfırlama, doğrulama kodu, yönetici testi): EMAIL_DAILY_LIMIT'e kadar
#   - "normal"  (hoş geldin, destek bildirimi/alındı, erişim bilgisi): EMAIL_DAILY_SOFT_LIMIT'e kadar
# Ayrıca aynı alıcıya günde en fazla EMAIL_PER_RECIPIENT_DAILY "normal" e-posta gider.
# Sayaçlar bellekte tutulur (tek işçi); yeniden başlatmada sıfırlanır — kota koruması için yeterli.
import threading as _threading
from datetime import datetime as _dt, timedelta as _td, timezone as _tz

_BUDGET_LOCK = _threading.Lock()
_BUDGET = {"day": None, "total": 0, "normal": 0, "per_recipient": {}}


def _istanbul_day() -> str:
    return (_dt.now(_tz.utc) + _td(hours=3)).strftime("%Y-%m-%d")


def _limits() -> Dict[str, int]:
    def _int(name, default):
        try:
            return max(0, int(os.getenv(name, str(default))))
        except ValueError:
            return default
    return {
        "hard": _int("EMAIL_DAILY_LIMIT", 290),
        "soft": _int("EMAIL_DAILY_SOFT_LIMIT", 180),
        "per_recipient": _int("EMAIL_PER_RECIPIENT_DAILY", 3),
    }


def _reserve_budget(to: str, priority: str) -> Optional[str]:
    """Gönderim hakkı ayırır; hak yoksa nedenini döner (None = gönderilebilir)."""
    lim = _limits()
    rcpt = (to or "").strip().lower()
    with _BUDGET_LOCK:
        today = _istanbul_day()
        if _BUDGET["day"] != today:
            _BUDGET.update({"day": today, "total": 0, "normal": 0, "per_recipient": {}})
        if _BUDGET["total"] >= lim["hard"]:
            return "Günlük e-posta sınırına ulaşıldı."
        if priority != "kritik":
            if _BUDGET["normal"] >= lim["soft"]:
                return "Günlük bilgilendirme e-postası sınırına ulaşıldı (kritik e-postalar için ayrıldı)."
            if _BUDGET["per_recipient"].get(rcpt, 0) >= lim["per_recipient"]:
                return "Bu alıcıya bugün yeterince e-posta gönderildi."
            _BUDGET["normal"] += 1
            _BUDGET["per_recipient"][rcpt] = _BUDGET["per_recipient"].get(rcpt, 0) + 1
        _BUDGET["total"] += 1
    return None


def get_email_budget() -> Dict[str, Any]:
    lim = _limits()
    with _BUDGET_LOCK:
        same_day = _BUDGET["day"] == _istanbul_day()
        return {
            "day": _istanbul_day(),
            "sent_total": _BUDGET["total"] if same_day else 0,
            "sent_normal": _BUDGET["normal"] if same_day else 0,
            "daily_limit": lim["hard"],
            "normal_limit": lim["soft"],
        }


def send_email_verbose(to: str, subject: str, text: str, html: str = "", priority: str = "normal") -> Dict[str, Any]:
    """E-postayı gönderir ve tanı sonucu döner; gizli bilgi içermez."""
    c = _cfg()
    provider = email_provider()
    if not provider:
        msg = "E-posta sağlayıcısı ayarlı değil (EMAIL_FROM ve BREVO_API_KEY / RESEND_API_KEY / SMTP gerekli)."
        log.warning("E-posta ayarlı değil; gönderilmedi: %s", subject)
        return _record_delivery(False, "none", to, subject, msg)

    blocked = _reserve_budget(to, priority)
    if blocked:
        log.warning("E-posta bütçe nedeniyle gönderilmedi (%s): %s", priority, subject)
        return _record_delivery(False, provider, to, subject, blocked)

    try:
        if provider == "resend":
            import httpx
            r = httpx.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {c['resend_key']}"},
                json={
                    "from": c["from"],
                    "to": [to],
                    "subject": subject,
                    "text": text,
                    **({"html": html} if html else {}),
                },
                timeout=12,
            )
            if r.status_code >= 300:
                err = f"Resend hata {r.status_code}: {r.text[:300]}"
                log.error("%s", err)
                return _record_delivery(False, provider, to, subject, err)
            return _record_delivery(True, provider, to, subject)

        if provider == "brevo":
            import httpx
            name, addr = parseaddr(c["from"])
            sender_obj: Dict[str, str] = {"email": addr or c["from"]}
            if name:
                sender_obj["name"] = name
            payload: Dict[str, Any] = {
                "sender": sender_obj,
                "to": [{"email": to}],
                "subject": subject,
                "textContent": text,
            }
            if html:
                payload["htmlContent"] = html
            r = httpx.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": c["brevo_key"],
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=payload,
                timeout=12,
            )
            if r.status_code >= 300:
                err = f"Brevo hata {r.status_code}: {r.text[:300]}"
                log.error("%s", err)
                return _record_delivery(False, provider, to, subject, err)
            return _record_delivery(True, provider, to, subject)

        msg = EmailMessage()
        name, addr = parseaddr(c["from"])
        msg["From"] = formataddr((name, addr)) if name else addr
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(text)
        if html:
            msg.add_alternative(html, subtype="html")
        context = ssl.create_default_context()
        if c["smtp_port"] == 465:
            with smtplib.SMTP_SSL(c["smtp_host"], 465, context=context, timeout=15) as s:
                s.login(c["smtp_user"], c["smtp_password"])
                s.send_message(msg)
        else:
            with smtplib.SMTP(c["smtp_host"], c["smtp_port"], timeout=15) as s:
                # SMTP_STARTTLS=0 yalnızca yerel test sunucuları (MailHog vb.) içindir
                if os.getenv("SMTP_STARTTLS", "1").strip() != "0":
                    s.starttls(context=context)
                s.login(c["smtp_user"], c["smtp_password"])
                s.send_message(msg)
        return _record_delivery(True, provider, to, subject)
    except Exception as exc:  # ağ, kimlik doğrulama vb.
        err = f"{type(exc).__name__}: {exc}"
        log.error("E-posta gönderilemedi (%s): %s", provider, err)
        return _record_delivery(False, provider, to, subject, err)


def send_email(to: str, subject: str, text: str, html: str = "", priority: str = "normal") -> bool:
    """Gönderir; başarıda True. Hata kullanıcıya sızdırılmaz, yalnızca loglanır."""
    return bool(send_email_verbose(to, subject, text, html, priority=priority).get("success"))


# ------------------------------------------------------------------ şablonlar
def _wrap(title: str, body_html: str) -> str:
    return f"""<!doctype html><html lang="tr"><body style="margin:0;background:#f1f5f9;font-family:Segoe UI,Arial,sans-serif">
<div style="max-width:520px;margin:24px auto;background:#fff;border-radius:16px;padding:28px;border:1px solid #e2e8f0">
<div style="font-weight:800;font-size:18px;color:#1e3a8a;margin-bottom:12px">PrepMaster — Üniversite Hazırlık & Muafiyet Platformu</div>
<h1 style="font-size:18px;color:#0f172a;margin:0 0 12px">{title}</h1>
{body_html}
<hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0 12px">
<p style="font-size:12px;color:#64748b;margin:0">Öğrenci Destek & KVKK İletişim: <b>prepmasteryonetici@gmail.com</b> • Tel: <b>0539 838 18 87</b></p>
<p style="font-size:11px;color:#94a3b8;margin-top:8px">Bu e-postayı siz istemediyseniz yok sayabilirsiniz; hesabınızda bir değişiklik yapılmaz.</p>
</div></body></html>"""


def _code_box(code: str) -> str:
    return (f'<div style="font-size:30px;font-weight:800;letter-spacing:8px;text-align:center;'
            f'background:#eff6ff;color:#1d4ed8;border-radius:12px;padding:14px;margin:16px 0">{code}</div>')


def send_password_reset_email(to: str, code: str, minutes: int = 15) -> bool:
    text = (f"PrepMaster şifre sıfırlama kodunuz: {code}\n\n"
            f"Kod {minutes} dakika geçerlidir. Bu isteği siz yapmadıysanız bu e-postayı yok sayın.")
    html = _wrap("Şifre sıfırlama kodunuz",
                 f'<p style="color:#334155;font-size:14px">Uygulamadaki "Şifremi unuttum" ekranına bu kodu girin:</p>'
                 f'{_code_box(code)}<p style="color:#64748b;font-size:13px">Kod {minutes} dakika geçerlidir.</p>')
    return send_email(to, f"PrepMaster şifre sıfırlama kodu: {code}", text, html, priority="kritik")


def send_student_otp_email(to: str, code: str, minutes: int = 5) -> bool:
    text = (f"PrepMaster öğrenci e-postası doğrulama kodunuz: {code}\n\nKod {minutes} dakika geçerlidir.")
    html = _wrap("Öğrenci e-postası doğrulama",
                 f'<p style="color:#334155;font-size:14px">Öğrenci e-postanızı doğrulamak için bu kodu girin:</p>'
                 f'{_code_box(code)}<p style="color:#64748b;font-size:13px">Kod {minutes} dakika geçerlidir.</p>')
    return send_email(to, f"PrepMaster doğrulama kodu: {code}", text, html, priority="kritik")


def send_welcome_email(to: str, full_name: str, username: str, university_name: str = "") -> bool:
    safe_name = _html.escape(full_name or username or "Öğrenci")
    safe_user = _html.escape(username or "-")
    safe_uni = _html.escape(university_name or "Seçili Üniversite")
    text = (
        f"Merhaba {full_name or username},\n\n"
        f"PrepMaster Üniversite Hazırlık & Muafiyet Platformuna hoş geldin!\n"
        f"Kullanıcı adın: @{username}\nHedef üniversiten: {university_name or 'Seçili Üniversite'}\n\n"
        f"E-Devlet öğrenci belgeni doğrulayarak kendi üniversitenin tüm hazırlık sorularını ücretsiz açabilirsin."
    )
    html = _wrap(
        "PrepMaster'a Hoş Geldin!",
        f'<p style="color:#334155;font-size:14px">Merhaba <b>{safe_name}</b>,</p>'
        f'<p style="color:#334155;font-size:14px">PrepMaster öğrenci hesabın başarıyla oluşturuldu. '
        f'E-Devlet öğrenci belgeni doğrulayarak kendi üniversitenin tüm deneme sınavlarını ücretsiz açabilirsin.</p>'
        f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:12px 16px;font-size:13px;color:#334155">'
        f'<div><b>Kullanıcı Adı:</b> @{safe_user}</div>'
        f'<div style="margin-top:4px"><b>Hedef Üniversite:</b> {safe_uni}</div></div>'
    )
    return send_email(to, "PrepMaster'a Hoş Geldin — Öğrenci Hesabın Hazır", text, html)


def send_support_ticket_notification(
    ticket_id: int,
    category: str,
    student_name: str,
    student_email: str,
    student_phone: str,
    message: str,
    to: str = "",
) -> bool:
    target = (to or _cfg()["support_notify_email"]).strip()
    if not target:
        return False
    text = (
        f"Yeni PrepMaster Destek / KVKK Talebi (#{ticket_id})\n"
        f"Kategori: {category}\n"
        f"Ad Soyad: {student_name or '-'}\n"
        f"E-Posta: {student_email or '-'}\n"
        f"Telefon: {student_phone or '-'}\n\n"
        f"Mesaj:\n{message}"
    )
    html = _wrap(
        f"Yeni Destek / KVKK Talebi (#{ticket_id})",
        f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px;font-size:13px;color:#334155;line-height:1.6">'
        f'<div><b>Kategori:</b> {_html.escape(category or "-")}</div>'
        f'<div><b>Gönderen:</b> {_html.escape(student_name or "Ziyaretçi")}</div>'
        f'<div><b>E-Posta:</b> {_html.escape(student_email or "-")}</div>'
        f'<div><b>Telefon:</b> {_html.escape(student_phone or "-")}</div></div>'
        f'<p style="color:#0f172a;font-size:14px;background:#eff6ff;padding:14px;border-radius:12px;margin-top:14px;white-space:pre-wrap">{_html.escape(message)}</p>'
    )
    return send_email(target, f"[PrepMaster Destek #{ticket_id}] {(category or 'Genel')[:60]}", text, html)


def send_support_ticket_receipt(to: str, ticket_id: int, category: str) -> bool:
    if not to or "@" not in to:
        return False
    text = (
        f"Merhaba,\n\n"
        f"#{ticket_id} numaralı ({category}) destek/KVKK talebiniz PrepMaster ekibine ulaşmıştır.\n"
        f"En kısa sürede prepmasteryonetici@gmail.com veya 0539 838 18 87 üzerinden size dönüş yapılacaktır."
    )
    html = _wrap(
        f"Destek Talebiniz Alındı (#{ticket_id})",
        f'<p style="color:#334155;font-size:14px"><b>#{ticket_id}</b> numaralı (<b>{_html.escape(category or "Genel")}</b>) talebiniz başarıyla kaydedildi.</p>'
        f'<p style="color:#334155;font-size:14px">Ekibimiz en kısa sürede dönüş yapacaktır. Acil durumlar için destek hattımızdan ulaşabilirsiniz.</p>'
    )
    return send_email(to, f"PrepMaster Destek Talebiniz Alındı (#{ticket_id})", text, html)


def send_access_granted_email(to: str, full_name: str, unlocked_universities: List[str]) -> bool:
    if not to or "@" not in to:
        return False
    unis = [u.upper() for u in (unlocked_universities or []) if u and u != "general"]
    summary = "Tüm 26 Üniversite (Tam Erişim)" if len(unis) >= 26 else (", ".join(unis) or "Genel Havuz")
    text = (
        f"Merhaba {full_name or 'Öğrenci'},\n\n"
        f"PrepMaster hesabınıza üniversite erişim yetkisi tanımlandı: {summary}\n"
        f"Platforma giriş yaparak tüm deneme sınavlarına hemen başlayabilirsiniz."
    )
    html = _wrap(
        "Üniversite Sınav Paketiniz Açıldı!",
        f'<p style="color:#334155;font-size:14px">Merhaba <b>{_html.escape(full_name or "Öğrenci")}</b>,</p>'
        f'<p style="color:#334155;font-size:14px">Yönetici onayıyla hesabınıza aşağıdaki üniversite erişimleri tanımlandı:</p>'
        f'<div style="background:#ecfdf5;border:1px solid #a7f3d0;color:#065f46;border-radius:12px;padding:12px 16px;font-weight:700;font-size:13px">{_html.escape(summary)}</div>'
    )
    return send_email(to, "PrepMaster Üniversite Erişiminiz Aktif Edildi", text, html)
