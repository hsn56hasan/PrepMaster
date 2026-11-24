# Ege: Language Use & Grammar %25, Reading Skills %35, Listening %20, Guided Writing %20
UNI = "ege"
ITEMS = [
    ("A1", "Grammar", "The weather in İzmir ____ usually warm and sunny.", "is", ["are", "be", "am"],
     "Özne 'the weather' tekil: 'is'."),
    ("A1", "Grammar", "We ____ swimming at the beach last weekend.", "went", ["go", "goes", "going"],
     "'last weekend' geçmiş zaman: 'went'."),
    ("A1", "Vocabulary", "İzmir is a city next to the ____.", "sea", ["desert", "moon", "snow"],
     "İzmir bir kıyı şehridir: 'next to the sea'."),
    ("A1", "Vocabulary", "The Aegean region is famous for its sweet ____.", "figs", ["chairs", "socks", "clocks"],
     "Ege bölgesi tatlı incirleriyle ünlüdür: 'figs'."),
    ("A2", "Grammar", "Ege University ____ in 1955.", "was founded", ["founded", "is founded", "has founded"],
     "Üniversite kuruldu (edilgen, geçmiş): 'was founded'."),
    ("A2", "Vocabulary", "Farmers in the Aegean region ____ olives in autumn.", "pick", ["drive", "sing", "break"],
     "Zeytin toplamak: 'pick olives'."),
    ("A2", "Dialogue", "A: Is the Bornova campus far from the city centre?\nB: ____\nA: Great, then I'll take the metro tomorrow.",
     "Not really; the metro takes about twenty minutes.",
     ["I'm studying agricultural engineering there.", "I usually have lunch on campus at noon.", "The campus has a very large university hospital."],
     "A 'harika, yarın metroya binerim' diyor; B uzaklığı ve metroyu anlatmış olmalı."),
    ("A2", "Paragraph Completion",
     "Olive oil has been produced in the Aegean region for thousands of years. ____. Today, scientists at Ege University study how to make production cleaner and more efficient.",
     "Ancient people pressed olives with heavy stones to get the oil",
     ["Many tourists visit İzmir's beaches every summer", "Fresh fish is a very popular dish in the coastal restaurants", "The city's football teams have many loyal fans"],
     "Paragraf zeytinyağı üretim tarihini anlatıyor; boşluğa eski üretim yöntemi gelir."),
    ("B2", "Grammar", "The researchers ____ the effects of drought on olive trees for three years before they published their results.",
     "had been studying", ["have been studying", "are studying", "study"],
     "Geçmişteki bir olaydan (yayın) önce süregelen eylem: Past Perfect Continuous."),
    ("B2", "Grammar", "Not only ____ the harvest smaller this year, but the quality of the oil was also lower.", "was",
     ["did", "has", "is"],
     "'Not only' devrik yapı ister; fiil 'be' ve geçmiş: 'was the harvest'."),
    ("B2", "Vocabulary", "Irrigation systems help farmers ____ the effects of dry summers.", "cope with",
     ["come up with", "run out of", "look forward to"],
     "Bir zorlukla başa çıkmak: 'cope with'."),
    ("B2", "Sentence Completion", "Unless farmers adapt to rising temperatures, ____.", "olive production in the region may fall sharply",
     ["olive production will certainly increase greatly", "they will have more water than they ever had", "the climate will soon become much colder"],
     "'Unless' = 'if not': uyum sağlanmazsa üretim düşebilir."),
    ("C2", "Grammar", "But for the cooperative's support, many small farmers ____ their land years ago.", "would have sold",
     ["would sell", "had sold", "will have sold"],
     "'But for' = 'If it hadn't been for'; geçmişe dair gerçekleşmemiş sonuç: 'would have sold'."),
    ("C2", "Vocabulary", "The region's ____ soil, rich in minerals, has supported agriculture for millennia.", "fertile",
     ["barren", "arid", "sterile"],
     "Mineralce zengin ve binlerce yıl tarımı besleyen toprak verimlidir: 'fertile'."),
    ("C2", "Restatement", "Scarcely had the new irrigation system been installed when the drought ended.",
     "The drought ended almost immediately after the new irrigation system was installed.",
     ["The new irrigation system was installed long after the drought had ended.", "The irrigation system was installed because the drought had ended.",
      "The drought continued for years despite the new irrigation system."],
     "'Scarcely ... when' = … olur olmaz; sistem kurulur kurulmaz kuraklık bitti."),
    ("C2", "Paragraph Completion",
     "Climate change is already reshaping Mediterranean agriculture. Warmer winters mean that some olive varieties no longer receive the cold period they need to flower properly. ____. Researchers are therefore testing varieties from hotter regions that may be better suited to future conditions.",
     "Consequently, yields in several traditional growing areas have become less predictable",
     ["Olive trees, however, can live and produce fruit for more than a thousand years", "Warmer winters have therefore greatly improved olive harvests",
      "The Mediterranean diet is famous for being very healthy"],
     "Soğuk dönemin eksikliğinin sonucu (verimin öngörülemez olması) gerekir; ardından yeni çeşit arayışı gelir."),
]
CLOZE = (
    "Ege University is in Bornova, (1) ____ is one of the largest districts of İzmir. It was founded in 1955 with only two faculties: "
    "medicine and agriculture. Today it has (2) ____ than fifteen faculties and a large university hospital. Because İzmir is a popular "
    "city, many students from other parts of Türkiye want (3) ____ there. The university's agricultural research is especially "
    "important (4) ____ the Aegean region produces large amounts of olives, figs and grapes.",
    [
        ("which", ["who", "where", "what"], "Virgüllü sıfat cümlesi Bornova'yı niteliyor ve özne görevinde: 'which'."),
        ("more", ["much", "many", "most"], "'more than fifteen' = on beşten fazla."),
        ("to study", ["studying", "study", "studied"], "'want to + fiil': 'want to study'."),
        ("because", ["although", "unless", "so that"], "Neden bildirir: bölge çok ürün yetiştirdiği için araştırma önemlidir."),
    ],
)
READING = (
    "A Warming Sea\n\nFishermen along Türkiye's Aegean coast have noticed changes that scientists are now documenting systematically. "
    "Species that were once rare in the region, such as certain kinds of rabbitfish, have become common, while some traditional catches "
    "have declined. Many of the newcomers originate in the Red Sea and entered the Mediterranean through the Suez Canal. As sea "
    "temperatures rise, they are able to survive further north than before.\n\nThe arrival of these species is not entirely negative; "
    "some have become valuable catches in local markets. However, others compete with native fish for food or damage seagrass meadows, "
    "which serve as nurseries for young fish. The overall effect on the ecosystem is difficult to predict, partly because records from "
    "earlier decades are incomplete.\n\nResearchers argue that better data are the first priority. Long-term monitoring programmes, in "
    "which fishermen record their catches and scientists track water temperatures, could help authorities adjust fishing quotas before "
    "stocks of native species decline beyond recovery.",
    [
        ("How did many of the new species reach the Mediterranean?", "through the Suez Canal from the Red Sea",
         ["on ships carrying farm products", "by swimming down from the Black Sea", "after fishermen released them deliberately"],
         "Metin: Kızıldeniz kökenli türler Süveyş Kanalı'ndan Akdeniz'e girdi."),
        ("Why are the newcomers now able to live further north?", "because the sea is getting warmer",
         ["because native fish have disappeared", "because fishing quotas have been reduced", "because seagrass meadows have grown larger"],
         "Deniz sıcaklığı arttıkça daha kuzeyde yaşayabiliyorlar."),
        ("According to the passage, why is the overall impact hard to predict?", "Data from earlier decades are incomplete.",
         ["Fishermen refuse to share their catches.", "The new species are impossible to identify.", "Sea temperatures cannot be measured accurately."],
         "Etkiyi öngörmek zor, kısmen önceki on yılların kayıtları eksik olduğu için."),
        ("What do researchers see as the first priority?", "collecting better long-term data",
         ["banning all fishing in the region", "removing every new species from the sea", "building new fish markets on the coast"],
         "'better data are the first priority' — uzun vadeli izleme programları."),
    ],
)
