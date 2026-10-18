# -*- coding: utf-8 -*-
"""
Expand data/listening.json so every CEFR level (A1, A2, B1, B2, C1, C2)
has at least 10 authentic listening tracks with complete questions and scripts.
Total: 60 listening tracks.
"""

import json
from pathlib import Path

TARGET_FILE = Path("data/listening.json")

with open(TARGET_FILE, "r", encoding="utf-8") as f:
    existing_tracks = json.load(f)

existing_ids = {t["id"] for t in existing_tracks}

# Build dataset of 46 new tracks
# A1: 10 tracks
# A2: 8 tracks
# B1: 8 tracks
# B2: 6 tracks
# C1: 6 tracks
# C2: 8 tracks

NEW_LISTENING_TRACKS = [
    # ==========================================
    # --- A1 LISTENING TRACKS (10 TRACKS) ---
    # ==========================================
    {
        "id": "lis_a1_01",
        "university_id": "ankara",
        "level": "A1",
        "type": "while_listening",
        "title": "Welcome to the University Library",
        "subtitle": "Ankara Üniversitesi Kütüphane Oryantasyonu",
        "target_university": "Ankara Üniversitesi",
        "duration_minutes": 5,
        "lecture_duration_seconds": 65,
        "instructions_tr": "Kütüphanecinin konuşmasını dinlerken soruları yanıtlayınız (While-Listening).",
        "audio_script": "Good morning and welcome to the central library. Our library is open from eight o'clock in the morning until nine o'clock at night on weekdays. On weekends, we open at ten o'clock. First-year students can borrow up to five books for two weeks. Please remember that food and open drinks are strictly forbidden inside the study rooms. However, you can bring a closed water bottle. If you need a computer for your research, they are located on the second floor next to the reference desk. Enjoy your study time.",
        "suggested_notes_tr": [
            "Hafta içi saatler: 08:00 - 21:00",
            "Hafta sonu açılış: 10:00",
            "Ödünç kitap kotası: 5 kitap / 2 hafta",
            "Yiyecek/içecek kuralı: Sadece kapalı su serbest",
            "Bilgisayarlar: 2. kat, danışma yanı"
        ],
        "questions": [
            {
                "id": "lis_a1_01_q1",
                "question": "What time does the library open on Saturday and Sunday?",
                "options": [
                    {"key": "A", "text": "At 8:00 AM"},
                    {"key": "B", "text": "At 9:00 AM"},
                    {"key": "C", "text": "At 10:00 AM"},
                    {"key": "D", "text": "At 12:00 PM"}
                ],
                "correct_answer": "C",
                "explanation_tr": "Metinde 'On weekends, we open at ten o'clock' denilerek hafta sonu saat 10:00'da açıldığı belirtilmiştir."
            },
            {
                "id": "lis_a1_01_q2",
                "question": "How many books can a first-year student borrow at one time?",
                "options": [
                    {"key": "A", "text": "Three books"},
                    {"key": "B", "text": "Five books"},
                    {"key": "C", "text": "Seven books"},
                    {"key": "D", "text": "Ten books"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'First-year students can borrow up to five books for two weeks' ifadesi geçmektedir."
            },
            {
                "id": "lis_a1_01_q3",
                "question": "Where are the research computers located?",
                "options": [
                    {"key": "A", "text": "In the cafeteria"},
                    {"key": "B", "text": "On the ground floor entrance"},
                    {"key": "C", "text": "On the second floor near the reference desk"},
                    {"key": "D", "text": "In the outdoor garden"}
                ],
                "correct_answer": "C",
                "explanation_tr": "Bilgisayarların 2. katta danışmanın (reference desk) yanında olduğu söylenmiştir."
            }
        ]
    },
    {
        "id": "lis_a1_02",
        "university_id": "hacettepe",
        "level": "A1",
        "type": "while_listening",
        "title": "First Day at Preparatory English School",
        "subtitle": "Hacettepe YDYO Bilgilendirme Konuşması",
        "target_university": "Hacettepe Üniversitesi",
        "duration_minutes": 5,
        "lecture_duration_seconds": 60,
        "instructions_tr": "Ders saatleri ve kurallara ilişkin bilgilendirmeyi dinleyip soruları cevaplayınız.",
        "audio_script": "Hello students, my name is Sarah Jenkins, and I am your English preparatory instructor. Our classes meet every Monday, Tuesday, and Thursday from nine to twelve. On Wednesdays, we have vocabulary workshops in the language lab. Regular attendance is very important. If you miss more than twenty percent of classes, you cannot take the final level exam. Please purchase your coursebook from the university bookstore before next Monday. Have a wonderful semester.",
        "suggested_notes_tr": [
            "Ders günleri: Pazartesi, Salı, Perşembe (09:00-12:00)",
            "Çarşamba: Dil laboratuvarında kelime atölyesi",
            "Devamsızlık sınırı: %20'yi aşarsa sınava girilemez",
            "Ders kitabı: Kampüs kitabevinden alınmalı"
        ],
        "questions": [
            {
                "id": "lis_a1_02_q1",
                "question": "What activity takes place on Wednesdays?",
                "options": [
                    {"key": "A", "text": "Grammar tests in the cafeteria"},
                    {"key": "B", "text": "Vocabulary workshops in the language lab"},
                    {"key": "C", "text": "Sports competitions"},
                    {"key": "D", "text": "Independent reading at home"}
                ],
                "correct_answer": "B",
                "explanation_tr": "Metinde 'On Wednesdays, we have vocabulary workshops in the language lab' denmektedir."
            },
            {
                "id": "lis_a1_02_q2",
                "question": "What happens if a student misses more than 20 percent of classes?",
                "options": [
                    {"key": "A", "text": "They receive extra homework"},
                    {"key": "B", "text": "They must change their department"},
                    {"key": "C", "text": "They cannot take the final level exam"},
                    {"key": "D", "text": "They pay an administrative fine"}
                ],
                "correct_answer": "C",
                "explanation_tr": "'If you miss more than twenty percent of classes, you cannot take the final level exam' denilmiştir."
            }
        ]
    },
    {
        "id": "lis_a1_03",
        "university_id": "gazi",
        "level": "A1",
        "type": "while_listening",
        "title": "Ordering Lunch at the Student Dining Hall",
        "subtitle": "Kampüs Yemekhanesi Diyaloğu",
        "target_university": "Gazi Üniversitesi",
        "duration_minutes": 5,
        "lecture_duration_seconds": 55,
        "instructions_tr": "Öğrenci ile yemekhane görevlisi arasındaki diyaloğu dinleyin.",
        "audio_script": "Worker: Hello, what would you like for lunch today? Student: Hi! Could I have the lentil soup and the grilled chicken, please? Worker: Certainly. Would you prefer rice or pasta as a side dish? Student: Rice, please. Worker: And would you like a bottle of mineral water or orange juice? Student: Just water, thank you. How much is the meal? Worker: With your student ID card, the lunch menu is thirty liras. Student: Here is my card. Thank you very much.",
        "suggested_notes_tr": [
            "Seçilen yemekler: Mercimek çorbası, ızgara tavuk, pilav",
            "İçecek: Su",
            "Öğrenci kartı ile menü fiyatı: 30 TL"
        ],
        "questions": [
            {
                "id": "lis_a1_03_q1",
                "question": "Which side dish did the student choose?",
                "options": [
                    {"key": "A", "text": "Mashed potatoes"},
                    {"key": "B", "text": "Rice"},
                    {"key": "C", "text": "Pasta"},
                    {"key": "D", "text": "Mixed salad"}
                ],
                "correct_answer": "B",
                "explanation_tr": "Öğrenci açıkça 'Rice, please' cevabını vermiştir."
            },
            {
                "id": "lis_a1_03_q2",
                "question": "How much does the lunch menu cost with a student ID?",
                "options": [
                    {"key": "A", "text": "Twenty liras"},
                    {"key": "B", "text": "Thirty liras"},
                    {"key": "C", "text": "Fifty liras"},
                    {"key": "D", "text": "Free of charge"}
                ],
                "correct_answer": "B",
                "explanation_tr": "Görevli 'With your student ID card, the lunch menu is thirty liras' demiştir."
            }
        ]
    },
    {
        "id": "lis_a1_04",
        "university_id": "ege",
        "level": "A1",
        "type": "while_listening",
        "title": "Campus Transportation and Bus Services",
        "subtitle": "Ege Üniversitesi Kampüs Ulaşımı",
        "target_university": "Ege Üniversitesi",
        "duration_minutes": 5,
        "lecture_duration_seconds": 60,
        "instructions_tr": "Kampüs içi ring seferleri duyurusunu dinleyip soruları işaretleyiniz.",
        "audio_script": "Attention all students. The free campus shuttle bus departs from the metro station every ten minutes between eight in the morning and six in the evening. The bus stops at the Faculty of Medicine, the sports arena, and the preparatory language school. After six o'clock, buses run every twenty minutes until ten at night. Please show your student transport card to the driver when boarding. Bicycles are also welcome on campus bike lanes.",
        "suggested_notes_tr": [
            "Ring servisleri: 08:00 - 18:00 arası her 10 dakikada bir",
            "18:00 sonrası: Her 20 dakikada bir (22:00'ye kadar)",
            "Duraklar: Tıp Fakültesi, Spor Salonu, Yabancı Diller Hazırlık",
            "Ücretsiz ve bisiklet yolları mevcut"
        ],
        "questions": [
            {
                "id": "lis_a1_04_q1",
                "question": "How frequently do shuttle buses depart during the morning peak hours?",
                "options": [
                    {"key": "A", "text": "Every five minutes"},
                    {"key": "B", "text": "Every ten minutes"},
                    {"key": "C", "text": "Every half hour"},
                    {"key": "D", "text": "Once an hour"}
                ],
                "correct_answer": "B",
                "explanation_tr": "Metinde 'every ten minutes between eight in the morning and six in the evening' denilmektedir."
            },
            {
                "id": "lis_a1_04_q2",
                "question": "What is required when boarding the free campus bus?",
                "options": [
                    {"key": "A", "text": "Cash ticket"},
                    {"key": "B", "text": "Student transport card"},
                    {"key": "C", "text": "Passport"},
                    {"key": "D", "text": "Library membership form"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'Please show your student transport card to the driver' ifadesi yer almaktadır."
            }
        ]
    },
    {
        "id": "lis_a1_05",
        "university_id": "ytu",
        "level": "A1",
        "type": "while_listening",
        "title": "Joining Student Clubs and Societies",
        "subtitle": "YTÜ Kulüpler Birliği Tanıtımı",
        "target_university": "Yıldız Teknik Üniversitesi",
        "duration_minutes": 5,
        "lecture_duration_seconds": 60,
        "instructions_tr": "Öğrenci kulüpleri festivali duyurusunu dinleyip soruları cevaplayın.",
        "audio_script": "Welcome new freshmen! Today is Club Day at the student center. There are over forty active student clubs on campus, including the robotics club, the photography society, and the outdoor mountaineering club. Joining a club is free for all enrolled students. Visit the registration booths in the central courtyard before four o'clock today to sign up. Members meet every Tuesday evening for workshops and events.",
        "suggested_notes_tr": [
            "Kulüp sayısı: 40'tan fazla aktif kulüp",
            "Örnek kulüpler: Robotik, Fotoğrafçılık, Dağcılık",
            "Ücret: Tüm kayıtlı öğrencilere ücretsiz",
            "Kayıt son saat: Bugün 16:00'ya kadar orta avluda"
        ],
        "questions": [
            {
                "id": "lis_a1_05_q1",
                "question": "How much does it cost for enrolled students to join a club?",
                "options": [
                    {"key": "A", "text": "Fifty liras per month"},
                    {"key": "B", "text": "One hundred liras annually"},
                    {"key": "C", "text": "It is completely free"},
                    {"key": "D", "text": "Only senior students can join"}
                ],
                "correct_answer": "C",
                "explanation_tr": "'Joining a club is free for all enrolled students' cümlesi kulüplerin tamamen ücretsiz olduğunu belirtir."
            },
            {
                "id": "lis_a1_05_q2",
                "question": "What time do registration booths close today?",
                "options": [
                    {"key": "A", "text": "At 2:00 PM"},
                    {"key": "B", "text": "At 4:00 PM"},
                    {"key": "C", "text": "At 6:00 PM"},
                    {"key": "D", "text": "At midnight"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'before four o'clock today' denilerek saat 16:00'da kapanacağı söylenmiştir."
            }
        ]
    },
    {
        "id": "lis_a1_06",
        "university_id": "general",
        "level": "A1",
        "type": "while_listening",
        "title": "Finding Books in the Campus Bookstore",
        "subtitle": "Kitabevi Alışveriş Diyaloğu",
        "target_university": "Genel Hazırlık & CEFR A1",
        "duration_minutes": 5,
        "lecture_duration_seconds": 55,
        "instructions_tr": "Kitabevindeki konuşmayı dinleyerek soruları yanıtlayın.",
        "audio_script": "Clerk: Good afternoon, can I help you find something? Student: Yes, please. I am looking for the English Grammar in Use textbook for level A1. Clerk: Certainly. That textbook is on shelf number four, under the language learning section. We also have workbook editions with audio CDs. Student: Does the book include online practice tests? Clerk: Yes, there is an access code inside the front cover. Student: Wonderful, I will take it.",
        "suggested_notes_tr": [
            "Aranan kitap: English Grammar in Use (A1)",
            "Konum: 4 numaralı raf, dil öğrenimi bölümü",
            "Özellik: Ön kapakta online deneme testleri erişim kodu var"
        ],
        "questions": [
            {
                "id": "lis_a1_06_q1",
                "question": "On which shelf is the grammar textbook located?",
                "options": [
                    {"key": "A", "text": "Shelf number two"},
                    {"key": "B", "text": "Shelf number four"},
                    {"key": "C", "text": "Shelf number seven"},
                    {"key": "D", "text": "Behind the cash register"}
                ],
                "correct_answer": "B",
                "explanation_tr": "Görevli 'That textbook is on shelf number four' demiştir."
            },
            {
                "id": "lis_a1_06_q2",
                "question": "Where is the online practice test code found?",
                "options": [
                    {"key": "A", "text": "On the sales receipt"},
                    {"key": "B", "text": "On the bookstore website"},
                    {"key": "C", "text": "Inside the front cover of the book"},
                    {"key": "D", "text": "Sent by email"}
                ],
                "correct_answer": "C",
                "explanation_tr": "'there is an access code inside the front cover' bilgisi verilmiştir."
            }
        ]
    },
    {
        "id": "lis_a1_07",
        "university_id": "general",
        "level": "A1",
        "type": "while_listening",
        "title": "Campus Health Center and Doctor Appointments",
        "subtitle": "Sağlık Merkezi Bilgilendirmesi",
        "target_university": "Genel Hazırlık & CEFR A1",
        "duration_minutes": 5,
        "lecture_duration_seconds": 60,
        "instructions_tr": "Üniversite sağlık merkezi duyurusunu dinleyip soruları cevaplayın.",
        "audio_script": "The student health center is located next to the main dormitory building. General medical doctors are available from nine in the morning until five in the afternoon without an appointment. If you need a dental checkup or eye examination, please book an appointment online through the student medical portal. In case of emergency after five o'clock, the campus ambulance service can be reached twenty-four hours a day by dialing extension 112.",
        "suggested_notes_tr": [
            "Konum: Ana yurt binasının yanı",
            "Genel hekim saatleri: 09:00 - 17:00 (randevusuz muayene)",
            "Diş / Göz: Portal üzerinden online randevu gerekir",
            "Acil durum: 24 saat ambulans (Dahili 112)"
        ],
        "questions": [
            {
                "id": "lis_a1_07_q1",
                "question": "When can students see a general doctor without an appointment?",
                "options": [
                    {"key": "A", "text": "Only on Monday mornings"},
                    {"key": "B", "text": "Between 9:00 AM and 5:00 PM"},
                    {"key": "C", "text": "After 8:00 PM"},
                    {"key": "D", "text": "On Sunday afternoons"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'General medical doctors are available from nine in the morning until five in the afternoon without an appointment' denilmiştir."
            },
            {
                "id": "lis_a1_07_q2",
                "question": "How should students arrange a dental appointment?",
                "options": [
                    {"key": "A", "text": "Call the city hospital"},
                    {"key": "B", "text": "Book online via the student portal"},
                    {"key": "C", "text": "Ask their English instructor"},
                    {"key": "D", "text": "Visit in person on weekends"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'please book an appointment online through the student medical portal' ifadesi geçer."
            }
        ]
    },
    {
        "id": "lis_a1_08",
        "university_id": "general",
        "level": "A1",
        "type": "while_listening",
        "title": "Weather Forecast for Campus Sports Tournament",
        "subtitle": "Hava Durumu ve Spor Etkinliği",
        "target_university": "Genel Hazırlık & CEFR A1",
        "duration_minutes": 5,
        "lecture_duration_seconds": 55,
        "instructions_tr": "Haftalık hava tahminini dinleyerek spor turnuvası programı sorularını yanıtlayın.",
        "audio_script": "Here is the campus weather forecast for this week. Monday and Tuesday will be partly cloudy with pleasant temperatures around eighteen degrees Celsius. On Wednesday, expect heavy rain and cooler winds, so the outdoor football matches will be moved inside the gymnasium. Thursday and Friday will be warm and sunny, with temperatures climbing to twenty-four degrees. Perfect weather for the track and field championship on Friday afternoon.",
        "suggested_notes_tr": [
            "Pazartesi-Salı: Parçalı bulutlu, 18 derece",
            "Çarşamba: Şiddetli yağmur, futbol kapalı spor salonuna alındı",
            "Perşembe-Cuma: Güneşli ve 24 derece, Cuma atletizm şampiyonası"
        ],
        "questions": [
            {
                "id": "lis_a1_08_q1",
                "question": "Why will the outdoor football matches be moved inside on Wednesday?",
                "options": [
                    {"key": "A", "text": "Due to extreme summer heat"},
                    {"key": "B", "text": "Because of heavy rain and wind"},
                    {"key": "C", "text": "The football field is under construction"},
                    {"key": "D", "text": "Lack of referee availability"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'expect heavy rain and cooler winds, so the outdoor football matches will be moved inside' denilmiştir."
            },
            {
                "id": "lis_a1_08_q2",
                "question": "What is the expected temperature for Friday afternoon?",
                "options": [
                    {"key": "A", "text": "Ten degrees"},
                    {"key": "B", "text": "Eighteen degrees"},
                    {"key": "C", "text": "Twenty-four degrees"},
                    {"key": "D", "text": "Thirty-five degrees"}
                ],
                "correct_answer": "C",
                "explanation_tr": "'temperatures climbing to twenty-four degrees' cümlesi yer almaktadır."
            }
        ]
    },
    {
        "id": "lis_a1_09",
        "university_id": "general",
        "level": "A1",
        "type": "while_listening",
        "title": "Computer Lab Guidelines and Printing Rules",
        "subtitle": "Bilgisayar Laboratuvarı ve Yazıcı Kuralları",
        "target_university": "Genel Hazırlık & CEFR A1",
        "duration_minutes": 5,
        "lecture_duration_seconds": 60,
        "instructions_tr": "Bilgisayar laboratuvarı kurallarını dinleyip soruları cevaplayın.",
        "audio_script": "Welcome to the engineering computer lab. Before using any workstation, log in using your student email and password. Each student receives fifty free printed pages per month. If you exceed this quota, additional pages cost fifty kuruş each. Please do not save personal files on desktop computers; store your homework on USB flash drives or cloud storage, as all desktop computers reset automatically every night at midnight.",
        "suggested_notes_tr": [
            "Giriş: Öğrenci e-postası ve şifresi ile",
            "Baskı kotası: Ayda 50 ücretsiz sayfa (sonrası 50 kuruş)",
            "Dosya saklama: Masaüstüne kaydetmeyin (gece yarısı sıfırlanır), bulut veya USB kullanın"
        ],
        "questions": [
            {
                "id": "lis_a1_09_q1",
                "question": "How many free printed pages does each student receive per month?",
                "options": [
                    {"key": "A", "text": "Ten pages"},
                    {"key": "B", "text": "Twenty-five pages"},
                    {"key": "C", "text": "Fifty pages"},
                    {"key": "D", "text": "One hundred pages"}
                ],
                "correct_answer": "C",
                "explanation_tr": "'Each student receives fifty free printed pages per month' ifadesi geçmektedir."
            },
            {
                "id": "lis_a1_09_q2",
                "question": "Why should students avoid saving files directly on lab desktop computers?",
                "options": [
                    {"key": "A", "text": "Printers will reject the file format"},
                    {"key": "B", "text": "Computers reset automatically at midnight"},
                    {"key": "C", "text": "Internet access is restricted"},
                    {"key": "D", "text": "The screens turn off during class"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'all desktop computers reset automatically every night at midnight' denilmiştir."
            }
        ]
    },
    {
        "id": "lis_a1_10",
        "university_id": "general",
        "level": "A1",
        "type": "while_listening",
        "title": "Lost and Found Office Announcement",
        "subtitle": "Kayıp Eşya Bürosu Anonsu",
        "target_university": "Genel Hazırlık & CEFR A1",
        "duration_minutes": 5,
        "lecture_duration_seconds": 55,
        "instructions_tr": "Kayıp eşya bürosu duyurusunu dinleyerek soruları yanıtlayın.",
        "audio_script": "This is an announcement from the campus security office. A black leather backpack containing a student notebook and silver laptop was found in lecture hall B yesterday afternoon. If you are the owner of this bag, please come to the lost and found office in building three. Bring your official student ID card to claim your belongings. The office is open from eight in the morning until four in the afternoon.",
        "suggested_notes_tr": [
            "Bulunan eşya: Siyah deri sırt çantası (içinde defter ve gümüş renkli dizüstü bilgisayar)",
            "Bulunduğu yer: B amfisi (dün öğleden sonra)",
            "Teslim yeri: 3 numaralı bina Kayıp Eşya Bürosu (08:00 - 16:00)",
            "Gerekli belge: Resmi öğrenci kimlik kartı"
        ],
        "questions": [
            {
                "id": "lis_a1_10_q1",
                "question": "Where was the black leather backpack found yesterday?",
                "options": [
                    {"key": "A", "text": "In the sports cafeteria"},
                    {"key": "B", "text": "In lecture hall B"},
                    {"key": "C", "text": "Inside the metro station"},
                    {"key": "D", "text": "At the campus gate"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'found in lecture hall B yesterday afternoon' denilmiştir."
            },
            {
                "id": "lis_a1_10_q2",
                "question": "What must the owner bring to claim the lost backpack?",
                "options": [
                    {"key": "A", "text": "A monetary reward"},
                    {"key": "B", "text": "A letter from the department dean"},
                    {"key": "C", "text": "Their official student ID card"},
                    {"key": "D", "text": "A purchase receipt for the laptop"}
                ],
                "correct_answer": "C",
                "explanation_tr": "'Bring your official student ID card to claim your belongings' ifadesi yer alır."
            }
        ]
    }
]

# Write builder script to append and balance tracks up to 10 per level
