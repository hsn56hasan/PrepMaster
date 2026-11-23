# PrepKampüs - Üniversite Hazırlık & Muafiyet Platformu
> **Çift Platformlu Mimari (Dual-Platform):** Web Platformu (FastAPI + Modern Web + PWA) & Native Mobil Uygulama (Flutter Android APK / iOS)

Türkiye'deki **26 üniversitenin** İngilizce hazırlık muafiyet (İTÜ Proficiency, Boğaziçi BUEPT, ODTÜ EPE, Bilkent PAE, YTÜ İYS, Koç KUEPE, Sabancı ELAE, Hacettepe, Ankara, Gazi, Ege, Marmara, İstanbul, Cerrahpaşa, Dokuz Eylül, İYTE, Anadolu, ESTÜ, GTÜ, Akdeniz, Çukurova, Uludağ, Özyeğin TRACE, Bahçeşehir, Yeditepe, TOBB ETÜ) ve kur bitirme (**CEFR A1–C2**) sınavlarına eksiksiz hazırlanabilmesi için tasarlanmış kapsamlı çalışma platformudur.

---

## 🌐 Canlı Erişim Adresleri (Railway Production)
- **Öğrenci Platformu:** https://prepmaster-web-production.up.railway.app
- **Bağımsız Yönetici Paneli (`/admin`):** https://prepmaster-web-production.up.railway.app/admin
- **6698 S. KVKK & Yasal Belgeler (`/kvkk`):** https://prepmaster-web-production.up.railway.app/kvkk
- **Android APK Doğrudan İndirme:** https://prepmaster-web-production.up.railway.app/api/download/apk

---

## 📊 İçerik ve Soru Bankası Kapasitesi
- **26 Üniversite + Genel Havuz:** Her üniversitenin kendi sınav formatına göre ayrılmış özgün soru ve simülasyon havuzu.
- **10.901 Çoktan Seçmeli Sınav Sorusu:** Her üniversite için **180 soru** (A1, A2, B1, B2, C1, C2 kurlarının her birinde **30'ar soruluk** tam kur sınavı).
  Genel havuzda ayrıca 120 özgün sınav tipi soru (`scripts/add_original_questions.py`) ve 2.019 kelimeden üretilen 5.855 kelime sorusu (`scripts/build_vocabulary.py`) bulunur.
- **2.019 Kelimelik Sözlük:** A1–C2, Türkçe anlam, İngilizce tanım, eş/zıt anlam, örnek cümle ve kalıp (`scripts/kelime_kaynak/`).
- **656 Akademik Listening Sınavı:** Her üniversite için **24 adet** (kur başına 4'er adet) Note-Taking ve While-Listening sesli ders simülasyonu.
- **657 Akademik Speaking Görevi:** Her üniversite için **24 adet** (kur başına 4'er adet) hazırlık/konuşma süreli mülakat simülasyonu.
- **190+ Akademik Kelime Kartı (Flashcards) & AI Writing Değerlendirici.**

---

## 🛡️ Güvenlik, DoS Koruması, Kalıcı Veritabanı & KVKK Uyumluluğu
- **Kalıcı Railway Volume (`/data/prepmaster.db`):** SQLite WAL modunda çalışan kalıcı disk ile tüm öğrenci kayıtları, sınav geçmişleri ve yönetici üniversite tanımlamaları sunucu yeniden başlasa bile kalıcı olarak korunur.
- **Çok Katmanlı DoS / Flood Savunma Sistemi (`DoSProtectionMiddleware`):**
  - IP bazlı patlama (burst), genel ve `/api/` hız sınırlandırması (`429 Too Many Requests` + `Retry-After`).
  - Sınırı ısrarla aşan saldırgan IP'lere **10 dakika otomatik geçici yasaklama (Auto-Ban)**.
  - Büyük gövde saldırılarına karşı `413 Payload Too Large` koruması (`2 MB` JSON / `10 MB` belge sınırı) ve Uvicorn `--limit-concurrency 300`.
- **6698 Sayılı KVKK Yasal Belgeler & Öğrenci Destek Hattı:**
  - Aydınlatma Metni (`PM-KVKK-01`), Açık Rıza Beyanı (`PM-KVKK-02`), Gizlilik & Çerez Politikası (`PM-KVKK-03`), Kullanıcı Sözleşmesi (`PM-HUKUK-04`) ve KVKK Başvuru Formu (`PM-KVKK-05`).
  - **Resmi Destek İletişim:** `prepmasteryonetici@gmail.com` | Tel & WhatsApp: `0539 838 18 87`.
- **Canlı E-Posta Altyapısı (Brevo / Resend / SMTP) & Hamburger Menü Düzeni:**
  - `backend/email_service.py` ile Railway planlarıyla tam uyumlu **Brevo HTTPS API**, **Resend HTTPS API** ve **SMTP** desteği; şifre sıfırlama, `.edu.tr` OTP, hoş geldin, Destek/KVKK bildirimi, üniversite açılış bilgilendirmesi ve `/admin` üzerinden canlı test e-postası gönderimi aktiftir.
  - Üst menü öğeleri ve `Destek & KVKK` erişimi `☰` hamburger menüde sadeleştirilmiştir.
  - **Bekleyen Adım:** PayTR mağaza başvurusu onaylandığında `PAYTR_MERCHANT_ID`, `PAYTR_MERCHANT_KEY` ve `PAYTR_MERCHANT_SALT` değişkenleri tanımlanarak ödeme akışı canlıya açılacaktır.
