# PrepMaster Fail2ban DDoS & Abuse Mitigation Template

Bu şablon, Nginx ters proxy loglarını izleyerek şüpheli veya kural dışı IP adreslerini otomatik olarak tespit eder ve güvenlik duvarı (iptables / nftables) seviyesinde engeller.

## Koruma Katmanları (Jails)
1. **`nginx-req-limit`**: Nginx rate limit (HTTP 429) sınırını 60 saniyede 8 kereden fazla aşan IP adreslerini 1 saat süreyle engeller.
2. **`nginx-auth`**: `/api/student/verify-otp` veya `/api/auth/` uç noktalarına 5 dakika içinde 5 hatalı deneme yapan IP adreslerini 2 saat süreyle engeller.
3. **`nginx-badbots`**: `.env`, `.git` taraması yapan veya `sqlmap`, `nikto` vb. tarayıcı imzası taşıyan istekleri 24 saat süreyle banlar.

## Çalıştırma Modelleri

### Seçenek A: Docker Compose İle Çalıştırma (Önerilen)
`docker-compose.yml` içerisindeki `fail2ban` servisini başlatın:
```bash
docker compose up -d fail2ban
```

Aktif ban listesini ve durumunu kontrol etmek için:
```bash
docker compose exec fail2ban fail2ban-client status
docker compose exec fail2ban fail2ban-client status nginx-req-limit
docker compose exec fail2ban fail2ban-client status nginx-auth
```

Bir IP adresinin engelini manuel kaldırmak için (Unban):
```bash
docker compose exec fail2ban fail2ban-client set nginx-auth unbanip <IP_ADRESI>
```

### Seçenek B: Host Seviyesinde Fail2ban
Eğer sunucu üzerinde halihazırda Fail2ban kurulu ise:
1. `filter.d/*` dosyalarını `/etc/fail2ban/filter.d/` dizinine kopyalayın.
2. `jail.d/prepmaster-jail.local` dosyasını `/etc/fail2ban/jail.d/` dizinine kopyalayın (logpath Docker volume yoluna göre ayarlanır).
3. `sudo systemctl restart fail2ban` komutunu çalıştırın.
