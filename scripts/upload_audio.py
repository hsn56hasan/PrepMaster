"""Üretilmiş dinleme MP3'lerini S3 uyumlu bir kovaya (Cloudflare R2) yükler.

Kullanım (proje kökünden):
    python -m pip install -r scripts/requirements-upload.txt     # bir kez
    python scripts/upload_audio.py --kuru                        # ne yükleneceğini yaz, yükleme
    python scripts/upload_audio.py                               # yükle

Kaynak klasör varsayılanı `.audio-build` (backend/generate_audio.py --cikti ile oraya üretir).

Ayarlar .env dosyasından okunur (backend/env_loader.py ile; ek paket gerekmez):
    S3_ENDPOINT_URL=https://<ACCOUNT_ID>.r2.cloudflarestorage.com
    S3_BUCKET=prepkampus-audio
    S3_ACCESS_KEY_ID=...
    S3_SECRET_ACCESS_KEY=...
    S3_REGION=auto
    S3_PREFIX=listening/

Betik idempotenttir: ikinci çalıştırmada her şey "atlandı" demelidir. Kovadaki nesne
listesi tek seferde çekilir ve BOYUT karşılaştırılır; dosya adları içerik özetli olduğu
için (ad değişmeden içerik değişemez) boyut eşitliği yeterlidir.

Her nesneye Cache-Control "public, max-age=31536000, immutable" yazılır. Bu baskı İLK
yüklemede doğru verilmelidir: sonradan düzeltmek nesneyi yeniden yüklemeyi gerektirir.

Anahtarlar hiçbir koşulda ekrana veya kayda basılmaz.
"""

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

try:
    from backend.env_loader import load_env  # noqa: E402
    load_env()
except Exception:
    pass  # .env yoksa ortam değişkenleri doğrudan kullanılır

CONTENT_TYPE = "audio/mpeg"
CACHE_CONTROL = "public, max-age=31536000, immutable"


def gerekli(ad: str) -> str:
    deger = os.getenv(ad, "").strip()
    if not deger:
        print(f"HATA: {ad} tanımlı değil. .env dosyasına ekleyin (değerleri sohbete yazmayın).",
              file=sys.stderr)
        raise SystemExit(1)
    return deger


def istemci_kur(isci: int):
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        print("HATA: boto3 kurulu değil.\n"
              "  python -m pip install -r scripts/requirements-upload.txt", file=sys.stderr)
        raise SystemExit(1)

    return boto3.session.Session().client(
        "s3",
        endpoint_url=gerekli("S3_ENDPOINT_URL"),
        region_name=os.getenv("S3_REGION", "auto"),
        aws_access_key_id=gerekli("S3_ACCESS_KEY_ID"),
        aws_secret_access_key=gerekli("S3_SECRET_ACCESS_KEY"),
        config=Config(
            retries={"total_max_attempts": 6, "mode": "standard"},
            # boto3 varsayılanı 10'dur; işçi sayısını geçmezse iş parçacıkları kuyruğa girer.
            max_pool_connections=isci + 4,
            connect_timeout=15,
            read_timeout=120,
        ),
    )


def kovadakiler(s3, bucket: str, onek: str) -> dict:
    """Önek altındaki nesnelerin {anahtar: boyut} eşlemesi (tek listeleme, 656 HEAD yerine)."""
    mevcut = {}
    sayfalayici = s3.get_paginator("list_objects_v2")
    for sayfa in sayfalayici.paginate(Bucket=bucket, Prefix=onek):
        for nesne in sayfa.get("Contents", []):
            mevcut[nesne["Key"]] = nesne["Size"]
    return mevcut


def yukle_bir(s3, bucket: str, yol: Path, anahtar: str):
    s3.upload_file(
        str(yol),
        bucket,
        anahtar,
        ExtraArgs={"ContentType": CONTENT_TYPE, "CacheControl": CACHE_CONTROL},
    )
    return anahtar


def main():
    p = argparse.ArgumentParser(description="Dinleme MP3'lerini S3 uyumlu kovaya yükler.")
    p.add_argument("--kaynak", default=str(ROOT / ".audio-build"), help="MP3 klasörü")
    p.add_argument("--onek", default=None, help="Kova içindeki önek (varsayılan S3_PREFIX ya da listening/)")
    p.add_argument("--isci", type=int, default=8, help="Eş zamanlı yükleme sayısı")
    p.add_argument("--kuru", action="store_true", help="Hiçbir şey yükleme, planı yaz")
    args = p.parse_args()

    kaynak = Path(args.kaynak).resolve()
    if not kaynak.is_dir():
        print(f"HATA: kaynak klasör yok: {kaynak}", file=sys.stderr)
        raise SystemExit(1)

    dosyalar = sorted(kaynak.glob("*.mp3"))
    if not dosyalar:
        print(f"HATA: {kaynak} içinde .mp3 yok. Önce üretin:\n"
              "  python backend/generate_audio.py --tumu --cikti .audio-build --url-onek yok",
              file=sys.stderr)
        raise SystemExit(1)

    onek = (args.onek or os.getenv("S3_PREFIX") or "listening/").strip()
    if onek and not onek.endswith("/"):
        onek += "/"

    toplam_bayt = sum(f.stat().st_size for f in dosyalar)
    print(f"Kaynak    : {kaynak}")
    print(f"Dosya     : {len(dosyalar)} ({toplam_bayt / 1024 / 1024:.1f} MB)")
    print(f"Önek      : {onek}")

    bucket = gerekli("S3_BUCKET")
    s3 = istemci_kur(args.isci)

    print("Kovadaki nesneler listeleniyor...")
    mevcut = kovadakiler(s3, bucket, onek)
    print(f"Kovada hâlihazırda {len(mevcut)} nesne var.")

    yapilacak, atlanan = [], 0
    for f in dosyalar:
        anahtar = onek + f.name
        if mevcut.get(anahtar) == f.stat().st_size:
            atlanan += 1
            continue
        yapilacak.append((f, anahtar))

    print(f"Yüklenecek: {len(yapilacak)} | Atlanacak (zaten var): {atlanan}")

    if args.kuru:
        for f, anahtar in yapilacak[:10]:
            print(f"  - {f.name} -> {anahtar} ({f.stat().st_size // 1024} KB)")
        if len(yapilacak) > 10:
            print(f"  ... ve {len(yapilacak) - 10} dosya daha")
        print("(kuru çalışma: hiçbir şey yüklenmedi)")
        return 0

    if not yapilacak:
        print("Yapılacak bir şey yok.")
        return 0

    basarili, hatalar = 0, []
    with ThreadPoolExecutor(max_workers=args.isci) as havuz:
        isler = {havuz.submit(yukle_bir, s3, bucket, f, a): (f, a) for f, a in yapilacak}
        for i, is_ in enumerate(as_completed(isler), 1):
            f, anahtar = isler[is_]
            try:
                is_.result()
                basarili += 1
                if basarili % 25 == 0 or basarili == len(yapilacak):
                    print(f"  {basarili}/{len(yapilacak)} yüklendi")
            except Exception as e:  # noqa: BLE001 - hangi dosyanın neden düştüğünü görmek istiyoruz
                hatalar.append((f.name, type(e).__name__ + ": " + str(e)[:200]))

    print("\n--- ÖZET ---")
    print(f"Yüklendi : {basarili}")
    print(f"Atlandı  : {atlanan}")
    print(f"Hata     : {len(hatalar)}")
    for ad, hata in hatalar[:20]:
        print(f"    {ad}: {hata}")
    if len(hatalar) > 20:
        print(f"    ... ve {len(hatalar) - 20} hata daha")

    if not hatalar:
        print("\nDoğrulama için (PowerShell):")
        ornek = dosyalar[0].name
        taban = os.getenv("AUDIO_BASE_URL", "https://ses.prepkampus.com/listening/")
        print(f"  curl.exe -I {taban.rstrip('/')}/{ornek}")
        print("  -> content-type: audio/mpeg, cache-control: ...immutable, cf-cache-status")

    return 1 if hatalar else 0


if __name__ == "__main__":
    raise SystemExit(main())
