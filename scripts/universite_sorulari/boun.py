# BUEPT: Reading (Selective & Careful) %33, Listening %33, Writing %34 -> okuma becerisi ağırlıklı
UNI = "boun"
ITEMS = [
    ("A1", "Vocabulary", "From the South Campus, students can watch big ____ passing on the Bosphorus.", "ships", ["trees", "houses", "trains"],
     "Boğaz'dan geçen büyük taşıtlar gemilerdir: 'ships'."),
    ("A1", "Vocabulary", "Albert Long Hall is a ____ where students listen to concerts and talks.", "building", ["river", "sandwich", "pencil"],
     "Konser ve konuşmaların yapıldığı yer bir binadır: 'building'."),
    ("A1", "Grammar", "Look! The students ____ a play in front of the library now.", "are performing", ["perform", "performed", "is performing"],
     "'Look!' ve 'now' şu anda olan eylemi gösterir: Present Continuous."),
    ("A1", "Grammar", "Boğaziçi is ____ old university with beautiful stone buildings.", "an", ["a", "some", "any"],
     "'old' ünlüyle başladığı için 'an' kullanılır."),
    ("A2", "Vocabulary", "I always ____ my essays carefully before I hand them in.", "check", ["lose", "forget", "break"],
     "Teslim etmeden önce ödevi kontrol etmek: 'check'."),
    ("A2", "Grammar", "The campus is ____ than I expected; it takes twenty minutes to walk across it.", "bigger", ["big", "biggest", "more big"],
     "'than' karşılaştırma ister; tek heceli sıfat: 'bigger'."),
    ("A2", "Dialogue", "A: How was your first BUEPT practice test?\nB: ____\nA: Don't worry, the listening part gets easier with practice.",
     "The reading was fine, but the listening was hard.",
     ["I bought the practice book from the campus shop.", "The test starts at nine o'clock tomorrow.", "I don't think I'll study at Boğaziçi next year."],
     "A'nın 'dinleme kısmı pratikle kolaylaşır' cevabı, B'nin dinlemede zorlandığını söylediğini gösterir."),
    ("A2", "Paragraph Completion",
     "Many students at Boğaziçi live in dormitories near the campus. ____. Because of this, they often study together in the evenings and become close friends.",
     "They share rooms and eat their meals together in the same dining hall",
     ["The city of Istanbul has a population of more than fifteen million", "Some students prefer to travel abroad during the long summer holiday",
      "The university first opened as an American college in the nineteenth century"],
     "Akşam birlikte çalışıp arkadaş olmalarının nedeni oda ve yemekhaneyi paylaşmalarıdır."),
    ("B2", "Vocabulary", "The lecturer asked us to ____ the article quickly to find the year the study was published.", "scan",
     ["summarise", "memorise", "translate"],
     "Belirli bir bilgiyi bulmak için metne hızla göz gezdirmek 'scan' denir (seçici okuma)."),
    ("B2", "Vocabulary", "The author's ____ is clear from the first paragraph: she believes the policy will fail.", "stance",
     ["audience", "glossary", "appendix"],
     "Yazarın konuya karşı tutumu 'stance' olarak adlandırılır."),
    ("B2", "Sentence Completion", "While the first study found a strong link between social media use and anxiety, ____.",
     "the second found no significant relationship at all",
     ["it also found that social media use was linked to anxiety", "many teenagers use social media every single day", "the researchers published their results in 2019"],
     "'While' burada zıtlık bildirir; ikinci çalışmanın farklı sonuç bulması gerekir."),
    ("B2", "Paragraph Completion",
     "Selective reading is a key skill in the BUEPT. Instead of reading a text from beginning to end, students look for specific information. ____. With practice, students can answer these questions much faster than by careful reading.",
     "For example, they may search for names, dates or numbers in the question",
     ["Careful reading, by contrast, is rarely needed in university courses", "The BUEPT is taken by thousands of students every single year",
      "Some students prefer reading novels to articles in their free time"],
     "Belirli bilgi aramayı örnekleyen cümle gerekir: isim, tarih, sayı aramak."),
    ("C2", "Vocabulary", "The novel's ending is deliberately ____, leaving readers to decide for themselves what happened to the narrator.",
     "ambiguous", ["conclusive", "explicit", "predictable"],
     "Okura karar bırakan son, bilinçli olarak belirsizdir: 'ambiguous'."),
    ("C2", "Vocabulary", "Critics ____ the historian for relying on a single, possibly biased source.", "faulted", ["credited", "acquitted", "commended"],
     "Tek ve taraflı olabilecek kaynağa dayanmak eleştirilir: 'fault someone for' = kusurlu bulmak."),
    ("C2", "Restatement", "Far from being a neutral record of events, the diary reflects its author's political sympathies at every turn.",
     "The diary is not an objective account; the author's political views shape it throughout.",
     ["The diary is a neutral record that never reveals its author's political views.", "The author kept the diary only to record the political events of the time.",
      "Readers have found it difficult to identify any political views in the diary."],
     "'Far from being neutral' = tarafsız olmak şöyle dursun; günlük yazarın siyasi eğilimini her yerde yansıtır."),
    ("C2", "Paragraph Completion",
     "Historians increasingly treat oral testimony as a legitimate source rather than a mere supplement to written archives. ____. Nonetheless, they caution that memories are reshaped over time and must be checked against other evidence.",
     "Interviews can capture the experiences of groups who left few written records",
     ["Written archives, however, are always complete and free from any bias", "Most historians therefore refuse to use interviews in their research",
      "Oral history became popular soon after the invention of printing"],
     "Sözlü tanıklığın neden meşru kaynak sayıldığını açıklayan cümle gerekir; ardından 'Nonetheless' ile sınırlılığı geliyor."),
]
CLOZE = (
    "Boğaziçi University began life in 1863 as Robert College, (1) ____ was one of the first American schools founded outside the "
    "United States. In 1971, the college buildings (2) ____ to the Turkish state, and the university received its present name. "
    "Today, the language of instruction is still English, so new students must show that their English is good (3) ____ to follow "
    "their courses. Those who do not pass the BUEPT study at the School of Foreign Languages (4) ____ they reach the required level.",
    [
        ("which", ["who", "where", "what"], "Virgüllü sıfat cümlesi kuruma (Robert College) gönderme yapıyor: 'which'."),
        ("were transferred", ["transferred", "were transferring", "have transferred"],
         "Binalar devredildi (edilgen), 1971 geçmiş zaman: 'were transferred'."),
        ("enough", ["too", "so", "very"], "'good enough to follow' = takip edecek kadar iyi."),
        ("until", ["unless", "since", "while"], "Gerekli seviyeye ulaşıncaya KADAR hazırlıkta okurlar: 'until'."),
    ],
)
READING = (
    "The Two Currents of the Bosphorus\n\nTo a visitor watching from the hills of Bebek, the Bosphorus looks like a single river "
    "flowing towards the Sea of Marmara. In reality, the strait contains two currents moving in opposite directions. Because the "
    "Black Sea receives large amounts of fresh water from rivers such as the Danube, its surface water is less salty and therefore "
    "lighter. This water flows south along the surface. Beneath it, denser, saltier water from the Mediterranean moves north "
    "towards the Black Sea.\n\nFishermen have exploited this phenomenon for centuries; there are accounts of nets being lowered "
    "into the deep current so that boats could be pulled northwards against the surface flow. For scientists, the system is of "
    "more than local interest. The exchange of water through the strait regulates the salinity of the Black Sea, and changes in "
    "river flow caused by dams or climate change could therefore alter the ecology of the entire basin. Monitoring stations along "
    "the Bosphorus now measure both currents continuously.",
    [
        ("According to the passage, why does the surface water flow south?", "It is lighter because rivers make it less salty.",
         ["It is pushed by strong winds from the north.", "It is heavier than the water from the Mediterranean.", "Fishermen pull it south with their nets."],
         "Nehirlerden gelen tatlı su yüzey suyunu daha az tuzlu ve hafif yapar; bu su güneye akar."),
        ("The example of the fishermen is used to show that ____.", "the deep current has long been known and used",
         ["fishing is no longer possible in the Bosphorus", "the surface current is stronger than the deep one", "boats cannot travel north through the strait"],
         "Ağların derin akıntıya indirilmesi, akıntının yüzyıllardır bilinip kullanıldığını gösterir."),
        ("It can be inferred that dams on rivers flowing into the Black Sea might ____.", "affect how salty the Black Sea becomes",
         ["stop the surface current from moving south", "make the Bosphorus easier for ships to cross", "increase the number of fish in the Marmara"],
         "Barajlar tatlı su akışını değiştirir; metin bunun Karadeniz'in tuzluluğunu etkileyebileceğini söylüyor."),
        ("The word 'exploited' in the second paragraph is closest in meaning to ____.", "made practical use of",
         ["seriously damaged", "carefully measured", "deliberately ignored"],
         "Balıkçılar akıntıdan pratik olarak yararlanmış: 'exploit' burada 'faydalanmak' anlamında."),
    ],
)
