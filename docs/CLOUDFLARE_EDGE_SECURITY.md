# PrepMaster Üretim Güvenliği & Cloudflare Edge WAF Dağıtım Rehberi

Bu belge, **PrepMaster (Üniversite Hazırlık & Muafiyet Platformu)** sisteminin dış dünyaya (Public Internet) açılması sırasında uygulanması gereken **Edge Güvenliği**, **Cloudflare WAF**, **Nginx Ters Proxy**, **Docker İzolasyonu** ve **DDoS Koruması** mimarisini ve adım adım yapılandırma yönergelerini içerir.

---

## 1. Mimari Genel Bakış

PrepMaster, çok katmanlı bir savunma derinliği (Defense-in-Depth) stratejisi kullanır:

```
[ İnternet / İstemciler ]
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Cloudflare Anycast Edge Ağı                              │
│    - DDoS Koruması (Layer 3/4 & Layer 7)                   │
│    - DNS Proxy (Origin IP Gizleme - Orange Cloud)           │
│    - Bot Fight Mode & Under Attack Mode                    │
│    - Edge Cache (Static Audio / CSS / JS)                   │
│    - WAF & Rate Limiting (OTP & Auth Brute Force Kalkanı)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / TLS v1.3 (Full Strict)
                               │ Header: CF-Connecting-IP
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Nginx Ters Proxy (Frontend Network - Port 443/80)         │
│    - Cloudflare Origin CA Doğrulaması                       │
│    - Nginx Rate Limiting (15 req/s genel, 3 req/s auth)     │
│    - Buffer Overflow & Slowloris Koruması                   │
│    - Statik Dosya & MP3 Doğrudan Önbellek Sunumu            │
│    - Güvenlik Başlıkları (HSTS, CSP, X-Frame, X-XSS)        │
│    - Fail2ban Log Entegrasyonu                              │
└──────────────────────────────┬──────────────────────────────┘
                               │ Yalnızca Dahili Ağ (backend_net)
                               │ Port: 8050 (Dışarıya Kapalı)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PrepMaster Backend Konteyneri (Python 3.12 / FastAPI)    │
│    - Root Yetkisi Olmayan Kullanıcı (prepmaster)            │
│    - Read-Only Bağımlılıklar                                │
│    - SQLite Kalıcı Veri Birimi (prepmaster_data)             │
│    - Kaynak Limitleri (1.5 CPU, 1GB RAM)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Cloudflare DNS & Origin Cloaking (IP Gizleme)

DDoS saldırganlarının doğrudan sunucunuza saldırmasını engellemek için sunucu gerçek IP adresinin internetten gizlenmesi şarttır.

### 2.1. DNS Kayıtları (Orange Cloud Aktif)
Cloudflare Dashboard > **DNS > Records**:
- **A Kaydı:** `prepmaster.edu.tr` -> `Sunucu_Public_IP` -> **Proxy status: Proxied (Turuncu Bulut)**
- **CNAME Kaydı:** `www` -> `prepmaster.edu.tr` -> **Proxy status: Proxied (Turuncu Bulut)**

> [!IMPORTANT]
> - Sunucuda posta (MX) servisi bulunuyorsa, MX kaydını kesinlikle doğrudan sunucu IP'sine yönlendirmeyin (Google Workspace, Microsoft 365 veya harici bir SMTP geçidi kullanın).
> - Doğrudan sunucu IP'sine giden kayıtlar Shodan veya Censys tarafından taranarak Cloudflare'in atlatılmasına (Bypass) yol açabilir.

### 2.2. DNSSEC (DNS Security Extensions)
1. Cloudflare Dashboard > **DNS > Settings** yolunu izleyin.
2. **Enable DNSSEC** seçeneğini etkinleştirin.
3. Üretilen `DS` kaydı bilgilerini alan adı kayıt firmanızın (Domain Registrar) yönetim paneline ekleyin. Böylece DNS önbellek zehirleme (DNS Spoofing) saldırıları engellenir.

---

## 3. SSL / TLS Full (Strict) ve Origin CA Yapılandırması

Trafik akışının istemciden Cloudflare'e ve Cloudflare'den Nginx sunucunuza kadar kesintisiz şifrelenmesi için **Full (Strict)** modu zorunludur.

### 3.1. Cloudflare Origin CA Sertifikası Oluşturma
1. Cloudflare Dashboard > **SSL/TLS > Origin Server** menüsüne gidin.
2. **Create Certificate** butonuna tıklayın.
3. **Key type:** `RSA (2048)` veya `ECDSA (P-256)`.
4. **Hostnames:** `prepmaster.edu.tr`, `*.prepmaster.edu.tr`, `prepmaster.local`.
5. **Certificate Validity:** `15 years` seçin.
6. **Create** butonuna basın:
   - **Origin Certificate** içeriğini kopyalayın ve sunucudaki `nginx/ssl/prepmaster.crt` dosyasına kaydedin.
   - **Private Key** içeriğini kopyalayın ve sunucudaki `nginx/ssl/prepmaster.key` dosyasına kaydedin (İzinleri `chmod 600` yapın).

### 3.2. Cloudflare SSL Modunu Ayarlama
1. Cloudflare Dashboard > **SSL/TLS > Overview** menüsüne gidin.
2. SSL/TLS şifreleme modunu **Full (Strict)** olarak seçin.
3. **Edge Certificates** sekmesinde:
   - **Always Use HTTPS:** `On`
   - **HTTP Strict Transport Security (HSTS):** `Enable` (Max-Age: 6 months / 1 year, Subdomains: Yes, Preload: Yes)
   - **Minimum TLS Version:** `TLS 1.2`
   - **Opportunistic Encryption:** `On`
   - **TLS 1.3:** `On`

### 3.3. Authenticated Origin Pulls (AOP) - Opsiyonel İleri Seviye Sıkılaştırma
Sunucunuzun yalnızca Cloudflare'den gelen istekleri kabul etmesini, doğrudan IP'ye gelen korsan istekleri TLS seviyesinde reddetmesini sağlamak için:
1. Cloudflare CA sertifikasını indirin:
   ```bash
   curl -s https://developers.cloudflare.com/ssl/static/authenticated_origin_pull_ca.pem -o nginx/ssl/cloudflare_origin_pull.pem
   ```
2. `nginx/conf.d/default.conf` içerisine ekleyin:
   ```nginx
   ssl_client_certificate /etc/nginx/ssl/cloudflare_origin_pull.pem;
   ssl_verify_client on;
   ```
3. Cloudflare Dashboard > **SSL/TLS > Origin Server > Authenticated Origin Pulls** seçeneğini `On` yapın.

---

## 4. Bot Koruması & "Under Attack Mode" Yönetimi

### 4.1. Bot Fight Mode
1. Cloudflare Dashboard > **Security > Bots** bölümüne gidin.
2. **Bot Fight Mode** anahtarını `On` konumuna getirin.
3. Otomatik kötü amaçlı botlar, web kazıyıcılar ve bilinen saldırı araçları CAPTCHA / JavaScript zorluğuna takılır.

### 4.2. "Under Attack Mode" (Saldırı Anında Tek Tıkla Devreye Alma)
Platform aktif bir HTTP Flood / L7 DDoS saldırısı altındaysa:
1. Cloudflare Dashboard ana sayfasında veya **Security > Settings** bölümünde **Under Attack Mode**'u `I'm Under Attack!` olarak etkinleştirin.
2. **Etki:** Her yeni ziyaretçiye 5 saniyelik şeffaf JavaScript / Managed Challenge doğrulaması uygular. Otomatik botlar betiği çalıştıramadığı için origin sunucuya tek bir istek dahi ulaşamaz.
3. **Cloudflare CLI / API İle Acil Durum Aktivasyonu:**
   ```bash
   curl -X PATCH "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/settings/security_level" \
        -H "Authorization: Bearer <API_TOKEN>" \
        -H "Content-Type: application/json" \
        --data '{"value":"under_attack"}'
   ```
4. Saldırı sona erdiğinde seviyeyi tekrar **High** veya **Medium** seviyesine indirin.

---

## 5. Cloudflare WAF & IP Throttling Kuralları

Cloudflare Dashboard > **Security > WAF** altında aşağıdaki kuralları tanımlayın:

### Kural 1: Öğrenci Doğrulama & OTP Brute-Force Kalkanı (Rate Limiting)
- **Kural Adı:** `PrepMaster_OTP_Rate_Limit`
- **Trafik Eşleşmesi (When incoming requests match):**
  - `(http.request.uri.path contains "/api/student/request-otp" or http.request.uri.path contains "/api/student/verify-otp")`
- **Rate Limit Kriteri:**
  - İstek sayısı: `5 requests` per `1 minute` per `IP`
- **Eylem (Action):** `Managed Challenge` (veya `Block` for 10 minutes)

### Kural 2: Bilinen Güvenlik Tarayıcılarını ve Exploit Araçlarını Engelleme
- **Kural Adı:** `Block_Exploit_Scanners`
- **İfade:**
  ```text
  (http.user_agent contains "sqlmap" or 
   http.user_agent contains "nikto" or 
   http.user_agent contains "masscan" or 
   http.user_agent contains "nmap" or 
   http.user_agent contains "acunetix" or 
   http.user_agent contains "wpscan" or
   http.user_agent contains "gobuster")
  ```
- **Eylem (Action):** `Block`

### Kural 3: Hassas Dosya Problarını Edge Seviyesinde Engelleme
- **Kural Adı:** `Block_Sensitive_Files`
- **İfade:**
  ```text
  (http.request.uri.path contains "/.env" or 
   http.request.uri.path contains "/.git" or 
   http.request.uri.path contains "/wp-login" or 
   http.request.uri.path contains "/phpmyadmin")
  ```
- **Eylem (Action):** `Block`

### Kural 4: Coğrafi Risk Filtresi (Geo-Fencing)
PrepMaster Türkiye üniversiteleri (İTÜ, Boğaziçi, ODTÜ, Bilkent vb.) hazırlık öğrencilerine odaklandığından:
- **Kural Adı:** `Challenge_Non_Domestic_Traffic`
- **İfade:** `(ip.geoip.country ne "TR" and not cf.client.bot)`
- **Eylem (Action):** `Managed Challenge` (Turnstile)
- *Not: Yurt dışındaki Türk öğrencilerin ve akademisyenlerin erişimini kesmez, sadece bot olmadıklarını şeffafça doğrular.*

---

## 6. DDoS Koruması ve Edge Önbellekleme Stratejisi

PrepMaster üzerinde dinleme sınavları için yüksek kaliteli akademik ses dosyaları (`track_1.mp3`..`track_8.mp3`, `lis_buept_*.mp3`, vb.) bulunmaktadır. Bu dosyaların doğrudan Cloudflare Edge CDN'den servis edilmesi origin sunucu yükünü %95 azaltır.

### Cache Rules (Önbellekleme Kuralları)
Cloudflare Dashboard > **Caching > Cache Rules**:

1. **Ses Dosyaları & Statik Varlıklar Kuralı:**
   - **Field:** `URI Path` -> `starts_with` -> `/static/`
   - **Cache Eligibility:** `Eligible for cache`
   - **Edge TTL:** `Override origin` -> `30 days` (Ses dosyaları için `90 days`)
   - **Browser TTL:** `Respect origin`
   - **Serve Stale Content while updating:** `Enabled`

2. **API İstekleri Kuralı (Bypass):**
   - **Field:** `URI Path` -> `starts_with` -> `/api/`
   - **Cache Eligibility:** `Bypass cache`

---

## 7. Origin Nginx & Gerçek Ziyaretçi IP'sinin Alınması (Real-IP)

Cloudflare arkasındaki ters proxy'lerde en sık yapılan hata, tüm ziyaretçilerin IP'sinin Cloudflare Anycast IP'si olarak görünmesidir. Bu durum Fail2ban'ın veya Nginx rate limit'in yanlışlıkla Cloudflare IP'lerini engellemesine yol açabilir.

PrepMaster yapılandırmasında bu durum şu şekilde çözülmüştür:
1. `nginx/cloudflare_ips.conf` dosyasında resmi Cloudflare IPv4 & IPv6 CIDR blokları tanımlanmıştır.
2. `real_ip_header CF-Connecting-IP;` ve `real_ip_recursive on;` direktifleri ile Nginx, gerçek istemci IP adresini `$remote_addr` değişkenine yazar.
3. Nginx logları ve Fail2ban doğrudan **gerçek saldırgan IP'sini** tespit eder ve engeller.

---

## 8. Üretim Dağıtım Adımları (Adım Adım)

### Adım 1: Depo Klonlama ve Çalışma Dizinine Geçiş
```bash
git clone https://github.com/prepmaster/prepmaster.git C:\Projeler\PrepMaster
cd C:\Projeler\PrepMaster
```

### Adım 2: SSL Sertifikalarının Yerleştirilmesi
Test/Geliştirme için:
```bash
python nginx/ssl/generate_dev_certs.py
```
Canlı Ortam için:
- Cloudflare Origin CA sertifikanızı `nginx/ssl/prepmaster.crt` ve anahtarını `nginx/ssl/prepmaster.key` olarak yerleştirin.

### Adım 3: Ortam Değişkenlerinin Yapılandırılması
```bash
cp .env.example .env
# .env dosyası içindeki SECRET_KEY'i güçlü bir rastgele anahtar ile güncelleyin
```

### Adım 4: Docker Stack Başlatma
```bash
docker compose up -d --build
```

### Adım 5: Konteyner ve Ağ İzolasyonunu Doğrulama
```bash
# Konteyner durumlarını kontrol et
docker compose ps

# Nginx sözdizimini doğrula
docker compose exec nginx nginx -t

# Fail2ban durumunu kontrol et
docker compose exec fail2ban fail2ban-client status
```

---

## 9. Acil Durum & İzleme İpuçları

| Senaryo | Yapılması Gereken İşlem |
|---|---|
| **Ani DDoS Saldırısı** | Cloudflare Dashboard üzerinden **Under Attack Mode**'u açın. |
| **Öğrenci OTP Spam Saldırısı** | Cloudflare WAF üzerinde `/api/student/*` kuralının rate limitini 1 dakikada 2 isteğe düşürün. |
| **Yanlışlıkla Banlanan Bir IP'yi Açma** | `docker compose exec fail2ban fail2ban-client set nginx-auth unbanip <IP_ADRESI>` |
| **Nginx Loglarını Canlı İzleme** | `docker compose logs -f nginx` |
| **Sistem Bütünlük Doğrulaması** | `python deploy_check.py` |
