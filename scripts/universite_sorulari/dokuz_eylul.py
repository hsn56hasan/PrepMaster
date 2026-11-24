# Dokuz Eylül: Grammar & Vocabulary %25, Reading %35, Listening %20, Writing %20
UNI = "dokuz_eylul"
ITEMS = [
    ("A1", "Grammar", "Dokuz Eylül University ____ many campuses in İzmir.", "has", ["have", "having", "is"],
     "Özne tekil: 'has'."),
    ("A1", "Grammar", "I ____ like cold weather. I love summer.", "don't", ["doesn't", "am not", "isn't"],
     "Özne 'I' ile geniş zaman olumsuzu: 'don't like'."),
    ("A1", "Vocabulary", "Marine scientists study fish and other animals that live in the ____.", "sea", ["sky", "desert", "forest"],
     "Deniz bilimciler denizdeki canlıları inceler: 'sea'."),
    ("A1", "Vocabulary", "It's very hot today. Let's drink some cold ____.", "water", ["bread", "soup", "coffee"],
     "Sıcakta soğuk su içilir: 'water'."),
    ("A2", "Grammar", "When I arrived at the Tınaztepe campus, the lecture ____ already.", "had started",
     ["has started", "starts", "was start"],
     "Geçmişteki bir andan (varış) önce tamamlanan eylem: Past Perfect."),
    ("A2", "Vocabulary", "An earthquake ____ the city in 2020, and many buildings were damaged.", "hit", ["fell", "lost", "won"],
     "Deprem bir şehri vurur: 'hit'."),
    ("A2", "Dialogue", "A: Excuse me, how can I get to the Faculty of Fine Arts?\nB: ____\nA: Thank you very much.",
     "Take the 202 bus and get off at the last stop.",
     ["It's a very good faculty, I think.", "I'm studying fine arts there this year, actually.", "I don't like buses, to be honest."],
     "A yol soruyor; B yol tarifi vermeli."),
    ("A2", "Dialogue", "A: What time does the library close?\nB: ____\nA: Oh, I'd better hurry then.",
     "In about fifteen minutes.", ["It's on the second floor.", "I borrowed three books.", "It opened last year."],
     "A 'acele etsem iyi olur' diyor; B kapanışa az süre kaldığını söylemiş olmalı."),
    ("B2", "Grammar", "Modern buildings in İzmir are required ____ to strict earthquake regulations.", "to be built",
     ["building", "to build", "be built"],
     "'be required to' + edilgen yalın fiil: 'to be built'."),
    ("B2", "Grammar", "The scientists, ____ ship returned yesterday, collected samples from the seabed.", "whose",
     ["who", "which", "whom"],
     "Gemi bilim insanlarına ait: 'whose'."),
    ("B2", "Vocabulary", "After the earthquake, engineers ____ the damaged buildings to decide which were safe.", "inspected",
     ["ignored", "abandoned", "decorated"],
     "Hasar tespiti için binalar incelenir: 'inspected'."),
    ("B2", "Sentence Completion", "Although İzmir lies on several active faults, ____.",
     "many older buildings were not designed to resist earthquakes",
     ["the city has never experienced any earthquakes in its history", "all the buildings in the city are completely earthquake-proof",
      "the faults have no effect on the region whatsoever"],
     "'Although' zıtlık kurar: aktif faylara rağmen eski binalar depreme göre tasarlanmamış."),
    ("C2", "Grammar", "On no account ____ the laboratory without wearing protective glasses.", "should students enter",
     ["students should enter", "students enter", "enter students should"],
     "'On no account' cümle başında devrik yapı ister: 'should students enter'."),
    ("C2", "Vocabulary", "Coastal cities are particularly ____ to rising sea levels.", "vulnerable", ["immune", "resistant", "indifferent"],
     "Kıyı şehirleri deniz seviyesinin yükselmesine karşı savunmasızdır: 'vulnerable to'."),
    ("C2", "Restatement", "The damage would have been far worse had the building not been reinforced only a year earlier.",
     "Strengthening the building a year earlier greatly reduced the damage.",
     ["The building was damaged badly because it had not been reinforced.", "The building was reinforced a year after the damage occurred.",
      "Reinforcing the building made the damage considerably worse."],
     "Devrik üçüncü tip koşul: bina bir yıl önce güçlendirilmeseydi hasar çok daha kötü olurdu."),
    ("C2", "Paragraph Completion",
     "Seismologists cannot predict exactly when an earthquake will strike. ____. Such maps help authorities decide where stricter building codes are most urgently needed.",
     "They can, however, estimate which areas face the greatest long-term risk",
     ["Earthquakes usually occur during the night in coastal regions", "Therefore, building codes are no longer necessary in most cities",
      "Many people feel anxious after experiencing an earthquake"],
     "'Such maps' risk haritalarına gönderme yapar; boşlukta uzun vadeli risk tahmini anlatılmalı."),
]
CLOZE = (
    "Dokuz Eylül University takes its name (1) ____ the ninth of September 1922, the day İzmir celebrates its liberation. The "
    "university was founded in 1982 and now has campuses (2) ____ several parts of the city. Its Institute of Marine Sciences and "
    "Technology studies the Aegean Sea and (3) ____ research ships to collect data. Many students also say that İzmir is a pleasant "
    "city to live in (4) ____ of its mild climate and relaxed lifestyle.",
    [
        ("from", ["of", "by", "with"], "Adını bir şeyden almak: 'take its name from'."),
        ("in", ["on", "at", "to"], "Şehrin bölgelerinde: 'in several parts'."),
        ("uses", ["use", "using", "used to"], "Özne 'Its Institute' tekil; geniş zaman: 'studies ... and uses'."),
        ("because", ["despite", "instead", "regardless"], "Neden: 'because of its mild climate'."),
    ],
)
READING = (
    "Sleep and Memory\n\nStudents preparing for exams often sacrifice sleep to gain extra hours of study. Research in neuroscience "
    "suggests that this strategy may be counterproductive. During sleep, the brain does not simply rest; it actively processes the "
    "information acquired during the day. Memories that are initially fragile are replayed and gradually transferred to more stable "
    "long-term storage.\n\nIn one type of experiment, participants learn a list of word pairs and are then tested either after a night "
    "of sleep or after the same number of hours awake. Those who have slept typically remember significantly more. Sleep also appears to "
    "help people discover hidden patterns in information, which may explain the common experience of waking up with the solution to a "
    "problem.\n\nThe practical implications are straightforward. Spreading study over several days, with adequate sleep in between, is "
    "generally more effective than staying up all night before an exam. A short nap after learning new material may also provide some "
    "benefit, although it cannot fully replace a night's sleep.",
    [
        ("According to the passage, what happens to memories during sleep?", "They are strengthened and moved into long-term storage.",
         ["They are erased so that the brain can rest completely.", "They are replaced by the dreams people have at night.",
          "They remain fragile until the person reviews them again."],
         "Uykuda kırılgan anılar tekrar oynatılıp uzun süreli depolamaya aktarılır."),
        ("In the experiments described, participants who slept ____.", "remembered more word pairs than those who stayed awake",
         ["learnt the word pairs faster than any other group", "forgot more word pairs than those who stayed awake", "spent fewer hours studying the word pairs"],
         "Uyuyanlar, aynı süre uyanık kalanlara göre anlamlı ölçüde daha çok hatırladı."),
        ("The common experience of 'waking up with the solution' is mentioned to show that sleep ____.", "can help people find patterns",
         ["makes people forget their problems", "is less useful than studying late", "only helps people remember words"],
         "Uyku, bilgideki gizli örüntüleri keşfetmeye yardımcı olabilir."),
        ("What advice does the passage give students?", "Study over several days and sleep well in between.",
         ["Stay awake all night before the exam to revise.", "Replace a full night's sleep with several short naps.",
          "Study only in the morning after waking up early."],
         "Çalışmayı birkaç güne yaymak ve arada iyi uyumak daha etkilidir."),
    ],
)
