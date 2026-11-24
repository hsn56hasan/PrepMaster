# Sabancı SU-EPE: Reading %35, Listening & Note-taking %25, Writing %25, Language Use %15
UNI = "sabanci"
ITEMS = [
    ("A1", "Grammar", "Sabancı University ____ in Tuzla, on the Asian side of Istanbul.", "is", ["are", "am", "be"],
     "Özne 'Sabancı University' tekil: 'is'."),
    ("A1", "Grammar", "Our first lesson ____ at nine o'clock.", "starts", ["start", "starting", "to start"],
     "Özne 'our first lesson' tekil; geniş zaman: 'starts'."),
    ("A1", "Vocabulary", "I listen to the lecture and write short ____ in my notebook.", "notes", ["shoes", "plates", "trees"],
     "Ders dinlerken not alınır: 'notes'."),
    ("A1", "Vocabulary", "The campus bus ____ at the metro station every twenty minutes.", "stops", ["sleeps", "cooks", "sings"],
     "Otobüs durakta durur: 'stops'."),
    ("A2", "Grammar", "First-year students don't choose their major ____ the end of their first year.", "until", ["since", "during", "while"],
     "'not ... until' = -e kadar değil; anadal birinci yılın sonuna kadar seçilmez."),
    ("A2", "Vocabulary", "In the listening exam, you hear each recording only ____, so you must listen carefully.", "once",
     ["twice", "never", "always"],
     "Kaydı yalnızca bir kez duymak dikkatli dinlemeyi gerektirir: 'once'."),
    ("A2", "Dialogue", "A: What are you going to study?\nB: ____\nA: That sounds great. You can choose later, then.",
     "I'm not sure yet; we decide at the end of the first year.",
     ["I'm going to take the shuttle bus to the station today.", "My dormitory room is on the second floor of the building.",
      "I usually study in the library after my lessons end."],
     "A 'o zaman sonra seçebilirsin' diyor; B henüz karar vermediğini söylemiş olmalı."),
    ("A2", "Dialogue", "A: Can I borrow your notes from yesterday's lecture?\nB: ____\nA: Thanks! I'll give them back tomorrow.",
     "Sure, here you are.", ["No, I didn't eat yesterday.", "Yes, the lecture was in Tuzla.", "I'm fine, thank you."],
     "A teşekkür edip notları yarın geri vereceğini söylüyor; B notları vermiş olmalı."),
    ("B2", "Grammar", "The lecturer suggested ____ the key terms before the listening task.", "reviewing",
     ["to review", "review", "reviewed"],
     "'suggest' fiilinden sonra -ing gelir: 'suggested reviewing'."),
    ("B2", "Vocabulary", "Good note-takers do not write every word; they ____ the main ideas and key details.", "identify",
     ["overlook", "dismiss", "forget"],
     "İyi not alan, ana fikirleri ve önemli ayrıntıları belirler: 'identify'."),
    ("B2", "Sentence Completion", "Because the programme is interdisciplinary, ____.",
     "students take courses from several different fields",
     ["students study only one subject for four whole years", "no courses are taught in English at the university at all",
      "every student must become an engineer when they graduate"],
     "Disiplinlerarası program, öğrencilerin farklı alanlardan ders almasını gerektirir."),
    ("B2", "Paragraph Completion",
     "Taking notes during a lecture is a demanding skill. ____. For this reason, many students use abbreviations and symbols instead of full sentences.",
     "Listeners must understand, select and write at the same time",
     ["Most lectures at the university begin at nine in the morning", "Some students prefer to study in the library at weekends",
      "The listening section of the exam has four different parts"],
     "'For this reason' kısaltma kullanımını açıklıyor; neden, aynı anda anlama, seçme ve yazma zorunluluğudur."),
    ("C2", "Grammar", "Little ____ that their research would one day lead to a new industry.", "did the scientists suspect",
     ["the scientists suspected", "suspected the scientists", "the scientists did suspect"],
     "Olumsuz anlamlı 'Little' cümle başında devrik yapı ister: 'Little did the scientists suspect'."),
    ("C2", "Vocabulary", "The nanotechnology centre was set up to ____ collaboration between engineers and natural scientists.", "foster",
     ["thwart", "stifle", "curtail"],
     "İş birliğini teşvik etmek, geliştirmek: 'foster'. Diğerleri engellemek/kısmak anlamındadır."),
    ("C2", "Restatement", "Far from being a distraction, the first-year foundation courses proved essential to the students' later success.",
     "The first-year foundation courses turned out to be very important for the students' later success.",
     ["The first-year foundation courses distracted students and lowered their later success.",
      "Students who skipped the foundation courses were the most successful later on.",
      "The foundation courses were neither useful nor harmful for most of the students."],
     "'Far from being a distraction' = dikkat dağıtmak şöyle dursun; dersler başarı için gerekli çıktı."),
    ("C2", "Paragraph Completion",
     "Interdisciplinary education is often praised for producing flexible graduates. ____. Employers, they argue, still look for specialists who can solve specific technical problems.",
     "Critics, however, worry that students may gain breadth at the expense of depth",
     ["Consequently, every graduate finds a well-paid job within the first month", "Most universities were founded in the twentieth century",
      "Flexible working hours have become popular in many offices"],
     "Sonraki cümledeki 'they argue' eleştirmenlere gönderme yapar; boşluk eleştiriyi başlatmalı."),
]
CLOZE = (
    "Sabancı University opened in 1999 in Tuzla, Istanbul. Unlike most Turkish universities, it does not ask new students to "
    "(1) ____ a department immediately. Instead, all first-year students take foundation courses (2) ____ subjects such as science, "
    "social science and the humanities. At the end of the year, they choose the programme that suits them (3) ____. Because all "
    "courses are in English, students must also pass the SU-EPE exam, (4) ____ focuses on academic reading, listening and writing.",
    [
        ("choose", ["choosing", "chose", "chosen"], "'ask someone to + yalın fiil': 'to choose'."),
        ("in", ["on", "at", "of"], "Bir alanda ders almak: 'courses in science'."),
        ("best", ["better", "good", "well"], "Kendilerine en çok uyan: 'suits them best'."),
        ("which", ["who", "where", "what"], "Sınavı niteleyen virgüllü sıfat cümlesi: 'which'."),
    ],
)
READING = (
    "Learning by Hand\n\nMany students now bring laptops to lectures, assuming that typing allows them to record more information. "
    "They are usually right: typists capture considerably more words than students writing by hand. Several studies, however, suggest "
    "that more is not always better. When students were later tested on the lecture content, those who had taken notes by hand often "
    "performed as well as, or better than, laptop users on questions that required understanding rather than recall.\n\nResearchers "
    "propose that the slowness of handwriting is precisely its advantage. Because hand-writers cannot record everything, they are forced "
    "to listen, decide what matters and rephrase it in their own words. Typists, by contrast, tend to transcribe the lecturer's words "
    "almost verbatim, a process that requires little thought.\n\nLater studies have produced more mixed results, and the effect appears "
    "smaller than early reports claimed. Nevertheless, the research offers a practical lesson for any device: notes are most useful "
    "when they are processed, not merely copied.",
    [
        ("According to the passage, what is the main advantage of typing notes?", "Students can record more words.",
         ["Students understand lectures better.", "Students remember the content for longer.", "Students listen more carefully to lecturers."],
         "Klavye kullananlar elle yazanlardan çok daha fazla kelime kaydediyor."),
        ("Why might handwriting help understanding?", "It forces students to select and rephrase information.",
         ["It allows students to copy the lecturer's exact words.", "It is faster than typing for most of the students.",
          "It lets students avoid listening to the whole lecture."],
         "Yavaşlık, öğrenciyi dinlemeye, seçmeye ve kendi sözleriyle yazmaya zorlar."),
        ("The word 'verbatim' in the second paragraph is closest in meaning to ____.", "word for word",
         ["very slowly", "in a short summary", "with errors"],
         "'verbatim' = kelimesi kelimesine."),
        ("What does the final paragraph suggest?", "Thinking about notes matters more than the device used.",
         ["Laptops should be banned from every lecture.", "Early studies on note-taking were completely wrong.",
          "Handwriting always leads to much higher grades."],
         "Ders: hangi araç olursa olsun notlar işlendiğinde yararlıdır."),
    ],
)
