# PrepMaster — Yol Haritası
**14.11.2026** · 5 araştırma ajanı (kod taraması, pedagoji, içerik denetimi, pazar, canlıya çıkış). Kritik iddialar kodda ayrıca doğrulandı (✔).

Kısaltmalar: **K** küçük (saatler) · **O** orta (1–2 gün) · **B** büyük (günler+) · 🤖 LLM gerekir · 👤 kodla değil, senin yapman gereken iş

---

## 1. HEMEN — şu an kullanıcıyı yanıltan ya da bozuk olanlar

> ✅ **14.11.2026'da 10'u da yapıldı.** Testler: `backend/test_quick_fixes.py` (11 test). Notlar:
> şıklar `scripts/shuffle_answer_keys.py` ile kalıcı karıştırıldı (A %70 → %27; dinlemede B %70 → %25), açıklamalardaki
> harf atıfları da eşlendi; "doğru şık en uzun şık" ipucu (%68) HÂLÂ duruyor — içerik işi. Sahte fatura yerine
> "Ödeme özeti — fatura değildir". Şifremi unuttum / Google butonları e-posta ve gerçek Google girişi gelene kadar gizlendi.
> Mobil: INTERNET izni eklendi, ama yayın sürümü düz `http` adresine yine bağlanamaz (Android varsayılanı) — canlı sunucu HTTPS olmalı.

| # | Sorun | Kanıt | İş |
|---|---|---|---|
| 1 | **Web'de 50 TL ödeme penceresi ve belge dosyası yükleme çalışmıyor.** `app.js:1406` tanımsız `submitStudentVerification`'a atıf yapıp hata veriyor; dosyanın geri kalanı yürümüyor, sonradaki `let` değişkenleri (`currentPaywallTargetUniId`, `selectedDocFile`) erişilemez kalıyor. ✔ | `static/js/app.js:1406, 1430, 1638` | K |
| 2 | **Doğru cevapların %70'i "A"** (197 sorudan 137) ve şıklar hiçbir yerde karıştırılmıyor. Okumadan hep A diyen yüksek puan alır. Doğru şık %68 oranında en uzun şık. ✔ | `data/questions.json` | K (karıştırma) + O (çeldiricileri düzeltme) |
| 3 | **Ödeme sonrası sahte "GİB e-Arşiv onaylı" fatura** uydurma vergi dairesi/numarasıyla gösteriliyor. Gerçek para alınırken yasal risk. ✔ | `backend/database.py:483-484`, `static/index.html:~1276` | K |
| 4 | **Çalışma serisi hep "1 Gün"**; hiçbir kod artırmıyor. ✔ | `database.py:37`, `app.js:226` | K |
| 5 | **Tam deneme = hep aynı ilk 15 soru**; puan "doğru/cevaplanan" olduğu için boş bırakmak puanı şişiriyor. ✔ | `app.py` `combined_questions[:15]`, `score = correct/answered` | K |
| 6 | **Dinlemedeki yanlışlar Hata Kasası'na düşmüyor**, üstüne %0'lık sahte deneme kaydı açıyor (istatistikleri bozuyor). | `listening.js:731`, `app.py /api/exam/submit` | O |
| 7 | **ODTÜ içeriğinin bir kısmı görünmüyor**: `odtu` kimliğiyle 2 soru + 2 dinleme + 3 konuşma; üniversite kimliği `metu`. | `data/*.json` | K |
| 8 | "Şifremi unuttum" ve "Google ile giriş" butonları ölü (auth.js yüklenmiyor, form HTML'i yok). | `index.html:902, 920` | O |
| 9 | Mobil yayın sürümünde **INTERNET izni yok** → telefona kurulan APK sunucuya bağlanamaz. ✔ | `mobile/android/app/src/main/AndroidManifest.xml` | K |
| 10 | Küçükler: deneme başlığı görünmüyor (`exam-active-title` yok); dar ekranda Dinleme/Konuşma/Analiz sekmelerine ulaşılamıyor. | `exam.js:148`, `index.html:633-653` | K |

---

## 2. CANLIYA ÇIKIŞ — ilk 50 TL için zorunlu

**Önce sen (en uzun süren kısım, haftalar):**
- 👤 Vergi kaydı (şahıs şirketi yeterli olabilir) + mali müşavir. PayTR ve fatura bunsuz olmaz.
- 👤 PayTR mağaza başvurusu — sitede yasal metinler hazır olmalı.
- 👤 Yasal metinler: KVKK aydınlatma, gizlilik, mesafeli satış sözleşmesi + ön bilgilendirme, iade/cayma (dijital içerik istisnası için ödeme öncesi onay kutusu). `static/` içinde hiçbiri yok.
- 👤 Alan adı + sunucu (Hetzner benzeri ~6 €/ay yeterli; Türk VPS yurt dışı veri aktarımı yükünü azaltır).

**Kod tarafı (~3–5 iş günü tahmini):**
| # | İş | Neden | İş |
|---|---|---|---|
| 11 | ✅ **(14.11 yapıldı — web ↔ mobil eşitleme dahil; `backend/test_per_user_sync.py`)** **Kullanıcı bazlı veri**: `vocab_progress`, `mistake_vault`, `question_bookmarks` anahtarı yalnızca kelime/soru id'si; `exam_attempts.user_id` hep 1; `/api/profile, /mistakes, /stats, /sync, /report` kimlik sormuyor. | Şu an herkes herkesin verisini görüp değiştiriyor. Kişiselleştirme önerilerinin hiçbiri bunsuz anlamlı değil. | O–B |
| 12 | **PayTR iFrame'i web'e bağlamak** (simüle 3DS yerine), nginx CSP'ye `frame-src paytr.com`, gerçek müşteri IP'si (`--proxy-headers`), tekrar eden bildirime karşı sipariş tablosu, `debug_on=0`. | Şu an canlıda ödeme almanın hiçbir yolu yok. | O |
| 13 | ✅ **(14.11 kod tarafı yapıldı — SMTP/Resend, web+mobil "Şifremi unuttum"; `.env`e SMTP bilgisi girilince açılır)** **E-posta gönderimi** (Resend: 3.000/ay ücretsiz, Brevo: 300/gün ücretsiz) + şifre sıfırlama ekranı. | Şifre sıfırlama ve OTP canlıda çalışmıyor. | K–O |
| 14 | Öğrenci belgesi yerine **.edu.tr e-posta doğrulaması** (belge şartsa: doğrula, dosyayı hemen sil). | KVKK kararları TC kimlik no içeren belge kopyası saklamayı aşırı veri işleme sayıyor. | O |
| 15 | SQLite WAL modu + gece yedeği (sunucu dışına). Yedekleme şu an hiç yok. | Veri kaybı | K |
| 16 | Mobil ödemeyi web'e bırakmak. | Play Store dijital içerikte Google Play Billing istiyor; Türkiye için alternatif ödeme yolu açık değil. | K |

---

## 3. ÜRÜN — öğrenciyi geri getiren ve rakiplerden ayıran özellikler
Değere göre sıralı. Pazar araştırmasına göre öğrencilerin en çok zorlandığı 5 şey: **essay**, **note-taking**, **okuma hızı**, **akademik kelime/collocation**, **üniversiteye özgü format**.

| # | Özellik | Neden | İş |
|---|---|---|---|
| 17 | **Gerçek aralıklı tekrar (SRS)** kelime kartlarında: "bugün tekrar edilecek N kelime". Şu an 600 kart sırayla dönüyor; `review_count/last_reviewed` var ama okunmuyor. | Her gün geri gelme nedeni. | O |
| 18 | **Note-taking modülü**: 10–15 dk akademik ders → not al → notlarla soru cevapla → örnek notla karşılaştır. Rakiplerde yalnızca bir ODTÜ blogu yapıyor. | ODTÜ, BUEPT, Bilkent'te ağır bölüm; öğrencilerin "ciddi zor" dediği şey. | B |
| 19 | **Üniversite rubriğine göre essay değerlendirme** (+ dilbilgisi geri bildirimi, Hata Kasası'na bağlantı). Şu an kelime sayan kural tabanlı; anlamsız ama "akademik kelimeli" metin yüksek puan alır. Kısa vade: rubriği göster, sınava göre kelime aralığı (İTÜ 300–350, sabit 250 değil). | En zor bölüm; Temadil bunu ayda 10.500 TL'ye satıyor. | K (rubrik) + O 🤖 |
| 20 | **Seviye tespit sınavı + ilk giriş akışı** (hedef üniversite, sınav tarihi, seviye). Şu an herkes B2'de başlıyor. | Doğru seviyeden başlatma | O |
| 21 | **Gerçeğe uygun tam deneme**: rastgele, sınavın gerçek soru sayısı, bölüm ağırlıkları, dinleme+yazma bölümleri. Arka uç bu bölümleri zaten gönderiyor, istemci kullanmıyor. | "Üniversiteye birebir simülasyon" rakiplerin hiçbirinde yok. | B |
| 22 | **Uzun metinli okuma modülü** (400–1000 kelime, parça başına 4–6 soru, süreli). Mevcut okuma parçaları 56–125 kelime. | Reading tüm sınavlarda en büyük bölüm (%30–35). | B (içerik ağırlıklı) |
| 23 | **Zayıf konu analizi + sınav tarihine göre çalışma planı.** Şu an "hazır mısın" tek satırlık kural. | "Neye çalışmalıyım?" | O |
| 24 | Hata Kasası'nda aralıklı yeniden sorma (tek doğru cevapla "çözüldü" sayılmasın). | Kalıcı öğrenme | K |
| 25 | Gramer mikro dersleri + sorulara konu etiketi (197 sorunun hiçbirinde `topic` yok). | Yanlıştan derse bağlantı | O–B |
| 26 | Bildirim / günlük hedef (mobilde bildirim paketi yok). | Geri gelme | O |

---

## 4. İÇERİK — gerçek sınava göre eksikler

| Üniversite | Okuma sorusu var / sınavda | Diğer eksik |
|---|---|---|
| Gazi | **0** / 20 | Vocabulary 4/15 |
| ODTÜ | 5 / 30 | Language Use |
| Bilkent | 5 / 25 | |
| İTÜ | 7 / 25 | Toplam 20 soru, sınavda 50 |
| YTÜ | 3 / 20 | Toplam yalnızca 7 soru; Vocabulary in Context 1/15 |
| Ankara | 4 / 25 | |
| Hacettepe | 8 / 30 | Use of English 4/25 |

- **52 dinleme parçasının MP3'ü yok** (yalnızca 8 gerçek ses; `track_1-8` bu 8'in kopyası, silinebilir). `generate_audio.py` ile üretilebilir.
- 600 kelimenin 57'si tekrar (aslında 543 farklı kelime); A1'de B1–B2 kelimeler var.
- 24 farklı kategori etiketi → 6–7 standart etikete indirilmeli.
- Yazma rehberlerinin hiçbiri üniversiteye bağlı değil.
- Tahmini ihtiyaç: ~250 yeni soru + 52 ses + 8 uzun ders dinlemesi.

---

## 5. İŞ MODELİ
- **50 TL çok düşük olabilir** (Temadil: aylık 10.500 TL) — değer algısını zayıflatır. Öneri: "ömür boyu" yerine **bir sınav dönemi** erişimi (Eylül / Ocak / Haziran'a kadar).
- **AI essay/speaking değerlendirmesi ayrı kredi** olarak satılabilir (maliyeti var, rakipler pahalıya satıyor).
- **Takvim**: muafiyet sınavlarının zirvesi **Eylül başı** (ODTÜ 8–9, BUEPT 7–8, İTÜ 9–11 Eylül 2026); ikinci dalga Aralık–Ocak, üçüncü Haziran. Pazarlama Temmuz–Ağustos'ta YKS yerleşmesiyle başlamalı.
- Kendi üniversitesi ücretsiz kalsın — kullanıcı kazanmanın ana yolu.

---

## Önerilen sıra
1. **Bölüm 1 (Hemen)** — ~1 gün, hepsi küçük. Şu an bozuk olanları düzeltir.
2. **#11 Kullanıcı bazlı veri** — diğer her şeyin ön koşulu.
3. Paralelde 👤 vergi kaydı + PayTR başvurusu (takvimi en uzun iş).
4. **#17 SRS + #20 seviye tespiti + #4/#24** — öğrenciyi geri getiren çekirdek.
5. Bölüm 2'nin kalanı → canlıya çıkış (Eylül 2027 dönemine yetişmek için en geç Temmuz).
6. **#18 note-taking, #19 AI essay, #21 tam deneme** — farklılaştıran özellikler.
7. İçerik genişletme sürekli, paralel.

**Doğrulanmamış (ajanların işaretlediği):** PayTR'nin kesin belge listesi ve kendi fatura çözümü, Türkiye için Play ödeme kuralı, ETBİS/VERBİS eşikleri, KVKK yurt dışı aktarım ayrıntıları, bazı rakip fiyatları, Bilkent/Hacettepe 2026–27 sınav tarihleri.
