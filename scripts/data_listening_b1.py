# -*- coding: utf-8 -*-
"""
Curated listening track database for B1, B2, C1, and C2 levels.
Appends to data/listening.json to achieve exactly 10 tracks per level across all 6 CEFR tiers.
"""

import json
from pathlib import Path
from scripts.expand_listening import NEW_LISTENING_TRACKS as A1_TRACKS
from scripts.generate_all_listening import MORE_TRACKS as A2_TRACKS

DATA_PATH = Path("data/listening.json")

B1_TRACKS = [
    {
        "id": "lis_b1_03",
        "university_id": "ankara",
        "level": "B1",
        "type": "note_taking",
        "title": "Smart Irrigation in Mediterranean Agriculture",
        "subtitle": "Ankara Üniversitesi Ziraat Fakültesi Dersi",
        "target_university": "Ankara Üniversitesi",
        "duration_minutes": 10,
        "lecture_duration_seconds": 90,
        "instructions_tr": "Akıllı sulama teknolojileri dersini dinleyiniz. Dinlerken notlarınızı dijital deftere kaydediniz; ardından soruları yanıtlayınız.",
        "audio_script": "Good morning class. Today we explore smart precision irrigation in modern Mediterranean farming. Conventional flood irrigation is notoriously wasteful, losing up to fifty percent of water to surface evaporation and runoff. In contrast, automated smart irrigation integrates subterranean soil moisture sensors with localized meteorological satellite data. These internet-of-things sensors continuously transmit real-time telemetry regarding soil osmotic potential to a centralized cloud controller. The automated system then activates subterranean drip lines only when plant roots truly require hydration, typically during pre-dawn hours when evaporative heat is lowest. Agronomical field trials in the Konya basin demonstrate that smart drip systems diminish total agricultural water consumption by thirty-five percent while increasing crop yield by twelve percent. As freshwater reserves face severe climate volatility, precision irrigation becomes an essential ecological adaptation.",
        "suggested_notes_tr": [
            "Geleneksel sulama: %50 su kaybı (buharlaşma ve yüzey akışı)",
            "Akıllı hassas sulama: Toprak nem sensörleri + Hava durumu uyduları + IoT bulut kontrolü",
            "Sulama zamanı: Şafak öncesi (buharlaşmanın en düşük olduğu saatler)",
            "Konya havzası saha deneyi: %35 su tasarrufu, %12 verim artışı",
            "Önemi: İklim krizinde tatlı su kaynaklarını korumak için şart"
        ],
        "questions": [
            {
                "id": "lis_b1_03_q1",
                "question": "Why does conventional flood irrigation result in severe water waste?",
                "options": [
                    {"key": "A", "text": "It requires expensive satellite subscriptions"},
                    {"key": "B", "text": "Up to fifty percent of water is lost to evaporation and runoff"},
                    {"key": "C", "text": "Plant roots cannot absorb untreated freshwater"},
                    {"key": "D", "text": "It damages underground electrical lines"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'Conventional flood irrigation is notoriously wasteful, losing up to fifty percent of water to surface evaporation and runoff' denilmiştir."
            },
            {
                "id": "lis_b1_03_q2",
                "question": "What were the empirical results of smart drip irrigation in the Konya basin trial?",
                "options": [
                    {"key": "A", "text": "Ten percent water savings with lower crop yield"},
                    {"key": "B", "text": "Thirty-five percent water reduction and twelve percent yield increase"},
                    {"key": "C", "text": "Complete soil salinization within six months"},
                    {"key": "D", "text": "Higher electricity costs with no water savings"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'diminish total agricultural water consumption by thirty-five percent while increasing crop yield by twelve percent' ifadesi geçer."
            }
        ]
    },
    {
        "id": "lis_b1_04",
        "university_id": "hacettepe",
        "level": "B1",
        "type": "while_listening",
        "title": "The Mechanism of Antibiotics and Bacterial Resistance",
        "subtitle": "Hacettepe Üniversitesi Tıp & Eczacılık Semineri",
        "target_university": "Hacettepe Üniversitesi",
        "duration_minutes": 10,
        "lecture_duration_seconds": 90,
        "instructions_tr": "Antibiyotiklerin çalışma mekanizması ve direnç sorununu dinleyip soruları cevaplayınız.",
        "audio_script": "In nineteen twenty-eight, Alexander Fleming serendipitously discovered penicillin, inaugurating the antibiotic era. Antibiotics function by selectively attacking cellular components unique to bacteria that are absent in human mammalian cells. For instance, beta-lactam antibiotics inhibit the synthesis of peptidoglycan, the rigid structural molecule that forms bacterial cell walls. Without this protective wall, osmotic pressure causes the bacterial cell to burst and die. However, widespread overprescription of antibiotics in veterinary livestock and clinical medicine has accelerated antibacterial resistance. Through spontaneous genetic mutation and horizontal gene transfer via plasmids, resistant bacterial strains produce enzymes like beta-lactamases that neutralize medical drugs. The World Health Organization warns that superbugs could cause ten million annual fatalities by 2050 unless novel antimicrobial therapies are developed.",
        "suggested_notes_tr": [
            "Keşif: Alexander Fleming (1928, Penisilin)",
            "Çalışma mekanizması: Peptidoglikan hücre duvarı sentezini engelleme -> Hücre patlar",
            "Direnç nedeni: Hayvancılık ve tıpta aşırı/gereksiz kullanım",
            "Direnç mekanizması: Genetik mutasyon, plazmidler ile gen aktarımı, beta-laktamaz enzimleri",
            "DSÖ uyarısı: 2050 yılına kadar yılda 10 milyon ölüm riski"
        ],
        "questions": [
            {
                "id": "lis_b1_04_q1",
                "question": "How do beta-lactam antibiotics selectively destroy bacterial cells without harming human cells?",
                "options": [
                    {"key": "A", "text": "By increasing intracellular glucose oxidation"},
                    {"key": "B", "text": "By inhibiting peptidoglycan cell wall synthesis"},
                    {"key": "C", "text": "By blocking human hormone receptors"},
                    {"key": "D", "text": "By generating high body fever"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'beta-lactam antibiotics inhibit the synthesis of peptidoglycan, the rigid structural molecule that forms bacterial cell walls' denilmiştir."
            },
            {
                "id": "lis_b1_04_q2",
                "question": "What is one major mechanism by which bacteria share resistance genes with each other?",
                "options": [
                    {"key": "A", "text": "Horizontal gene transfer via plasmids"},
                    {"key": "B", "text": "Airborne sound vibrations"},
                    {"key": "C", "text": "Thermal conduction in water"},
                    {"key": "D", "text": "Cellular respiration shutdown"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'Through spontaneous genetic mutation and horizontal gene transfer via plasmids' bilgisi verilmiştir."
            }
        ]
    },
    {
        "id": "lis_b1_05",
        "university_id": "ege",
        "level": "B1",
        "type": "while_listening",
        "title": "Geothermal Energy Development in Western Anatolia",
        "subtitle": "Ege Üniversitesi Jeotermal Enerji Dersi",
        "target_university": "Ege Üniversitesi",
        "duration_minutes": 10,
        "lecture_duration_seconds": 85,
        "instructions_tr": "Ege Bölgesi jeotermal enerji santralleri hakkındaki dersi dinleyiniz.",
        "audio_script": "Western Anatolia is one of the world's most tectonically active geothermal zones due to widespread continental extensional faulting along the Aegean graben systems. Deep subsurface reservoirs contain pressurized water superheated to over two hundred degrees Celsius by geothermal magma gradients. In binary-cycle power stations, this hydrothermal fluid is extracted through deep boreholes to vaporize a secondary working fluid with a lower boiling point, which drives electrical generation turbines. Crucially, contemporary environmental standards mandate complete closed-loop reinjection. Once the heat is extracted, the cooled mineralized brine must be pumped back into the subterranean reservoir to prevent surface river contamination and preserve aquifer pressure. Turkey is currently ranked fourth globally in installed geothermal electricity capacity.",
        "suggested_notes_tr": [
            "Jeolojik yapı: Ege graben sistemleri, tektonik fay hatları",
            "Sıcaklık: Yeraltında 200°C'yi aşan basınçlı hidrotermal akışkan",
            "İkili çevrim santralleri (Binary-cycle): İkincil akışkanı buharlaştırıp türbini çevirir",
            "Çevre kuralı: Kapalı devre geri basma (Reinjection) zorunlu",
            "Türkiye konumu: Dünyada kurulu güçte 4. sırada"
        ],
        "questions": [
            {
                "id": "lis_b1_05_q1",
                "question": "Why must cooled geothermal brine be reinjected into subterranean reservoirs?",
                "options": [
                    {"key": "A", "text": "To increase surface river acidity for farming"},
                    {"key": "B", "text": "To prevent surface river contamination and sustain aquifer pressure"},
                    {"key": "C", "text": "To stop local tectonic earthquakes immediately"},
                    {"key": "D", "text": "To generate hydrogen fuel at the surface"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'cooled mineralized brine must be pumped back into the subterranean reservoir to prevent surface river contamination and preserve aquifer pressure' denilmiştir."
            },
            {
                "id": "lis_b1_05_q2",
                "question": "What is Turkey's global ranking in installed geothermal power capacity?",
                "options": [
                    {"key": "A", "text": "First"},
                    {"key": "B", "text": "Fourth"},
                    {"key": "C", "text": "Tenth"},
                    {"key": "D", "text": "Twentieth"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'Turkey is currently ranked fourth globally in installed geothermal electricity capacity' cümlesi mevcuttur."
            }
        ]
    },
    {
        "id": "lis_b1_06",
        "university_id": "gazi",
        "level": "B1",
        "type": "while_listening",
        "title": "Cybersecurity Architecture and Phishing Defenses",
        "subtitle": "Gazi Üniversitesi Bilişim Güvenliği Dersi",
        "target_university": "Gazi Üniversitesi",
        "duration_minutes": 10,
        "lecture_duration_seconds": 85,
        "instructions_tr": "Siber saldırı yöntemleri ve kimlik avı korumasını dinleyip soruları cevaplayınız.",
        "audio_script": "In contemporary information security, social engineering attacks such as phishing remain the single most pervasive vector for corporate data breaches. Rather than attempting to crack complex cryptographic firewalls, malicious actors exploit human cognitive heuristics through deception. A typical spear-phishing email mimics an urgent communication from a university administrator or banking official, prompting the recipient to click a fraudulent hyperlink and input credentials. Robust organizational cybersecurity requires a multi-layered defense model. First, machine-learning email filters analyze sender domain signatures and quarantine suspicious attachments. Second, mandating multi-factor authentication ensures that stolen passwords alone are insufficient to compromise accounts. Finally, regular employee simulation drills build institutional vigilance against social manipulation.",
        "suggested_notes_tr": [
            "Kimlik avı (Phishing): Sosyal mühendislik ve insan zaafını hedef alır",
            "Mekanizma: Acil durum izlenimi veren sahte kurumsal e-posta ile şifre çalma",
            "Çok katmanlı savunma:",
            "1. Makine öğrenimli alan adı ve ek tarama filtreleri",
            "2. Çok faktörlü kimlik doğrulama (MFA - Multi-factor auth)",
            "3. Düzenli personel simülasyon eğitimleri"
        ],
        "questions": [
            {
                "id": "lis_b1_06_q1",
                "question": "Why is multi-factor authentication (MFA) considered an essential defense against phishing?",
                "options": [
                    {"key": "A", "text": "It permanently deletes fraudulent emails from servers"},
                    {"key": "B", "text": "Stolen passwords alone are insufficient to access accounts"},
                    {"key": "C", "text": "It prevents computers from connecting to the internet"},
                    {"key": "D", "text": "It eliminates the need for software updates"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'mandating multi-factor authentication ensures that stolen passwords alone are insufficient to compromise accounts' denilmiştir."
            },
            {
                "id": "lis_b1_06_q2",
                "question": "What primary vulnerability do social engineering attacks exploit?",
                "options": [
                    {"key": "A", "text": "Physical hardware cable damage"},
                    {"key": "B", "text": "Human cognitive heuristics and trust"},
                    {"key": "C", "text": "Satellite weather interference"},
                    {"key": "D", "text": "Outdated screen monitors"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'malicious actors exploit human cognitive heuristics through deception' ifadesi geçer."
            }
        ]
    },
    {
        "id": "lis_b1_07",
        "university_id": "itu",
        "level": "B1",
        "type": "while_listening",
        "title": "Satellite Earth Observation and Environmental Monitoring",
        "subtitle": "İTÜ Uzay ve Uydu Mühendisliği Semineri",
        "target_university": "İstanbul Teknik Üniversitesi",
        "duration_minutes": 10,
        "lecture_duration_seconds": 90,
        "instructions_tr": "Uydularla Dünya gözlemi ve çevre izleme teknolojisini dinleyin.",
        "audio_script": "Earth observation satellites operating in low Earth orbit provide critical spatial telemetry for tracking planetary climate shifts. Optical multi-spectral sensors capture sunlight reflected from the Earth's surface across various electromagnetic wavelengths, including invisible near-infrared bands. Because healthy plant chlorophyll absorbs red light while strongly reflecting near-infrared radiation, agronomists calculate the Normalized Difference Vegetation Index (NDVI) to assess regional crop drought stress and forest canopy health. In addition to optical cameras, synthetic aperture radar satellites can penetrate thick cloud cover and nighttime darkness, measuring ground deformation down to millimeter precision. This radar capability allows civil engineers to detect subtle tectonic subsidence around major bridges, dams, and municipal aquifers before catastrophic failures occur.",
        "suggested_notes_tr": [
            "Yörünge: Alçak Dünya Yörüngesi (Low Earth Orbit - LEO)",
            "Çok bantlı optik sensörler: Kızılötesi ve görünür ışık dalga boyları",
            "NDVI İndeksi: Klorofil kırmızı ışığı emer, yakın kızılötesini yansıtır -> Kuraklık/orman sağlığı takibi",
            "Sentetik Açıklıklı Radar (SAR): Bulut ve gece fark etmeksizin milimetrik yer çökmesini tespit eder"
        ],
        "questions": [
            {
                "id": "lis_b1_07_q1",
                "question": "How does the Normalized Difference Vegetation Index (NDVI) detect healthy plant growth?",
                "options": [
                    {"key": "A", "text": "By measuring microwave radiation from tree bark"},
                    {"key": "B", "text": "By calculating the ratio between absorbed red light and reflected near-infrared"},
                    {"key": "C", "text": "By detecting nitrogen gas release from leaves"},
                    {"key": "D", "text": "By measuring soil temperature variations"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'healthy plant chlorophyll absorbs red light while strongly reflecting near-infrared radiation, agronomists calculate the Normalized Difference Vegetation Index' denilmiştir."
            },
            {
                "id": "lis_b1_07_q2",
                "question": "What is the primary advantage of synthetic aperture radar (SAR) satellites?",
                "options": [
                    {"key": "A", "text": "They operate without battery power"},
                    {"key": "B", "text": "They can penetrate cloud cover and darkness to measure millimeter ground deformation"},
                    {"key": "C", "text": "They predict earthquakes months in advance"},
                    {"key": "D", "text": "They replace all ground weather stations"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'synthetic aperture radar satellites can penetrate thick cloud cover and nighttime darkness, measuring ground deformation down to millimeter precision' bilgisi verilir."
            }
        ]
    },
    {
        "id": "lis_b1_08",
        "university_id": "ytu",
        "level": "B1",
        "type": "while_listening",
        "title": "Autonomous Drones in Post-Disaster Search and Rescue",
        "subtitle": "YTÜ Mekatronik ve Robotik Dersi",
        "target_university": "Yıldız Teknik Üniversitesi",
        "duration_minutes": 10,
        "lecture_duration_seconds": 85,
        "instructions_tr": "Afet sonrası arama kurtarmada insansız hava araçlarının rolünü dinleyin.",
        "audio_script": "Following major seismic disasters, the first seventy-two hours represent the golden window for rescuing victims trapped beneath structural rubble. However, collapsed infrastructure often prevents human rescue teams and heavy vehicles from reaching devastated urban zones. Autonomous unmanned aerial vehicles equipped with thermal imaging cameras and acoustic sensors can rapidly survey disaster perimeters. Thermal infrared sensors detect human body heat signatures even under concrete debris or at night, transmitting precise GPS coordinates to response commanders. Furthermore, lightweight drone swarms can deploy temporary cellular mesh communications, enabling trapped survivors to send emergency signals from their smartphones. Robotic reconnaissance minimizes search times while keeping emergency responders safe from secondary aftershock collapses.",
        "suggested_notes_tr": [
            "İlk 72 saat: 'Altın saatler' (En kritik kurtarma penceresi)",
            "İHA Donanımı: Termal kızılötesi kameralar ve akustik sensörler",
            "Termal algılama: Beton moloz altındaki ve geceki vücut ısısını tespit edip GPS koordinatı gönderir",
            "Hücresel ağ: İHA sürüleri geçici hücresel ağ kurarak telefon sinyali almayı sağlar"
        ],
        "questions": [
            {
                "id": "lis_b1_08_q1",
                "question": "What critical capability do thermal infrared sensors provide during post-earthquake search operations?",
                "options": [
                    {"key": "A", "text": "They clear collapsed concrete walls automatically"},
                    {"key": "B", "text": "They detect human body heat signatures beneath debris and in darkness"},
                    {"key": "C", "text": "They purify contaminated city drinking water"},
                    {"key": "D", "text": "They repair electrical grid cables"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'Thermal infrared sensors detect human body heat signatures even under concrete debris or at night' denilmiştir."
            },
            {
                "id": "lis_b1_08_q2",
                "question": "How can drone swarms reestablish contact with survivors when city antennas collapse?",
                "options": [
                    {"key": "A", "text": "By dropping paper maps into streets"},
                    {"key": "B", "text": "By establishing temporary cellular mesh networks for smartphones"},
                    {"key": "C", "text": "By emitting high-frequency acoustic sirens"},
                    {"key": "D", "text": "By using laser projection on clouds"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'deploy temporary cellular mesh communications, enabling trapped survivors to send emergency signals from their smartphones' ifadesi mevcuttur."
            }
        ]
    },
    {
        "id": "lis_b1_09",
        "university_id": "koc",
        "level": "B1",
        "type": "while_listening",
        "title": "The Psychology of Consumer Brand Attachment",
        "subtitle": "Koç Üniversitesi Davranışsal Pazarlama Semineri",
        "target_university": "Koç Üniversitesi",
        "duration_minutes": 10,
        "lecture_duration_seconds": 85,
        "instructions_tr": "Tüketicilerin markalara duygusal bağlılık geliştirmesinin psikolojik temellerini dinleyin.",
        "audio_script": "In behavioral marketing, brand attachment refers to the emotional bond connecting a consumer's personal self-identity with a specific commercial brand. Cognitive psychologists have demonstrated that consumers do not evaluate products solely on utilitarian attributes like price or functionality. Rather, brands function as psychological symbols through which individuals express their ideal self-concept and social group belonging. When a brand embodies values that mirror an individual's personal ethics—such as environmental sustainability or technological innovation—consumers develop intense emotional loyalty. Neurological imaging scans indicate that loyal consumers exhibit brain activation patterns in regions associated with interpersonal affection when viewing preferred brand logos, making them highly resistant to switching to competitors despite price increases.",
        "suggested_notes_tr": [
            "Marka bağlılığı: Tüketici kimliği ile marka arasındaki duygusal bağ",
            "Rasyonellik ötesi: Tüketiciler sadece fiyat ve işleve bakmaz; ideal benliklerini markayla ifade eder",
            "Nörolojik bulgu: Sadık tüketicilerin beyin taramalarında sevgi ve şefkat merkezleri aktive olur",
            "Sonuç: Fiyat artışına rağmen rakip markaya geçişe direnç gösterirler"
        ],
        "questions": [
            {
                "id": "lis_b1_09_q1",
                "question": "Why do consumers often remain loyal to specific brands despite higher prices?",
                "options": [
                    {"key": "A", "text": "There are no alternative products available in stores"},
                    {"key": "B", "text": "Brands serve as psychological extensions of their personal identity and values"},
                    {"key": "C", "text": "Consumers are legally obligated by purchase contracts"},
                    {"key": "D", "text": "Advertising laws forbid price comparisons"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'brands function as psychological symbols through which individuals express their ideal self-concept and social group belonging' denilmiştir."
            },
            {
                "id": "lis_b1_09_q2",
                "question": "What do neuroimaging studies reveal about consumers viewing preferred brand logos?",
                "options": [
                    {"key": "A", "text": "Activation in neural regions associated with interpersonal affection"},
                    {"key": "B", "text": "Sudden drops in auditory brain processing"},
                    {"key": "C", "text": "Complete deactivation of long-term memory"},
                    {"key": "D", "text": "Elevated physical pain responses"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'exhibit brain activation patterns in regions associated with interpersonal affection when viewing preferred brand logos' bilgisi verilir."
            }
        ]
    },
    {
        "id": "lis_b1_10",
        "university_id": "sabanci",
        "level": "B1",
        "type": "while_listening",
        "title": "Nanotechnology and Graphene Water Filtration",
        "subtitle": "Sabancı Üniversitesi Malzeme Mühendisliği",
        "target_university": "Sabancı Üniversitesi",
        "duration_minutes": 10,
        "lecture_duration_seconds": 90,
        "instructions_tr": "Grafen nanotüpler ve su arıtma teknolojilerini dinleyip soruları cevaplayın.",
        "audio_script": "Access to clean drinking water is one of the most critical challenges of the twenty-first century. Traditional reverse osmosis desalination requires massive electrical energy to force seawater through dense polymer membranes at high hydrostatic pressures. However, materials scientists are revolutionizing water purification through graphene oxide membranes. Graphene, an atomic monolayer of carbon atoms arranged in a hexagonal lattice, possesses unprecedented tensile strength and chemical resistance. When perforated with sub-nanometer pores, graphene membranes allow water molecules to permeate at extraordinary velocities while completely obstructing larger dissolved sodium and chloride salt ions. Laboratory trials indicate that graphene filtration could reduce the energy consumption of industrial seawater desalination by up to fifty percent, making clean water accessible to arid coastal regions globally.",
        "suggested_notes_tr": [
            "Geleneksel Ters Osmoz (Reverse Osmosis): Çok yüksek enerji ve basınç gerektirir",
            "Grafen oksit membranlar: Tek atom kalınlığında karbon, altıgen örgü yapısı",
            "Çalışma prensibi: Milimetrenin milyonda biri gözeneklerden su molekülleri geçer, tuz (Na/Cl) iyonları bloke edilir",
            "Avantaj: Tuzdan arındırmada enerji tüketimini %50'ye kadar düşürebilir"
        ],
        "questions": [
            {
                "id": "lis_b1_10_q1",
                "question": "What structural feature of graphene oxide membranes allows them to desalinate seawater?",
                "options": [
                    {"key": "A", "text": "Thick layers of absorbent cotton fibers"},
                    {"key": "B", "text": "Sub-nanometer pores that permit water molecules while blocking salt ions"},
                    {"key": "C", "text": "Electric currents that evaporate seawater instantly"},
                    {"key": "D", "text": "Chemical chlorine additives embedded in the lattice"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'When perforated with sub-nanometer pores, graphene membranes allow water molecules to permeate at extraordinary velocities while completely obstructing larger dissolved sodium and chloride salt ions' denilmiştir."
            },
            {
                "id": "lis_b1_10_q2",
                "question": "By how much could graphene membranes reduce the energy consumption of industrial desalination?",
                "options": [
                    {"key": "A", "text": "By five percent"},
                    {"key": "B", "text": "By up to fifty percent"},
                    {"key": "C", "text": "By ninety-nine percent"},
                    {"key": "D", "text": "No energy savings are expected"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'reduce the energy consumption of industrial seawater desalination by up to fifty percent' ifadesi mevcuttur."
            }
        ]
    }
]

print(f"Compiled B1 tracks: {len(B1_TRACKS)}")
