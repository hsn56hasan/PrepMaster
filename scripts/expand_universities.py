import json
from pathlib import Path

DATA_PATH = Path("data/universities.json")

new_universities = [
    {
        "id": "ankara",
        "name": "Ankara Üniversitesi",
        "short_name": "Ankara Üni",
        "exam_name": "Ankara Üniversitesi Hazırlık Muafiyet Sınavı",
        "passing_score": 70,
        "duration_minutes": 150,
        "total_questions": 60,
        "badge_color": "blue",
        "description": "Ankara Üniversitesi Yabancı Diller Yüksekokulu tarafından uygulanan; Use of English, Okuma-Anlama, Dinleme ve Kompozisyon aşamalarından oluşan muafiyet sınavı.",
        "sections": [
            {
                "name": "Grammar & Structure",
                "questions_count": 20,
                "weight_percent": 25,
                "description": "Cümle tamamlama, bağlaç seçimi ve ileri düzey akademik dilbilgisi kuralları."
            },
            {
                "name": "Vocabulary & Collocations",
                "questions_count": 15,
                "weight_percent": 20,
                "description": "Akademik bağlamda sözcük dağarcığı ve eşdizimlilik (collocation) kullanımı."
            },
            {
                "name": "Reading Comprehension",
                "questions_count": 25,
                "weight_percent": 35,
                "description": "Bilimsel ve sosyal makaleler üzerinden ana fikir ve çıkarım soruları."
            },
            {
                "name": "Essay Writing",
                "questions_count": 1,
                "weight_percent": 20,
                "description": "Verilen iki akademik konudan birinde 250-300 kelimelik fikir veya neden-sonuç yazısı."
            }
        ],
        "tips": [
            "Ankara Üniversitesi sınavında kelime soruları çoğunlukla Academic Word List (AWL) temellidir.",
            "Okuma parçalarında yazarın tutumu (tone & attitude) sorularına dikkat edin.",
            "Writing bölümünde tez cümlenizin (thesis statement) net ve tartışılabilir olmasına özen gösterin."
        ]
    },
    {
        "id": "hacettepe",
        "name": "Hacettepe Üniversitesi",
        "short_name": "Hacettepe",
        "exam_name": "Hacettepe YDYO Muafiyet ve Düzey Belirleme Sınavı",
        "passing_score": 65,
        "duration_minutes": 160,
        "total_questions": 70,
        "badge_color": "red",
        "description": "Hacettepe Üniversitesi Yabancı Diller Yüksekokulu hazırlık muafiyet sınavı; Use of English, Dinleme (Listening), Okuma ve Yazma (Writing) bölümlerini içerir.",
        "sections": [
            {
                "name": "Use of English & Vocabulary",
                "questions_count": 25,
                "weight_percent": 25,
                "description": "Cloze test, cümle tamamlama ve akademik kelime kalıpları."
            },
            {
                "name": "Listening (While-Listening & Note-Taking)",
                "questions_count": 15,
                "weight_percent": 25,
                "description": "Akademik diyalog ve ders sunumunu dinleyerek soruları yanıtlama."
            },
            {
                "name": "Reading Comprehension",
                "questions_count": 30,
                "weight_percent": 30,
                "description": "Ayrıntılı okuma, paragraf akışını bozan cümleyi bulma ve referans sözcükleri."
            },
            {
                "name": "Academic Writing",
                "questions_count": 1,
                "weight_percent": 20,
                "description": "Opinion veya For & Against formatında en az 300 kelimelik akademik essay."
            }
        ],
        "tips": [
            "Listening aşamasında not alırken kısaltmalar kullanın ve sayısal verileri kaçırmayın.",
            "Reading bölümünde paragrafın ilk ve son cümlelerine odaklanarak ana fikri hızla belirleyin.",
            "Dilbilgisi bölümünde zaman uyumu (tense consistency) ve devrik cümle yapılarına dikkat edin."
        ]
    },
    {
        "id": "gazi",
        "name": "Gazi Üniversitesi",
        "short_name": "Gazi Üni",
        "exam_name": "Gazi YDYO Yabancı Dil Yeterlik Sınavı",
        "passing_score": 60,
        "duration_minutes": 135,
        "total_questions": 60,
        "badge_color": "emerald",
        "description": "Gazi Üniversitesi Yabancı Diller Yüksekokulu tarafından uygulanan; dilbilgisi, kelime bilgisi, okuma ve yazılı anlatımı ölçen yeterlik sınavı.",
        "sections": [
            {
                "name": "Use of English & Grammar",
                "questions_count": 25,
                "weight_percent": 30,
                "description": "Temel ve orta-ileri düzey dilbilgisi, bağlaçlar ve edatlar."
            },
            {
                "name": "Vocabulary",
                "questions_count": 15,
                "weight_percent": 20,
                "description": "Eşanlamlı, zıtanlamlı ve bağlamsal kelime bilgisi."
            },
            {
                "name": "Reading Comprehension",
                "questions_count": 20,
                "weight_percent": 30,
                "description": "Orta ve ileri düzey metinlerden çıkarım ve detay soruları."
            },
            {
                "name": "Writing",
                "questions_count": 1,
                "weight_percent": 20,
                "description": "Konuya uygun giriş-gelişme-sonuç yapısında kompozisyon yazımı."
            }
        ],
        "tips": [
            "Kelime bilgisinde phrasal verbs ve prepositional phrases yapılarını tekrar edin.",
            "Okuma metinlerinde parçanın bütününe yayılmış ana fikri tespit etmeye odaklanın."
        ]
    },
    {
        "id": "ege",
        "name": "Ege Üniversitesi",
        "short_name": "Ege Üni",
        "exam_name": "Ege Üniversitesi YDYO Yeterlik Sınavı",
        "passing_score": 60,
        "duration_minutes": 140,
        "total_questions": 60,
        "badge_color": "sky",
        "description": "Ege Üniversitesi Yabancı Diller Yüksekokulu hazırlık muafiyet sınavı; dilbilgisi, okuma-anlama, dinleme ve yazma aşamalarından oluşur.",
        "sections": [
            {
                "name": "Language Use & Grammar",
                "questions_count": 20,
                "weight_percent": 25,
                "description": "Yapısal dilbilgisi ve akademik cümle yapıları."
            },
            {
                "name": "Reading Skills",
                "questions_count": 25,
                "weight_percent": 35,
                "description": "Skimming, scanning ve detaylı okuma becerileri."
            },
            {
                "name": "Listening",
                "questions_count": 15,
                "weight_percent": 20,
                "description": "Ders anlatımı ve mülakat kayıtlarından dinleme soruları."
            },
            {
                "name": "Guided Writing",
                "questions_count": 1,
                "weight_percent": 20,
                "description": "Verilen yönergelere uygun akademik paragraf veya kısa essay."
            }
        ],
        "tips": [
            "Metin sorularında doğrudan metinde geçen ifadeler yerine eşanlamlıları (paraphrase) işaretleyin.",
            "Dinleme başlamadan önce soru köklerini hızlıca okuyarak ipucu yakalayın."
        ]
    },
    {
        "id": "koc",
        "name": "Koç Üniversitesi",
        "short_name": "Koç Üni",
        "exam_name": "KUEPE (Koç University English Proficiency Exam)",
        "passing_score": 65,
        "duration_minutes": 180,
        "total_questions": 55,
        "badge_color": "amber",
        "description": "Koç Üniversitesi İngilizce Dil Merkezi (ELC) tarafından hazırlanan; Reading, Listening, Writing ve Speaking yetkinliğini ileri düzeyde (C1) sınayan kapsamlı muafiyet sınavı.",
        "sections": [
            {
                "name": "Reading Comprehension",
                "questions_count": 25,
                "weight_percent": 30,
                "description": "Akademik makaleler, eleştirel analiz, çıkarım ve metinlerarası sentez."
            },
            {
                "name": "Listening Comprehension",
                "questions_count": 20,
                "weight_percent": 25,
                "description": "Kapsamlı üniversite dersi kaydından not alma ve detayları yanıtlama."
            },
            {
                "name": "Academic Essay Writing",
                "questions_count": 1,
                "weight_percent": 30,
                "description": "Okuma metinlerine atıfta bulunarak sentez odaklı argümantatif kompozisyon."
            },
            {
                "name": "Speaking Interview",
                "questions_count": 1,
                "weight_percent": 15,
                "description": "Akademik bir konuda 2 dakikalık sunum ve jüri sorularını yanıtlama."
            }
        ],
        "tips": [
            "KUEPE'de ezbere şablonlar kesinlikle kabul edilmez; eleştirel düşünme ve özgün argümantasyon esastır.",
            "Synthesis writing için dinleme ve okuma kaynaklarındaki verileri karşılaştırarak sentezlemeyi öğrenin."
        ]
    },
    {
        "id": "sabanci",
        "name": "Sabancı Üniversitesi",
        "short_name": "Sabancı",
        "exam_name": "ELAE (English Language Assessment Exam)",
        "passing_score": 65,
        "duration_minutes": 190,
        "total_questions": 50,
        "badge_color": "indigo",
        "description": "Sabancı Üniversitesi Diller Okulu (SL) tarafından düzenlenen iki aşamalı ELAE sınavı; akademik okuma, dinleme ve essay yazma becerilerini uluslararası standartta ölçer.",
        "sections": [
            {
                "name": "Careful & Search Reading",
                "questions_count": 20,
                "weight_percent": 30,
                "description": "İleri düzey akademik metin analizi ve ana fikir tespiti."
            },
            {
                "name": "Listening & Note Taking",
                "questions_count": 15,
                "weight_percent": 30,
                "description": "Uzun soluklu akademik konferans kaydını dinleyerek soru yanıtlama."
            },
            {
                "name": "Academic Writing Task",
                "questions_count": 1,
                "weight_percent": 40,
                "description": "Verilen iki farklı perspektifi sentezleyerek 350-400 kelimelik akademik essay kaleme alma."
            }
        ],
        "tips": [
            "ELAE 1. aşamasını geçemeyenler 2. aşamaya giremez; Use of English ve hızlı okuma pratiği yapın.",
            "Not alırken fikir geçişlerini ve konuşmacının vurguladığı istisnaları mutlaka işaretleyin."
        ]
    }
]

with open(DATA_PATH, "r", encoding="utf-8") as f:
    existing = json.load(f)

existing_ids = {u["id"] for u in existing}
added = 0
for u in new_universities:
    if u["id"] not in existing_ids:
        existing.append(u)
        added += 1

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"Added {added} new universities. Total universities: {len(existing)}")
