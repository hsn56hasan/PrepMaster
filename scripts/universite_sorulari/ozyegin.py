# Özyeğin: Reading %30, Listening %25, Writing %25, Speaking %20
UNI = "ozyegin"
ITEMS = [
    ("A1", "Grammar", "Özyeğin University ____ in Çekmeköy, on the Asian side of Istanbul.", "is", ["are", "am", "be"],
     "Özne tekil: 'is'."),
    ("A1", "Grammar", "____ your name, please?", "What's", ["Who's", "Where's", "How's"],
     "İsim sormak: 'What's your name?'."),
    ("A1", "Vocabulary", "I listen to English podcasts on my ____ every day.", "phone", ["table", "pillow", "spoon"],
     "Podcast telefonda dinlenir: 'phone'."),
    ("A1", "Vocabulary", "The campus has a lot of trees and green ____.", "areas", ["clouds", "letters", "tickets"],
     "Yeşil alanlar: 'green areas'."),
    ("A2", "Dialogue", "A: How long have you been learning English?\nB: ____\nA: Wow, that's a long time!",
     "For about eight years now.", ["Last summer in London.", "With my friends at school.", "Because I like it a lot."],
     "'How long' süre sorar; cevap süre bildirmeli."),
    ("A2", "Dialogue", "A: Would you like to join our study group?\nB: ____\nA: Great, we meet every Tuesday at five.",
     "I'd love to. When do you meet?",
     ["No, I don't like studying at all.", "I studied at the library yesterday.", "My group is in another building."],
     "A buluşma gününü söylüyor; B katılmayı kabul edip zamanını sormuş olmalı."),
    ("A2", "Grammar", "I'm really looking forward ____ my new classmates.", "to meeting", ["to meet", "meeting", "for meet"],
     "'look forward to' + -ing: 'to meeting'."),
    ("A2", "Vocabulary", "In the speaking exam, try to ____ eye contact with the examiner.", "make", ["do", "take", "give"],
     "Göz teması kurmak: 'make eye contact'."),
    ("B2", "Vocabulary", "In the listening section, you should ____ the questions before the recording starts.", "skim",
     ["ignore", "erase", "postpone"],
     "Kayıt başlamadan sorulara hızlıca göz atmak: 'skim'."),
    ("B2", "Grammar", "The examiner asked me what I ____ to do after graduation.", "planned",
     ["plan", "did I plan", "am planning"],
     "Dolaylı soruda zaman bir geri kayar ve devrik olmaz: 'what I planned'."),
    ("B2", "Sentence Completion", "If you don't understand a question in the speaking exam, ____.",
     "it is acceptable to ask the examiner to repeat it",
     ["you should stay silent until the time runs out", "you must leave the room and come back later", "the examiner will give you zero points at once"],
     "Anlamadığın soruyu tekrarlatmak kabul edilebilir bir stratejidir."),
    ("B2", "Paragraph Completion",
     "Özyeğin University's campus was designed with sustainability in mind. ____. As a result, the buildings use considerably less energy than conventional ones.",
     "Many buildings use solar energy, natural ventilation and good insulation",
     ["Students can take a shuttle bus from the metro station", "The university also offers programmes in aviation and hospitality",
      "Most students live with their families in Istanbul"],
     "'As a result' enerji tasarrufunu sonuç olarak veriyor; neden güneş enerjisi ve yalıtım gibi önlemlerdir."),
    ("C2", "Vocabulary", "The speaker's argument was so ____ that even sceptical listeners were convinced.", "compelling",
     ["unconvincing", "tedious", "far-fetched"],
     "Şüphecileri bile ikna eden argüman etkileyicidir: 'compelling'."),
    ("C2", "Vocabulary", "Her answers in the interview were ____, showing a clear and logical line of thought.", "coherent",
     ["rambling", "disjointed", "muddled"],
     "Açık ve mantıklı düşünce akışı tutarlılığı gösterir: 'coherent'."),
    ("C2", "Restatement", "Green buildings cost more to construct, but the savings on energy bills usually more than make up for this.",
     "Green buildings cost more to build, but their energy savings usually exceed the extra cost.",
     ["Green buildings are cheaper to build but more expensive to run.", "The energy savings of green buildings rarely cover their much higher construction costs.",
      "Green buildings cost the same to build and run as other buildings."],
     "'more than make up for' = fazlasıyla telafi etmek; enerji tasarrufu ek maliyeti aşar."),
    ("C2", "Paragraph Completion",
     "Listening in a foreign language is demanding partly because speech, unlike text, cannot be reread. ____. Skilled listeners compensate by predicting what speakers are likely to say next.",
     "Listeners must process information in real time as it arrives",
     ["Most people find reading much easier than writing essays", "Therefore, listening is always easier than reading for students",
      "Many universities test listening as part of their exams"],
     "Konuşma tekrar okunamaz; dinleyici bilgiyi geldiği anda işlemelidir."),
]
CLOZE = (
    "Özyeğin University was founded in 2007 by the Hüsnü M. Özyeğin Foundation. Its campus in Çekmeköy is known (1) ____ its modern, "
    "environmentally friendly buildings. All students must show that their English is good enough (2) ____ courses taught in English. "
    "The proficiency exam tests reading, listening, writing and speaking, and students who do not pass (3) ____ the English preparatory "
    "programme. Many students say that the speaking section helps them become (4) ____ confident.",
    [
        ("for", ["as", "by", "with"], "'be known for' kalıbı."),
        ("to follow", ["following", "follow", "followed"], "'good enough to + fiil'."),
        ("attend", ["attending", "attended", "to attend"], "Özne 'students who do not pass' + geniş zaman: 'attend'."),
        ("more", ["most", "much", "many"], "'become more confident' karşılaştırma."),
    ],
)
READING = (
    "Accent and Understanding\n\nMany language learners worry that their accent will prevent others from understanding them. Research "
    "suggests that this concern, while understandable, is often misplaced. Linguists distinguish between accentedness, how different "
    "a speaker sounds from a particular standard, and intelligibility, how easily listeners understand them. The two are related but "
    "far from identical: speakers with strong accents are frequently perfectly easy to understand.\n\nWhat matters most for "
    "intelligibility appears to be a relatively small set of features, such as stressing the right syllable in a word and pausing in "
    "sensible places. Errors in these areas can confuse listeners even when individual sounds are pronounced accurately. By contrast, "
    "many features that make an accent noticeable have little effect on comprehension.\n\nFor teachers and learners, the implication is "
    "that pronunciation practice should focus on the features that affect understanding, rather than on eliminating every trace of a "
    "first-language accent, a goal that few adult learners achieve and that is rarely necessary.",
    [
        ("What is the difference between accentedness and intelligibility?", "One is how different a speaker sounds; the other is how easily they are understood.",
         ["One concerns grammar mistakes; the other concerns the speed of someone's speech.",
          "One is measured by teachers; the other is measured by the learners themselves.",
          "One applies to native speakers; the other applies only to language learners."],
         "Aksanlılık standarttan farklı duyulma, anlaşılırlık kolay anlaşılmadır."),
        ("According to the passage, speakers with strong accents ____.", "can often be understood without difficulty",
         ["are always difficult for listeners to follow", "should avoid speaking in public until fluent", "usually make more grammar mistakes than others"],
         "Güçlü aksanlı konuşanlar çoğu zaman gayet kolay anlaşılır."),
        ("Which feature is mentioned as important for being understood?", "stressing the correct syllable in words",
         ["using a very wide range of vocabulary", "speaking as fast as native speakers do", "pronouncing every sound perfectly well"],
         "Kelimede doğru heceyi vurgulamak anlaşılırlık için önemlidir."),
        ("What does the author recommend?", "focusing on features that affect understanding",
         ["removing every trace of a first-language accent", "practising only individual sounds every day", "avoiding all pronunciation practice entirely"],
         "Telaffuz çalışması anlaşılırlığı etkileyen özelliklere odaklanmalı."),
    ],
)
