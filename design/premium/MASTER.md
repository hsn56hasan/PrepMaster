# PrepKampüs — Premium Tasarım Yönü: "Orman & Kâğıt"

> Bu klasör bir **tasarım önerisidir**; canlı siteye dokunmaz. Onaylanırsa `tokens.css` ve bileşen kuralları
> `static/css/style.css` ve `static/index.html` içine aşamalı olarak taşınır.

Dosyalar:
- `tokens.css`: 3 katmanlı tokenlar (primitive → semantic → component), aydınlık ve karanlık mod.
- `landing-page.html`: premium ana sayfa prototipi (gerçek içerik ve sayılarla).
- `banners.html`: 3 sanat yönünde reklam görselleri (kare, dikey, yatay).

---

## 1. Fikir: neden bu yön?

PrepKampüs'ün rakipleri iki uçta duruyor:
- Pahalı kurslar: kurumsal, mavi-kırmızı ve kalabalık.
- Ücretsiz içerik siteleri: dağınık ve reklamlı.

Premium his pahalı görünmekten gelmiyor. **Sakinlik, düzen ve özenden** geliyor.

Yön: **akademik bir dergi ile iyi tasarlanmış bir uygulamanın kesişimi.**
- **Kâğıt:** Sıcak, krem tonlu zemin. Saf beyaz ve soğuk gri yok; sayfa ucuz SaaS gibi görünmez.
- **Orman:** Marka zümrüdü, koyu bir "mürekkep yeşili" (`#062A21`) ile derinleşir. Koyu bölümler siyah değil, orman yeşilidir.
- **Serif başlıklar:** Fraunces. Akademik güven ile modern sıcaklığı birleştirir; Türkçe karakterleri tam destekler. Gövde metni mevcut Plus Jakarta Sans'ta kalır, yani site ile süreklilik korunur.
- **Pirinç vurgu:** Sadece "değer" anlarında kullanılır: yıldız, başarı, premium rozet. Her yerde altın kullanmak ucuzlatır.

Duygu hedefi: *"Bu ekip işini ciddiye alıyor ve benim okulumu tanıyor."*

## 2. Tasarım kadranları

| Kadran | Değer | Anlamı |
|---|---|---|
| Variance | **6/10** | Dengeli modern düzen. Hero asimetrik (metin + ürün önizlemesi), özellikler bento ızgarada, geri kalanı sakin ve simetrik. |
| Motion | **4/10** | Kaydırınca yumuşak beliriş, kademeli kart girişleri, düğmelerde 160–260 ms geçiş. Parallax ve GSAP koreografisi yok; "hareketi azalt" tercihinde hepsi kapanır. |
| Density | **3/10** | Ferah. Bölüm aralığı 72–128 px, satır uzunluğu en fazla ~68 karakter. |

Stil: **Editorial / Magazine + Soft UI.** Glassmorphism ve neon gradyan kullanılmaz.

## 3. Renk

| Rol | Aydınlık | Karanlık | Kullanım |
|---|---|---|---|
| Arka plan | `#FBFAF6` kâğıt | `#06110D` gece | Sayfa zemini |
| Alternatif zemin | `#F5F3EC` | `#0A1A15` | Bant bölümler |
| Yüzey | `#FFFFFF` | `#0A1A15` | Kartlar |
| Ters yüzey | `#062A21` orman mürekkebi | `#F4F1E8` | Hero altı, final CTA |
| Metin | `#0E1A16` | `#EEF3EF` | Gövde (kontrast 17:1) |
| İkincil metin | `#55645D` | `#93A39B` | Açıklamalar (aydınlıkta 5.9:1) |
| Birincil | `#059669` | `#34B88A` | CTA, bağlantı, aktif durum |
| Adaçayı | `#6FA287` | — | İkincil grafik, etiket |
| Pirinç | `#B8893B` | `#E3C489` | Yıldız, "premium", başarı |
| Çizgi | `#ECE9DF` | `#1A372D` | 1 px ayırıcılar |

**Kural:** Üst çubuk dışında, görünür alanda en fazla **bir** dolu zümrüt CTA olur. Diğer düğmeler hayalet (çerçeveli) veya metin bağlantısıdır.

## 4. Tipografi

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..800;1,9..144,400..700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
```

| Öğe | Font | Boyut | Ağırlık | Not |
|---|---|---|---|---|
| Display (hero) | Fraunces | 44–88 px (akışkan) | 500 | `letter-spacing: -0.02em`. Vurgulanan sözcük *italik* ve zümrüt renkte. |
| H2 | Fraunces | 30–44 px | 500 | `text-wrap: balance` |
| H3 | Plus Jakarta Sans | 18–20 px | 700 | Kart başlıkları |
| Gövde | Plus Jakarta Sans | 16–18 px | 400–500 | `line-height: 1.6` |
| Üst etiket | Plus Jakarta Sans | 12 px | 700 | BÜYÜK HARF, `letter-spacing: .16em`, numaralı ("01 — Yöntem") |
| Sayılar | Plus Jakarta Sans | — | 700 | `font-variant-numeric: tabular-nums` |

Türkçe kontrolü: Fraunces ve Jakarta'da ğ, ş, ı, İ, ç, ö, ü doğru çiziliyor. Büyük harfe çevirmede `lang="tr"` zorunlu (i → İ).

## 5. Sayfa mimarisi (landing pattern: Hero + Ürün önizlemesi + Kanıt + Bento + Fiyat + SSS)

1. **Üst çubuk:** Logo, 4 bağlantı ve "Giriş yap" (hayalet) ile "Ücretsiz başla" (dolu). Kaydırınca kâğıt rengi buzlu zemine geçer.
2. **Hero:**
   - Sol: üst etiket, serif başlık ("Muafiyet sınavına *okulunun formatında* hazırlan."), tek cümlelik açıklama, iki CTA ve güven satırı ("Kredi kartı gerekmez · Öğrenci belgesiyle kendi okulun ücretsiz").
   - Sağ: elde çizilmiş **ürün önizlemesi**. Ekran görüntüsü değil, HTML'den kurulmuş bir pencere: Konu Yolu düğümleri, günlük görev kartı, kur ilerlemesi.
3. **Okul şeridi:** 26 okulun kısa adları, yavaş akan bir şeritte. Logo kullanılmaz, sadece isim. Altında küçük not: *"Bağımsız bir hazırlık platformudur; üniversitelerle resmi bağı yoktur."*
4. **Rakamlar:** 4 sütunlu ince çizgili "defter" düzeni: 26 okul, 11.525 soru, 2.078 kelime, 120 ders.
5. **01 Yöntem:** Seviye tespiti → Günlük görev → Konu Yolu → Okul denemesi → Hata Kasası. Yatay, numaralı 5 adım.
6. **02 Özellikler (bento):** Büyük kart Konu Yolu, orta kart okul formatında deneme, küçük kartlar dinleme/konuşma/yazma, Hata Kasası, mobil uygulama.
7. **03 Okulun:** Okul seçici. Bir okul seçince sınavın adı, süresi, soru sayısı ve geçme puanı gösterilir (`universities.json` verisi). "Okulunu tanıyoruz" vaadinin kanıtı burası.
8. **04 Fiyat:** İki kart:
   - "Kendi okulun: öğrenci belgesiyle ücretsiz"
   - "Başka bir okul: okul başına 50 TL, tek sefer"
   - Ayrıca her şeyin ücretsiz olduğunu gösteren genel havuz satırı.
9. **SSS:** 6 soru, açılır-kapanır.
10. **Final CTA:** Orman mürekkebi zemin, serif başlık, tek düğme.
11. **Alt bilgi:** KVKK, iletişim, sınav rehberleri bağlantıları.

## 6. Bileşen durum matrisi

| Bileşen | Varsayılan | Hover | Basılı | Focus-visible | Devre dışı | Yükleniyor |
|---|---|---|---|---|---|---|
| Birincil düğme | Zümrüt, beyaz yazı, hap | Bir ton koyu, 2 px yukarı, yumuşak zümrüt gölge | 1 px aşağı, gölge yok | 4 px halka `--color-ring` | %45 opaklık, imleç yok | Döner ikon + "Hazırlanıyor…" (genişlik sabit) |
| Hayalet düğme | Şeffaf, 1 px güçlü çizgi | Zemin `--color-surface` | 1 px aşağı | Halka | %45 | — |
| Kart | Beyaz, 1 px çizgi, orta gölge | 3 px yukarı, büyük gölge (yalnız tıklanabilir kartlarda) | — | Halka (tıklanabilirse) | — | İskelet çizgileri |
| Çip | Zümrüt-50 zemin, koyu zümrüt yazı | — | — | — | Gri | — |
| Girdi | Beyaz, güçlü çizgi, 14 px köşe | Çizgi koyulaşır | — | Zümrüt çizgi + halka | Gri zemin | — |

Dokunma alanı en az 44×44 px. Bütün geçişler `transform` ve `opacity` ile yapılır; layout kaydırılmaz.

## 7. Hareket

- Bölüm girişleri: `opacity 0 → 1`, `translateY 16px → 0`, 600 ms `--ease-out`, kart başına 60 ms gecikme. IntersectionObserver ile tetiklenir.
- Okul şeridi: 60 saniyelik doğrusal kayma. Hover'da durur; "hareketi azalt"ta statik ızgaraya döner.
- Hero ürün önizlemesi: "BAŞLA" balonunda 1.8 s'lik hafif yukarı-aşağı hareket.
- Yasak: sayfa açılışında 1 s'den uzun animasyon, kaydırmaya bağlı parallax, otomatik oynayan video.

## 8. Yasaklar (anti-pattern kalkanı)

- Emoji ikon kullanılmaz. Yalnızca Lucide (1.75 px çizgi kalınlığı).
- Mor, pembe ya da neon "AI" gradyanları kullanılmaz.
- **Uydurma kullanıcı yorumu, sahte başarı yüzdesi veya "X öğrenci kazandı" gibi doğrulanmamış iddia kullanılmaz.** Kanıt olarak yalnızca gerçek içerik sayıları ve okul formatı bilgisi kullanılır.
- "Yapay zekâ ile puanlama" denmez. Puanlama bir simülasyondur; "otomatik geri bildirim" ifadesi kullanılır.
- Üniversite logoları ve resmi renkleri kullanılmaz; sadece kısa adlar ve bağımsızlık notu.
- "%100 garanti", "kesin muafiyet" gibi vaatler verilmez.
- Saf siyah (`#000`) ve soğuk gri zemin kullanılmaz.
- Üst çubuk dışında, görünür alanda birden fazla dolu CTA olmaz.

## 9. Mevcut siteye geçiş planı (onaylanırsa)

1. **Tokenlar:**
   - `tokens.css` dosyasını `static/css/` altına ekle.
   - `theme_palette.js` içindeki zümrüt ölçeği aynı kalır; arka plan kâğıt tonuna çekilir.
2. **Tipografi:** Fraunces'i yalnızca başlıklara ekle (`h1`, `h2`, `.landing-title`). Gövde metnine dokunma.
3. **Giriş sayfası:** `#auth-modal` landing düzenini bu prototipin bölüm sırasına göre genişlet. Kayıt kartı ve ID'ler korunur.
4. **Uygulama içi:**
   - Panel ve Konu Yolu kartlarına kâğıt zemin, 1 px çizgi ve orta gölge.
   - Hero bantlarında orman mürekkebi.
5. **Mobil (Flutter):** `AppTheme` yüzeylerini kâğıt tonlarına çek ve başlıklar için Fraunces ekle (`google_fonts` paketi gerekmez; font dosyası `assets/fonts` altına konur).
6. Her adımda: taşma taraması, 375/768/1024/1440 genişlik kontrolü, aydınlık ve karanlık mod.
