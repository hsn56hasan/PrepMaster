# -*- coding: utf-8 -*-
"""
Curated listening track database for B2, C1, and C2 levels.
Total: 20 tracks (6 for B2, 6 for C1, 8 for C2).
"""

B2_TRACKS = [
    {
        "id": "lis_b2_05",
        "university_id": "metu",
        "level": "B2",
        "type": "note_taking",
        "title": "Microplastics in Marine Trophic Chains",
        "subtitle": "ODTÜ Çevre Mühendisliği ve Oşinografi Dersi",
        "target_university": "Orta Doğu Teknik Üniversitesi",
        "duration_minutes": 12,
        "lecture_duration_seconds": 95,
        "instructions_tr": "Bu bir Note-Taking sınavıdır. Dinleme esnasında not defterine ana fikirleri ve sayısal verileri kaydediniz; ardından soruları yanıtlayınız.",
        "audio_script": "Good morning. In today's marine biology seminar, we examine the ecotoxicological dynamics of microplastics across aquatic food webs. Microplastics, defined as synthetic polymer fragments under five millimeters in diameter, originate from two primary sources: primary microbeads manufactured for industrial cosmetics, and secondary fragments generated via mechanical weathering and solar ultraviolet photolysis of discarded packaging. Once washed into marine environments, buoyant microplastics adsorb hydrophobic organic pollutants, such as polychlorinated biphenyls and DDT, from surrounding seawater at concentrations up to a million times higher than ambient levels. Filter-feeding zooplankton indiscriminately ingest these toxin-coated synthetic particles, mistakenly treating them as organic phytoplankton. As apex marine predators like tuna and swordfish consume thousands of contaminated prey species, chemical toxins bioaccumulate and biomagnify up the trophic pyramid, ultimately reaching human seafood consumers and inducing endocrine disruption.",
        "suggested_notes_tr": [
            "Mikroplastik tanımı: 5 mm'den küçük polimer parçacıkları",
            "Birincil vs. İkincil kaynaklar: Kozmetik mikrotanecikleri vs. Güneş ve mekanik aşınmayla parçalanan ambalajlar",
            "Toksik adsorpsiyon: Çevre suyundan PCB ve DDT gibi kirleticileri 1 milyon kat konsantrasyonda emer",
            "Trofik basamaklar: Zooplankton -> Balıklar -> Apex avcılar (Ton balığı) -> İnsan",
            "Biyoakümülasyon ve Biyomagnifikasyon: Besin zincirinde zehir yoğunlaşır, endokrin sistemi bozar"
        ],
        "questions": [
            {
                "id": "lis_b2_05_q1",
                "question": "What is the defining particle size limit for microplastics?",
                "options": [
                    {"key": "A", "text": "Under five millimeters in diameter"},
                    {"key": "B", "text": "Over ten centimeters"},
                    {"key": "C", "text": "Visible only under electron microscopes"},
                    {"key": "D", "text": "Under one nanometer"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'defined as synthetic polymer fragments under five millimeters in diameter' denilmiştir."
            },
            {
                "id": "lis_b2_05_q2",
                "question": "Why do microplastics pose an amplified chemical toxicity risk to marine organisms?",
                "options": [
                    {"key": "A", "text": "They evaporate and increase water salinity"},
                    {"key": "B", "text": "They adsorb hydrophobic organic pollutants at concentrations a million times above ambient seawater"},
                    {"key": "C", "text": "They emit nuclear gamma rays"},
                    {"key": "D", "text": "They freeze ocean surface currents"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'adsorb hydrophobic organic pollutants ... at concentrations up to a million times higher than ambient levels' denilmiştir."
            }
        ]
    },
    {
        "id": "lis_b2_06",
        "university_id": "bilkent",
        "level": "B2",
        "type": "note_taking",
        "title": "Behavioral Economics and Choice Architecture",
        "subtitle": "Bilkent COPE Tarzı Note-Taking Sınavı",
        "target_university": "Bilkent Üniversitesi",
        "duration_minutes": 12,
        "lecture_duration_seconds": 95,
        "instructions_tr": "Davranışsal iktisat ve 'Dürtme' (Nudge) teorisini dinleyerek not alınız.",
        "audio_script": "Traditional neoclassical economics rested upon the premise of Homo economicus—an idealized human agent possessing infinite cognitive capacity and relentless rationality. However, behavioral economists Richard Thaler and Cass Sunstein proved that human decision-making is systematically bounded by cognitive heuristics, emotional biases, and inertia. To improve social outcomes without coercive mandates, they formulated 'nudge theory' and choice architecture. A nudge alters the context in which individuals make choices without forbidding any options or altering economic incentives. For example, in organ donation policy, countries operating under opt-in systems—where citizens must actively sign a donor card—exhibit consent rates around fifteen percent. Conversely, in opt-out regimes, where citizens are automatically registered as organ donors unless they explicitly check a box to decline, consent rates exceed ninety percent. Simply altering the default choice leverages human status-quo inertia to save thousands of lives.",
        "suggested_notes_tr": [
            "Homo economicus eleştirisi: İnsanlar kusursuz rasyonel değil; önyargı ve eylemsizlik (inertia) sahibidir",
            "Nudge (Dürtme) Teorisi: Thaler & Sunstein. Seçenekleri yasaklamadan karar bağlamını düzenleme (Choice architecture)",
            "Organ bağışı örneği:",
            "  - Opt-in (katılmak için form doldur): %15 rıza",
            "  - Opt-out (otomatik kayıtlı, istemeyen çıkar): %90+ rıza",
            "Sonuç: Varsayılan (default) seçeneği değiştirmek insan eylemsizliğini kamu yararına dönüştürür"
        ],
        "questions": [
            {
                "id": "lis_b2_06_q1",
                "question": "How does 'nudge theory' influence human decision-making?",
                "options": [
                    {"key": "A", "text": "By imposing heavy financial criminal penalties"},
                    {"key": "B", "text": "By altering choice architecture without forbidding options or changing economic payoffs"},
                    {"key": "C", "text": "By eliminating all consumer choices entirely"},
                    {"key": "D", "text": "By broadcasting mandatory television propaganda"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'alters the context in which individuals make choices without forbidding any options or altering economic incentives' denilmiştir."
            },
            {
                "id": "lis_b2_06_q2",
                "question": "Why do opt-out organ donation policies achieve consent rates exceeding ninety percent?",
                "options": [
                    {"key": "A", "text": "Citizens receive monthly tax deductions"},
                    {"key": "B", "text": "They leverage human status-quo bias and inertia as the default setting"},
                    {"key": "C", "text": "Citizens are threatened with legal prosecution"},
                    {"key": "D", "text": "Doctors choose donors randomly without patient consent"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'Simply altering the default choice leverages human status-quo inertia to save thousands of lives' ifadesi yer alır."
            }
        ]
    },
    {
        "id": "lis_b2_07",
        "university_id": "boun",
        "level": "B2",
        "type": "while_listening",
        "title": "Quantum Computing: Superposition and Entanglement",
        "subtitle": "Boğaziçi Üniversitesi Kuantum Bilişim Dersi",
        "target_university": "Boğaziçi Üniversitesi",
        "duration_minutes": 12,
        "lecture_duration_seconds": 90,
        "instructions_tr": "Kuantum bilgisayarların temel ilkelerini dinleyip soruları cevaplayınız.",
        "audio_script": "Classical digital computers store and process information in binary digits, or bits, which exist strictly in one of two deterministic states: zero or one. Quantum computers, by contrast, utilize quantum bits, or qubits, which harness the bizarre principles of quantum mechanics. The first fundamental principle is quantum superposition. Thanks to wave-particle duality, a qubit can exist in a linear combination of both zero and one simultaneously until a physical measurement collapses its wavefunction. This allows a quantum processor containing three hundred qubits to represent more computational states simultaneously than there are atoms in the observable universe. The second principle is quantum entanglement, an interconnected state where the measurement of one qubit instantaneously determines the state of its paired partner, regardless of physical separation. Together, superposition and entanglement enable quantum algorithms to solve complex molecular simulations and factor massive prime numbers exponentially faster than classical supercomputers.",
        "suggested_notes_tr": [
            "Klasik bit vs. Kuantum kübiti (qubit): 0 veya 1 deterministik vs. Süperpozisyon",
            "Kuantum süperpozisyon: Ölçüm yapılana kadar aynı anda 0 ve 1 durumunda bulunabilme",
            "Kapasite: 300 kübit, evrendeki atom sayısından daha fazla durumu aynı anda temsil edebilir",
            "Kuantum dolanıklık (Entanglement): Birbirinden bağımsız iki kübitin anında birbirinin durumunu belirlemesi",
            "Uygulamalar: Moleküler simülasyonlar, asallara ayırma, şifre kırma"
        ],
        "questions": [
            {
                "id": "lis_b2_07_q1",
                "question": "What allows a quantum qubit to represent multiple states simultaneously?",
                "options": [
                    {"key": "A", "text": "Higher electrical voltage inside copper wires"},
                    {"key": "B", "text": "The principle of quantum superposition"},
                    {"key": "C", "text": "Liquid cooling fans"},
                    {"key": "D", "text": "Classical binary logic gates"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'The first fundamental principle is quantum superposition ... a qubit can exist in a linear combination of both zero and one simultaneously' denilmiştir."
            },
            {
                "id": "lis_b2_07_q2",
                "question": "How does quantum entanglement link paired qubits?",
                "options": [
                    {"key": "A", "text": "Through physical fiber-optic cables"},
                    {"key": "B", "text": "Measuring one qubit instantaneously determines the state of its partner across space"},
                    {"key": "C", "text": "By increasing mechanical resistance between processors"},
                    {"key": "D", "text": "By synchronizing their battery recharge cycles"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'measurement of one qubit instantaneously determines the state of its paired partner, regardless of physical separation' bilgisi verilir."
            }
        ]
    },
    {
        "id": "lis_b2_08",
        "university_id": "itu",
        "level": "B2",
        "type": "while_listening",
        "title": "Urban Heat Islands and Bioclimatic Architecture",
        "subtitle": "İTÜ Mimarlık ve Şehir Planlama Semineri",
        "target_university": "İstanbul Teknik Üniversitesi",
        "duration_minutes": 12,
        "lecture_duration_seconds": 90,
        "instructions_tr": "Kentsel ısı adası etkisi ve biyoklimatik mimari çözümlerini dinleyin.",
        "audio_script": "The urban heat island phenomenon occurs when metropolitan centers experience ambient air temperatures several degrees higher than surrounding rural peripheries. This thermal disparity stems from modern urban morphology: dark asphalt roadways and dense concrete structures possess high thermal mass and low albedo, absorbing solar radiation during peak daylight and reradiating sensible heat well into the night. Furthermore, tall skyscrapers create deep urban canyons that trap anthropogenic heat emitted by vehicular combustion and air conditioning units. Bioclimatic architects mitigate this thermal trap through passive environmental engineering. First, retrofitting building roofs with high-albedo cool paints and intensive vegetative green roofs reduces surface absorption and promotes evapotranspirative cooling. Second, designing municipal street orientations to align with prevailing sea breezes ventilates trapped pollutants, lowering city center temperatures by up to four degrees Celsius.",
        "suggested_notes_tr": [
            "Kentsel Isı Adası (UHI): Şehir merkezlerinin kırsala göre birkaç derece daha sıcak olması",
            "Nedenleri: Düşük albedo (yansıtma) ve yüksek termal kütleye sahip koyu asfalt ve beton; klima ve egzoz ısısı",
            "Kentsel kanyonlar: Gökdelenlerin rüzgarı kesmesi ve ısıyı hapsetmesi",
            "Biyoklimatik çözümler:",
            "  1. Yüksek albedolu boyalar ve yeşil çatılar (Evapotranspirasyon ile soğutma)",
            "  2. Sokak yönelimini hakim rüzgarlara göre ayarlayarak doğal havalandırma (4°C'ye kadar düşüş)"
        ],
        "questions": [
            {
                "id": "lis_b2_08_q1",
                "question": "What material characteristic of asphalt and concrete exacerbates the urban heat island effect?",
                "options": [
                    {"key": "A", "text": "Excessive water transparency"},
                    {"key": "B", "text": "Low albedo and high thermal heat retention"},
                    {"key": "C", "text": "High electrical conductivity"},
                    {"key": "D", "text": "Frequent chemical combustion"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'dark asphalt roadways and dense concrete structures possess high thermal mass and low albedo, absorbing solar radiation' denilmiştir."
            },
            {
                "id": "lis_b2_08_q2",
                "question": "How do vegetative green roofs contribute to urban cooling?",
                "options": [
                    {"key": "A", "text": "By reflecting radar signals"},
                    {"key": "B", "text": "Through evapotranspirative cooling and reduced solar heat absorption"},
                    {"key": "C", "text": "By absorbing city noise pollution exclusively"},
                    {"key": "D", "text": "By generating artificial wind currents"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'vegetative green roofs reduces surface absorption and promotes evapotranspirative cooling' ifadesi yer alır."
            }
        ]
    },
    {
        "id": "lis_b2_09",
        "university_id": "ankara",
        "level": "B2",
        "type": "while_listening",
        "title": "Biofuels: First vs. Second Generation Bioethanol",
        "subtitle": "Ankara Üniversitesi Kimya Mühendisliği Dersi",
        "target_university": "Ankara Üniversitesi",
        "duration_minutes": 12,
        "lecture_duration_seconds": 90,
        "instructions_tr": "Birinci ve ikinci nesil biyoyakıtların farklarını dinleyiniz.",
        "audio_script": "As nations strive to decarbonize transportation, liquid biofuels have emerged as critical transition fuels. However, there is a fundamental technological and ethical division between first and second-generation biofuels. First-generation bioethanol is derived from edible food crops, such as sugarcane and corn, by fermenting simple starch sugars. While technologically straightforward, this sparked the 'food versus fuel' debate, as diverting arable farmland toward ethanol production precipitated global grain price inflation and deforestation. In contrast, second-generation advanced biofuels utilize non-food lignocellulosic biomass, including agricultural residues like wheat straw, corn husks, and dedicated energy grasses. Breaking down resilient lignocellulose requires complex enzymatic hydrolysis and specialized microbial fermentation, but it avoids competition with human food supplies while generating eighty percent fewer greenhouse emissions than petroleum.",
        "suggested_notes_tr": [
            "Birinci nesil: Mısır, şeker kamışı gibi yenilebilir gıda ürünlerinden üretilir",
            "Sorun: 'Gıda vs. Yakıt' krizi, gıda enflasyonu ve tarım arazisi rekabeti",
            "İkinci nesil: Lignoselülozik atıklar (buğday samanı, mısır koçanı, odunsu artıklar)",
            "Üretim süreci: Enzimatik hidroliz ve mikrobiyal fermantasyon",
            "Avantaj: Gıda arzını tehdit etmez, petrole göre %80 daha az sera gazı salımı"
        ],
        "questions": [
            {
                "id": "lis_b2_09_q1",
                "question": "What major ethical dilemma arose from first-generation bioethanol production?",
                "options": [
                    {"key": "A", "text": "Excessive nuclear radiation in crop soils"},
                    {"key": "B", "text": "The 'food versus fuel' conflict causing grain price spikes and food insecurity"},
                    {"key": "C", "text": "Engines corroding within twenty-four hours"},
                    {"key": "D", "text": "Severe shortages of copper catalyst metals"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'sparked the food versus fuel debate, as diverting arable farmland toward ethanol production precipitated global grain price inflation' denilmiştir."
            },
            {
                "id": "lis_b2_09_q2",
                "question": "What feedstock is utilized in second-generation advanced biofuels?",
                "options": [
                    {"key": "A", "text": "Refined white sugar exclusively"},
                    {"key": "B", "text": "Non-edible lignocellulosic agricultural residues and energy grasses"},
                    {"key": "C", "text": "Purified petroleum distillates"},
                    {"key": "D", "text": "Dairy milk proteins"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'second-generation advanced biofuels utilize non-food lignocellulosic biomass, including agricultural residues like wheat straw' bilgisi mevcuttur."
            }
        ]
    },
    {
        "id": "lis_b2_10",
        "university_id": "hacettepe",
        "level": "B2",
        "type": "while_listening",
        "title": "Corporate Governance and Whistleblower Protections",
        "subtitle": "Hacettepe Üniversitesi Hukuk ve İş Etiği",
        "target_university": "Hacettepe Üniversitesi",
        "duration_minutes": 12,
        "lecture_duration_seconds": 90,
        "instructions_tr": "Şirket içi ihbarcılık (whistleblowing) ve hukuk mekanizmalarını dinleyin.",
        "audio_script": "Corporate whistleblower mechanisms represent an indispensable pillar of modern institutional integrity. When executives engage in accounting fraud, toxic waste dumping, or product safety concealment, external government regulators often lack internal visibility. Employees working within the firm possess granular first-hand evidence of systemic malfeasance. However, prospective whistleblowers face acute retaliation risks, including immediate termination, industry blacklisting, and civil lawsuits for disclosing trade secrets. Modern corporate governance frameworks, such as the Sarbanes-Oxley Act and European Union whistleblower directives, establish robust legal shields. These laws mandate confidential anonymous reporting channels, enforce punitive statutory damages against employers who retaliate, and occasionally award financial bounties to informants whose disclosures prevent massive fraud against investors.",
        "suggested_notes_tr": [
            "İhbarcı (Whistleblower): Şirket içi yolsuzluğu, sahtekarlığı veya çevre suçunu ifşa eden çalışan",
            "Karşılaşılan riskler: İşten kovulma, sektörde kara listeye alınma, ticari sır davaları",
            "Hukuki korumalar (Sarbanes-Oxley, AB direktifleri):",
            "  - Gizli ve anonim ihbar kanalları",
            "  - Misilleme yapan işverene ağır tazminat cezaları",
            "  - Finansal ödül (bounty) sistemleri"
        ],
        "questions": [
            {
                "id": "lis_b2_10_q1",
                "question": "Why do internal employees play a vital role in detecting corporate malfeasance?",
                "options": [
                    {"key": "A", "text": "They have full authority to rewrite corporate bylaws"},
                    {"key": "B", "text": "They possess first-hand granular evidence invisible to external regulators"},
                    {"key": "C", "text": "They own majority shareholder votes"},
                    {"key": "D", "text": "They are exempt from all federal tax laws"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'Employees working within the firm possess granular first-hand evidence of systemic malfeasance' denilmiştir."
            },
            {
                "id": "lis_b2_10_q2",
                "question": "Which legal protection is mandated by modern whistleblower directives?",
                "options": [
                    {"key": "A", "text": "Mandatory public television interviews"},
                    {"key": "B", "text": "Confidential anonymous reporting channels and shields against employer retaliation"},
                    {"key": "C", "text": "Instant promotion to the board of directors"},
                    {"key": "D", "text": "Automatic transfer to a government agency"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'These laws mandate confidential anonymous reporting channels, enforce punitive statutory damages against employers who retaliate' denilmiştir."
            }
        ]
    }
]

# --- C1 TRACKS (6 TRACKS) ---
C1_TRACKS = [
    {
        "id": "lis_c1_05",
        "university_id": "boun",
        "level": "C1",
        "type": "note_taking",
        "title": "Algorithmic Echo Chambers and Democratic Polarization",
        "subtitle": "Boğaziçi BUEPT Tarzı Note-Taking Sınavı",
        "target_university": "Boğaziçi Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 105,
        "instructions_tr": "Bu bir Note-Taking sınavıdır. Dinleme esnasında sorular gizlidir. Aşağıdaki dijital not defterine kavramları not alınız; dinleme bittikten sonra soruları açıp yanıtlayınız.",
        "audio_script": "Good morning. Today we examine the epistemological crisis triggered by algorithmic information filtering in digital public spheres. Contemporary social media platforms operate upon surveillance capitalism business models: user attentional retention is the primary monetizable commodity. To maximize engagement metrics, recommendation algorithms prioritize content that triggers intense visceral arousal, particularly righteous moral indignation. When users interact with sensationalist partisan posts, the neural ranking system constructs an epistemological filter bubble. The algorithm systematically conceals nuanced moderate discourse while inundating the user with affirming ideological narratives. This generates epistemic echo chambers where confirmation bias operates unimpeded. Sociological studies at Harvard demonstrate that this algorithmic tribalism destroys the shared empirical baseline necessary for democratic deliberation. When citizens of a republic cannot agree upon verified scientific or historical facts, governance degenerates into affective polarization where opposing factions view each other not as political rivals, but as existential threats to the body politic.",
        "suggested_notes_tr": [
            "Gözetim Kapitalizmi (Surveillance Capitalism): Kullanıcı dikkati paraya dönüştürülen ana metadır",
            "Algoritmik öncelik: Ahlaki öfke (moral indignation) ve duygusal uyarılmayı tetikleyen içerikler öne çıkarılır",
            "Filtre balonu ve Yankı odası: Karşıt/ılımlı görüşler gizlenir, yanlı içerikler sürekli beslenir",
            "Demokratik kriz: Ortak ampirik gerçeklik zemini yok olur; siyasi rakipler varoluşsal düşman olarak algılanır"
        ],
        "questions": [
            {
                "id": "lis_c1_05_q1",
                "question": "According to the lecturer, what type of emotional arousal do social media recommendation algorithms preferentially amplify to maximize user retention?",
                "options": [
                    {"key": "A", "text": "Tranquil intellectual reflection"},
                    {"key": "B", "text": "Righteous moral indignation and visceral outrage"},
                    {"key": "C", "text": "Artistic melancholy"},
                    {"key": "D", "text": "Mathematical skepticism"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'recommendation algorithms prioritize content that triggers intense visceral arousal, particularly righteous moral indignation' denilmiştir."
            },
            {
                "id": "lis_c1_05_q2",
                "question": "What is the primary societal consequence when algorithmic filter bubbles destroy a shared empirical baseline?",
                "options": [
                    {"key": "A", "text": "Rapid deflation of corporate tech stocks"},
                    {"key": "B", "text": "Democratic governance degenerates into acute affective polarization"},
                    {"key": "C", "text": "Higher voter turnout across all demographics"},
                    {"key": "D", "text": "Decreased municipal broadband infrastructure spending"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'destroys the shared empirical baseline ... governance degenerates into affective polarization' ifadesi geçer."
            }
        ]
    },
    {
        "id": "lis_c1_06",
        "university_id": "hacettepe",
        "level": "C1",
        "type": "note_taking",
        "title": "Neuroplasticity and Synaptic Consolidation in Sleep",
        "subtitle": "Hacettepe Üniversitesi Nörobilim Dersi",
        "target_university": "Hacettepe Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 105,
        "instructions_tr": "Nöroplastisite ve uykuda hafıza pekiştirme dersini dinleyip not alınız.",
        "audio_script": "For centuries, the human brain was conceptualized as a static, immutable anatomical apparatus once biological adulthood was reached. Modern neurobiology has demolished this dogma through the paradigm of neuroplasticity—the nervous system's capacity to structurally reorganize its architecture and synaptic connectivity in response to experiential learning. Long-term potentiation, or LTP, serves as the primary cellular mechanism underlying memory formation: repeated high-frequency stimulation between presynaptic and postsynaptic neurons strengthens dendritic receptor density. However, synaptic potentiation alone is insufficient for permanent knowledge retention; it requires sleep-dependent consolidation. During slow-wave non-REM sleep, the hippocampus acts as a temporary buffer, replaying newly acquired neuronal firing sequences to the neocortex via sharp-wave ripples. This active system consolidation permanently stabilizes fragile short-term memories into enduring cortical schemas. Concurrently, during REM sleep, synaptic pruning downscales redundant neural connections, optimizing metabolic efficiency and integrating abstract conceptual insights.",
        "suggested_notes_tr": [
            "Nöroplastisite: Beynin yetişkinlikte de deneyimle sinaptik yapısını yeniden şekillendirme kapasitesi",
            "LTP (Long-Term Potentiation): Sık uyarılan sinapslarda reseptör yoğunluğunun artmasıyla güçlenme",
            "Slow-Wave (Non-REM) uykusu: Hipokampüs geçici bellek tamponu gibi davranıp 'keskin dalga dalgalanmaları' (sharp-wave ripples) ile neokortekse aktarır",
            "REM uykusu: Sinaptik budama (synaptic pruning) ile gereksiz bağlar temizlenir, soyut bağlantılar kurulur"
        ],
        "questions": [
            {
                "id": "lis_c1_06_q1",
                "question": "What role does the hippocampus play during slow-wave non-REM sleep?",
                "options": [
                    {"key": "A", "text": "It permanently deletes all declarative linguistic memories"},
                    {"key": "B", "text": "It replays firing sequences via sharp-wave ripples to transfer memories to the neocortex"},
                    {"key": "C", "text": "It synthesizes physical bone calcium reserves"},
                    {"key": "D", "text": "It slows down cardiac muscle contraction"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'the hippocampus acts as a temporary buffer, replaying newly acquired neuronal firing sequences to the neocortex via sharp-wave ripples' denilmiştir."
            },
            {
                "id": "lis_c1_06_q2",
                "question": "What is the primary function of synaptic pruning during REM sleep?",
                "options": [
                    {"key": "A", "text": "It downscales redundant neural connections to optimize metabolic efficiency"},
                    {"key": "B", "text": "It induces permanent motor paralysis after waking"},
                    {"key": "C", "text": "It generates auditory hallucinations exclusively"},
                    {"key": "D", "text": "It halts all blood circulation to the brain"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'synaptic pruning downscales redundant neural connections, optimizing metabolic efficiency' bilgisi verilir."
            }
        ]
    },
    {
        "id": "lis_c1_07",
        "university_id": "bilkent",
        "level": "C1",
        "type": "while_listening",
        "title": "International Trade Law and Sovereign Debt Restructuring",
        "subtitle": "Bilkent Uluslararası Hukuk Semineri",
        "target_university": "Bilkent Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 100,
        "instructions_tr": "Uluslararası ticaret hukuku ve devlet borçları yapılandırmasını dinleyip soruları cevaplayınız.",
        "audio_script": "When sovereign nation-states encounter balance-of-payments crises and face fiscal insolvency, the international legal architecture lacks a statutory bankruptcy mechanism analogous to domestic corporate liquidation courts. Sovereign immunity shields state infrastructure from direct judicial asset seizure abroad. Consequently, sovereign debt restructuring relies heavily on decentralized contractual arrangements between debtor states and international bondholder cartels. A recurring legal obstacle is the 'holdout creditor' problem. Speculative hedge funds, termed vulture funds, purchase defaulted sovereign bonds on secondary markets at steep discounts, deliberately refusing to participate in negotiated debt haircuts. They then litigate in New York or London commercial courts, demanding one hundred percent face-value repayment plus accrued punitive interest. To neutralize predatory holdout litigation, contemporary sovereign bond indentures incorporate Collective Action Clauses (CACs). Under modern aggregation CACs, if a supermajority of creditors—typically seventy-five percent—approves a restructuring agreement, the modified financial terms become legally binding across all outstanding bondholders, preserving the sovereign debtor's fiscal solvency.",
        "suggested_notes_tr": [
            "Devlet iflası: Uluslararası hukukta kurumsal iflas mahkemeleri benzeri bir üst organ yoktur",
            "Holdout alacaklı / Akbaba fon (Vulture fund) sorunu: İndirimli borcu alıp yapılandırmayı reddederek mahkemede %100 tahsilat talep ederler",
            "Çözüm: Kolektif Eylem Klozları (Collective Action Clauses - CACs)",
            "Çalışma prensibi: Alacaklıların %75 gibi bir nitelikli çoğunluğu anlaştığında karar tüm tahvil sahipleri için bağlayıcı olur"
        ],
        "questions": [
            {
                "id": "lis_c1_07_q1",
                "question": "What strategy is pursued by speculative 'vulture funds' during sovereign debt crises?",
                "options": [
                    {"key": "A", "text": "They donate emergency humanitarian medical grants to debtor states"},
                    {"key": "B", "text": "They acquire discounted defaulted bonds and litigate in foreign courts for full face-value repayment"},
                    {"key": "C", "text": "They forgive national debts unconditionally"},
                    {"key": "D", "text": "They establish international commercial trading banks"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'purchase defaulted sovereign bonds on secondary markets at steep discounts ... demanding one hundred percent face-value repayment' denilmiştir."
            },
            {
                "id": "lis_c1_07_q2",
                "question": "How do Collective Action Clauses (CACs) prevent holdout creditors from derailing debt restructuring?",
                "options": [
                    {"key": "A", "text": "They revoke the debtor state's diplomatic sovereignty"},
                    {"key": "B", "text": "Supermajority approval legally binds all outstanding bondholders to the modified terms"},
                    {"key": "C", "text": "They eliminate all bond trading on secondary markets"},
                    {"key": "D", "text": "They replace commercial currency with gold bullion"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'if a supermajority of creditors ... approves a restructuring agreement, the modified financial terms become legally binding across all outstanding bondholders' denilmiştir."
            }
        ]
    },
    {
        "id": "lis_c1_08",
        "university_id": "metu",
        "level": "C1",
        "type": "while_listening",
        "title": "Cryosphere Feedbacks and Abrupt Climate Tipping Points",
        "subtitle": "ODTÜ İklim Fiziği ve Okyanus Bilimleri Dersi",
        "target_university": "Orta Doğu Teknik Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 100,
        "instructions_tr": "Kriyosfer geri besleme döngüleri ve iklim eşik noktalarını dinleyin.",
        "audio_script": "Climate science increasingly focuses on nonlinear dynamics: critical thresholds where minor incremental shifts in atmospheric greenhouse concentrations precipitate irreversible, self-reinforcing biophysical transformations, known as tipping points. Among the most precarious systems is the polar cryosphere. The ice-albedo positive feedback loop illustrates this vulnerability. Bright sea ice reflects up to eighty-five percent of incoming solar radiation back into space. As rising global temperatures melt Arctic ice sheets, reflective white surfaces are replaced by dark ocean water, which absorbs over ninety percent of solar thermal energy. This accelerated oceanic heat absorption triggers further sea ice melting in an escalating spiral. Concurrently, warming Arctic temperatures destabilize sub-polar permafrost, unleashing vast subterranean reservoirs of sequestered methane gas. Because methane possesses a greenhouse warming potential approximately eighty times greater than carbon dioxide over a twenty-year horizon, permafrost thaw threatens to trigger runaway global warming that transcends human emissions mitigation.",
        "suggested_notes_tr": [
            "Eşik Noktaları (Tipping Points): Küçük artışların geri döndürülemez, kendi kendini besleyen döngüleri tetiklemesi",
            "Buz-Albedo geri beslemesi: Beyaz buz %85 yansıtır; eriyince yerini alan koyu okyanus %90 soğurur -> Isınma hızlanır",
            "Permafrost erimesi: Donmuş toprak altındaki metan gazı salınır",
            "Metan tehlikesi: 20 yıllık vadede CO2'den 80 kat daha güçlü sera etkisi yaratır -> Kontrol dışı ısınma"
        ],
        "questions": [
            {
                "id": "lis_c1_08_q1",
                "question": "Why does melting Arctic sea ice create a positive feedback loop accelerating global warming?",
                "options": [
                    {"key": "A", "text": "Open dark ocean water absorbs over ninety percent of solar radiation instead of reflecting it"},
                    {"key": "B", "text": "Cold sea water cools deep volcanic magma vents"},
                    {"key": "C", "text": "Ice melting halts the flow of atmospheric oxygen"},
                    {"key": "D", "text": "It triggers immediate global tectonic shifts"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'reflective white surfaces are replaced by dark ocean water, which absorbs over ninety percent of solar thermal energy' denilmiştir."
            },
            {
                "id": "lis_c1_08_q2",
                "question": "Why is the thawing of Arctic permafrost regarded as an alarming climate tipping point?",
                "options": [
                    {"key": "A", "text": "It permanently freezes transatlantic shipping lanes"},
                    {"key": "B", "text": "It releases sequestered methane, which is eighty times more potent than carbon dioxide in the short term"},
                    {"key": "C", "text": "It increases polar agricultural crop yields too rapidly"},
                    {"key": "D", "text": "It eliminates the Earth's geomagnetic field"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'methane possesses a greenhouse warming potential approximately eighty times greater than carbon dioxide over a twenty-year horizon' ifadesi yer alır."
            }
        ]
    },
    {
        "id": "lis_c1_09",
        "university_id": "koc",
        "level": "C1",
        "type": "while_listening",
        "title": "Synthetic Genomics and Directed Molecular Evolution",
        "subtitle": "Koç Üniversitesi Moleküler Biyoloji Semineri",
        "target_university": "Koç Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 100,
        "instructions_tr": "Sentetik genomik ve yönlendirilmiş evrim teknolojisini dinleyin.",
        "audio_script": "The transition from classical recombinant DNA technology to synthetic genomics marks a paradigm shift from reading and editing genetic codes to writing de novo artificial genomes. Pioneered by synthetic biologist Craig Venter, researchers synthesized the complete bacterial genome of Mycoplasma mycoides chemically from raw nucleotides and transplanted it into anucleated recipient cells, generating viable synthetic organism capable of independent replication. Concurrently, Nobel laureate Frances Arnold developed the methodology of directed evolution, harnessing Darwinian natural selection in test tubes. By generating iterative rounds of random mutagenesis across targeted gene sequences and screening for optimal enzymatic phenotypes, directed evolution creates biocatalysts with unprecedented catalytic efficiency. These engineered enzymes synthesize complex pharmaceutical molecules without petroleum solvents, degrade non-biodegradable plastics in landfills, and optimize biohydrogen generation. However, dual-use biosecurity risks necessitate stringent genomic surveillance to prevent malicious synthesis of biological pathogens.",
        "suggested_notes_tr": [
            "Sentetik Genomik: DNA'yı okuma/düzenlemeden baştan yapay genom yazmaya geçiş (De novo sentez)",
            "Craig Venter: Mycoplasma mycoides genomunu kimyasal olarak sentezleyip hücreye aktardı",
            "Frances Arnold (Yönlendirilmiş Evrim): Test tüpünde mutasyon ve seçilimle üstün enzimler üretme",
            "Uygulamalar: Yeşil ilaç üretimi, plastik parçalayan enzimler, hidrojen üretimi",
            "Biyogüvenlik riski: Sentetik patojen üretimini önlemek için genomik denetim şart"
        ],
        "questions": [
            {
                "id": "lis_c1_09_q1",
                "question": "How does directed evolution optimize enzymes in laboratory environments?",
                "options": [
                    {"key": "A", "text": "By exposing test tubes to zero-gravity vacuum chambers"},
                    {"key": "B", "text": "Through iterative rounds of random mutagenesis coupled with selective phenotype screening"},
                    {"key": "C", "text": "By freezing DNA at absolute zero"},
                    {"key": "D", "text": "Through manual mechanical carving of protein atoms"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'generating iterative rounds of random mutagenesis across targeted gene sequences and screening for optimal enzymatic phenotypes' denilmiştir."
            },
            {
                "id": "lis_c1_09_q2",
                "question": "What is one major ecological application of enzymes engineered through directed evolution?",
                "options": [
                    {"key": "A", "text": "Degrading non-biodegradable plastic polymers in landfills"},
                    {"key": "B", "text": "Producing nuclear fission fuel"},
                    {"key": "C", "text": "Preventing tectonic continental drift"},
                    {"key": "D", "text": "Eliminating atmospheric nitrogen"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'degrade non-biodegradable plastics in landfills, and optimize biohydrogen generation' bilgisi verilir."
            }
        ]
    },
    {
        "id": "lis_c1_10",
        "university_id": "ankara",
        "level": "C1",
        "type": "while_listening",
        "title": "Constitutional Jurisprudence and the Counter-Majoritarian Dilemma",
        "subtitle": "Ankara Üniversitesi Anayasa Hukuku Dersi",
        "target_university": "Ankara Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 100,
        "instructions_tr": "Anayasa yargısı ve çoğunlukçu demokrasi arasındaki gerilimi dinleyin.",
        "audio_script": "In constitutional theory, judicial review refers to the institutional power of supreme or constitutional courts to invalidate legislative statutes enacted by elected parliaments if they violate fundamental constitutional protections. In nineteen sixty-two, legal scholar Alexander Bickel coined the phrase 'the counter-majoritarian difficulty' to encapsulate the core philosophical tension of judicial review: how can a constitutional democracy justify allowing a small panel of unelected, life-tenured judges to overturn laws passed by the democratically elected representatives of the popular majority? Defenders of constitutionalism, rooted in Ronald Dworkin’s rights-based jurisprudence, counter that authentic democracy is not crude majoritarian tyranny. True democratic legitimacy requires substantive preconditions: universal franchise, freedom of speech, and the protection of minority populations against majoritarian prejudice. When constitutional courts strike down discriminatory legislation, they are not thwarting democracy; they are upholding the fundamental constitutional integrity that makes democratic self-governance morally legitimate in the first place.",
        "suggested_notes_tr": [
            "Anayasa Yargısı (Judicial Review): Seçilmiş parlamentoların yasalarını anayasaya aykırılık gerekçesiyle iptal etme yetkisi",
            "Karşı-Çoğunlukçu İkilem (Alexander Bickel, 1962): Seçilmemiş yargıçların halkın seçtiği temsilcilerin yasalarını iptal etmesinin demokratik meşruiyeti",
            "Dworkin'in Haklar Temelli Hukuk Felsefesi: Demokrasi kaba çoğunluk tahakkümü (majoritarian tyranny) değildir",
            "Yargı denetiminin meşruiyeti: Azınlık haklarını koruyarak demokratik sistemin ahlaki ve hukuki zeminini muhafaza eder"
        ],
        "questions": [
            {
                "id": "lis_c1_10_q1",
                "question": "What is Alexander Bickel's 'counter-majoritarian difficulty' primarily concerned with?",
                "options": [
                    {"key": "A", "text": "The expense of conducting national legislative elections"},
                    {"key": "B", "text": "The philosophical tension of unelected judges invalidating laws passed by elected majorities"},
                    {"key": "C", "text": "The lack of female candidates in municipal elections"},
                    {"key": "D", "text": "The regulation of commercial lobbying contributions"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'how can a constitutional democracy justify allowing a small panel of unelected, life-tenured judges to overturn laws passed by the democratically elected representatives' denilmiştir."
            },
            {
                "id": "lis_c1_10_q2",
                "question": "According to Ronald Dworkin's jurisprudence, why is judicial review essential to democracy?",
                "options": [
                    {"key": "A", "text": "It guarantees that parliaments never meet"},
                    {"key": "B", "text": "It preserves substantive rights and minority protections necessary for democratic legitimacy"},
                    {"key": "C", "text": "It allows judges to collect sovereign taxes directly"},
                    {"key": "D", "text": "It replaces political parties with civil servants"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'True democratic legitimacy requires substantive preconditions ... protection of minority populations against majoritarian prejudice' ifadesi yer alır."
            }
        ]
    }
]

# --- C2 TRACKS (8 TRACKS) ---
C2_TRACKS = [
    {
        "id": "lis_c2_03",
        "university_id": "boun",
        "level": "C2",
        "type": "note_taking",
        "title": "Epistemological Fallibilism and Underdetermination of Scientific Theory",
        "subtitle": "Boğaziçi BUEPT Doktora & İleri C2 Note-Taking",
        "target_university": "Boğaziçi Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 110,
        "instructions_tr": "Bilim felsefesi ve Quine-Duhem tezini dinleyiniz. Dinlerken notlarınızı dijital deftere kaydediniz; ardından soruları yanıtlayınız.",
        "audio_script": "In the philosophy of science, the Duhem-Quine thesis articulates the holist underdetermination of scientific theory by empirical evidence. Classical logical positivism presupposed that individual scientific hypotheses could be subjected to isolated experimental verification or Popperian falsification. Willard Van Orman Quine decisively undermined this atomistic reductionism by asserting that our knowledge of the world faces the tribunal of experience not as disconnected propositions, but as an interconnected web of belief. When an empirical observation contradicts a theoretical prediction, logic alone cannot specify which particular thread within the theoretical fabric is falsified. A recalcitrant observation can always be accommodated by introducing auxiliary hypotheses, re-calibrating observational instruments, or revising background assumptions. Consequently, multiple rival theoretical paradigms can remain logically compatible with identical empirical data sets. Scientific realism must therefore embrace fallibilism: recognizing that empirical paradigms are underdetermined heuristic models rather than mirror reflections of metaphysical reality.",
        "suggested_notes_tr": [
            "Duhem-Quine Tezi: Bilimsel teorilerin ampirik veriler tarafından 'yetersiz belirlenimi' (underdetermination)",
            "İnanç Ağı (Web of Belief - Quine): Bilgilerimiz tekil doğrulamaya değil, bütüncül bir ağ halinde deneyime tabi tutulur",
            "Yanlışlamanın imkansızlığı: Çelişen bir gözlemde hangi hipotezin çöktüğü bilinemez; yardımcı hipotezler veya araç kalibrasyonuyla teori kurtarılabilir",
            "Sonuç: Birbiriyle çelişen iki rakip teori aynı veri setiyle tamamen uyumlu olabilir",
            "Epistemolojik yanılabilirlik (Fallibilism): Bilimsel modeller metafiziksel mutlak gerçeklik değil, heuristik inşalardır"
        ],
        "questions": [
            {
                "id": "lis_c2_03_q1",
                "question": "What is the core argument of the Duhem-Quine underdetermination thesis?",
                "options": [
                    {"key": "A", "text": "All scientific theories can be definitively proven true using mathematics alone"},
                    {"key": "B", "text": "Empirical evidence is insufficient to uniquely determine a single scientific theory over rival paradigms"},
                    {"key": "C", "text": "Physical reality does not exist outside the human mind"},
                    {"key": "D", "text": "Hypothesis testing requires no auxiliary experimental assumptions"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'multiple rival theoretical paradigms can remain logically compatible with identical empirical data sets' denilmiştir."
            },
            {
                "id": "lis_c2_03_q2",
                "question": "How did W.V.O. Quine conceptualize human knowledge in relation to empirical experience?",
                "options": [
                    {"key": "A", "text": "As an interconnected holistic web of belief"},
                    {"key": "B", "text": "As disconnected, isolated linguistic atoms"},
                    {"key": "C", "text": "As an immutable theological hierarchy"},
                    {"key": "D", "text": "As pure sensory illusion devoid of syntax"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'faces the tribunal of experience not as disconnected propositions, but as an interconnected web of belief' ifadesi mevcuttur."
            }
        ]
    },
    {
        "id": "lis_c2_04",
        "university_id": "metu",
        "level": "C2",
        "type": "note_taking",
        "title": "Posthumanism, Cyborg Ontology, and the Dissolution of Liberal Humanism",
        "subtitle": "ODTÜ İleri Felsefe ve Eleştirel Teori",
        "target_university": "Orta Doğu Teknik Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 110,
        "instructions_tr": "Posthümanizm ve siborg ontolojisi üzerine akademik dersi dinleyip not alınız.",
        "audio_script": "Critical posthumanism mounts an ontological deconstruction of the Enlightenment humanist subject—the sovereign, rational, autonomous individual historically constructed through patriarchal, colonial, and anthropocentric exclusions. As cultural theorist Donna Haraway demonstrated in her seminal Cyborg Manifesto, technological interfaces have irreversibly collapsed the foundational dualisms underpinning Western metaphysics: the ontological boundaries between nature and culture, organism and mechanism, human and animal. The cyborg figure is not a dystopic alienation from an Edenic natural origin, but an affirmation of hybridity, relationality, and leaky boundaries. In the contemporary Anthropocene, human survival necessitates abandoning the illusion of sovereign planetary mastery. A relational posthumanist ethics demands acknowledging non-human agency and technological imbrication, recognizing that human subjectivity is fundamentally distributed across ecological webs, algorithmic neural networks, and biological symbiogeneses.",
        "suggested_notes_tr": [
            "Aydınlanma hümanist öznesinin eleştirisi: Evrensel değil; sömürgeci, eril ve antroposentrik bir kurgudur",
            "Donna Haraway (Siborg Manifestosu): Doğa/kültür, mekanizma/organizma, insan/hayvan ikiliklerinin yıkılması",
            "Siborg ontolojisi: Saflık/köken arayışı değil; melezlik, ilişkisellik ve geçirgen sınırlar (leaky boundaries)",
            "İlişkisel posthümanist etik: İnsanın egemen efendi yanılsamasından vazgeçip biyolojik, ekolojik ve algoritmik ağlarla paylaşılan failliği (distributed agency) tanıması"
        ],
        "questions": [
            {
                "id": "lis_c2_04_q1",
                "question": "What metaphysical dualisms are dismantled by Donna Haraway's cyborg ontology?",
                "options": [
                    {"key": "A", "text": "The mathematical dichotomy between positive and negative integers"},
                    {"key": "B", "text": "The dualisms between nature and culture, organism and machine, and human and animal"},
                    {"key": "C", "text": "The boundary between alternating and direct electrical current"},
                    {"key": "D", "text": "The divide between ancient and medieval Latin syntax"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'collapsed the foundational dualisms ... between nature and culture, organism and mechanism, human and animal' denilmiştir."
            },
            {
                "id": "lis_c2_04_q2",
                "question": "What does relational posthumanist ethics demand in the Anthropocene?",
                "options": [
                    {"key": "A", "text": "Absolute technological domination over biological ecosystems"},
                    {"key": "B", "text": "Recognizing distributed non-human agency and human ecological imbrication"},
                    {"key": "C", "text": "The immediate prohibition of all prosthetic medical technology"},
                    {"key": "D", "text": "A return to pre-industrial feudal agriculture"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'demands acknowledging non-human agency and technological imbrication, recognizing that human subjectivity is fundamentally distributed' ifadesi yer alır."
            }
        ]
    },
    {
        "id": "lis_c2_05",
        "university_id": "bilkent",
        "level": "C2",
        "type": "while_listening",
        "title": "Frankfurt School Critique of Instrumental Reason",
        "subtitle": "Bilkent Üniversitesi Eleştirel Teori Semineri",
        "target_university": "Bilkent Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 105,
        "instructions_tr": "Adorno ve Horkheimer'ın 'Aydınlanmanın Diyalektiği' ve araçsal akıl eleştirisini dinleyin.",
        "audio_script": "In 'Dialectic of Enlightenment', Frankfurt School theorists Max Horkheimer and Theodor Adorno interrogated why humanity, instead of entering a truly human condition, was sinking into a new kind of barbarism. Their diagnosis centered upon the catastrophic degeneration of subjective reason into pure instrumental rationality. The Enlightenment promised emancipation from myth and theological superstition through scientific understanding. However, in subduing external nature, reason was stripped of its capacity to evaluate objective moral ends, values, and human justice. Instrumental reason became an operational calculating technique dedicated solely to utilitarian mastery, technical efficiency, and commodity exchange. Consequently, nature—and ultimately human beings themselves—were reduced to quantifiable, manipulable objects of administrative control. When reason is reduced to a tool of domination, bureaucratic efficiency culminates not in human liberation, but in totalitarian administration and industrial mass destruction.",
        "suggested_notes_tr": [
            "Horkheimer & Adorno: 'Aydınlanmanın Diyalektiği' (Dialectic of Enlightenment)",
            "Sorun: İnsanlığın aydınlanmayla özgürleşmek yerine yeni bir barbarlığa ve tahakküme sürüklenmesi",
            "Araçsal Akıl (Instrumental Reason): Amacı ve adaleti sorgulama yeteneğini kaybedip sadece teknik verimlilik ve hesaplamaya indirgenmiş akıl",
            "Sonuç: Doğanın ve insanın metaya, niceliksel ve manipüle edilebilir nesneye dönüştürülmesi; totaliter yönetim"
        ],
        "questions": [
            {
                "id": "lis_c2_05_q1",
                "question": "What primary degeneration of Enlightenment reason did Adorno and Horkheimer identify?",
                "options": [
                    {"key": "A", "text": "The resurgence of medieval astrological belief"},
                    {"key": "B", "text": "The reduction of objective reason to instrumental rationality and technical calculation"},
                    {"key": "C", "text": "The complete abolition of written legal constitutions"},
                    {"key": "D", "text": "The refusal of scholars to utilize mathematics"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'Their diagnosis centered upon the catastrophic degeneration of subjective reason into pure instrumental rationality' denilmiştir."
            },
            {
                "id": "lis_c2_05_q2",
                "question": "How are human beings treated when instrumental reason governs social administration?",
                "options": [
                    {"key": "A", "text": "As autonomous, inviolable moral sovereigns"},
                    {"key": "B", "text": "As quantifiable, manipulable objects of administrative and economic control"},
                    {"key": "C", "text": "As divine theological entities"},
                    {"key": "D", "text": "As non-cognitive biological flora"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'nature—and ultimately human beings themselves—were reduced to quantifiable, manipulable objects of administrative control' bilgisi geçer."
            }
        ]
    },
    {
        "id": "lis_c2_06",
        "university_id": "sabanci",
        "level": "C2",
        "type": "while_listening",
        "title": "Biosemiotics and Jakob von Uexküll's Umwelt Theory",
        "subtitle": "Sabancı Üniversitesi Biyosemiyotik Dersi",
        "target_university": "Sabancı Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 105,
        "instructions_tr": "Biyosemiyotik ve canlıların algısal dünyalarını (Umwelt) anlatan dersi dinleyiniz.",
        "audio_script": "Biosemiotics bridges theoretical biology and semiotics by positing that life is fundamentally mediated through sign processes and meaning-making, or semiosis. Early twentieth-century theoretical biologist Jakob von Uexküll overthrew mechanistic behaviorism by introducing the concept of the 'Umwelt'—the subjective perceptual bubble unique to every organism. Mechanistic science assumes an objective, universal physical environment, or 'Umgebung', identical for all creatures. Uexküll proved that an organism does not interact with the entirety of physical reality, but only with those environmental cues for which its specialized sensory receptors, or 'Merkorgane', are physiologically tuned. For a blind tick, the world consists of only three operational carrier signs: the scent of butyric acid, the thermal heat of mammalian blood, and the hairiness of skin. All other physical stimuli—colors, symphonies, chemical pollutants—are non-existent within its phenomenological reality. Thus, nature is not a monolithic physical mechanism, but a vast, polyphonic polyphony of interlocking perceptual Umwelten.",
        "suggested_notes_tr": [
            "Biyosemiyotik: Yaşamın işaret süreçleri ve anlamlandırma (semiosis) ile kurulduğu tezi",
            "Jakob von Uexküll: 'Umwelt' (Öznel algı dünyası) kavramı",
            "Umgebung (Nesnel çevre) vs. Umwelt: Canlılar tüm fiziksel evrenle değil, alıcılarının (Merkorgane) algıladığı işaretlerle etkileşir",
            "Kene örneği: Sadece bütirik asit kokusu, memeli vücut ısısı ve deri tüyü onun gerçekliğidir; gerisi yoktur",
            "Sonuç: Doğa tek parça mekanik bir saat değil, iç içe geçmiş öznel algı dünyalarının polifonik senfonisidir"
        ],
        "questions": [
            {
                "id": "lis_c2_06_q1",
                "question": "What is the fundamental distinction between 'Umgebung' and 'Umwelt' in Uexküll's theoretical biology?",
                "options": [
                    {"key": "A", "text": "Umgebung is microscopic while Umwelt is macroscopic"},
                    {"key": "B", "text": "Umgebung is the objective physical environment, whereas Umwelt is the organism's subjective perceptual reality"},
                    {"key": "C", "text": "Umgebung applies to plants while Umwelt applies only to bacteria"},
                    {"key": "D", "text": "There is no theoretical distinction between the terms"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'Mechanistic science assumes an objective, universal physical environment, or Umgebung ... Uexküll proved that an organism does not interact with the entirety of physical reality, but only with its Umwelt' denilmiştir."
            },
            {
                "id": "lis_c2_06_q2",
                "question": "According to biosemiotics, what constitutes an organism's reality?",
                "options": [
                    {"key": "A", "text": "Every physical particle existing in quantum space"},
                    {"key": "B", "text": "Only those environmental carrier signs that its physiological receptors can sense and interpret"},
                    {"key": "C", "text": "Human linguistic translations exclusively"},
                    {"key": "D", "text": "Electromagnetic gravity alone"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'an organism does not interact with the entirety of physical reality, but only with those environmental cues for which its specialized sensory receptors ... are physiologically tuned' denilmiştir."
            }
        ]
    },
    {
        "id": "lis_c2_07",
        "university_id": "koc",
        "level": "C2",
        "type": "while_listening",
        "title": "Systemic Risk, Network Topology, and Financial Contagion",
        "subtitle": "Koç Üniversitesi İleri Ekonometri ve Finans Semineri",
        "target_university": "Koç Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 105,
        "instructions_tr": "Finansal ağ topolojisi ve sistemik çöküş modellemelerini dinleyiniz.",
        "audio_script": "The two-thousand-eight global financial collapse decisively demonstrated that systemic risk cannot be appraised by evaluating individual financial institutions in micro-prudential isolation. Modern macroprudential econometrics models financial stability through complex network topology. Financial systems are structured as directed, weighted graphs where nodes represent banking institutions and edges denote interbank obligations, derivative exposures, and collateralized debt cross-holdings. In quiescent economic periods, dense interconnectedness enhances financial resilience by dissipating localized liquidity shocks across the entire network. However, network theorists Andrew Haldane and Robert May revealed a non-linear tipping point: when shocks exceed a critical threshold, dense topological interconnectedness transforms into a hyper-efficient conduit for financial contagion. As distressed institutions liquidate illiquid assets in fire sales, asset depreciation cascades through counterparty balance sheets, triggering systemic insolvency. Effective macroprudential regulation requires identifying systemic topologically central nodes and enforcing countercyclical capital buffers.",
        "suggested_notes_tr": [
            "Mikro-ihtiyati tecrit eleştirisi: Kurumları tek başına incelemek sistemik riski ölçemez",
            "Ağ Topolojisi (Network Topology): Bankalar düğüm (node), türev/borç bağları kenar (edge) olan yönlü çizge",
            "Çift taraflı etki (Haldane & May):",
            "  - Sakin dönemde yoğun bağlantılılık yerel şokları dağıtarak direnç sağlar",
            "  - Kriz anında ise sistemik bulaşma (contagion) kanalına dönüşür",
            "Mekanizma: Varlık yangın satışı (fire sale) -> Bilanço erimesi -> Zincirleme iflas",
            "Çözüm: Ağın merkezindeki kritik düğümlere döngü karşıtı sermaye tamponu (countercyclical buffer) zorunluluğu"
        ],
        "questions": [
            {
                "id": "lis_c2_07_q1",
                "question": "How does dense network interconnectedness exhibit non-linear behavior during financial crises?",
                "options": [
                    {"key": "A", "text": "It permanently freezes all currency exchange rates"},
                    {"key": "B", "text": "It dissipates small shocks in calm periods, but amplifies contagion once a critical shock threshold is exceeded"},
                    {"key": "C", "text": "It eliminates the need for central banking authorities"},
                    {"key": "D", "text": "It guarantees perpetual economic growth"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'In quiescent economic periods, dense interconnectedness enhances financial resilience ... when shocks exceed a critical threshold, dense topological interconnectedness transforms into a hyper-efficient conduit for financial contagion' denilmiştir."
            },
            {
                "id": "lis_c2_07_q2",
                "question": "What is the macroprudential regulatory response to topologically central financial nodes?",
                "options": [
                    {"key": "A", "text": "Nationalizing all retail consumer branches"},
                    {"key": "B", "text": "Enforcing heightened countercyclical capital buffers and stress-testing interbank exposures"},
                    {"key": "C", "text": "Prohibiting all electronic interbank transactions"},
                    {"key": "D", "text": "Forbidding foreign commercial investment"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'identifying systemic topologically central nodes and enforcing countercyclical capital buffers' ifadesi geçer."
            }
        ]
    },
    {
        "id": "lis_c2_08",
        "university_id": "ankara",
        "level": "C2",
        "type": "while_listening",
        "title": "Necropolitics, Sovereignty, and Spaces of Exception in Border Regimes",
        "subtitle": "Ankara Üniversitesi Siyaset Felsefesi Dersi",
        "target_university": "Ankara Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 110,
        "instructions_tr": "Nekropolitika ve egemen istisna halleri üzerine felsefi dersi dinleyin.",
        "audio_script": "Achille Mbembe’s seminal paradigm of 'necropolitics' reformulates classical theories of sovereignty by positing that ultimate sovereign power resides not in the management and optimization of biological life—as Michel Foucault argued in his biopolitical lectures—but in the sovereign prerogative to dictate who is disposable and who may be exposed to death. Synthesizing Giorgio Agamben’s concept of the 'state of exception' with postcolonial critique, Mbembe demonstrates that modern sovereignty materializes most tangibly in geographical border regimes. Frontiers, offshore detention centers, and militarized maritime boundaries operate as contemporary spaces of exception where constitutional guarantees and international humanitarian law are suspended through administrative decree. Within these necropolitical zones, stateless refugees are stripped of political existence, reduced to what Agamben termed 'bare life'—human existence devoid of juridical rights. By weaponizing hostile geography—forcing migrants into treacherous desert expanses or unnavigable maritime channels—the sovereign state manufactures conditions of mass mortality while preserving formal legal deniability.",
        "suggested_notes_tr": [
            "Achille Mbembe (Nekropolitika): Nihai egemenlik gücü yaşamı yönetmekte değil, kimin ölüme terk edileceğini (disposable) belirlemektir",
            "Agamben'in İstisna Hali (State of Exception): Anayasal hakların ve uluslararası hukukun askıya alındığı alanlar",
            "Sınır rejimleri ve gözaltı kampları: Modern istisna mekanları",
            "Çıplak Yaşam (Bare Life): Hukuki haklarından arındırılmış saf biyolojik varoluş",
            "Coğrafyanın silah haline getirilmesi: Çöl veya tehlikeli deniz rotalarına iterek ölümü doğallaştırma ve hukuki sorumluluktan kaçınma"
        ],
        "questions": [
            {
                "id": "lis_c2_08_q1",
                "question": "What is the defining prerogative of sovereign power according to Achille Mbembe's necropolitics?",
                "options": [
                    {"key": "A", "text": "The monetary printing of physical fiat currency"},
                    {"key": "B", "text": "The capacity to dictate who is disposable and expose targeted populations to death"},
                    {"key": "C", "text": "The scientific mapping of planetary geography"},
                    {"key": "D", "text": "The management of domestic agricultural production"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'ultimate sovereign power resides ... in the sovereign prerogative to dictate who is disposable and who may be exposed to death' denilmiştir."
            },
            {
                "id": "lis_c2_08_q2",
                "question": "How does Giorgio Agamben characterize 'bare life' (homo sacer)?",
                "options": [
                    {"key": "A", "text": "Human biological existence stripped of juridical rights and political status"},
                    {"key": "B", "text": "A citizen exercising full constitutional democratic voting rights"},
                    {"key": "C", "text": "An immortal mythological archetype"},
                    {"key": "D", "text": "A diplomat holding international sovereign immunity"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'reduced to what Agamben termed bare life—human existence devoid of juridical rights' bilgisi yer alır."
            }
        ]
    },
    {
        "id": "lis_c2_09",
        "university_id": "itu",
        "level": "C2",
        "type": "while_listening",
        "title": "Thermodynamic Entropy, Information Theory, and Cosmological Arrows of Time",
        "subtitle": "İTÜ Teorik Fizik ve Kozmoloji Semineri",
        "target_university": "İstanbul Teknik Üniversitesi",
        "duration_minutes": 15,
        "lecture_duration_seconds": 110,
        "instructions_tr": "Termodinamik entropi, bilgi teorisi ve zamanın oku dersini dinleyin.",
        "audio_script": "The macroscopic unidirectionality of time represents one of the most enigmatic conundrums in fundamental physics. While the microscopic laws of classical mechanics, quantum wavefunctions, and general relativity are strictly time-reversal symmetric, human macroscopic reality exhibits an immutable chronological arrow pointing inexorably from past to future. The second law of thermodynamics grounds this asymmetry in statistical entropy: the spontaneous evolution of isolated thermodynamic systems from macrostates of low multiplicity to macrostates of overwhelmingly higher probability. In the nineteen forties, Claude Shannon formulated mathematical information theory, proving that thermodynamic entropy is mathematically isomorphic to information entropy: entropy quantifies the missing microscopic information required to specify a physical microstate given macroscopic thermodynamic coordinates. To account for why our present universe has not already reached thermal equilibrium or 'heat death', cosmologists postulate the Past Hypothesis: our universe originated in an extraordinarily low-entropy gravitational boundary condition at the Big Bang, establishing the thermodynamic reservoir from which all cosmic complexity and subjective time flow.",
        "suggested_notes_tr": [
            "Mikroskopik simetri vs. Makroskopik asimetri: Temel fizik denklemleri zaman simetriktir ama gerçekte zaman tek yönlü akar",
            "Termodinamiğin 2. Yasası: Yalıtılmış sistemlerde entropi (olasılık/düzensizlik) daima artar",
            "Claude Shannon (Bilgi Teorisi): Termodinamik entropi, eksik mikroskobik bilgi ile matematiksel olarak özdeştir (izomorfik)",
            "Geçmiş Hipotezi (Past Hypothesis): Evren Büyük Patlama anında olağanüstü düşük entropili bir başlangıç sınır durumundaydı; bu rezerv bugün karmaşıklığı ve zaman akışını besler"
        ],
        "questions": [
            {
                "id": "lis_c2_09_q1",
                "question": "What mathematical isomorphism did Claude Shannon demonstrate between thermodynamics and information theory?",
                "options": [
                    {"key": "A", "text": "Thermodynamic entropy is isomorphic to missing microscopic information"},
                    {"key": "B", "text": "Electrical voltage is identical to cosmic dark matter"},
                    {"key": "C", "text": "Sound velocity is isomorphic to quantum gravitational curvature"},
                    {"key": "D", "text": "Biological cell reproduction is mathematically identical to binary code"}
                ],
                "correct_answer": "A",
                "explanation_tr": "'Shannon formulated mathematical information theory, proving that thermodynamic entropy is mathematically isomorphic to information entropy: entropy quantifies the missing microscopic information' denilmiştir."
            },
            {
                "id": "lis_c2_09_q2",
                "question": "What is the 'Past Hypothesis' proposed by contemporary cosmologists?",
                "options": [
                    {"key": "A", "text": "The universe has no physical beginning in time"},
                    {"key": "B", "text": "The universe began in an extraordinary state of exceptionally low gravitational entropy at the Big Bang"},
                    {"key": "C", "text": "Time moves backward in black hole horizons"},
                    {"key": "D", "text": "Entropy decreases spontaneously across cosmic clusters"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'cosmologists postulate the Past Hypothesis: our universe originated in an extraordinarily low-entropy gravitational boundary condition at the Big Bang' denilmiştir."
            }
        ]
    },
    {
        "id": "lis_c2_10",
        "university_id": "general",
        "level": "C2",
        "type": "while_listening",
        "title": "Structural Semiotics and Derrida's Différance",
        "subtitle": "Genel C2 İleri Felsefe ve Dilbilim",
        "target_university": "Genel Hazırlık & CEFR C2",
        "duration_minutes": 15,
        "lecture_duration_seconds": 110,
        "instructions_tr": "Jacques Derrida'nın yapısöküm (deconstruction) ve différance kavramını dinleyip soruları yanıtlayın.",
        "audio_script": "In twentieth-century continental philosophy, Jacques Derrida's deconstructive intervention radicalized Saussurean structural linguistics by interrogating the Western metaphysical tradition of the 'metaphysics of presence'. Ferdinand de Saussure had demonstrated that language is a system of differential signs without positive terms: a signifier signifies only by virtue of what it is not within a relational network. Derrida observed that Western philosophy had persistently repressed this differential nature by seeking an ultimate 'transcendental signified'—an unmediated, self-present origin such as God, Reason, or Sensory Immediacy. To deconstruct this illusion, Derrida coined the neologism 'différance', combining the dual French meanings of differing and deferring. Meaning, Derrida asserts, is never fully present in a discrete linguistic sign; it is spatially differentiated from other signifiers and temporally deferred across an infinite chain of sign substitution. Because meaning is perpetually postponed, all texts contain unresolvable internal contradictions, or aporias, that systematically undo their own totalizing claims.",
        "suggested_notes_tr": [
            "Jacques Derrida ve Yapısöküm (Deconstruction)",
            "Varlık Metafiziği (Metaphysics of Presence): Batı felsefesinin nihai bir 'Aşkın Gösterilen' (Tanrı, Akıl, Özne) arayışının eleştirisi",
            "Différance kavramı: Fransızca 'differ' (farklılaşmak) ve 'defer' (ertelemek) kelimelerinin birleşimi",
            "Anlamın yapısı: Anlam hiçbir zaman tek bir kelimede tam olarak 'mevcut' değildir; uzamsal olarak farklılaşır ve zamansal olarak sonsuz zincirde ertelenir",
            "Aporia (Çıkmaz): Tüm metinler kendi iddialarını bozan içsel çözülemez çelişkiler barındırır"
        ],
        "questions": [
            {
                "id": "lis_c2_10_q1",
                "question": "What dual meanings are combined in Jacques Derrida's neologism 'différance'?",
                "options": [
                    {"key": "A", "text": "Definition and deduction"},
                    {"key": "B", "text": "Differing in space and deferring in time"},
                    {"key": "C", "text": "Describing and destroying"},
                    {"key": "D", "text": "Demonstration and debate"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'coined the neologism différance, combining the dual French meanings of differing and deferring' denilmiştir."
            },
            {
                "id": "lis_c2_10_q2",
                "question": "Why did Derrida argue that meaning is never fully present in a single linguistic sign?",
                "options": [
                    {"key": "A", "text": "Because vowels have no acoustic resonance"},
                    {"key": "B", "text": "Meaning is spatially differentiated from other signs and temporally deferred across an infinite chain of signifiers"},
                    {"key": "C", "text": "Because language was invented recently"},
                    {"key": "D", "text": "Because human memory has limited neurological storage"}
                ],
                "correct_answer": "B",
                "explanation_tr": "'Meaning, Derrida asserts, is never fully present in a discrete linguistic sign; it is spatially differentiated from other signifiers and temporally deferred across an infinite chain of sign substitution' denilmiştir."
            }
        ]
    }
]

print(f"Loaded: B2: {len(B2_TRACKS)}, C1: {len(C1_TRACKS)}, C2: {len(C2_TRACKS)}")
