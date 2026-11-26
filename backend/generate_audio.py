"""Dinleme parçalarının MP3'lerini üretir (edge-tts).

Kullanım:
    python backend/generate_audio.py --universite general        # yalnız ücretsiz havuz (32 parça)
    python backend/generate_audio.py --universite itu boun
    python backend/generate_audio.py --id lis_a1_06 lis_c2_10
    python backend/generate_audio.py --tumu                      # 656 parça, ~253 MB
    python backend/generate_audio.py --universite general --kuru # hiçbir şey üretme, planı yaz

Dosya adı içerik özetlidir: <id>.<hash8>.mp3
    Metin veya ses değişirse ad da değişir. nginx `/static/audio/` için 90 gün
    "immutable" önbellek verdiğinden (nginx/conf.d/default.conf), aynı adla yeniden
    üretmek tarayıcılara üç ay boyunca eski sesi servis ettirirdi.

Üretilen her parçanın yolu data/listening.json içine "audio_url" olarak yazılır.
audio_url alanı olmayan parçayı istemci tarayıcının kendi seslendirmesiyle okur.

Üretim başarısız olursa DOSYA YAZILMAZ ve parça audio_url almaz. Sessiz ya da bozuk
bir dosya üretip "bu parçanın sesi var" demek, hiç ses olmamasından daha kötüdür.

NOT: edge-tts, Microsoft Edge'in "Sesli Oku" ucunu kullanan resmi olmayan bir
istemcidir. Üretim tek seferliktir; uç kapanırsa üretilmiş dosyalar etkilenmez.
"""

import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LISTENING_JSON = DATA_DIR / "listening.json"

# --cikti ve --url-onek ile değiştirilir (main içinde).
AUDIO_DIR = BASE_DIR / "static" / "audio"
URL_ONEK = "/static/audio/"

# Parça kimliğinden türetilir: dosya sırası değişse bile aynı parça aynı sesi alır.
VOICES = [
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-US-AriaNeural",
    "en-US-ChristopherNeural",
]

ESZAMANLI = 4


def voice_for(track_id: str) -> str:
    h = hashlib.sha1(track_id.encode("utf-8")).hexdigest()
    return VOICES[int(h[:8], 16) % len(VOICES)]


def content_hash(script: str, voice: str) -> str:
    return hashlib.sha256((script + "|" + voice).encode("utf-8")).hexdigest()[:8]


def target_name(track_id: str, script: str, voice: str) -> str:
    return f"{track_id}.{content_hash(script, voice)}.mp3"


def load_tracks():
    return json.loads(LISTENING_JSON.read_text(encoding="utf-8"))


def save_tracks(tracks):
    # Dosyanın mevcut biçimi: ensure_ascii=False, indent=2. Tüm dosyanın yeniden
    # biçimlenmemesi (dev bir diff çıkmaması) için aynısını kullanıyoruz.
    LISTENING_JSON.write_text(
        json.dumps(tracks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def select(tracks, args):
    if args.id:
        istenen = set(args.id)
        secili = [t for t in tracks if t["id"] in istenen]
        bulunamayan = istenen - {t["id"] for t in secili}
        if bulunamayan:
            print("UYARI: bulunamayan kimlikler:", ", ".join(sorted(bulunamayan)))
        return secili
    if args.universite:
        istenen = set(args.universite)
        return [t for t in tracks if (t.get("university_id") or "general") in istenen]
    if args.tumu:
        return list(tracks)
    return []


async def generate_one(track, sem, sonuclar):
    track_id = track["id"]
    script = (track.get("audio_script") or "").strip()
    if not script:
        sonuclar["atlandi_metinsiz"].append(track_id)
        return

    voice = voice_for(track_id)
    ad = target_name(track_id, script, voice)
    hedef = AUDIO_DIR / ad

    if hedef.exists() and hedef.stat().st_size > 1000:
        sonuclar["zaten_var"].append((track_id, ad))
        return

    async with sem:
        try:
            import edge_tts

            gecici = hedef.with_suffix(".mp3.tmp")
            communicate = edge_tts.Communicate(script, voice)
            await communicate.save(str(gecici))
            if not gecici.exists() or gecici.stat().st_size <= 1000:
                gecici.unlink(missing_ok=True)
                raise RuntimeError("üretilen dosya boş ya da çok küçük")
            gecici.replace(hedef)
            sonuclar["uretildi"].append((track_id, ad, hedef.stat().st_size))
            print(f"  + {ad} ({hedef.stat().st_size // 1024} KB)")
        except Exception as e:  # noqa: BLE001 - hangi parçanın neden düştüğünü görmek istiyoruz
            sonuclar["basarisiz"].append((track_id, str(e)))
            print(f"  ! {track_id} ÜRETİLEMEDİ: {e}", file=sys.stderr)


async def main_async(args):
    tracks = load_tracks()
    secili = select(tracks, args)
    if not secili:
        print("Seçili parça yok. --universite, --id ya da --tumu verin.")
        return 1

    toplam_karakter = sum(len((t.get("audio_script") or "")) for t in secili)
    print(f"Seçilen parça: {len(secili)} | toplam {toplam_karakter} karakter")
    print(f"Kaba tahmin: ~{toplam_karakter * 386 / 1024 / 1024:.1f} MB, "
          f"~{toplam_karakter * 0.0059 / 60:.0f} dk (eş zamanlı {ESZAMANLI} ile daha kısa)")

    if args.kuru:
        for t in secili[:10]:
            script = (t.get("audio_script") or "").strip()
            print(f"  - {t['id']} -> {target_name(t['id'], script, voice_for(t['id']))}")
        if len(secili) > 10:
            print(f"  ... ve {len(secili) - 10} parça daha")
        print("(kuru çalışma: hiçbir dosya yazılmadı)")
        return 0

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    sonuclar = {"uretildi": [], "zaten_var": [], "basarisiz": [], "atlandi_metinsiz": []}
    sem = asyncio.Semaphore(ESZAMANLI)
    await asyncio.gather(*(generate_one(t, sem, sonuclar) for t in secili))

    # audio_url'leri yaz: yalnızca dosyası gerçekten duran parçalar için.
    hazir = {}
    for t in secili:
        script = (t.get("audio_script") or "").strip()
        if not script:
            continue
        ad = target_name(t["id"], script, voice_for(t["id"]))
        if (AUDIO_DIR / ad).exists():
            hazir[t["id"]] = URL_ONEK + ad

    degisen = 0
    if URL_ONEK == "yok":
        print("\n(--url-onek yok: listening.json'a audio_url YAZILMADI)")
    else:
        for t in tracks:
            yeni = hazir.get(t["id"])
            if yeni and t.get("audio_url") != yeni:
                t["audio_url"] = yeni
                degisen += 1
        if degisen:
            save_tracks(tracks)

    print("\n--- ÖZET ---")
    print(f"Üretildi      : {len(sonuclar['uretildi'])}")
    print(f"Zaten vardı   : {len(sonuclar['zaten_var'])}")
    print(f"Metni yok     : {len(sonuclar['atlandi_metinsiz'])}")
    print(f"Başarısız     : {len(sonuclar['basarisiz'])}")
    for tid, hata in sonuclar["basarisiz"]:
        print(f"    {tid}: {hata}")
    print(f"listening.json'da güncellenen audio_url: {degisen}")

    if sonuclar["uretildi"]:
        toplam = sum(b for _, _, b in sonuclar["uretildi"])
        print(f"Bu çalışmada yazılan: {toplam / 1024 / 1024:.1f} MB")

    # Aynı parçanın eski sürüm dosyaları (içerik değiştiyse) elle silinebilir.
    beklenen = set(hazir.values())
    eskiler = [
        p.name for p in AUDIO_DIR.glob("*.mp3")
        if p.name.count(".") == 2 and (URL_ONEK + p.name) not in beklenen
        and p.name.split(".")[0] in hazir
    ]
    if eskiler:
        print("\nEski sürüm dosyaları (silinebilir, otomatik silinmedi):")
        for ad in eskiler:
            print("   ", ad)

    return 0 if not sonuclar["basarisiz"] else 2


def main():
    p = argparse.ArgumentParser(description="Dinleme parçaları için MP3 üretir (edge-tts).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--universite", nargs="+", help="university_id listesi (ör. general itu)")
    g.add_argument("--id", nargs="+", help="parça kimlikleri")
    g.add_argument("--tumu", action="store_true", help="bütün parçalar (~253 MB)")
    p.add_argument("--kuru", action="store_true", help="hiçbir şey üretme, ne yapılacağını yaz")
    p.add_argument("--cikti", help="MP3'lerin yazılacağı klasör (varsayılan: static/audio)")
    p.add_argument("--url-onek", dest="url_onek",
                   help="audio_url öneki (varsayılan /static/audio/). 'yok' verilirse "
                        "listening.json'a hiç yazılmaz - dosyalar bir kovaya yüklenecekse bunu kullanın.")
    args = p.parse_args()

    global AUDIO_DIR, URL_ONEK
    if args.cikti:
        AUDIO_DIR = Path(args.cikti).resolve()
    if args.url_onek:
        URL_ONEK = args.url_onek if args.url_onek == "yok" else args.url_onek.rstrip("/") + "/"

    raise SystemExit(asyncio.run(main_async(args)))


if __name__ == "__main__":
    main()
