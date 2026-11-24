# TOBB ETÜ: Grammar & Vocabulary %25, Reading %35, Listening %20, Writing %20 (dönemli iş başında eğitim)
UNI = "tobb"
ITEMS = [
    ("A1", "Grammar", "TOBB ETÜ ____ in Söğütözü, in Ankara.", "is", ["are", "am", "be"],
     "Özne tekil: 'is'."),
    ("A1", "Grammar", "My sister ____ in an office near the campus.", "works", ["work", "working", "is work"],
     "Özne tekil, geniş zaman: 'works'."),
    ("A1", "Vocabulary", "I wear a ____ and tie to my job interview.", "suit", ["swimsuit", "pyjama", "raincoat"],
     "İş görüşmesine takım elbise giyilir: 'suit'."),
    ("A1", "Vocabulary", "My office is on the fifth ____ of the building.", "floor", ["door", "roof", "wall"],
     "Binanın beşinci katı: 'fifth floor'."),
    ("A2", "Grammar", "Students at TOBB ETÜ study ____ work in companies during their degree.", "and", ["but", "or", "so"],
     "İki eylem birlikte yapılıyor: 'study and work'."),
    ("A2", "Grammar", "I ____ my first internship last summer.", "did", ["do", "does", "have do"],
     "'last summer' geçmiş zaman; staj yapmak 'do an internship': 'did'."),
    ("A2", "Vocabulary", "Before the interview, you should ____ your CV carefully.", "prepare", ["break", "lose", "throw"],
     "Özgeçmişi hazırlamak: 'prepare your CV'."),
    ("A2", "Dialogue", "A: How was your first day at the company?\nB: ____\nA: That's great. I'm glad you liked it.",
     "Really good. Everyone was very helpful.",
     ["I'll start working there next Monday, I think.", "The company is in Ankara.", "I'm not sure where it is."],
     "A 'beğenmene sevindim' diyor; B olumlu bir deneyim anlatmış olmalı."),
    ("B2", "Grammar", "By the time they graduate, TOBB ETÜ students ____ in several companies.", "will have worked",
     ["will work", "have worked", "would be working"],
     "Gelecekteki bir andan önce tamamlanmış olacak eylem: Future Perfect."),
    ("B2", "Grammar", "The manager suggested that the intern ____ a short report every week.", "write",
     ["writes", "wrote", "to write"],
     "'suggest that' + yalın fiil (subjunctive): 'the intern write'."),
    ("B2", "Vocabulary", "Internships give students the chance to ____ practical experience before they graduate.", "gain",
     ["lose", "waste", "refuse"],
     "Deneyim kazanmak: 'gain experience'."),
    ("B2", "Sentence Completion", "Because students alternate between classes and work, ____.",
     "they can apply what they learn in real companies",
     ["they never have to attend any classes at all", "they cannot find any jobs after graduating", "companies refuse to hire them as interns"],
     "Ders ve iş dönemleri değiştiği için öğrendiklerini gerçek şirketlerde uygulayabilirler."),
    ("C2", "Grammar", "Not until she had completed her third internship ____ which career she wanted to pursue.", "did she realise",
     ["she realised", "realised she", "she did realise"],
     "'Not until' devrik yapı ister: 'did she realise'."),
    ("C2", "Vocabulary", "Employers increasingly value graduates who can ____ quickly to new situations.", "adapt",
     ["adopt", "adept", "adjoin"],
     "Yeni durumlara uyum sağlamak: 'adapt to'. 'adopt' benimsemek demektir."),
    ("C2", "Restatement", "The company was reluctant to hire anyone without work experience, however strong their grades were.",
     "The company did not want inexperienced people, no matter how good their grades were.",
     ["The company only hired graduates with very good grades and no experience.", "The company hired many people without any experience simply because of their good grades.",
      "Good grades were more important to the company than work experience."],
     "'however strong their grades were' = notları ne kadar iyi olursa olsun."),
    ("C2", "Paragraph Completion",
     "Cooperative education programmes combine academic study with periods of paid work. ____. Critics, however, point out that such programmes may lengthen the time needed to complete a degree.",
     "Supporters argue that graduates enter the job market with valuable experience",
     ["Most universities in Ankara were founded at some point in the twentieth century", "As a result, students never have to study for exams",
      "Many companies have offices in the city centre"],
     "'Critics, however' karşı görüşü getiriyor; boşluğa destekçilerin görüşü gelmeli."),
]
CLOZE = (
    "TOBB University of Economics and Technology was founded in 2003 by the Union of Chambers and Commodity Exchanges of Türkiye. "
    "It is known for its cooperative education system, (1) ____ students spend some terms working in companies instead of attending "
    "classes. This allows them to gain experience (2) ____ they are still at university. Because the system requires students to study "
    "throughout the year, the academic calendar is divided (3) ____ three terms. Many graduates say that their work terms helped them "
    "find a job much more (4) ____.",
    [
        ("in which", ["which", "whose", "what"], "Sistemin içinde: 'a system in which students spend'."),
        ("while", ["during", "until", "unless"], "Üniversitedeyken: 'while they are still at university'."),
        ("into", ["in", "to", "by"], "Bölmek: 'be divided into'."),
        ("easily", ["easy", "easier", "ease"], "Fiili niteleyen zarf: 'find a job much more easily'."),
    ],
)
READING = (
    "Learning on the Job\n\nCooperative education, often shortened to co-op, alternates periods of classroom study with periods of "
    "full-time employment related to the student's field. The model originated in the United States in the early twentieth century, "
    "when an engineering professor argued that some skills could only be learnt in real workplaces. Today, co-op programmes exist "
    "around the world, particularly in engineering, business and computing.\n\nResearch on co-op graduates generally reports positive "
    "outcomes. They tend to find jobs sooner after graduation and often receive higher starting salaries than their peers. Many are "
    "hired by companies where they completed a work term, which reduces recruitment costs for employers.\n\nThe benefits, however, "
    "depend heavily on the quality of the placements. A work term spent on routine tasks with little supervision adds little to a "
    "student's education. The most successful programmes therefore set clear learning goals for each placement, assign workplace "
    "mentors and ask students to reflect on their experience when they return to the classroom.",
    [
        ("Why was cooperative education first introduced?", "Some skills were thought to be learnable only at work.",
         ["Universities did not have enough classrooms.", "Students wanted to earn money during their studies.", "Companies demanded cheaper workers from universities."],
         "Bir mühendislik profesörü bazı becerilerin yalnızca gerçek iş yerlerinde öğrenilebileceğini savundu."),
        ("According to the passage, co-op graduates often ____.", "find jobs faster and earn more at first",
         ["take longer to find their first job", "prefer to work for very small companies", "earn less than other graduates at first"],
         "İşe daha çabuk girer ve çoğu zaman daha yüksek başlangıç maaşı alırlar."),
        ("How do employers benefit from co-op programmes?", "They spend less on recruiting new employees.",
         ["They do not need to pay students at all.", "They receive money from the universities.", "They can avoid training any new staff."],
         "Staj yapılan şirketlerin öğrenciyi işe alması işe alım maliyetini düşürür."),
        ("What makes a co-op programme successful, according to the last paragraph?", "clear goals, mentors and reflection",
         ["longer work terms with fewer classes", "routine tasks with little supervision", "higher salaries for all students"],
         "Net öğrenme hedefleri, iş yeri mentorları ve deneyim üzerine düşünme."),
    ],
)
