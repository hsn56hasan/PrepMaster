# Marmara: Use of English %30, Grammar %20, Vocabulary %20, Reading %30
UNI = "marmara"
ITEMS = [
    ("A1", "Grammar", "The Göztepe campus ____ near Kadıköy.", "is", ["are", "be", "am"],
     "Özne 'the campus' tekil: 'is'."),
    ("A1", "Grammar", "We ____ English lessons every morning.", "have", ["has", "having", "is have"],
     "Özne 'we': 'have'."),
    ("A1", "Vocabulary", "We take the ____ across the Bosphorus to get to the European side.", "ferry", ["chair", "lamp", "cake"],
     "Boğaz'ı vapurla geçeriz: 'ferry'."),
    ("A1", "Vocabulary", "Kadıköy is a busy ____ with many shops and cafés.", "district", ["animal", "sandwich", "pencil"],
     "Kadıköy dükkânlarla dolu hareketli bir semttir: 'district'."),
    ("A2", "Grammar", "There aren't ____ seats left in the lecture hall, so some students are standing.", "any",
     ["some", "much", "no"],
     "Olumsuz cümlede 'any' kullanılır: 'aren't any seats'."),
    ("A2", "Grammar", "If it rains tomorrow, we ____ the class trip.", "will cancel", ["cancelled", "would cancel", "cancel will"],
     "Birinci tip koşul: 'If + present, will + V1'."),
    ("A2", "Vocabulary", "I'm ____ in economics, so I'm going to study it at university.", "interested", ["boring", "tired", "afraid"],
     "Bir şeye ilgi duymak: 'be interested in'."),
    ("A2", "Vocabulary", "Students can ____ books from the library for two weeks.", "borrow", ["lend", "sell", "steal"],
     "Kütüphaneden kitap ödünç almak: 'borrow'. 'lend' ödünç vermektir."),
    ("B2", "Grammar", "By the time the ferry arrived, we ____ for almost an hour.", "had been waiting",
     ["have been waiting", "were waiting", "are waiting"],
     "Geçmişteki bir andan önce süregelen eylem: Past Perfect Continuous."),
    ("B2", "Grammar", "The faculty needs more classrooms, ____ is why a new building is being constructed.", "which",
     ["what", "that", "who"],
     "Önceki cümlenin tamamına gönderme yapan 'which is why'."),
    ("B2", "Vocabulary", "The lecture was ____ because of a problem with the projector.", "called off",
     ["called on", "called for", "called back"],
     "'call off' = iptal etmek."),
    ("B2", "Vocabulary", "The university offers ____ for students who cannot afford their tuition fees.", "scholarships",
     ["penalties", "obstacles", "complaints"],
     "Ücret ödeyemeyen öğrencilere burs verilir: 'scholarships'."),
    ("C2", "Grammar", "Were the city ____ more public transport, traffic congestion near the campus would ease.", "to provide",
     ["provided", "providing", "provide"],
     "'Were + özne + to + V1' devrik koşul yapısıdır (If the city were to provide)."),
    ("C2", "Vocabulary", "The economist's forecasts proved remarkably ____, matching the actual figures almost exactly.", "accurate",
     ["erroneous", "misleading", "haphazard"],
     "Gerçek rakamlarla neredeyse birebir örtüşen tahmin isabetlidir: 'accurate'."),
    ("C2", "Vocabulary", "The new policy was introduced to ____ the effects of rising rents on students.", "mitigate",
     ["aggravate", "exacerbate", "intensify"],
     "Kira artışının etkilerini hafifletmek: 'mitigate'. Diğerleri kötüleştirmek anlamındadır."),
    ("C2", "Restatement", "Had the ferry not been delayed, we would have arrived in time for the opening speech.",
     "We missed the opening speech because the ferry was delayed.",
     ["We arrived early for the opening speech because the ferry left on time.",
      "The ferry was delayed, but we still heard the whole opening speech.",
      "We decided not to attend the opening speech even though the ferry was on time."],
     "Devrik üçüncü tip koşul: vapur gecikmeseydi yetişecektik, yani geciktiği için kaçırdık."),
]
CLOZE = (
    "Marmara University traces its history (1) ____ 1883, when a school of commerce was founded in Istanbul. Today it is one of the "
    "largest universities in the city, with campuses on (2) ____ sides of the Bosphorus. Many students live in Kadıköy, (3) ____ they "
    "can easily reach the Göztepe campus. Students often say that the best thing about studying at Marmara is being in a lively city "
    "(4) ____ so many cultural events.",
    [
        ("back to", ["back in", "back on", "back at"], "Tarihini bir yıla dayandırmak: 'trace its history back to'."),
        ("both", ["either", "each", "every"], "İki yakanın ikisinde de: 'both sides' (çoğul isimle)."),
        ("where", ["which", "who", "when"], "Yer bildiren sıfat cümlesi: 'Kadıköy, where they can reach'."),
        ("with", ["of", "by", "from"], "Bir şeye sahip olan şehir: 'a city with many events'."),
    ],
)
READING = (
    "The Price of a Room\n\nIn many large cities, students now spend a greater share of their budgets on housing than on anything "
    "else. As rents rise, some choose to live far from campus and accept long daily commutes, while others share small flats with "
    "several roommates. Surveys in a number of countries suggest that housing stress is linked to lower academic performance, partly "
    "because students who work long hours to pay rent have less time to study.\n\nUniversities have responded in different ways. "
    "Some have built new dormitories, though construction is slow and expensive in crowded city centres. Others have partnered with "
    "local residents through 'homeshare' schemes, in which older people who live alone offer a room at a low price in exchange for "
    "some help around the house and company. Such schemes are modest in scale, but participants on both sides often describe them "
    "as unexpectedly rewarding.\n\nExperts agree that no single solution will be enough. A combination of public investment, private "
    "building and creative arrangements is likely to be needed.",
    [
        ("According to the passage, why may housing stress affect students' grades?", "Students who work to pay rent have less time to study.",
         ["Students who share flats always argue with their roommates.", "Dormitories are too noisy for students to study properly.",
          "Long commutes make students too tired to attend any classes."],
         "Kira için uzun saat çalışan öğrencilerin ders çalışmaya daha az vakti kalıyor."),
        ("What is a disadvantage of building new dormitories mentioned in the passage?", "It is slow and costly in city centres.",
         ["Students do not want to live in them at all.", "They are always located too far from campus.", "Local residents usually oppose them strongly."],
         "Kalabalık şehir merkezlerinde inşaat yavaş ve pahalıdır."),
        ("In a 'homeshare' scheme, students ____.", "pay low rent and help an older person at home",
         ["share a large flat with other students only", "live in a dormitory owned by the city council", "pay no rent but work full-time for the owner"],
         "Yaşlı ev sahibi düşük kirayla oda verir; öğrenci ev işlerinde yardım eder ve arkadaşlık eder."),
        ("What is the author's conclusion?", "A mix of different solutions will be necessary.",
         ["Homeshare schemes alone can solve the problem.", "Universities should stop building any dormitories.", "Students should always live with their parents."],
         "Tek bir çözüm yetmez; kamu, özel sektör ve yaratıcı düzenlemelerin birleşimi gerekir."),
    ],
)
