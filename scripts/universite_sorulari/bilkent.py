# Bilkent COPE/PAE: Reading & Text Analysis %35, Listening %25, Academic Writing %40 (Part A: dil bilgisi + kelime)
UNI = "bilkent"
ITEMS = [
    ("A1", "Grammar", "Bilkent ____ two campuses in Ankara.", "has", ["have", "having", "is have"],
     "Özne 'Bilkent' tekil; geniş zamanda 'has' kullanılır."),
    ("A1", "Grammar", "____ you like the concert last night?", "Did", ["Do", "Were", "Are"],
     "'last night' geçmiş zaman; soru 'Did + özne + yalın fiil' ile kurulur."),
    ("A1", "Vocabulary", "The orchestra plays classical ____ in the concert hall.", "music", ["football", "bread", "weather"],
     "Orkestra klasik müzik çalar: 'classical music'."),
    ("A1", "Vocabulary", "I'm ____ because I didn't eat breakfast this morning.", "hungry", ["tall", "early", "quiet"],
     "Kahvaltı etmeyen kişi açtır: 'hungry'."),
    ("A2", "Grammar", "I have studied at Bilkent ____ 2024.", "since", ["for", "ago", "during"],
     "Present Perfect ile başlangıç noktası (2024) 'since' ile verilir."),
    ("A2", "Grammar", "You ____ smoke anywhere on the campus; it is not allowed.", "can't", ["don't have to", "should", "must"],
     "İzin verilmeyen şey için 'can't' (yapamazsın) kullanılır."),
    ("A2", "Vocabulary", "The library is ____ 24 hours a day during exam week.", "open", ["empty", "noisy", "expensive"],
     "Sınav haftasında 24 saat açık olan kütüphane: 'open'."),
    ("A2", "Sentence Completion", "I joined the university choir ____.", "because I love singing with other people",
     ["although I love singing with other people", "so I don't really like music at all", "but I already sang in the choir"],
     "Koroya katılmanın mantıklı nedeni başkalarıyla şarkı söylemeyi sevmektir."),
    ("B2", "Grammar", "By the time she graduates, she ____ at Bilkent for five years.", "will have studied",
     ["will be studying", "has studied", "studied"],
     "Gelecekteki bir ana kadar tamamlanmış süre: Future Perfect 'will have studied'."),
    ("B2", "Vocabulary", "The orchestra's performance received ____ reviews; every critic praised it.", "glowing",
     ["mixed", "hostile", "lukewarm"],
     "Bütün eleştirmenlerin övdüğü yorumlar 'glowing' (övgü dolu) olur."),
    ("B2", "Vocabulary", "Students are expected to ____ all the sources they use in their essays to avoid plagiarism.", "cite",
     ["delete", "invent", "hide"],
     "İntihalden kaçınmak için kaynaklar gösterilir: 'cite sources'."),
    ("B2", "Restatement", "It's not worth taking a taxi to the East Campus; the shuttle is just as quick.",
     "The shuttle is as quick as a taxi, so there is no need to take one.",
     ["A taxi is much faster than the shuttle to the East Campus.", "There is no shuttle service to the East Campus at the moment.",
      "It is worth paying for a taxi because the shuttle is very slow."],
     "'not worth' = değmez; servis taksi kadar hızlı olduğu için taksiye gerek yok."),
    ("C2", "Grammar", "Were the university ____ its tuition fees, many students would struggle to continue their studies.", "to raise",
     ["raises", "raising", "had raised"],
     "'Were + özne + to + fiil' devrik koşul yapısıdır (If the university were to raise)."),
    ("C2", "Vocabulary", "The conductor was known for his ____ attention to detail, rehearsing a single bar for an hour if necessary.",
     "meticulous", ["cursory", "haphazard", "perfunctory"],
     "Tek bir ölçüyü bir saat çalıştırmak titizliktir: 'meticulous'."),
    ("C2", "Paragraph Completion",
     "Founded in 1984, Bilkent was the first non-profit foundation university in Türkiye. ____. Its model was later followed by dozens of other institutions, changing the landscape of Turkish higher education.",
     "It showed that a privately funded university could reach high academic standards",
     ["Before 1984, there were no universities at all in the capital city of Ankara", "Consequently, all state universities were closed during the following decade",
      "The main campus is located on the western side of the capital city"],
     "Sonraki cümle modelin örnek alındığını söylüyor; boşluk modelin başarısını göstermeli."),
    ("C2", "Paragraph Completion",
     "Live music is often thought to benefit performers more than audiences. ____. Researchers measuring heart rates during a symphony concert found that listeners' pulses tended to synchronise at emotionally intense moments.",
     "Yet there is growing evidence that attending a concert has measurable effects on listeners",
     ["Most orchestras, however, perform only in very large and wealthy capital cities", "Recorded music is therefore always preferred by most audiences",
      "Symphony orchestras usually consist of about eighty musicians"],
     "Yaygın görüşe karşı çıkan ('Yet') ve dinleyici üzerindeki etkiyi tanıtan cümle gerekir; ardından nabız araştırması geliyor."),
]
CLOZE = (
    "Bilkent University was founded in 1984 by Professor İhsan Doğramacı. It was the first private university in Türkiye (1) ____ was "
    "set up by a foundation. Its name comes from the words 'bilim' and 'kent', which (2) ____ 'science' and 'city' in English. The "
    "university is (3) ____ known for its music department, and its symphony orchestra gives concerts every week. Students (4) ____ "
    "want to study there must show a good level of English.",
    [
        ("that", ["what", "where", "whose"], "Tanımlayıcı sıfat cümlesi 'university'yi niteler: 'that'."),
        ("mean", ["means", "meaning", "to mean"], "Özne 'which' = 'the words' (çoğul): 'which mean'."),
        ("also", ["too", "either", "yet"], "Cümle ortasında 'ayrıca' anlamında 'also' kullanılır."),
        ("who", ["which", "whose", "what"], "İnsanları niteleyen sıfat cümlesi: 'Students who want'."),
    ],
)
READING = (
    "The Language of Caution\n\nReaders new to academic texts are often surprised by how rarely scientists make direct claims. "
    "Instead of writing 'X causes Y', researchers prefer phrases such as 'X may contribute to Y' or 'the results suggest a possible "
    "link'. This habit, known as hedging, is sometimes mistaken for weakness or indecision. In fact, it reflects the cautious nature "
    "of scientific knowledge: a single study can rarely prove a general claim, and overstated conclusions are quickly challenged by "
    "other researchers.\n\nHedging also has a social function. By softening their claims, writers show respect for the reader's "
    "judgement and leave room for disagreement, which can make their arguments more persuasive rather than less. However, excessive "
    "hedging carries its own risks. A paper in which every sentence is qualified can leave readers unsure of what the author actually "
    "believes. Skilled writers therefore hedge selectively, stating well-established facts firmly and reserving cautious language for "
    "genuinely uncertain findings.",
    [
        ("According to the passage, why do scientists use hedging?", "Because single studies seldom prove general claims.",
         ["Because they doubt their own research methods.", "Because journals do not permit direct claims.", "Because readers prefer short, simple sentences."],
         "Metin: tek bir çalışma genel bir iddiayı nadiren kanıtlar; temkinli dil bundan doğar."),
        ("The 'social function' of hedging is that it ____.", "acknowledges that readers may hold different views",
         ["allows authors to avoid all criticism", "makes academic texts shorter and clearer", "hides the author's real opinion from readers"],
         "Temkinli dil okurun yargısına saygı gösterir ve itiraza yer bırakır."),
        ("What problem does the author associate with excessive hedging?", "Readers may not know the writer's actual position.",
         ["Papers become too short to be published.", "Other researchers stop citing the paper.", "Writers are forced to state facts too firmly."],
         "Her cümlenin sınırlandırıldığı bir makalede okur yazarın gerçekte ne düşündüğünü anlayamaz."),
        ("The phrase 'hedge selectively' in the last sentence means that skilled writers ____.",
         "use cautious language only where findings are uncertain",
         ["never use any cautious language in their research papers", "qualify every sentence that they write", "avoid stating well-established facts"],
         "Yerleşik gerçekleri net söyler, temkinli dili yalnızca belirsiz bulgulara ayırırlar."),
    ],
)
