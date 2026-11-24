# Hacettepe: Use of English & Vocabulary %25, Listening %25, Reading %30, Academic Writing %20
UNI = "hacettepe"
ITEMS = [
    ("A1", "Grammar", "The children's hospital ____ near the Sıhhiye metro station.", "is", ["are", "be", "am"],
     "Özne 'the hospital' tekil: 'is'."),
    ("A1", "Grammar", "Can you ____ the board from the back row?", "see", ["sees", "seeing", "saw"],
     "'can' kipinden sonra fiil yalın gelir: 'can you see'."),
    ("A1", "Vocabulary", "When you are ill, you go to see a ____.", "doctor", ["teacher", "farmer", "driver"],
     "Hasta olunca doktora gidilir: 'doctor'."),
    ("A1", "Vocabulary", "The Beytepe campus is very ____; it takes a long time to walk across it.", "large", ["small", "short", "quick"],
     "Yürüyerek geçmesi uzun süren kampüs büyüktür: 'large'."),
    ("A2", "Grammar", "Medical students must ____ hard to pass their anatomy exams.", "study", ["studies", "studying", "studied"],
     "'must' kipinden sonra yalın fiil: 'must study'."),
    ("A2", "Vocabulary", "Wash your hands before you ____ the patient's room.", "enter", ["invite", "cook", "borrow"],
     "Hasta odasına girmeden önce: 'enter the room'."),
    ("A2", "Dialogue", "A: I've got a terrible headache.\nB: ____\nA: Good idea. I'll go to the health centre after this lecture.",
     "Why don't you see a doctor about it?",
     ["I bought a new phone last week, look.", "Our next lecture starts at ten o'clock.", "My sister studies nursing at Hacettepe."],
     "A 'iyi fikir, sağlık merkezine gideceğim' diyor; B doktora gitmeyi önermiş olmalı."),
    ("A2", "Dialogue", "A: Could you speak a bit more slowly, please?\nB: ____\nA: Thanks, that's much easier to follow.",
     "Of course. Is this better?", ["No, the lecture is in English.", "I'm from Ankara, actually.", "Yes, I'm in my fourth year."],
     "A 'teşekkürler, şimdi daha kolay' diyor; B yavaşlamayı kabul etmiş olmalı."),
    ("B2", "Grammar", "The new vaccine, ____ trials were completed last year, is now being used in hospitals.", "whose",
     ["which", "that", "who"],
     "Denemeler aşıya ait; iyelik bildiren 'whose'."),
    ("B2", "Vocabulary", "Smoking significantly ____ the risk of heart disease.", "increases", ["prevents", "cures", "lowers"],
     "Sigara kalp hastalığı riskini artırır: 'increases the risk'."),
    ("B2", "Vocabulary", "The patient was ____ from hospital after two days because she had recovered well.", "discharged",
     ["admitted", "examined", "diagnosed"],
     "İyileşen hastanın taburcu edilmesi 'be discharged from hospital' ile anlatılır."),
    ("B2", "Sentence Completion", "Although the symptoms seemed mild at first, ____.", "the patient's condition worsened quickly",
     ["the patient felt fine and went home", "the doctors did not need to do anything", "the illness was not serious at all"],
     "'Although' zıtlık ister: belirtiler hafif görünse de durum hızla kötüleşti."),
    ("C2", "Grammar", "Should the symptoms ____, the patient must return to the clinic immediately.", "persist",
     ["persisting", "persisted", "to persist"],
     "'Should + özne + yalın fiil' devrik koşuldur (If the symptoms persist)."),
    ("C2", "Vocabulary", "The drug's side effects are ____ in most patients, causing little more than mild drowsiness.", "negligible",
     ["debilitating", "severe", "irreversible"],
     "Hafif uyuşukluktan öteye geçmeyen yan etki ihmal edilebilir düzeydedir: 'negligible'."),
    ("C2", "Restatement", "It was only when the second scan was compared with the first that the tumour's growth became apparent.",
     "The growth of the tumour was noticed only after the two scans were compared.",
     ["The tumour was clearly visible in the first scan on its own.", "The doctors did not compare the first and second scans with each other at all.",
      "Comparing the two scans showed that the tumour had not grown."],
     "'It was only when ... that' = ancak ... olunca; büyüme ancak iki tarama karşılaştırılınca fark edildi."),
    ("C2", "Paragraph Completion",
     "Antibiotics have saved countless lives since the mid-twentieth century. ____. As a result, infections that were once easily treated are becoming dangerous again.",
     "However, their overuse has allowed resistant bacteria to spread",
     ["They were first discovered by accident in a London laboratory", "Therefore, infections have become much easier to treat today",
      "Most antibiotics today are produced in very large factories"],
     "Sonraki cümle eskiden kolay tedavi edilen enfeksiyonların tehlikeli hâle geldiğini söylüyor; nedeni direnç gelişmesidir."),
]
CLOZE = (
    "Hacettepe University started as a small school of children's health in 1957 and grew into (1) ____ of Türkiye's leading "
    "universities. Its medical faculty and hospitals are in Sıhhiye, in the centre of Ankara, (2) ____ most other faculties are on the "
    "large Beytepe campus. Students often travel (3) ____ the two campuses by shuttle bus. Many international students choose Hacettepe "
    "(4) ____ of its strong research in medicine and health sciences.",
    [
        ("one", ["some", "any", "every"], "'one of the leading universities' kalıbı."),
        ("while", ["because", "so", "unless"], "İki kampüs karşılaştırılıyor: 'while'."),
        ("between", ["among", "across", "over"], "İki yer arasında gidip gelmek: 'between the two campuses'."),
        ("because", ["instead", "despite", "regardless"], "Neden bildiren 'because of' kalıbı."),
    ],
)
READING = (
    "Tired Doctors\n\nFor decades, long working hours were considered an essential part of medical training. Junior doctors routinely "
    "worked shifts of thirty hours or more, on the assumption that following patients continuously would teach them more than handing "
    "over care to colleagues. Over the past twenty years, however, research has challenged this tradition. Studies have shown that "
    "after twenty-four hours without sleep, a person's reaction time and judgement are comparable to those of someone who is legally "
    "drunk.\n\nSeveral countries have therefore limited the number of hours junior doctors may work. The results have been less "
    "straightforward than reformers hoped. Shorter shifts mean more frequent handovers, and each handover is an opportunity for "
    "important information to be lost. Some studies found that errors decreased after the reforms, while others found no clear "
    "change.\n\nMost experts now argue that hours alone are not the problem. What matters is how fatigue is managed: protected time for "
    "rest, well-designed handover procedures and a culture in which tired doctors feel able to ask for help.",
    [
        ("Why were long shifts traditionally considered useful?", "Following patients continuously was thought to teach doctors more.",
         ["Hospitals could not afford to employ more doctors.", "Junior doctors actually preferred to work very long hours without breaks.",
          "Patients asked to see the same doctor throughout."],
         "Hastayı kesintisiz izlemenin daha çok şey öğrettiği varsayılıyordu."),
        ("The comparison with someone who is legally drunk is used to show that ____.", "lack of sleep seriously impairs performance",
         ["many doctors drink alcohol during their shifts", "drinking alcohol improves reaction time", "doctors should never work at night at all"],
         "24 saat uykusuzluğun tepki ve yargıyı sarhoşluk düzeyinde bozduğu vurgulanıyor."),
        ("According to the passage, what is a disadvantage of shorter shifts?", "More handovers increase the risk of losing information.",
         ["Doctors become even more tired than before.", "Patients have to wait much longer before they are treated.", "Junior doctors earn less money each month."],
         "Kısa vardiya daha sık devir teslim demek; her devir bilgi kaybı riski taşır."),
        ("Which statement best reflects the experts' view in the final paragraph?", "Managing fatigue well matters more than simply cutting hours.",
         ["Working hours should return to thirty-hour shifts.", "Handovers between doctors should be avoided completely.",
          "Tired doctors should never ask colleagues for help."],
         "Uzmanlara göre sorun yalnızca saat değil, yorgunluğun nasıl yönetildiğidir."),
    ],
)
