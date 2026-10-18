# -*- coding: utf-8 -*-
"""
Curated listening track generator for PrepMaster.
Builds exactly 60 listening tracks (10 for A1, 10 for A2, 10 for B1, 10 for B2, 10 for C1, 10 for C2).
"""

import json
from pathlib import Path
from scripts.expand_listening import NEW_LISTENING_TRACKS as A1_TRACKS

DATA_PATH = Path("data/listening.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    existing_tracks = json.load(f)

# Group existing by level
by_level = {"A1": [], "A2": [], "B1": [], "B2": [], "C1": [], "C2": []}
for t in existing_tracks:
    lvl = t.get("level", "B2")
    if lvl in by_level:
        by_level[lvl].append(t)

print("Existing listening tracks by level:", {k: len(v) for k, v in by_level.items()})

# We will generate remaining tracks for A2, B1, B2, C1, C2
MORE_TRACKS = [
    # --- A2 TRACKS (8 TRACKS) ---
    {
        "id": "lis_a2_03",
        "university_id": "ankara",
        "level": "A2",
        "type": "while_listening",
        "title": "Introduction to Marine Biology Field Trip",
        "subtitle": "Ankara Üniversitesi Biyoloji Bölümü Duyurusu",
        "target_university": "Ankara Üniversitesi",
        "duration_minutes": 8,
        "lecture_duration_seconds": 75,
        "instructions_tr": "Saha gezisi hakkındaki bilgilendirmeyi dinlerken soruları yanıtlayın.",
        "audio_script": "Good afternoon, biology undergraduates. Today I want to outline the schedule for our weekend coastal ecology field trip to Sinop. We will depart by chartered bus from the main campus gate at six in the morning on Saturday. Please bring waterproof field boots, a digital notebook, and weather-resistant clothing. The university covers hotel accommodations and breakfast, but students are responsible for their own dinner expenses. We will collect seawater samples on Saturday afternoon and analyze microbial specimens in the mobile lab on Sunday morning. Attendance is mandatory for passing the laboratory component.",
        "suggested_notes_tr": [
            "Hedef: Sinop kıyı ekolojisi saha gezisi",
            "Hareket: Cumartesi sabah 06:00, ana kampüs kapısı",
            "Getirilecekler: Su geçirmez çizme, dijital defter, mevsime uygun giysi",
            "Maliyet: Otel ve kahvaltı üniversiteden, akşam yemeği öğrenciye ait",
            "Program: Cumartesi numune toplama, Pazar mobil laboratuvar analizi"
        ],
        "questions": [
            {
                "id": "lis_a2_03_q1",
                "question": "What time will the chartered bus depart on Saturday morning?",
                "options": [
                    {"key": "A", "text": "At 5:00 AM"},
                    {"key": "B", "text": "At 6:00 AM"},
                    {"key": "C", "text": "At 8:30 AM"},
                    {"key": "D", "text": "At noon"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'depart by chartered bus from the main campus gate at six in the morning' denilmiştir."
            },
            {
                "id": "lis_a2_03_q2",
                "question": "Which expense is NOT covered by the university during the trip?",
                "options": [
                    {"key": "A", "text": "Hotel accommodations"},
                    {"key": "B", "text": "Breakfast meals"},
                    {"key": "C", "text": "Dinner expenses"},
                    {"key": "D", "text": "Chartered bus transportation"}
                ],
                "correct_answer": "C",
                "explanation_tr": "'students are responsible for their own dinner expenses' denilmiştir."
            }
        ]
    },
    {
        "id": "lis_a2_04",
        "university_id": "hacettepe",
        "level": "A2",
        "type": "while_listening",
        "title": "How Spaced Repetition Improves Language Memory",
        "subtitle": "Hacettepe YDYO Öğrenme Stratejileri Dersi",
        "target_university": "Hacettepe Üniversitesi",
        "duration_minutes": 8,
        "lecture_duration_seconds": 80,
        "instructions_tr": "Aralıklı tekrar yönteminin anlatıldığı dersi dinleyip soruları cevaplayınız.",
        "audio_script": "Welcome everyone. In today's mini-lecture, we explore the science of spaced repetition. In the late nineteenth century, German psychologist Hermann Ebbinghaus discovered the forgetting curve. He proved that humans forget nearly fifty percent of newly learned information within twenty-four hours unless it is reviewed. Spaced repetition counteracts this by scheduling reviews at systematically increasing intervals—such as after one day, three days, one week, and one month. Using digital flashcards that employ spaced algorithms allows language students to transfer words from short-term memory into permanent long-term storage.",
        "suggested_notes_tr": [
            "Hermann Ebbinghaus: Unutma eğrisi (Forgetting curve)",
            "Bulgu: Yeni bilginin %50'si 24 saatte unutulur",
            "Aralıklı tekrar: Artan zaman aralıklarıyla gözden geçirme (1 gün, 3 gün, 1 hafta, 1 ay)",
            "Amaç: Kısa süreli bellekten kalıcı uzun süreli belleğe aktarım"
        ],
        "questions": [
            {
                "id": "lis_a2_04_q1",
                "question": "According to Hermann Ebbinghaus, how much information is lost within 24 hours without review?",
                "options": [
                    {"key": "A", "text": "Nearly ten percent"},
                    {"key": "B", "text": "Nearly twenty-five percent"},
                    {"key": "C", "text": "Nearly fifty percent"},
                    {"key": "D", "text": "One hundred percent"}
                ],
                "correct_answer": "C",
                "explanation_tr": "'humans forget nearly fifty percent of newly learned information within twenty-four hours' bilgisi verilir."
            },
            {
                "id": "lis_a2_04_q2",
                "question": "What is the primary benefit of spaced repetition algorithms?",
                "options": [
                    {"key": "A", "text": "They replace the need for reading textbooks"},
                    {"key": "B", "text": "They transfer knowledge into permanent long-term storage"},
                    {"key": "C", "text": "They automatically grade essay exams"},
                    {"key": "D", "text": "They eliminate all grammar errors"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'allows language students to transfer words from short-term memory into permanent long-term storage' denilmiştir."
            }
        ]
    },
    {
        "id": "lis_a2_05",
        "university_id": "gazi",
        "level": "A2",
        "type": "while_listening",
        "title": "Basic Principles of Renewable Wind Energy",
        "subtitle": "Gazi Üniversitesi Mühendisliğe Giriş",
        "target_university": "Gazi Üniversitesi",
        "duration_minutes": 8,
        "lecture_duration_seconds": 75,
        "instructions_tr": "Rüzgar türbinlerinin çalışma prensibini dinleyip soruları cevaplayın.",
        "audio_script": "Good morning class. Today we examine the mechanics of wind turbines. A modern wind turbine converts kinetic energy from moving air into mechanical energy, and then into electricity via an internal generator. The giant aerodynamic blades are designed like airplane wings; as wind passes over them, lift force causes the rotor to spin. Most utility-scale turbines begin generating electricity at wind speeds of approximately three meters per second and automatically shut down during extreme gales exceeding twenty-five meters per second to prevent mechanical failure. Turkey currently produces over eleven thousand megawatts of wind power.",
        "suggested_notes_tr": [
            "Enerji dönüşümü: Kinetik enerji -> Mekanik enerji -> Elektrik (jeneratör ile)",
            "Kanat aerodinamiği: Uçak kanadı gibi kaldırma kuvveti (lift force)",
            "Çalışma hızı: 3 m/s hızda başlar, 25 m/s fırtınada güvenlik için otomatik durur",
            "Türkiye kurulu güç: 11.000 megavat üzeri"
        ],
        "questions": [
            {
                "id": "lis_a2_05_q1",
                "question": "What happens to a wind turbine when wind speeds exceed twenty-five meters per second?",
                "options": [
                    {"key": "A", "text": "It generates double the electrical output"},
                    {"key": "B", "text": "It automatically shuts down for safety"},
                    {"key": "C", "text": "Its blades reverse rotational direction"},
                    {"key": "D", "text": "It switches to solar mode"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'automatically shut down during extreme gales exceeding twenty-five meters per second to prevent mechanical failure' denilmiştir."
            },
            {
                "id": "lis_a2_05_q2",
                "question": "What aerodynamic force causes wind turbine blades to spin?",
                "options": [
                    {"key": "A", "text": "Gravitational pull"},
                    {"key": "B", "text": "Lift force"},
                    {"key": "C", "text": "Frictional resistance"},
                    {"key": "D", "text": "Magnetic repulsion"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'as wind passes over them, lift force causes the rotor to spin' bilgisi açıkça yer alır."
            }
        ]
    },
    {
        "id": "lis_a2_06",
        "university_id": "ege",
        "level": "A2",
        "type": "while_listening",
        "title": "The History of Olive Cultivation in the Mediterranean",
        "subtitle": "Ege Üniversitesi Ziraat ve Tarih Semineri",
        "target_university": "Ege Üniversitesi",
        "duration_minutes": 8,
        "lecture_duration_seconds": 75,
        "instructions_tr": "Akdeniz'de zeytin tarımının tarihini dinleyip soruları cevaplayın.",
        "audio_script": "Olive trees have been cultivated across the Mediterranean basin for over six thousand years. Originating in ancient Anatolia and the Levant, olive farming spread to Greece, Rome, and North Africa through Phoenician maritime merchants. Ancient Mediterranean civilizations valued olive oil not only as dietary sustenance, but also as fuel for ceramic lamps, medicinal ointment, and sacred ceremonial anointment. Olive trees are remarkably drought-resistant, capable of thriving in rocky, arid soils where conventional cereal crops perish. Some ancient olive trees in the Aegean region are estimated to be over a thousand years old.",
        "suggested_notes_tr": [
            "Tarih: 6.000 yıldan fazla geçmiş",
            "Köken: Antik Anadolu ve Levant; Fenikeli tüccarlarla Akdeniz'e yayıldı",
            "Kullanım alanları: Besin, kandil yakıtı, tıbbi merhem, dini törenler",
            "Özellik: Kuraklığa dayanıklı, kayalık topraklarda 1000 yıldan fazla yaşayabilir"
        ],
        "questions": [
            {
                "id": "lis_a2_06_q1",
                "question": "How did olive cultivation spread across the Mediterranean in antiquity?",
                "options": [
                    {"key": "A", "text": "Through Phoenician maritime merchants"},
                    {"key": "B", "text": "By migrating nomadic hunters"},
                    {"key": "C", "text": "Via medieval railway routes"},
                    {"key": "D", "text": "Through airborne pollination alone"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'spread to Greece, Rome, and North Africa through Phoenician maritime merchants' denilmiştir."
            },
            {
                "id": "lis_a2_06_q2",
                "question": "Why are olive trees particularly well-suited to the Mediterranean climate?",
                "options": [
                    {"key": "A", "text": "They require continuous daily rain"},
                    {"key": "B", "text": "They are remarkably drought-resistant and thrive in rocky soils"},
                    {"key": "C", "text": "They only grow in dense rainforests"},
                    {"key": "D", "text": "They cannot survive sunlight"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'remarkably drought-resistant, capable of thriving in rocky, arid soils' ifadesi geçer."
            }
        ]
    },
    {
        "id": "lis_a2_07",
        "university_id": "koc",
        "level": "A2",
        "type": "while_listening",
        "title": "Understanding the Human Circadian Rhythm",
        "subtitle": "Koç Üniversitesi Sağlık Bilimleri Dersi",
        "target_university": "Koç Üniversitesi",
        "duration_minutes": 8,
        "lecture_duration_seconds": 80,
        "instructions_tr": "Biyolojik saat ve uyku döngüsünü anlatan dersi dinleyin.",
        "audio_script": "Every human body possesses an internal biological clock known as the circadian rhythm. Regulated by a tiny cluster of cells in the brain called the suprachiasmatic nucleus, this 24-hour cycle governs sleepiness, core body temperature, and hormone production. When specialized photoreceptors in our retinas detect morning sunlight, the brain suppresses the sleep hormone melatonin, making us alert. Conversely, in the evening, darkness triggers melatonin synthesis, preparing the body for rest. Exposing eyes to bright blue light from smartphone screens before bed disrupts melatonin secretion, leading to chronic insomnia among students.",
        "suggested_notes_tr": [
            "Sirkadiyen ritim: 24 saatlik iç biyolojik saat",
            "Merkez: Beyindeki 'suprachiasmatic nucleus'",
            "Sabah ışığı: Melatonin hormonunu baskılar, uyanıklık sağlar",
            "Karanlık: Melatonin salgısını artırır, uykuya hazırlar",
            "Mavi ışık tehlikesi: Akıllı telefon ekranları melatonin üretimini bozar"
        ],
        "questions": [
            {
                "id": "lis_a2_07_q1",
                "question": "Which hormone is suppressed by the brain when morning sunlight enters the eyes?",
                "options": [
                    {"key": "A", "text": "Insulin"},
                    {"key": "B", "text": "Melatonin"},
                    {"key": "C", "text": "Adrenaline"},
                    {"key": "D", "text": "Dopamine"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'the brain suppresses the sleep hormone melatonin, making us alert' denilmiştir."
            },
            {
                "id": "lis_a2_07_q2",
                "question": "Why does using smartphones before bed cause sleep difficulties?",
                "options": [
                    {"key": "A", "text": "Blue light disrupts evening melatonin secretion"},
                    {"key": "B", "text": "It lowers body temperature too rapidly"},
                    {"key": "C", "text": "It drains brain glucose reserves"},
                    {"key": "D", "text": "It stimulates ear canal infections"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'Exposing eyes to bright blue light from smartphone screens before bed disrupts melatonin secretion' ifadesi yer alır."
            }
        ]
    },
    {
        "id": "lis_a2_08",
        "university_id": "sabanci",
        "level": "A2",
        "type": "while_listening",
        "title": "The Fundamentals of 3D Printing Technology",
        "subtitle": "Sabancı Üniversitesi Üretim Teknolojileri",
        "target_university": "Sabancı Üniversitesi",
        "duration_minutes": 8,
        "lecture_duration_seconds": 75,
        "instructions_tr": "3D yazıcı teknolojisi ve eklemeli imalatı dinleyin.",
        "audio_script": "Three-dimensional printing, technically referred to as additive manufacturing, creates physical objects directly from digital computer-aided design models. Unlike traditional subtractive manufacturing—which cuts or carves material away from a solid block—a 3D printer deposits successive layers of plastic, resin, or metal powder on top of each other until the object is complete. This layer-by-layer technique drastically minimizes raw material waste and allows engineers to fabricate complex internal geometries that are impossible with conventional molds. Today, 3D printing is utilized in aerospace engineering, custom medical prosthetics, and architectural modeling.",
        "suggested_notes_tr": [
            "3D Yazıcı = Eklemeli İmalat (Additive manufacturing)",
            "Gelenekselden farkı: Bloktan yontarak değil, katman katman ekleyerek üretir",
            "Avantajlar: Hammadde israfını azaltır, karmaşık iç geometrileri basabilir",
            "Kullanım: Havacılık, kişiye özel tıbbi protezler, mimari modeller"
        ],
        "questions": [
            {
                "id": "lis_a2_08_q1",
                "question": "How does additive manufacturing differ fundamentally from subtractive manufacturing?",
                "options": [
                    {"key": "A", "text": "It carves material from large solid metal blocks"},
                    {"key": "B", "text": "It deposits successive layers of material on top of each other"},
                    {"key": "C", "text": "It requires manual hand carving"},
                    {"key": "D", "text": "It only produces two-dimensional paper printouts"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'a 3D printer deposits successive layers of plastic, resin, or metal powder on top of each other' denilmiştir."
            },
            {
                "id": "lis_a2_08_q2",
                "question": "Which industry is mentioned as utilizing 3D printing for customized patient care?",
                "options": [
                    {"key": "A", "text": "Automotive tire retreading"},
                    {"key": "B", "text": "Medical prosthetics"},
                    {"key": "C", "text": "Oil refining"},
                    {"key": "D", "text": "Textile spinning"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'custom medical prosthetics, and architectural modeling' cümlesi mevcuttur."
            }
        ]
    },
    {
        "id": "lis_a2_09",
        "university_id": "general",
        "level": "A2",
        "type": "while_listening",
        "title": "Urban Bees and Rooftop Beekeeping",
        "subtitle": "Kentsel Ekoloji ve Çatı Arıcılığı",
        "target_university": "Genel Hazırlık & CEFR A2",
        "duration_minutes": 8,
        "lecture_duration_seconds": 70,
        "instructions_tr": "Şehirlerde arıcılık ve biyoçeşitlilik dersini dinleyin.",
        "audio_script": "In major global metropolises from London to Istanbul, rooftop beekeeping has evolved into a popular ecological movement. Honeybees play a vital pollination role for urban community gardens, parks, and fruit trees. Surprisingly, research demonstrates that urban bees often produce more diverse and pesticide-free honey than rural agricultural bees. This is because modern cities feature diverse decorative flowers blooming continuously across private balconies and public parks, whereas intensive rural farmland frequently relies on monoculture crops sprayed with agricultural insecticides. Urban beehives help maintain city biodiversity while raising ecological awareness.",
        "suggested_notes_tr": [
            "Kentsel arıcılık: Çatılarda ve parklarda yaygınlaşan hareket",
            "Şaşırtıcı bulgu: Şehir arıları kırsal arılara göre daha çeşitli ve pestisitsiz bal üretebiliyor",
            "Neden: Şehir parklarında sürekli açan çiçek çeşitliliği var; kırsalda tek tip ürün ve kimyasal ilaçlama yaygın"
        ],
        "questions": [
            {
                "id": "lis_a2_09_q1",
                "question": "Why do urban bees often produce cleaner honey than rural bees?",
                "options": [
                    {"key": "A", "text": "Cities have no rain"},
                    {"key": "B", "text": "Urban flowers are free from intensive agricultural pesticides"},
                    {"key": "C", "text": "Urban bees are fed artificial sugar water"},
                    {"key": "D", "text": "Hives are kept indoors at warm temperatures"}
                ],
                "correct_answer": "B",
                "explanation_tr": "Metinde kırsaldaki monokültür ve kimyasal ilaçlamaya (insecticides) kıyasla şehirde çeşitlilik ve pestisitsiz çiçekler vurgulanmıştır."
            },
            {
                "id": "lis_a2_09_q2",
                "question": "What primary ecological benefit do bees provide to urban parks and gardens?",
                "options": [
                    {"key": "A", "text": "Pollination of flowers and fruit trees"},
                    {"key": "B", "text": "Reduction of carbon dioxide levels directly"},
                    {"key": "C", "text": "Eradication of mosquito larvae"},
                    {"key": "D", "text": "Cleaning soil pollutants"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'Honeybees play a vital pollination role for urban community gardens, parks, and fruit trees' denilmiştir."
            }
        ]
    },
    {
        "id": "lis_a2_10",
        "university_id": "general",
        "level": "A2",
        "type": "while_listening",
        "title": "The Engineering of Suspension Bridges",
        "subtitle": "Asma Köprülerin Mühendislik Prensipleri",
        "target_university": "Genel Hazırlık & CEFR A2",
        "duration_minutes": 8,
        "lecture_duration_seconds": 75,
        "instructions_tr": "Asma köprülerin yük taşıma sistemini dinleyip soruları cevaplayınız.",
        "audio_script": "Suspension bridges are magnificent feats of civil engineering capable of spanning vast waterways. The architectural principle relies on balancing tension and compression. The roadway deck is hung suspended from vertical suspender cables, which are in turn connected to two massive main cables draped over soaring concrete towers. The immense weight of vehicles transfers upward into tension along the cables, and then downward into compression through the towers into bedrock foundations. The 1915 Çanakkale Bridge in Turkey currently holds the world record for the longest main suspension span, measuring 2,023 meters.",
        "suggested_notes_tr": [
            "Temel ilke: Çekme (tension) ve Basınç (compression) dengesi",
            "Yapı: Tabliye dikey kablolarla ana kablolara, ana kablolar kulelere bağlı",
            "Yük aktarımı: Araç ağırlığı kablolarda çekmeye, kulelerde ise zemine basınç kuvvetine dönüşür",
            "Rekor: 1915 Çanakkale Köprüsü (2.023 metre ana açıklık ile dünya rekoru)"
        ],
        "questions": [
            {
                "id": "lis_a2_10_q1",
                "question": "How is the weight of traffic on a suspension bridge transmitted into the earth?",
                "options": [
                    {"key": "A", "text": "Through tension in cables and compression down the towers"},
                    {"key": "B", "text": "Through floating pontoons beneath the deck"},
                    {"key": "C", "text": "Via magnetic repulsion rails"},
                    {"key": "D", "text": "Only through horizontal steel beams"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'transfers upward into tension along the cables, and then downward into compression through the towers' ifadesi yer alır."
            },
            {
                "id": "lis_a2_10_q2",
                "question": "What record is held by the 1915 Çanakkale Bridge?",
                "options": [
                    {"key": "A", "text": "Oldest operational bridge"},
                    {"key": "B", "text": "Longest main suspension span in the world"},
                    {"key": "C", "text": "Highest railway bridge"},
                    {"key": "D", "text": "First bridge made entirely of carbon fiber"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'holds the world record for the longest main suspension span, measuring 2,023 meters' denilmiştir."
            }
        ]
    }
]

print(f"Loaded additional A2 tracks: {len(MORE_TRACKS)}")
