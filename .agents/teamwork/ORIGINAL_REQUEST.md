# Original User Request

## 2026-10-14T09:54:56Z

Requested team: Full multi-agent team for dual-platform development (Web + Native Flutter)

Complete all remaining functional and content gaps in the PrepMaster English proficiency preparation platform across both the Web Portal and Native Flutter Mobile application with 100% feature parity.

Working directory: C:\Projeler\PrepMaster
Integrity mode: development

## Requirements

### R1. User Authentication & Account Management UI (Web & Mobile)
- Connect existing backend authentication endpoints (/api/auth/register, /api/auth/login, /api/auth/me) to the user interfaces.
- Web: Implement responsive Login / Register modals and dynamic session state in the header (displaying user name, verification badge, and logout action).
- Mobile: Implement Login and Register screens/bottom sheets with persistent local token storage and automatic session restoration.

### R2. High-Scoring Essay Library & Writing Exemplars
- Expand the Writing section with an authentic library of annotated student sample essays (Band 85+ exemplars and common pitfall analyses) for Opinion, For & Against, and Problem-Solution essay types.
- Ensure exemplars are accessible both online and offline across Web and Flutter.

### R3. Academic Listening Track Expansion (4 → 8 Tracks)
- Add 4 new university-specific academic listening tracks (covering Boğaziçi, ODTÜ, İTÜ, and Bilkent) with note-taking guidelines, transcripts, and multiple-choice questions.
- Maintain dual-platform asset synchronization between data/listening.json and mobile/assets/data/listening.json.

### R4. Dark Mode (Gece Modu) Theme Support
- Implement a persistent Dark/Light theme toggle for both Web (Tailwind dark classes / CSS variables) and Flutter Mobile (ThemeMode.dark with custom dark AppTheme palette).

## Acceptance Criteria

### Authentication & Multi-User Parity
- [ ] Users can register, log in, and log out with custom credentials on both Web and Mobile.
- [ ] Logged-in user's student status, university, and progress sync seamlessly across devices.

### Content & Parity Verification
- [ ] data/listening.json contains at least 8 complete tracks and parses with 100% valid fields in mobile/test/dataset_integrity_test.dart.
- [ ] Writing library renders annotated model essays with thesis, topic sentences, and CEFR breakdown.

### Code Quality & Build Verification
- [ ] flutter analyze reports 0 errors and 0 warnings.
- [ ] flutter test passes all unit and integration tests (100%).
- [ ] flutter build apk --debug completes with exit code 0.
- [ ] All changes are cleanly committed to Git.

## 2026-10-18T12:30:47Z

Requested team: Full multi-agent platform team for dual-platform full stack development

PrepMaster platformunda yeni eklenen üniversiteler için özgün akademik soru havuzu üretimi, 3D Secure Sanal POS sandbox ödeme geçidi, Google OAuth & şifre sıfırlama ve Flutter mobil arayüz entegrasyonunu (Paywall & Belge Tarama BottomSheet) %100 çift platform eşitliğiyle hayata geçirin.

Working directory: C:\Projeler\PrepMaster
Integrity mode: development

## Requirements

### R1. Yeni Üniversiteler İçin Özgün Akademik Soru Havuzu Üretimi (Hacettepe, Ankara, Gazi, Ege, Koç, Sabancı)
- Boğaziçi (BUEPT), ODTÜ (EPE) ve İTÜ sınavları örnek alınarak 6 yeni üniversitenin her biri için en az 12'şer adet (toplam 72+ yeni soru) özgün soru üretin:
  - **Hacettepe Üniversitesi**: Restatement, Paragraph Comprehension, Academic Structure & Reading.
  - **Ankara Üniversitesi**: Cloze Test, Reading Analysis, Vocabulary in Context.
  - **Gazi Üniversitesi**: Use of English, Grammar & Academic Collocations.
  - **Ege Üniversitesi**: Sentence Completion, Contextual Inference, Paragraph Flow.
  - **Koç Üniversitesi (KUEPE)**: Advanced Academic Reading, Critical Analysis, High-Level Restatement.
  - **Sabancı Üniversitesi (ELAE)**: Search Reading, Synthesizing Text, Academic Vocabulary.
- Soruların tamamını Türkçe detaylı açıklamaları (`explanation_tr`), akademik ipuçları ve CEFR seviyeleriyle donatın.
- Hem `data/questions.json` hem de `mobile/assets/data/questions.json` dosyalarını birebir senkronize edin.

### R2. 50 TL Sanal POS / 3D Secure Sandbox Ödeme Geçidi & E-Arşiv Fişi
- İyzico / PayTR standartlarında 3D Secure ödeme simülasyonu:
  - Kart bilgileri girildikten sonra banka SMS onay ekranı (6 haneli doğrulama kodu penceresi) simülasyonu.
  - Başarılı ödeme sonrası Gelir İdaresi Başkanlığı (GİB) uyumlu E-Arşiv Fatura / Fiş Referansı (`EARSIV-2026-XXXX`) ve ödeme dekontu makbuzu üretimi.
  - `/api/membership/unlock` uç noktasının 3D Secure SMS doğrulamasını desteklemesi.

### R3. Google OAuth 2.0 & Şifre Sıfırlama Akışı
- **Google ile Giriş (Sign in with Google)**: Web giriş modalına "Google ile Giriş Yap" seçeneği ve backend `/api/auth/google` OAuth akışı (kullanıcı profili ve token üretimi).
- **Şifremi Unuttum (Forgot Password)**: E-postaya 6 haneli şifre sıfırlama kodu gönderimi (`/api/auth/forgot-password`) ve yeni şifre belirleme ekranı (`/api/auth/reset-password`).

### R4. Flutter Mobil 50 TL Paywall & Belge Tarama Arayüzü (BottomSheet / Dialog)
- Flutter mobil uygulamasında (`exams_screen.dart`, `dashboard_screen.dart`, `home_navigation.dart`):
  - **50 TL Paywall BottomSheet**: Kendi kayıtlı okulu dışındaki sınavlara veya okul değiştiriciye tıklandığında 50 TL üyelik penceresi, kart formu ve `api_service.unlockUniversityMembership` entegrasyonu.
  - **Öğrenci Belgesi Tarama BottomSheet**: E-Devlet metni yapıştırma veya 1-tık test şablonlarıyla `api_service.scanStudentDocument` tetikleme ve otomatik okul güncelleme.
  - Sınav başlatma butonlarına paywall denetimi (`api_service.checkUniversityAccess`) ekleme.

## Acceptance Criteria

### İçerik & Soru Havuzu Doğrulaması
- [ ] `data/questions.json` ve `mobile/assets/data/questions.json` toplam soru sayısı en az 195'e ulaşır.
- [ ] Hacettepe, Ankara, Gazi, Ege, Koç ve Sabancı üniversitelerinin her birinde en az 12'şer adet soru bulunur.
- [ ] `mobile/test/dataset_integrity_test.dart` tüm soruları hatasız parse eder.

### Ödeme & 3D Secure
- [ ] Web Paywall modalında kart bilgileri girildikten sonra 3D Secure SMS doğrulama adımı çalışır.
- [ ] Ödeme tamamlandığında E-Arşiv Fiş numarası üretilir ve okul kilidi açılır.

### Google Giriş & Şifre Sıfırlama
- [ ] Google ile giriş tıklandığında hesap oluşturulur veya oturum açılır.
- [ ] Şifremi unuttum akışı doğru kod girildiğinde şifreyi günceller.

### Mobil & Kod Kalitesi
- [ ] Flutter `flutter analyze` 0 hata ve 0 uyarı verir.
- [ ] Flutter `flutter test` tüm testleri %100 başarıyla geçer.
- [ ] Python testleri ve `deploy_check.py` 65/65 testi başarıyla geçer.
- [ ] Tüm geliştirmeler Git reposuna temiz bir commit ile kaydedilir.
