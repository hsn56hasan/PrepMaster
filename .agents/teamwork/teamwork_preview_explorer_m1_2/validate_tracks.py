import json

t1 = {
  "id": "lis_odtu_02",
  "university_id": "metu",
  "level": "C1",
  "type": "note_taking",
  "title": "Circular Economy and Industrial Symbiosis in Resource-Constrained Economies",
  "subtitle": "ODTÜ EPE Tarzı Note-Taking Sınavı",
  "target_university": "Orta Doğu Teknik Üniversitesi",
  "duration_minutes": 15,
  "lecture_duration_seconds": 105,
  "instructions_tr": "ODTÜ EPE formatında not alma simülasyonu. Ses kaydını dinlerken notlarınızı alınız. Kayıt bitiminde sorular açılacak ve notlarınıza dayanarak soruları cevaplayacaksınız.",
  "audio_script": "Good morning, engineering scholars. Today we examine industrial symbiosis as an operational foundation for the circular economy. Conventional manufacturing operates on a throughput-intensive linear model: virgin materials are extracted, processed, and ultimately discarded as non-recyclable refuse. Industrial symbiosis fundamentally disrupts this degenerative paradigm by organizing geographically clustered industries into closed-loop metabolic ecosystems. In such networks, the residual effluent, discarded by-product, or surplus thermal energy of one manufacturing facility is systematically repurposed as the direct secondary feedstock or energy supply for an adjacent enterprise. The quintessential empirical paradigm of this architecture is the Kalundborg eco-industrial park in Denmark. In Kalundborg, a large-scale combined heat and power plant pipelines high-temperature surplus steam directly to an adjacent pharmaceutical facility and an enzyme fermentation plant, eliminating independent industrial boiler combustion. Simultaneously, calcium sulfate dihydrate, commonly known as synthetic gypsum, is recovered directly from the sulfur dioxide flue-gas desulfurization scrubbers of the power station. This synthetic gypsum completely supplants virgin mined gypsum at an adjacent gypsum wallboard manufacturing plant. Cumulatively, these symbiotic exchanges conserve more than three million cubic meters of groundwater annually, achieve over six hundred thousand tons of net carbon dioxide abatement, and transform toxic disposal liabilities into lucrative commercial assets. Nonetheless, ecological engineers must confront a critical systemic vulnerability: co-dependency risk. Because participant facilities become structurally reliant on continuous byproduct streams, the unscheduled shutdown, economic contraction, or decommissioning of a primary anchor tenant can instantly destabilize the material supply chains of dependent downstream plants. Consequently, robust symbiotic architectures require auxiliary redundant buffers.",
  "suggested_notes_tr": [
    "Doğrusal vs Kapalı Devre Model: Klasik 'al-üret-at' (linear) model yerine, tesislerin atık ve enerjilerini birbirine aktardığı kapalı döngülü (closed-loop) endüstriyel simbiyoz.",
    "Temel Çalışma Mantığı: Bir fabrikanın atık ısısı, atık suyu veya yan ürününün komşu fabrikanın birincil girdisi (feedstock) haline gelmesi.",
    "Kalundborg Vakası (Danimarka): Termik santralin atık buharı ilaç/enzim tesisine gidiyor; baca gazı kükürt arıtımından çıkan sentetik alçı (gypsum) alçıpan fabrikasında işleniyor.",
    "Kazanımlar: Yılda 3 milyon m³ üzerinde yeraltı suyu tasarrufu, 600.000 ton CO2 azaltımı ve atık bertaraf maliyetlerinin gelire dönüşmesi.",
    "Sistemik Risk (Co-dependency): Tesislerin birbirine aşırı bağımlılığı; ana bir üreticinin (anchor tenant) durması halinde tüm ekosistemin tedarik zincirinin çökme tehlikesi ve tamponlama ihtiyacı."
  ],
  "questions": [
    {
      "id": "lis_odtu_02_q1",
      "question": "What constitutes the core operational principle of industrial symbiosis according to the lecture?",
      "options": [
        {"key": "A", "text": "Utilizing the residual by-products, effluent, or surplus energy of one facility as feedstock for another."},
        {"key": "B", "text": "Centralizing all regional manufacturing processes under a single state-owned conglomerate."},
        {"key": "C", "text": "Eliminating reliance on heavy industry by converting manufacturing plants into agricultural reserves."},
        {"key": "D", "text": "Subsidizing virgin material extraction through international carbon credit markets."}
      ],
      "correct_answer": "A",
      "explanation_tr": "Konuşmacıya göre endüstriyel simbiyozun temel çalışma prensibi, bir üretim tesisinin atık yan ürünlerinin, atık suyunun veya fazla termal enerjisinin başka bir komşu tesis için hammadde (feedstock) ya da enerji kaynağı olarak yeniden kullanılmasıdır."
    },
    {
      "id": "lis_odtu_02_q2",
      "question": "How is synthetic gypsum obtained and utilized within the Kalundborg eco-industrial cluster?",
      "options": [
        {"key": "A", "text": "It is chemically synthesized from virgin mineral deposits shipped from neighboring rural mines."},
        {"key": "B", "text": "It is extracted from municipal wastewater filtration beds to fertilize agricultural land."},
        {"key": "C", "text": "It is recovered from power plant flue-gas desulfurization scrubbers to manufacture wallboards."},
        {"key": "D", "text": "It is generated as an organic precipitate during pharmaceutical enzyme fermentation."}
      ],
      "correct_answer": "C",
      "explanation_tr": "Ders anlatımında belirtildiği üzere sentetik alçıtaşı (synthetic gypsum), elektrik santralinin baca gazı kükürt giderme (flue-gas desulfurization) filtrelerinden geri kazanılarak komşu alçıpan (wallboard) üretim tesisinde doğal alçıtaşının yerini almaktadır."
    },
    {
      "id": "lis_odtu_02_q3",
      "question": "Which pair of environmental benefits is explicitly attributed to the symbiotic material exchanges in Kalundborg?",
      "options": [
        {"key": "A", "text": "Complete elimination of industrial electricity tariffs and zero solid waste generation."},
        {"key": "B", "text": "A fifty percent reduction in global maritime shipping and total reforestation of regional wetlands."},
        {"key": "C", "text": "Immediate doubling of factory profit margins without any capital equipment modification."},
        {"key": "D", "text": "Over three million cubic meters of groundwater saved and over six hundred thousand tons of CO2 abated."}
      ],
      "correct_answer": "D",
      "explanation_tr": "Konuşmacı somut çevresel kazanımlar olarak yıllık 3 milyon metreküpten fazla yeraltı suyu tasarrufu sağlandığını ve 600.000 tonun üzerinde net karbondioksit azaltımı (CO2 abatement) gerçekleştirildiğini vurgulamıştır."
    },
    {
      "id": "lis_odtu_02_q4",
      "question": "What fundamental vulnerability does the lecturer identify regarding highly integrated symbiotic networks?",
      "options": [
        {"key": "A", "text": "High government excise taxation applied uniquely to closed-loop manufacturing facilities."},
        {"key": "B", "text": "Co-dependency risk, where the disruption of an anchor tenant imperils downstream material supply."},
        {"key": "C", "text": "The inability of chemical engineers to measure thermodynamic heat transfer across steam pipes."},
        {"key": "D", "text": "The legal prohibition against transferring secondary steam across industrial property lines."}
      ],
      "correct_answer": "B",
      "explanation_tr": "Konuşmacı, tesislerin birbirine yapısal olarak bağımlı hale gelmesiyle oluşan co-dependency (ortak bağımlılık) riskine dikkat çekmiştir. Ana bir çıpa tesisin (anchor tenant) üretimi durdurması veya kapanması, yan ürüne muhtaç alt tesislerin tedarik zincirini derhal istikrarsızlaştırabilir."
    }
  ]
}

t2 = {
  "id": "lis_itu_02",
  "university_id": "itu",
  "level": "B2",
  "type": "while_listening",
  "title": "Composite Materials and Structural Health Monitoring in Aerospace Engineering",
  "subtitle": "İTÜ Proficiency Tarzı While-Listening Sınavı",
  "target_university": "İstanbul Teknik Üniversitesi",
  "duration_minutes": 10,
  "lecture_duration_seconds": 85,
  "instructions_tr": "Bu bir While-Listening (Dinlerken Cevaplama) sınavıdır. Sorular ses kaydı boyunca açıktır. Kaydı dinlerken eş zamanlı olarak soruları yanıtlayabilirsiniz.",
  "audio_script": "Good afternoon, class. In modern aerospace engineering, structural efficiency is fundamentally governed by material selection. For decades, commercial and military aircraft structures relied primarily on aluminum alloys due to their predictable isotropic properties and well-established fabrication methods. However, the pressing necessity to maximize fuel efficiency and payload capacity has propelled a comprehensive transition toward advanced composite materials, predominantly Carbon-Fiber-Reinforced Polymers, or CFRP. Unlike traditional metals, composite materials possess an anisotropic nature, meaning their mechanical strength and stiffness can be customized along specific load trajectories by orienting the carbon fibers during the manufacturing layup. This yields an exceptionally high strength-to-weight ratio. In state-of-the-art commercial jetliners, such as the Boeing 787 and Airbus A350, composites account for more than fifty percent of the total structural airframe weight. This substantial weight reduction decreases operating fuel consumption by approximately twenty percent compared to legacy aluminum airliners, while delivering superior resistance against environmental corrosion and fatigue cracking. Nevertheless, composite structures introduce distinct maintenance and reliability challenges. Specifically, low-velocity impacts—such as ground service collisions or runway debris strikes—can induce internal delamination, which is the internal separation of resin plies. Because this damage often leaves no visible indentation on the external surface, it is known as Barely Visible Impact Damage. To diagnose subsurface flaws without destructive disassembly, aerospace engineers integrate continuous Structural Health Monitoring systems. By embedding networks of piezoelectric sensors and fiber-optic Bragg gratings into the composite laminates, acoustic emissions and ultrasonic wave reflections are continuously monitored, alerting technicians to structural degradation before catastrophic failure occurs.",
  "suggested_notes_tr": [
    "Havacılıkta Malzeme Evrimi: Klasik izotropik alüminyum alaşımlarından anizotropik Karbon Elyaf Takviyeli Polimerlere (CFRP) geçiş.",
    "CFRP Avantajları: Liflerin yük yönüne göre dizilebilmesi, yüksek mukavemet/ağırlık oranı, korozyon ve yorulma (fatigue) direnci.",
    "Uçak Performansı: Modern yolcu uçaklarında gövde ağırlığının %50'sinden fazlası kompozit; %20 yakıt tasarrufu.",
    "Mühendislik Sorunu (Delamination): Düşük hızlı çarpmalarda iç katmanların ayrılması; dıştan görünmeyen hasar (Barely Visible Impact Damage - BVID).",
    "Çözüm (SHM): Kompozit içine gömülen piezoelektrik ve fiber-optik Bragg sensörleriyle Gerçek Zamanlı Yapısal Sağlık İzleme."
  ],
  "questions": [
    {
      "id": "lis_itu_02_q1",
      "question": "Why do aerospace engineers orient carbon fibers along specific directions in composite manufacturing?",
      "options": [
        {"key": "A", "text": "To make the material completely transparent to air traffic radar signals."},
        {"key": "B", "text": "To align strength and stiffness with anticipated aerodynamic load trajectories."},
        {"key": "C", "text": "To guarantee that the fuselage expands uniformly at high altitudes."},
        {"key": "D", "text": "To allow the aircraft skin to melt harmlessly during atmospheric re-entry."}
      ],
      "correct_answer": "B",
      "explanation_tr": "Karbon Elyaf Takviyeli Polimerler (CFRP) anizotropik bir yapıya sahiptir; bu sayede mühendisler lifleri belirli yönlere dizerek mukavemet ve rijitliği beklenen aerodinamik yük rotalarına göre özelleştirebilirler."
    },
    {
      "id": "lis_itu_02_q2",
      "question": "According to the lecture, what structural proportion and fuel savings do composites achieve in modern commercial jetliners?",
      "options": [
        {"key": "A", "text": "Composites make up over fifty percent of structural weight, saving approximately twenty percent of fuel."},
        {"key": "B", "text": "Composites make up twenty percent of structural weight, saving five percent of fuel."},
        {"key": "C", "text": "Composites make up thirty-five percent of structural weight, saving twelve percent of fuel."},
        {"key": "D", "text": "Composites make up ninety percent of structural weight, saving over fifty percent of fuel."}
      ],
      "correct_answer": "A",
      "explanation_tr": "Ders anlatımında modern uçaklarda (Boeing 787 ve Airbus A350) kompozitlerin toplam gövde ağırlığının %50'sinden fazlasını oluşturduğu ve klasik alüminyum uçaklara kıyasla yaklaşık %20 yakıt tasarrufu sağladığı açıkça ifade edilmiştir."
    },
    {
      "id": "lis_itu_02_q3",
      "question": "What makes 'Barely Visible Impact Damage' particularly hazardous in composite airframes?",
      "options": [
        {"key": "A", "text": "It causes immediate hydraulic system fires in the cockpit."},
        {"key": "B", "text": "It permanently degrades the aircraft's autopilot navigation software."},
        {"key": "C", "text": "It causes external metal plating to corrode instantly when exposed to rain."},
        {"key": "D", "text": "It involves internal layer separation that leaves virtually no external surface mark."}
      ],
      "correct_answer": "D",
      "explanation_tr": "Düşük hızlı çarpmalar sonucu reçine tabakaları arasında iç katman ayrılması (delamination) meydana gelir. Bu hasar dış yüzeyde neredeyse hiç iz bırakmadığı (Barely Visible Impact Damage) için görsel muayeneyle fark edilemez ve büyük tehlike yaratır."
    },
    {
      "id": "lis_itu_02_q4",
      "question": "How do embedded Structural Health Monitoring systems detect internal flaws before failure occurs?",
      "options": [
        {"key": "A", "text": "By requiring ground technicians to dismantle the entire fuselage after every flight."},
        {"key": "B", "text": "By spraying chemical fluorescent dye along exterior wing surfaces during takeoff."},
        {"key": "C", "text": "By using piezoelectric and fiber-optic sensors to monitor acoustic and ultrasonic signals."},
        {"key": "D", "text": "By transmitting high-voltage electrical shocks through the wings to test conductivity."}
      ],
      "correct_answer": "C",
      "explanation_tr": "Gömülü Yapısal Sağlık İzleme (SHM) sistemleri, kompozit katmanlara yerleştirilen piezoelektrik sensörler ve fiber-optik Bragg ızgaraları aracılığıyla akustik emisyonları ve ultrasonik dalgaları sürekli izleyerek arızaları önceden tespit eder."
    }
  ]
}

required_keys = [
    "id", "university_id", "level", "type", "title", "subtitle",
    "target_university", "duration_minutes", "lecture_duration_seconds",
    "instructions_tr", "audio_script", "suggested_notes_tr", "questions"
]

for idx, track in enumerate([t1, t2]):
    print(f"\n--- Checking Track {track['id']} ---")
    for k in required_keys:
        assert k in track, f"Missing key {k}"
        assert track[k] is not None, f"Key {k} is None"
        print(f"Key '{k}': OK")
    
    words = len(track['audio_script'].split())
    print(f"Audio Script Word Count: {words}")
    assert 200 <= words <= 300, f"Audio script words {words} outside 200-300 range"
    
    notes_count = len(track['suggested_notes_tr'])
    print(f"Suggested Notes Count: {notes_count}")
    assert 4 <= notes_count <= 6, f"Suggested notes count {notes_count} outside 4-6"
    
    q_count = len(track['questions'])
    print(f"Questions Count: {q_count}")
    assert q_count == 4, f"Questions count {q_count} != 4"
    
    correct_answers = []
    for q in track['questions']:
        assert len(q['options']) == 4, f"Question {q['id']} options != 4"
        keys = [opt['key'] for opt in q['options']]
        assert keys == ['A', 'B', 'C', 'D'], f"Question {q['id']} keys not ABCD"
        assert q['correct_answer'] in ['A', 'B', 'C', 'D'], f"Question {q['id']} correct answer invalid"
        assert len(q['explanation_tr']) > 20, f"Question {q['id']} explanation too short"
        correct_answers.append(q['correct_answer'])
        print(f"  Question {q['id']}: Valid. Correct={q['correct_answer']}, Text={q['question'][:40]}...")
    
    print(f"Answer distribution: {set(correct_answers)}")
    assert set(correct_answers) == {'A', 'B', 'C', 'D'}, "Not all option letters used"

print("\nSUCCESS: All schema and quality criteria validated with 100% compliance!")

# Integration check with existing listening.json
with open('data/listening.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)

existing_ids = {t['id'] for t in existing}
assert t1['id'] not in existing_ids, "Collision with existing id in t1"
assert t2['id'] not in existing_ids, "Collision with existing id in t2"

combined = existing + [t1, t2]
print(f"Combined tracks count: {len(combined)}")
for track in combined:
    print(f"Track: {track['id']} | Univ: {track['university_id']} | Level: {track['level']} | Questions: {len(track['questions'])}")
