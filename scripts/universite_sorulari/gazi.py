# Gazi: Use of English & Grammar %30, Vocabulary %20, Reading %30, Writing %20 (eğitim fakültesi geleneği)
UNI = "gazi"
ITEMS = [
    ("A1", "Grammar", "Look at those students. They ____ for the bus.", "are waiting", ["is waiting", "waits", "waiting"],
     "'Look!' şu anki eylemi gösterir; özne 'they': 'are waiting'."),
    ("A1", "Grammar", "This is ____ teacher. She teaches us English.", "our", ["we", "us", "ours"],
     "İsimden önce iyelik sıfatı gelir: 'our teacher'."),
    ("A1", "Vocabulary", "Teachers write on the ____ with a marker.", "board", ["floor", "ceiling", "door"],
     "Öğretmen tahtaya yazar: 'board'."),
    ("A1", "Vocabulary", "The exam is on Friday, so I'm going to ____ all week.", "study", ["sleep", "swim", "sing"],
     "Sınav yaklaşınca ders çalışılır: 'study'."),
    ("A2", "Grammar", "Gazi University ____ thousands of good teachers since it opened.", "has trained", ["trained", "trains", "is training"],
     "'since' ile şimdiye uzanan süre: Present Perfect 'has trained'."),
    ("A2", "Grammar", "My essay is ____ than yours, but yours is better.", "longer", ["long", "longest", "more long"],
     "'than' karşılaştırma ister: 'longer than'."),
    ("A2", "Vocabulary", "Student teachers spend a few weeks ____ in real schools before they graduate.", "teaching",
     ["cooking", "shopping", "sleeping"],
     "Öğretmen adayları staj için okullarda ders verir: 'teaching'."),
    ("A2", "Sentence Completion", "I didn't understand the grammar rule, so ____.", "I asked my teacher to explain it again",
     ["I explained it to my whole class again", "the rule was very easy to understand", "I didn't need any help with it at all"],
     "Kuralı anlamamanın mantıklı sonucu öğretmenden tekrar açıklamasını istemektir."),
    ("B2", "Grammar", "The teacher made the students ____ their essays.", "rewrite", ["to rewrite", "rewriting", "rewrote"],
     "'make someone do' kalıbında yalın fiil gelir: 'made them rewrite'."),
    ("B2", "Grammar", "Hardly ____ the bell rung when the students rushed out of the classroom.", "had", ["did", "has", "was"],
     "'Hardly ... when' kalıbı devrik Past Perfect ister: 'Hardly had the bell rung'."),
    ("B2", "Vocabulary", "Good teachers try to ____ their students to think for themselves.", "encourage", ["prevent", "forbid", "avoid"],
     "'encourage someone to do' = teşvik etmek."),
    ("B2", "Sentence Completion", "The new teaching method was so effective that ____.", "students' exam results improved by twenty percent",
     ["nobody noticed any difference in the results", "teachers decided to stop using it at once", "it was not used in any of the classrooms"],
     "'so effective that' sonucu olumlu olmalı: sınav sonuçları yükseldi."),
    ("C2", "Grammar", "It is essential that every candidate ____ the instructions before the exam begins.", "read",
     ["reading", "to read", "will read"],
     "'It is essential that' sonrasında yalın fiil (subjunctive) gelir: 'every candidate read'."),
    ("C2", "Grammar", "Rarely ____ a teacher had such a lasting influence on his students.", "has", ["did", "was", "have"],
     "'Rarely' cümle başında devrik yapı ister; fiil 'had' (V3) olduğu için 'has ... had'."),
    ("C2", "Vocabulary", "The proposal to shorten teacher training met with ____ opposition from universities, which organised protests nationwide.",
     "fierce", ["tepid", "negligible", "token"],
     "Ülke çapında protestolar şiddetli bir muhalefeti gösterir: 'fierce'."),
    ("C2", "Paragraph Completion",
     "Teacher education in Türkiye has a long institutional history. ____. Over the following decades, these programmes became the foundation of today's education faculties.",
     "In 1926 an institute opened in Ankara to train secondary school teachers",
     ["Many students today prefer to become doctors rather than teachers", "Teachers in Türkiye work an average of thirty hours each week",
      "However, no teachers were trained in Ankara before the 1990s"],
     "'these programmes' ifadesinin gönderme yapacağı bir başlangıç (1926 enstitüsü) gerekir."),
]
CLOZE = (
    "Gazi University has its roots (1) ____ a teacher training school that opened in Ankara in 1926. For many years, it trained "
    "teachers (2) ____ worked in schools all over Türkiye. Today, the university has more than twenty faculties, but its Faculty of "
    "Education is (3) ____ one of the best known. Many students choose Gazi because they want to (4) ____ teachers after they graduate.",
    [
        ("in", ["on", "at", "for"], "Kökeni bir yerde olmak: 'have its roots in'."),
        ("who", ["which", "whose", "where"], "İnsanları niteleyen sıfat cümlesi: 'teachers who worked'."),
        ("still", ["yet", "already", "ever"], "Bugün de hâlâ: 'still one of the best known'."),
        ("become", ["becoming", "became", "becomes"], "'want to' sonrası yalın fiil: 'want to become'."),
    ],
)
READING = (
    "The Homework Debate\n\nFew aspects of schooling generate as much disagreement among parents as homework. Some see it as essential "
    "practice that builds discipline and reinforces classroom learning; others view it as a source of stress that eats into time for "
    "play, sport and sleep. Research suggests that both views contain some truth, but that the effects depend strongly on the age of "
    "the student.\n\nFor primary school children, studies have found little connection between the amount of homework and academic "
    "achievement. For secondary school students, a moderate amount, roughly one to two hours a day, is associated with better results, "
    "but the benefits disappear and may even reverse beyond that point. Researchers also emphasise that the type of task matters more "
    "than its length. Short assignments that ask students to apply what they have learnt tend to be more effective than repetitive "
    "exercises that merely fill time.\n\nTeachers, therefore, may achieve more by setting fewer but better-designed tasks than by simply "
    "increasing the workload.",
    [
        ("According to the passage, the effect of homework depends mainly on ____.", "the age of the students",
         ["the attitude of the parents", "the number of teachers", "the length of the school day"],
         "'the effects depend strongly on the age of the student'."),
        ("What does research say about homework for primary school children?", "It has little effect on their achievement.",
         ["It greatly improves their exam results.", "It should take at least two hours a day.", "It is more useful than lessons at school."],
         "İlkokulda ödev miktarı ile başarı arasında pek bağlantı bulunmamış."),
        ("The phrase 'may even reverse' suggests that too much homework can ____.", "harm students' results",
         ["make lessons shorter", "help younger children more", "reduce parents' stress"],
         "Belli bir noktadan sonra faydalar kaybolur, hatta tersine döner: fazla ödev zarar verebilir."),
        ("What does the author recommend in the last paragraph?", "setting fewer tasks that are designed more carefully",
         ["giving students much more homework every day", "replacing homework with extra lessons at school", "letting parents choose all of the homework"],
         "Daha az ama daha iyi tasarlanmış ödev önerilir."),
    ],
)
