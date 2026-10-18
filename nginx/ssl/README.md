# PrepMaster SSL / TLS Sertifika Yönetimi

Bu dizin, Nginx ters proxy için SSL/TLS sertifikalarını barındırır.

## Dosyalar
- `prepmaster.crt`: Sunucu SSL/TLS Sertifikası (PEM formatında)
- `prepmaster.key`: Sunucu Özel Anahtarı (RSA/ECDSA Private Key)
- `generate_dev_certs.py`: Geliştirme/test ortamları için 365 günlük SAN destekli self-signed sertifika oluşturucu.

## Canlı Ortamda Cloudflare Origin CA Sertifikası Kurulumu
1. Cloudflare Dashboard'a giriş yapın: **SSL/TLS > Origin Server**.
2. **Create Certificate** butonuna tıklayın.
3. Hostname listesine domainlerinizi ekleyin (örn. `prepmaster.edu.tr`, `*.prepmaster.edu.tr`).
4. Sertifika geçerlilik süresini seçin (Örn: 15 yıl).
5. Cloudflare tarafından üretilen **Origin Certificate** içeriğini kopyalayıp `prepmaster.crt` dosyasına yapıştırın.
6. **Private Key** içeriğini kopyalayıp `prepmaster.key` dosyasına yapıştırın.
7. Cloudflare Dashboard'da **SSL/TLS Encryption Mode** ayarını **Full (Strict)** olarak işaretleyin.
8. Nginx konteynerini yeniden yükleyin:
   ```bash
   docker compose exec nginx nginx -s reload
   ```
