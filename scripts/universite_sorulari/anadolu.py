# Anadolu: Grammar & Vocabulary %30, Reading %35, Listening %15, Writing %20 (açıköğretim geleneği)
UNI = "anadolu"
ITEMS = [
    ("A1", "Grammar", "My father ____ an open education student. He studies at home.", "is", ["are", "am", "be"],
     "Özne 'my father' tekil: 'is'."),
    ("A1", "Grammar", "We ____ our lessons online in the evening.", "watch", ["watches", "watching", "is watch"],
     "Özne 'we': 'watch'."),
    ("A1", "Vocabulary", "The Porsuk River goes through the ____ of Eskişehir.", "centre", ["window", "pocket", "kitchen"],
     "Porsuk Çayı şehir merkezinden geçer: 'centre'."),
    ("A1", "Vocabulary", "I can't watch the lesson because my ____ connection is very slow.", "internet", ["kitchen", "bicycle", "garden"],
     "Çevrim içi ders için internet bağlantısı gerekir: 'internet connection'."),
    ("A2", "Grammar", "Anadolu University ____ distance education since 1982.", "has offered", ["offers", "offered", "is offering"],
     "'since' şimdiye uzanan süre: Present Perfect 'has offered'."),
    ("A2", "Grammar", "Many people study at home ____ they have full-time jobs.", "because", ["but", "so", "or"],
     "Evde çalışmanın nedeni tam zamanlı iştir: 'because'."),
    ("A2", "Vocabulary", "You can ____ the video lesson and watch it again later.", "download", ["climb", "cook", "wash"],
     "Ders videosunu indirmek: 'download'."),
    ("A2", "Sentence Completion", "I missed the live online lesson, but ____.", "I watched the recording the next day",
     ["I attended the whole live lesson from the start", "I was in the online lesson the whole time", "the lesson was live and I watched it then"],
     "'but' zıtlık ister: canlı dersi kaçırdım ama kaydını izledim."),
    ("B2", "Grammar", "Students ____ submit their assignments on time will lose points.", "who fail to",
     ["which fail to", "who fails", "whose fail"],
     "İnsanları niteleyen sıfat cümlesi 'who' + 'fail to' (yapamamak)."),
    ("B2", "Grammar", "I wish I ____ more time to study when I was younger.", "had had", ["have had", "would have", "had"],
     "Geçmişe dair pişmanlık: 'wish + Past Perfect' (had had)."),
    ("B2", "Vocabulary", "Online learning requires a lot of self-____, because nobody checks whether you study.", "discipline",
     ["defence", "service", "portrait"],
     "Kimse denetlemediği için öz disiplin gerekir: 'self-discipline'."),
    ("B2", "Vocabulary", "The university ____ millions of students who could not attend classes on a campus.", "has reached",
     ["has refused", "has rejected", "has ignored"],
     "Uzaktan eğitim kampüse gidemeyen milyonlara ulaştı: 'has reached'."),
    ("C2", "Grammar", "Had it not been for distance education, millions of adults ____ a university degree.", "would never have earned",
     ["would never earn", "had never earned", "will never have earned"],
     "Devrik üçüncü tip koşul: 'would have + V3'."),
    ("C2", "Vocabulary", "Online courses have made higher education more ____ to people living in remote areas.", "accessible",
     ["exclusive", "remote", "elusive"],
     "Uzak bölgelerdeki insanlar için yükseköğretim daha erişilebilir oldu: 'accessible'."),
    ("C2", "Restatement", "Far from replacing teachers, digital platforms have made their guidance more important than ever.",
     "Digital platforms have actually increased the importance of teachers' guidance.",
     ["Digital platforms have replaced teachers in most online courses.", "Teachers' guidance has become less important because of digital platforms.",
      "Teachers refuse to use digital platforms in their online courses."],
     "'Far from replacing' = yerini almak şöyle dursun; rehberlik daha da önem kazandı."),
    ("C2", "Paragraph Completion",
     "Massive open online courses, or MOOCs, were once expected to transform higher education. ____. Researchers found that only a small percentage of those who enrolled completed their courses.",
     "In practice, however, the results proved disappointing",
     ["They were first introduced by universities in the 2000s", "As a result, every student finished their course successfully",
      "Many people enjoy learning new languages in their free time"],
     "Sonraki cümle düşük bitirme oranını anlatıyor; boşluk hayal kırıklığını ifade etmeli."),
]
CLOZE = (
    "Anadolu University is located in Eskişehir, a student city in central Anatolia. It is best known (1) ____ its Open Education "
    "Faculty, which has offered distance learning since 1982. Through this system, people who cannot attend classes on campus can "
    "study (2) ____ home using books, television programmes and online materials. Over the years, millions of students (3) ____ from "
    "the programme. Today, the university continues to develop digital platforms (4) ____ make learning more flexible.",
    [
        ("for", ["as", "by", "with"], "Bir şeyle tanınmak: 'be known for'."),
        ("at", ["in", "on", "to"], "Evde çalışmak: 'study at home'."),
        ("have graduated", ["graduate", "are graduating", "graduated have"], "'Over the years' şimdiye uzanır: Present Perfect."),
        ("that", ["what", "who", "where"], "Platformları niteleyen sıfat cümlesi: 'platforms that make'."),
    ],
)
READING = (
    "Why Online Learners Drop Out\n\nOnline courses offer flexibility that traditional programmes cannot match. Students can study at "
    "any time, from any place, and often at their own pace. Yet completion rates for many online courses remain considerably lower than "
    "for face-to-face programmes. Researchers have tried to understand why.\n\nOne explanation concerns isolation. In a classroom, "
    "students meet peers who share their difficulties and teachers who notice when someone falls behind. Online, a struggling student "
    "may simply stop logging in without anyone realising. Another factor is time management. The same flexibility that attracts adult "
    "learners can become a trap, as study is postponed in favour of more urgent work or family responsibilities.\n\nCourses with higher "
    "completion rates tend to share certain features. They set regular deadlines rather than a single final exam, include frequent "
    "interaction with instructors and create opportunities for learners to work together in small groups. Some also send automatic "
    "messages to students who have been inactive for several days.",
    [
        ("What problem does the passage mainly discuss?", "why many students do not complete online courses",
         ["why online courses are more expensive than others", "how teachers prepare online course materials", "which subjects are best taught on the internet"],
         "Metin, çevrim içi derslerde düşük tamamlama oranının nedenlerini ele alıyor."),
        ("According to the passage, why can isolation cause students to drop out?", "Nobody may notice when a student stops participating.",
         ["Students prefer to study alone without any teachers.", "Online classrooms are usually too crowded to learn in.",
          "Teachers cannot upload materials without help from students."],
         "Zorlanan öğrenci giriş yapmayı bırakabilir ve kimse fark etmeyebilir."),
        ("The author describes flexibility as 'a trap' because ____.", "students may keep postponing their study",
         ["courses must be completed in a single day", "it makes online courses more expensive", "students must study at fixed times"],
         "Esneklik, çalışmanın sürekli ertelenmesine yol açabilir."),
        ("Which feature is NOT mentioned as common in courses with high completion rates?", "shorter videos for each lesson",
         ["regular deadlines throughout the course", "frequent contact with instructors", "group work with other learners"],
         "Kısa videolardan söz edilmiyor; diğer üçü sayılıyor."),
    ],
)
