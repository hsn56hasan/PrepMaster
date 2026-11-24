# Koç KUEPE: Reading %30, Listening %25, Academic Essay %30, Speaking Interview %15
UNI = "koc"
ITEMS = [
    ("A1", "Grammar", "Koç University is near the Black Sea, in the north ____ Istanbul.", "of", ["in", "at", "on"],
     "'in the north of a city' kalıbı."),
    ("A1", "Grammar", "There ____ many students in the café at lunchtime.", "are", ["is", "be", "am"],
     "'many students' çoğul: 'there are'."),
    ("A1", "Vocabulary", "It is very ____ on the campus in winter because of the wind from the sea.", "cold", ["hot", "dry", "sweet"],
     "Kışın denizden esen rüzgâr havayı soğuk yapar: 'cold'."),
    ("A1", "Vocabulary", "I need a new ____ to carry my books.", "bag", ["spoon", "shoe", "clock"],
     "Kitap taşımak için çanta gerekir: 'bag'."),
    ("A2", "Vocabulary", "In the speaking exam, you have two minutes to ____ your answer.", "prepare", ["forget", "borrow", "break"],
     "Konuşma sınavında cevaba hazırlanma süresi verilir: 'prepare'."),
    ("A2", "Grammar", "She asked me where ____.", "I lived", ["did I live", "do I live", "I am live"],
     "Dolaylı soruda devrik yapı kullanılmaz ve zaman bir geri kayar: 'where I lived'."),
    ("A2", "Dialogue", "Examiner: Could you tell me a little about yourself?\nStudent: ____\nExaminer: Thank you. Now let's talk about your studies.",
     "Sure. I'm from Bursa and I love reading.",
     ["Sorry, I think the exam starts at ten.", "No, I have never visited that city before.", "Yes, I think this is the speaking room."],
     "Sınav görevlisi kendini tanıtmanı istiyor; uygun cevap kısa bir tanıtımdır."),
    ("A2", "Dialogue", "A: Did you understand the last part of the recording?\nB: ____\nA: No problem, let's listen to it again.",
     "Not really, it was a bit too fast for me.",
     ["Yes, I bought it at the bookshop yesterday.", "The recording room is on the second floor.", "I think the next lesson is at three today."],
     "A 'tekrar dinleyelim' diyor; B anlamadığını söylemiş olmalı."),
    ("B2", "Vocabulary", "In the essay, you must ____ your opinion with clear examples.", "support", ["delay", "ignore", "replace"],
     "Görüşü örneklerle desteklemek: 'support your opinion with examples'."),
    ("B2", "Vocabulary", "The speaker ____ his main points at the end of the lecture so that students could remember them.", "summarised",
     ["postponed", "contradicted", "abandoned"],
     "Öğrenciler hatırlasın diye ana noktalar sonda özetlenir: 'summarised'."),
    ("B2", "Sentence Completion", "Students who practise speaking regularly ____.", "tend to feel more relaxed in the interview",
     ["never need to prepare for any interview", "always forget their answers during the exam", "usually avoid talking to their classmates"],
     "Düzenli konuşma pratiği mülakatta daha rahat hissetmeyi sağlar."),
    ("B2", "Paragraph Completion",
     "A good academic essay usually begins with an introduction that presents the topic. ____. The body paragraphs then support this claim with evidence and examples.",
     "At the end of the introduction, the writer states the main argument",
     ["Most students prefer writing essays by hand rather than typing", "Essays in the exam must be written in pencil, not in pen",
      "Some universities do not include an essay in their exams"],
     "Sonraki cümledeki 'this claim' bir tez cümlesine gönderme yapıyor; boşluk tezi tanıtmalı."),
    ("C2", "Vocabulary", "The CEO's speech was ____ with jargon, making it hard for the audience to follow.", "littered",
     ["devoid", "bereft", "stripped"],
     "Jargonla dolu konuşma: 'littered with'. Diğerleri 'yoksun' anlamındadır ve 'with' ile kullanılmaz."),
    ("C2", "Vocabulary", "Her argument, though ____, rests on an assumption that the data do not support.", "ingenious",
     ["flawed", "incoherent", "specious"],
     "'though' zıtlık kurar: zekice ama verilerle desteklenmeyen bir varsayıma dayanıyor."),
    ("C2", "Restatement", "The success of the start-up owed less to its founders' technical skills than to their timing.",
     "The start-up succeeded mainly because its founders launched it at the right moment.",
     ["The founders' technical skills were the main reason for the start-up's success.", "The start-up failed because its founders launched it far too early.",
      "The founders had neither technical skills nor good timing at all."],
     "'owed less to X than to Y' = başarı X'ten çok Y'ye bağlıydı: doğru zamanlama."),
    ("C2", "Paragraph Completion",
     "Entrepreneurship programmes have become common at Turkish universities. ____. Critics, however, warn that most start-ups fail within five years and that students should not be encouraged to abandon their studies too early.",
     "Supporters say they help students turn research ideas into businesses",
     ["Universities in Türkiye were first founded in the fifteenth century", "Consequently, every start-up launched by students has succeeded",
      "Many students live in dormitories during their first year"],
     "'Critics, however' ile karşı görüş geliyor; boşluğa destekçilerin görüşü gelmeli."),
]
CLOZE = (
    "Koç University was founded in 1993 by the Vehbi Koç Foundation. Its main campus (1) ____ in Sarıyer, close to the Black Sea coast. "
    "All courses are taught in English, so students must take the KUEPE exam (2) ____ they begin their studies. The exam tests reading, "
    "listening, writing and speaking. Students who need more practice join the English Language Center, (3) ____ they study for up to "
    "one year. Many students say that the speaking interview is the part they find (4) ____ difficult.",
    [
        ("is", ["are", "be", "has"], "Özne 'its main campus' tekil: 'is'."),
        ("before", ["unless", "although", "since"], "Derslere başlamadan ÖNCE sınava girilir."),
        ("where", ["which", "who", "what"], "Yer bildiren sıfat cümlesi: 'where they study'."),
        ("most", ["more", "much", "many"], "Bölümler arasında en zoru: 'the part they find most difficult'."),
    ],
)
READING = (
    "Fear of Speaking\n\nMany language learners can read and write a foreign language well yet freeze when asked to speak it. "
    "Researchers call this foreign language anxiety, and it differs from general shyness: people who are confident speakers in their "
    "first language may still experience it. The fear usually centres on making mistakes in front of others and being judged "
    "negatively.\n\nInterestingly, anxiety does not always decline as proficiency increases. Some advanced learners report higher anxiety "
    "than beginners, perhaps because they hold themselves to stricter standards. Classroom practices also play a role. Being corrected "
    "publicly for every error tends to increase anxiety, whereas activities in small groups, where mistakes carry fewer social "
    "consequences, appear to reduce it.\n\nFor exam candidates, the most effective strategy seems to be repeated exposure under realistic "
    "conditions. Practising timed answers with a partner, recording oneself and listening back, and focusing on communicating ideas rather "
    "than producing perfect grammar can all make the actual interview feel less threatening.",
    [
        ("How is foreign language anxiety different from general shyness?", "Confident speakers of their first language can also experience it.",
         ["It only affects people who are naturally shy in every social situation.", "It disappears completely once learners become fluent.",
          "It is caused mainly by difficult reading texts."],
         "Ana dilinde rahat konuşan biri de yabancı dilde bu kaygıyı yaşayabilir."),
        ("Why might some advanced learners feel more anxious than beginners?", "They may expect more of themselves.",
         ["They have fewer chances to speak.", "Their teachers correct them less often.", "They are usually younger than beginners."],
         "İleri düzeydekiler kendilerine daha katı standartlar koyuyor olabilir."),
        ("According to the passage, which classroom practice is likely to increase anxiety?", "correcting every error in front of the class",
         ["working in small groups on speaking tasks", "recording answers and listening to them", "focusing on ideas rather than on grammar"],
         "Her hatanın herkesin önünde düzeltilmesi kaygıyı artırır."),
        ("What advice does the passage give exam candidates?", "Practise regularly in conditions similar to the real exam.",
         ["Avoid speaking until your grammar is perfect.", "Memorise long answers word for word.", "Study reading and writing instead of practising speaking."],
         "En etkili strateji gerçekçi koşullarda tekrarlı pratiktir."),
    ],
)
