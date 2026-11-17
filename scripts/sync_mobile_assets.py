"""
data/ -> mobile/assets/data/ kopyası (APK'ya gömülen veri).

APK herkesin indirip açabildiği bir dosyadır: içine gömülen her şey fiilen herkese açıktır.
Bu yüzden ücretli (üniversiteye özel) sorular, dinleme ve konuşma içerikleri APK'ya KONMAZ;
yalnızca ücretsiz genel havuz gömülür. Üniversite içeriği uygulamada sunucudan, erişim
kontrolünden geçerek gelir.

Kullanım: python scripts/sync_mobile_assets.py   (diğer içerik betikleri de bunu çağırır)
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data"
DST = ROOT / "mobile" / "assets" / "data"

AS_IS = ("universities.json", "vocabulary.json", "writing_guides.json")
GENERAL_ONLY = ("questions.json", "listening.json", "speaking.json")


def general_only(items):
    return [x for x in items if (x.get("university_id") or "general") == "general"]


def sync():
    DST.mkdir(parents=True, exist_ok=True)
    for name in AS_IS:
        shutil.copyfile(SRC / name, DST / name)
    counts = {}
    for name in GENERAL_ONLY:
        items = general_only(json.loads((SRC / name).read_text(encoding="utf-8")))
        (DST / name).write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        counts[name] = len(items)
    return counts


if __name__ == "__main__":
    print("Mobil varlıklar güncellendi (yalnız genel içerik):", sync())
