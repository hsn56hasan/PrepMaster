# PrepMaster - Üniversite Hazırlık & Muafiyet Platformu
> **Çift Platformlu Mimari (Dual-Platform):** Web Platformu (FastAPI + Modern Web) & Native Mobil Uygulama (Flutter iOS/Android)

Hazırlık öğrencilerinin üniversite muafiyet (İTÜ, ODTÜ, Boğaziçi BUEPT, Bilkent COPE, YTÜ) ve kur bitirme (CEFR A1–C2) sınavlarına eksiksiz hazırlanabilmesi için tasarlanmış kapsamlı çalışma platformudur.

---

## 📱 Platform 1: Native Mobil Uygulama (Flutter)

Flutter ile geliştirilmiş, tamamen offline çalışabilen ve yerel backend API ile senkronize olabilen yerel mobil uygulama.

### 🏃 Çalıştırma Seçenekleri
1. **Masaüstünde veya Bağlı Telefonda Başlatmak İçin:**
   - **`run_mobile.bat`** dosyasına çift tıklayın.
   - Seçenek menüsünden:
     - `1`: Bağlı telefon veya otomatik cihazda başlatır (`flutter run`).
     - `2`: Windows Masaüstü uygulaması olarak doğrudan açar (`flutter run -d windows`).
     - `3`: Web tarayıcısında Flutter çıktısı olarak açar (`flutter run -d chrome`).

2. **Android APK Oluşturmak (Telefona Direkt Yüklemek İçin):**
   - **`build_apk.bat`** dosyasına çift tıklayın.
   - İşlem bittiğinde oluşturulan dosya:
     `mobile\build\app\outputs\flutter-apk\app-debug.apk`
   - Bu APK dosyasını doğrudan WhatsApp, Bluetooth veya USB kablosu ile Android telefonunuza atıp kurabilirsiniz.

### 📱 Mobil Uygulama Özellikleri
- **Dashboard & Hedef Üniversite:** İTÜ, ODTÜ, Boğaziçi, Bilkent, YTÜ geçiş baraj puanları ve A1–C2 seviye filtreleri.
- **Sesli Dinleme & Not Alma (Listening):** Boğaziçi BUEPT, İTÜ ve ODTÜ EPE sesli ders simülasyonu, Note-Taking dijital not kağıdı ve While-Listening modları.
- **Yapay Zeka Destekli Essay Değerlendirici:** Öğrencinin yazdığı kompozisyona anlık CEFR notu (A2-C1), 4 temel kriter puanı (Task, Cohesion, Lexical, Grammar), bağlaç tespiti ve Türkçe iyileştirme tavsiyeleri (100% Çevrimdışı destekli).
- **Sınav Simülatörü (Exam Runner):** Canlı geri sayım, soru işaretleme (flagging), soru navigasyon paleti ve soru başına harcanan süre sayacı.
- **Detaylı Çözüm & Hız Analitiği:** 90 saniyeyi aşan zaman tuzaklarının tespiti ve Türkçe açıklamalı çözümler.
- **Akıllı Hata Defteri (Mistake Vault):** Yanlış soruların şık karşılaştırması ve tek tıkla *"Yanlışlarımı Sınav Olarak Tekrar Çöz"* motoru.
- **3D Çevrilebilir Kelime Kartları (Flashcards):** Kelime telaffuzu, collocations, Türkçe anlamlar ve "Öğrendim / Tekrar Et" durumu.
- **Writing Rehberi:** Essay iskeletleri, argüman yapıları, geçiş bağlaçları (transitions) ve hazır örnekler.
- **Offline-First & Smart Sync:** İnternet veya backend kapalı olsa bile tüm soru, dinleme ve kelime veritabanı mobil uygulama içinde gömülüdür (bundled assets). Backend açık olduğunda verileri anlık senkronize eder.

---

## 🌐 Platform 2: Web Platformu (PC & Mobil Tarayıcı)

FastAPI ve responsive web arayüzü ile güçlendirilmiş masaüstü ve tarayıcı portalı.

### 🚀 Hızlı Başlatma
- **`run.bat`** dosyasına çift tıklayın.
- **PC Tarayıcısından Erişim:**  
  👉 **http://localhost:8050**
- **Aynı Wi-Fi Ağındaki Telefondan / Tabletten Erişim:**  
  👉 **http://172.16.1.211:8050**
  *(Safari veya Chrome menüsünden "Ana Ekrana Ekle" diyerek PWA olarak da kullanılabilir.)*

---

## 📂 Proje Dizin Yapısı

```
C:\Projeler\PrepMaster\
│
├── run.bat                 # Web Sunucusunu Başlatıcı (Port 8050)
├── run_mobile.bat          # Flutter Mobil / Masaüstü Uygulama Başlatıcı
├── build_apk.bat           # Android APK Oluşturucu
│
├── backend/                # FastAPI REST API & SQLite Veritabanı
│   ├── app.py
│   └── database.py
│
├── data/                   # Ortak Veri Setleri (JSON)
│   ├── questions.json      # A1 - C2 Kapsamlı Soru Bankası
│   ├── universities.json   # Üniversite Sınav Formatları ve Barajları
│   ├── vocabulary.json     # Akademik Kelime Kartları
│   └── writing_guides.json # Essay Rehberleri ve Bağlaçlar
│
├── static/                 # Web Arayüzü (HTML5, CSS3, ES6 JS)
│   ├── css/style.css
│   ├── js/ (app.js, exam.js, flashcards.js)
│   ├── index.html
│   └── manifest.json
│
└── mobile/                 # Flutter Native Mobil Uygulama Kaynak Kodları
    ├── assets/data/        # Mobil Gömülü Veri Setleri
    ├── lib/
    │   ├── main.dart
    │   ├── models/         # Data Modelleri (University, Question, MistakeItem...)
    │   ├── services/       # ApiService (Auto Host Detection + Offline Fallback)
    │   ├── theme/          # AppTheme (Modern Indigo/Slate Tasarım Dili)
    │   └── screens/        # Dashboard, Exams, MistakeVault, Flashcards, Writing, Analytics
    └── test/               # Flutter Otomasyon Testleri
```

---

## 🔄 Çift Platform Geliştirme Politikası

Tüm yeni özellikler ve güncellemeler (Listening ses simülatörü, Yapay Zeka Essay Puanlama, yeni soru paketleri) her iki platforma (Web ve Flutter Mobil) aynı anda eklenecektir.
