# Gebze Teknik: Grammar %25, Vocabulary %20, Reading %35, Restatement/Sentence Completion %20
UNI = "gebze_teknik"
ITEMS = [
    ("A1", "Grammar", "Gebze ____ many big factories.", "has", ["have", "is", "are"],
     "Özne 'Gebze' tekil: 'has'."),
    ("A1", "Vocabulary", "Workers in a ____ make cars, machines and other products.", "factory", ["library", "beach", "kitchen"],
     "Ürünler fabrikada yapılır: 'factory'."),
    ("A1", "Grammar", "I ____ an engineering student.", "am", ["is", "are", "be"],
     "Özne 'I': 'am'."),
    ("A1", "Vocabulary", "Our chemistry ____ is on the first floor.", "laboratory", ["kitchen", "garden", "bedroom"],
     "Kimya dersi laboratuvarda yapılır: 'laboratory'."),
    ("A2", "Restatement", "The train from Gebze to Istanbul takes less than an hour.",
     "You can travel from Gebze to Istanbul by train in under an hour.",
     ["The train from Gebze to Istanbul takes more than an hour.", "There is no train between Gebze and Istanbul.",
      "The bus from Gebze to Istanbul is faster than the train."],
     "'less than an hour' = bir saatten az."),
    ("A2", "Sentence Completion", "I want to work in a technology company, so ____.", "I'm studying computer engineering",
     ["I'm going to become a professional cook", "I don't like computers at all", "I never use any technology"],
     "Teknoloji şirketinde çalışmak isteyen biri bilgisayar mühendisliği okur."),
    ("A2", "Grammar", "The new laboratory is ____ modern than the old one.", "more", ["most", "much", "many"],
     "Uzun sıfatlarda karşılaştırma: 'more modern than'."),
    ("A2", "Vocabulary", "Many engineers in Gebze ____ in the car industry.", "work", ["swim", "sleep", "dance"],
     "Mühendisler otomotiv sektöründe çalışır: 'work in'."),
    ("B2", "Restatement", "The company will not hire graduates unless they have completed an internship.",
     "Graduates must complete an internship if they want to be hired by the company.",
     ["The company hires graduates who have never done an internship.", "Graduates who complete an internship cannot work for the company.",
      "The company offers internships only to graduates it has already hired."],
     "'unless' = 'if not'; staj yapmadıkça işe alınmazlar."),
    ("B2", "Restatement", "The project was so complex that it took the team two years to complete.",
     "Because of its complexity, the team needed two years to finish the project.",
     ["The project was simple, so the team finished it in two weeks.", "The team refused to work on the project because it was complex.",
      "The project took two years to start because the team was far too small."],
     "'so ... that' sonuç bildirir: proje karmaşık olduğu için iki yıl sürdü."),
    ("B2", "Sentence Completion", "Provided that the prototype passes the final tests, ____.", "mass production will begin next spring",
     ["it failed all of the tests last year", "the tests have already been cancelled", "nobody will ever test it again"],
     "'Provided that' = 'şartıyla'; testleri geçerse seri üretim başlayacak."),
    ("B2", "Vocabulary", "Robots have ____ many repetitive tasks in modern factories.", "taken over",
     ["taken after", "taken apart", "taken in"],
     "Bir işi devralmak: 'take over'."),
    ("C2", "Restatement", "It was not until the materials were tested at high temperatures that their weakness became evident.",
     "The materials' weakness was only revealed when they were tested at high temperatures.",
     ["The materials were clearly weak before any tests were carried out.", "High temperatures made the materials stronger than expected.",
      "Nobody tested the materials at high temperatures because they were already known to be weak."],
     "'It was not until ... that' = ancak … olunca."),
    ("C2", "Restatement", "Whereas traditional manufacturing relies on cutting material away, 3D printing builds objects layer by layer.",
     "Unlike traditional manufacturing, which removes material, 3D printing adds layers.",
     ["Both traditional manufacturing and 3D printing remove material to make objects.", "3D printing cuts material away, while traditional methods add layers.",
      "Traditional manufacturing has been completely replaced by 3D printing."],
     "'Whereas' karşıtlık: geleneksel üretim malzeme çıkarır, 3B baskı katman ekler."),
    ("C2", "Sentence Completion", "Even if automation reduces the number of factory jobs, ____.",
     "new roles are likely to emerge in maintenance and programming",
     ["it will certainly increase the number of factory workers", "factories will need more workers than they ever did",
      "no factory will ever use robots or automation"],
     "'Even if' = -se bile; iş azalsa bile bakım ve programlamada yeni roller çıkabilir."),
    ("C2", "Vocabulary", "The firm's success can be ____ to its heavy investment in research and development.", "attributed",
     ["contributed", "distributed", "submitted"],
     "Başarıyı bir şeye bağlamak: 'attribute to'."),
]
CLOZE = (
    "Gebze Technical University is located in Kocaeli, one of Türkiye's most important (1) ____ regions. Hundreds of factories "
    "operate nearby, (2) ____ gives students many opportunities for internships. The university works closely with technology "
    "companies and research centres, and many of its graduates find jobs (3) ____ after graduation. Because Gebze is between Istanbul "
    "and Kocaeli, students can travel to (4) ____ city easily by train.",
    [
        ("industrial", ["industry", "industrially", "industrious"], "İsimden önce sıfat: 'industrial regions'."),
        ("which", ["what", "who", "that"], "Önceki cümlenin tamamına gönderme: ', which gives'."),
        ("soon", ["yet", "still", "ever"], "Mezuniyetten kısa süre sonra: 'soon after'."),
        ("either", ["both", "neither", "each other"], "İki şehirden herhangi birine: 'either city' (tekil isimle)."),
    ],
)
READING = (
    "Collaborative Robots\n\nFor decades, industrial robots worked behind safety fences. They were powerful, fast and precise, but "
    "potentially dangerous to any human who came too close. A newer generation of machines, known as collaborative robots or "
    "'cobots', is designed to work directly alongside people. Equipped with sensors that detect contact, cobots slow down or stop "
    "immediately if they touch a worker.\n\nCobots are typically smaller and less powerful than traditional robots, and they are not "
    "intended to replace entire production lines. Instead, they take on specific tasks that are repetitive or physically demanding, "
    "such as lifting parts or tightening screws, while humans handle work that requires judgement or dexterity. Because they can be "
    "reprogrammed relatively easily, they are particularly attractive to small and medium-sized firms that produce varied products in "
    "small quantities.\n\nCritics note that the safety features limit cobots' speed, so for high-volume manufacturing traditional robots "
    "remain more efficient. Supporters respond that the real value of cobots lies in flexibility rather than speed.",
    [
        ("What is the main difference between cobots and traditional industrial robots?", "Cobots are designed to work safely near people.",
         ["Cobots are larger and much more powerful.", "Cobots never need to be reprogrammed again.", "Cobots replace whole production lines alone."],
         "Cobotlar insanlarla yan yana güvenle çalışmak üzere tasarlanmıştır."),
        ("According to the passage, which task is a cobot most likely to perform?", "tightening screws on an assembly line",
         ["deciding which products the firm should make", "designing new products for small companies", "checking the quality of a finished design"],
         "Cobotlar vida sıkma gibi tekrarlı işleri üstlenir."),
        ("Why are cobots attractive to small and medium-sized firms?", "They can be reprogrammed easily for different products.",
         ["They are faster than all other types of robots.", "They do not need any electricity to operate.", "They can work for long periods without any human workers."],
         "Kolayca yeniden programlanabildikleri için az miktarda çeşitli ürün yapan firmalara uygundur."),
        ("What do supporters say in response to critics?", "Cobots are valuable mainly because they are flexible.",
         ["Cobots are actually faster than traditional robots.", "Traditional robots are too dangerous to be used.", "Cobots will soon be used for all mass production."],
         "Destekçilere göre cobotların asıl değeri hız değil esnekliktir."),
    ],
)
