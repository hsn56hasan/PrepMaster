# Yeditepe: Grammar %25, Vocabulary %20, Reading %35, Restatement/Sentence Completion %20
UNI = "yeditepe"
ITEMS = [
    ("A1", "Grammar", "Yeditepe University ____ on a hill in Ataşehir.", "is", ["are", "am", "be"],
     "Özne tekil: 'is'."),
    ("A1", "Vocabulary", "The dentist looks at your ____.", "teeth", ["shoes", "books", "hair"],
     "Diş hekimi dişlere bakar: 'teeth'."),
    ("A1", "Grammar", "My friends and I ____ lunch together every day.", "have", ["has", "having", "is have"],
     "Özne çoğul ('My friends and I'): 'have'."),
    ("A1", "Vocabulary", "Fine arts students paint ____ in the studio.", "pictures", ["cars", "plates", "phones"],
     "Güzel sanatlar öğrencileri atölyede resim yapar: 'paint pictures'."),
    ("A2", "Restatement", "I prefer studying in the library to studying at home.",
     "I like studying in the library more than studying at home.",
     ["I never study in the library or at home.", "I like studying at home more than studying in the library.", "The library is closer to my home."],
     "'prefer A to B' = A'yı B'ye tercih etmek."),
    ("A2", "Sentence Completion", "The campus is on a hill, so ____.", "you can see a large part of the city from it",
     ["it is the lowest point in the whole city", "you can't see anything from the campus", "nobody can walk to it from anywhere"],
     "Tepede olduğu için şehrin büyük kısmı görülebilir."),
    ("A2", "Grammar", "She has studied dentistry ____ 2022.", "since", ["for", "ago", "during"],
     "Başlangıç noktası (yıl) ile 'since'."),
    ("A2", "Vocabulary", "You should brush your teeth ____ a day.", "twice", ["twelve", "second", "double"],
     "Günde iki kez: 'twice a day'."),
    ("B2", "Restatement", "The patient was told that she must not eat anything for six hours before the operation.",
     "The patient was told to avoid eating for six hours before the operation.",
     ["The patient was told to eat a large meal before the operation.", "The patient was told she could eat whatever she wanted before the operation.",
      "The patient refused to eat for six hours after the operation."],
     "Ameliyattan önce altı saat bir şey yememesi söylendi."),
    ("B2", "Restatement", "Hardly anyone attended the lecture on dental history.",
     "Very few people came to the lecture on dental history.",
     ["The lecture on dental history was very difficult to attend.", "Almost everyone came to the lecture on dental history.",
      "The lecture on dental history was not given by anyone."],
     "'Hardly anyone' = neredeyse hiç kimse; çok az kişi katıldı."),
    ("B2", "Sentence Completion", "In order to reduce the risk of tooth decay, ____.", "people are advised to consume less sugar",
     ["people should eat as much sugar as they can", "dentists recommend never brushing your teeth", "nobody should ever visit a dentist again"],
     "Diş çürüğü riskini azaltmak için daha az şeker önerilir."),
    ("B2", "Vocabulary", "The artist's paintings were ____ in a gallery in Karaköy.", "exhibited", ["inhibited", "prohibited", "exhausted"],
     "Resimler sergilendi: 'exhibited'."),
    ("C2", "Restatement", "Contrary to what many patients assume, a painless tooth is not necessarily a healthy one.",
     "A tooth that does not hurt may still have problems, whatever many patients think.",
     ["Many patients correctly believe that a tooth which causes no pain is always healthy.", "A tooth that hurts is always healthier than a painless one.",
      "Most patients assume that every painful tooth must be removed."],
     "Ağrımayan diş mutlaka sağlıklı değildir; birçok hasta aksini sanar."),
    ("C2", "Restatement", "So convincing was the forgery that even experts were initially deceived.",
     "The fake was so realistic that at first even experts were fooled by it.",
     ["Experts immediately recognised that the painting was a fake when they saw it.", "The forgery was so poor that nobody was deceived by it.",
      "Experts created the forgery in order to deceive collectors."],
     "'So convincing was ...' devrik yapı: sahte eser o kadar inandırıcıydı ki uzmanlar bile başta aldandı."),
    ("C2", "Sentence Completion", "Whatever the critics may say about the exhibition, ____.",
     "it has attracted record numbers of visitors",
     ["the critics have said nothing about it at all", "it has been praised by every critic in the city", "the critics have always agreed with each other"],
     "'Whatever the critics may say' = eleştirmenler ne derse desin; sergi rekor ziyaretçi çekti."),
    ("C2", "Vocabulary", "The gallery's collection includes several works of ____ origin, whose artists remain unknown.", "obscure",
     ["renowned", "celebrated", "eminent"],
     "Sanatçısı bilinmeyen eserler belirsiz kökenlidir: 'obscure'."),
]
CLOZE = (
    "Yeditepe University was founded in 1996 by the Istanbul Education and Culture Foundation. Its campus is located (1) ____ a hill in "
    "Ataşehir, on the Asian side of Istanbul. The university is especially known for its faculties of dentistry and fine arts, "
    "(2) ____ students gain practical experience in clinics and studios. Most programmes are taught in English, so new students must "
    "pass a proficiency exam (3) ____ they can start their departments. The exam includes grammar, vocabulary and reading questions, "
    "(4) ____ as restatement and sentence completion tasks.",
    [
        ("on", ["at", "in", "over"], "Tepenin üzerinde: 'on a hill'."),
        ("where", ["which", "who", "when"], "Fakülteleri niteleyen yer bildiren sıfat cümlesi: 'where'."),
        ("before", ["unless", "although", "since"], "Bölüme başlamadan önce sınav geçilmeli: 'before'."),
        ("as well", ["as long", "as far", "as soon"], "Bunlara ek olarak: 'as well as'."),
    ],
)
READING = (
    "The Placebo Puzzle\n\nIn clinical trials, new drugs are usually compared with placebos, inactive treatments such as sugar pills. "
    "Patients receiving placebos often report real improvements in their symptoms, particularly for conditions like pain, nausea and "
    "anxiety. This placebo effect was long regarded simply as a nuisance that made it harder to measure a drug's true benefits.\n\n"
    "More recent research has treated the effect as a phenomenon worth studying in its own right. Brain imaging shows that expecting "
    "relief can trigger the release of the body's own pain-relieving chemicals. The context of treatment also matters: larger pills, "
    "injections and more expensive-looking packaging have all been associated with stronger placebo responses.\n\nPerhaps most "
    "surprisingly, some studies have found that placebos can work even when patients know they are taking one. These so-called "
    "'open-label' placebos have produced modest benefits in conditions such as chronic back pain. Researchers caution, however, that "
    "placebos cannot shrink tumours or cure infections; their effects are largely limited to how symptoms are experienced.",
    [
        ("How was the placebo effect traditionally viewed?", "as a problem that complicated drug trials",
         ["as the most effective form of treatment", "as a way to cure serious infections", "as a reason to stop all drug trials"],
         "Uzun süre ilacın gerçek faydasını ölçmeyi zorlaştıran bir engel olarak görüldü."),
        ("According to the passage, what can expecting relief cause?", "the release of natural pain-relieving chemicals",
         ["a sudden increase in the size of existing tumours", "a stronger reaction to real drugs", "a complete loss of all symptoms"],
         "Rahatlama beklentisi vücudun kendi ağrı kesici kimyasallarını salgılatabilir."),
        ("Which factor is associated with a stronger placebo response?", "more expensive-looking packaging",
         ["smaller and cheaper-looking pills", "treatment given at home", "shorter clinical trials"],
         "Daha büyük haplar, iğneler ve pahalı görünen ambalajlar daha güçlü tepkiyle ilişkili."),
        ("What is surprising about 'open-label' placebos?", "They can help even when patients know they are placebos.",
         ["They can cure infections that other drugs cannot.", "They are more effective than any real medicine.", "They are given only to patients with tumours."],
         "Hasta plasebo aldığını bilse bile fayda görülebiliyor."),
    ],
)
