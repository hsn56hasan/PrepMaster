# ODTÜ EPE: Language Use (Cloze & Grammar) %20, Reading %35, Listening & Note Taking %20
UNI = "metu"
ITEMS = [
    ("A1", "Grammar", "My roommate and I ____ from different cities.", "are", ["is", "am", "be"],
     "'My roommate and I' çoğul bir öznedir (we); 'are' kullanılır."),
    ("A1", "Grammar", "We usually ____ lunch at the cafeteria near the library.", "have", ["has", "having", "to have"],
     "Özne 'we', alışkanlık bildiren geniş zaman: 'we usually have lunch'."),
    ("A1", "Vocabulary", "On Sundays, many students go for a walk around Eymir ____.", "Lake", ["Kitchen", "Ticket", "Pencil"],
     "Eymir, ODTÜ'ye ait bir göldür: 'Eymir Lake'."),
    ("A1", "Vocabulary", "There are many ____ on the ODTÜ campus; students planted them over many years.", "trees", ["cars", "shops", "clouds"],
     "Öğrencilerin yıllar içinde dikebileceği şey ağaçtır: 'trees' (ODTÜ ormanı)."),
    ("A2", "Grammar", "The ODTÜ forest ____ by students and staff over many decades.", "was planted", ["planted", "was plant", "is planting"],
     "Orman kendi kendine dikilmez; geçmiş zaman edilgen yapı gerekir: 'was planted'."),
    ("A2", "Grammar", "If you ____ the shuttle bus, you will be late for the exam.", "miss", ["will miss", "missed", "are missing"],
     "Birinci tip koşul: 'If + geniş zaman, will + fiil'."),
    ("A2", "Vocabulary", "You need to ____ your student card to borrow books from the library.", "show", ["throw", "cook", "sing"],
     "Kitap almak için öğrenci kartını göstermek gerekir: 'show your card'."),
    ("A2", "Dialogue", "A: Excuse me, is this seat free?\nB: ____\nA: Thanks, I'll just put my bag here, then.",
     "Yes, nobody is sitting there.", ["No, I don't like this classroom.", "It's ten o'clock now.", "I'm studying chemistry here."],
     "A teşekkür edip çantasını koyuyor; B yerin boş olduğunu söylemiş olmalı."),
    ("B2", "Grammar", "The professor suggested that we ____ the experiment with a larger sample.", "repeat", ["repeating", "to repeat", "will repeat"],
     "'suggest that' yapısından sonra yalın fiil (subjunctive) gelir: 'that we repeat'."),
    ("B2", "Grammar", "Only after the results had been checked ____ to publish the report.", "did the team decide",
     ["the team decided", "decided the team", "the team did decide"],
     "'Only after ...' cümle başında olunca ana cümle devrik olur: 'did the team decide'."),
    ("B2", "Vocabulary", "The new rules are meant to ____ students from parking their cars in front of the faculty buildings.", "discourage",
     ["encourage", "persuade", "allow"],
     "'discourage someone from doing' = vazgeçirmek; diğerleri 'from' ile bu anlamda kullanılmaz."),
    ("B2", "Sentence Completion", "The experiment had to be stopped halfway ____.", "because the temperature in the lab rose dangerously",
     ["even though everything in the lab was working perfectly", "in order to finish it much more quickly", "unless the equipment worked properly"],
     "Deneyin yarıda durdurulmasının mantıklı nedeni sıcaklığın tehlikeli biçimde artmasıdır."),
    ("C2", "Grammar", "____ the committee's objections, the department went ahead with the new curriculum.", "Regardless of",
     ["Owing to", "On account of", "As a result of"],
     "İtirazlara RAĞMEN devam edildi; 'Regardless of' zıtlık bildirir, diğerleri neden bildirir."),
    ("C2", "Vocabulary", "The lecturer's explanation was so ____ that even first-year students could follow the complex argument.", "lucid",
     ["convoluted", "cryptic", "verbose"],
     "Birinci sınıfların bile anlayabildiği açıklama 'lucid' (açık, anlaşılır) olur."),
    ("C2", "Vocabulary", "The findings were ____ by a second team working independently, which strengthened confidence in them.", "corroborated",
     ["undermined", "fabricated", "obscured"],
     "Bağımsız ikinci ekip bulguları doğruladı: 'corroborate'. Güven artışı bunu gösterir."),
    ("C2", "Paragraph Completion",
     "The ODTÜ forest is often cited as an example of how a barren landscape can be transformed. When the campus was founded in the late 1950s, the land was almost entirely treeless steppe. ____. Today the forest provides habitat for wildlife and serves as a natural laboratory for environmental research.",
     "Over the following decades, students and staff planted millions of saplings",
     ["The steppe climate of central Anatolia has very hot summers and cold winters", "As a result, no trees were ever planted anywhere on the campus",
      "Many universities in Europe were also founded during the 1950s"],
     "Ağaçsız bozkırdan bugünkü ormana geçişi açıklayan cümle gerekir: fidanlar dikildi."),
]
CLOZE = (
    "Every September, thousands of new students arrive at ODTÜ in Ankara. (1) ____ they start their departments, most of them "
    "take the English Proficiency Exam. Students who are not successful attend the preparatory school (2) ____ one year. The "
    "programme focuses (3) ____ academic reading, listening and writing, because all courses at ODTÜ are taught in English. Many "
    "students say the year is hard, but it helps them (4) ____ confident in their departments.",
    [
        ("Before", ["Unless", "Although", "Despite"], "Bölüme başlamadan ÖNCE sınava girilir: 'Before'."),
        ("for", ["since", "ago", "until"], "Süre bildirirken 'for one year' kullanılır."),
        ("on", ["at", "in", "with"], "'focus on' kalıbı: … üzerine odaklanmak."),
        ("feel", ["feeling", "felt", "feels"], "'help someone (to) do' kalıbında yalın fiil gelir: 'help them feel'."),
    ],
)
READING = (
    "Taking Notes in English-Medium Lectures\n\nStudents who move from Turkish-medium high schools to English-medium universities "
    "often report that listening to lectures is more exhausting than reading textbooks. Part of the difficulty lies in speed: a "
    "lecturer may deliver 130 words per minute, leaving little time to translate mentally. Research on second-language learners "
    "suggests that the most successful note-takers do not attempt to write everything down. Instead, they listen for signposting "
    "expressions such as 'the key point here is' or 'by contrast', which reveal how the lecture is organised.\n\nAnother common "
    "strategy is to use abbreviations and symbols, for example an arrow for 'leads to'. However, studies warn that a personal "
    "system is only useful if it is practised before the exam; inventing symbols during a lecture tends to distract students "
    "rather than help them.\n\nFinally, reviewing notes within twenty-four hours seems to matter as much as taking them. Students "
    "who reorganised their notes on the same day remembered significantly more of the content a week later than those who did not.",
    [
        ("According to the passage, why do many new students find lectures tiring?", "Lecturers speak too fast for students to translate in their heads.",
         ["Lectures contain harder vocabulary than most textbooks.", "Students are usually not allowed to take any notes during lectures.",
          "Lecturers rarely organise their lectures very clearly."],
         "Metin: dakikada 130 kelimelik hız zihinde çeviriye zaman bırakmıyor."),
        ("What do successful note-takers do, according to research?", "They focus on expressions that show the structure of the lecture.",
         ["They try to write down every word the lecturer says.", "They translate the lecture into Turkish as they listen.",
          "They ask the lecturer to repeat all of the important sentences again."],
         "Başarılı not alanlar dersin düzenini gösteren yönlendirici ifadeleri dinliyor."),
        ("The author warns that symbols and abbreviations ____.", "should be practised before they are actually needed",
         ["are always more useful than writing words in full", "should be invented freshly during each new lecture", "are only helpful for students of mathematics"],
         "Kişisel kısaltma sistemi ancak sınavdan önce çalışılırsa işe yarar; ders sırasında uydurmak dikkati dağıtır."),
        ("Which conclusion is supported by the final paragraph?", "Reviewing notes soon after a lecture improves later recall.",
         ["Notes taken quickly are usually forgotten within a day.", "Reorganising notes is less useful than taking them carefully.",
          "Students remember more if they wait a week before reviewing."],
         "Aynı gün notlarını düzenleyenler bir hafta sonra daha fazlasını hatırlamış."),
    ],
)
