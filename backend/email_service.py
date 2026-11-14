"""
E-posta gönderimi (şifre sıfırlama ve öğrenci doğrulama kodları).

İki yol desteklenir, .env ile seçilir:
  1) SMTP — ör. vectonis.com'un Zoho Mail hesabı:
       SMTP_HOST=smtp.zoho.eu   SMTP_PORT=465   SMTP_USER=noreply@vectonis.com
       SMTP_PASSWORD=<Zoho uygulama şifresi>
  2) Resend (HTTP API):
       RESEND_API_KEY=re_...
Her ikisinde de:
       EMAIL_FROM="PrepMaster <noreply@vectonis.com>"

Hiçbiri ayarlı değilse email_configured() False döner; şifre sıfırlama kapalı kalır
(kod istemciye ASLA yanıtta gönderilmez, yalnızca DEMO_MODE hariç).
"""
import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

try:
    import env_loader  # noqa: F401  (.env'i yükler)
except ImportError:
    from backend import env_loader  # noqa: F401

log = logging.getLogger("prepmaster.email")


def _cfg():
    return {
        "from": os.getenv("EMAIL_FROM", "").strip(),
        "smtp_host": os.getenv("SMTP_HOST", "").strip(),
        "smtp_port": int(os.getenv("SMTP_PORT", "465") or 465),
        "smtp_user": os.getenv("SMTP_USER", "").strip(),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "resend_key": os.getenv("RESEND_API_KEY", "").strip(),
    }


def email_provider() -> str:
    c = _cfg()
    if not c["from"]:
        return ""
    if c["resend_key"]:
        return "resend"
    if c["smtp_host"] and c["smtp_user"] and c["smtp_password"]:
        return "smtp"
    return ""


def email_configured() -> bool:
    return bool(email_provider())


def send_email(to: str, subject: str, text: str, html: str = "") -> bool:
    """Gönderir; başarıda True. Hata kullanıcıya sızdırılmaz, yalnızca loglanır."""
    c = _cfg()
    provider = email_provider()
    if not provider:
        log.warning("E-posta ayarlı değil; gönderilmedi: %s", subject)
        return False
    try:
        if provider == "resend":
            import httpx
            r = httpx.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {c['resend_key']}"},
                json={"from": c["from"], "to": [to], "subject": subject, "text": text,
                      **({"html": html} if html else {})},
                timeout=10,
            )
            if r.status_code >= 300:
                log.error("Resend hata %s: %s", r.status_code, r.text[:300])
                return False
            return True

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
        return True
    except Exception as exc:  # ağ, kimlik doğrulama vb.
        log.error("E-posta gönderilemedi (%s): %s", provider, exc)
        return False


# ------------------------------------------------------------------ şablonlar
def _wrap(title: str, body_html: str) -> str:
    return f"""<!doctype html><html lang="tr"><body style="margin:0;background:#f1f5f9;font-family:Segoe UI,Arial,sans-serif">
<div style="max-width:480px;margin:24px auto;background:#fff;border-radius:16px;padding:28px;border:1px solid #e2e8f0">
<div style="font-weight:800;font-size:18px;color:#1e3a8a;margin-bottom:12px">PrepMaster</div>
<h1 style="font-size:18px;color:#0f172a;margin:0 0 12px">{title}</h1>
{body_html}
<p style="font-size:12px;color:#94a3b8;margin-top:24px">Bu e-postayı siz istemediyseniz yok sayabilirsiniz; hesabınızda bir değişiklik yapılmaz.</p>
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
    return send_email(to, f"PrepMaster şifre sıfırlama kodu: {code}", text, html)


def send_student_otp_email(to: str, code: str, minutes: int = 5) -> bool:
    text = (f"PrepMaster öğrenci e-postası doğrulama kodunuz: {code}\n\nKod {minutes} dakika geçerlidir.")
    html = _wrap("Öğrenci e-postası doğrulama",
                 f'<p style="color:#334155;font-size:14px">Öğrenci e-postanızı doğrulamak için bu kodu girin:</p>'
                 f'{_code_box(code)}<p style="color:#64748b;font-size:13px">Kod {minutes} dakika geçerlidir.</p>')
    return send_email(to, f"PrepMaster doğrulama kodu: {code}", text, html)
