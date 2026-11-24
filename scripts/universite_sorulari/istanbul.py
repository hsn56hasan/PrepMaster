# İstanbul Üniversitesi: Grammar %25, Vocabulary %20, Reading %35, Restatement/Sentence Completion %20
UNI = "istanbul"
ITEMS = [
    ("A1", "Grammar", "The main gate of Istanbul University ____ very old and beautiful.", "is", ["are", "be", "am"],
     "Özne 'the main gate' tekil: 'is'."),
    ("A1", "Vocabulary", "We buy books from the old ____ next to the Beyazıt campus.", "bookshops", ["hospitals", "airports", "stadiums"],
     "Beyazıt'taki Sahaflar Çarşısı eski kitapçılarla bilinir: 'bookshops'."),
    ("A1", "Grammar", "____ you like history?", "Do", ["Does", "Are", "Is"],
     "Özne 'you' ile geniş zaman sorusu 'Do' ile kurulur."),
    ("A1", "Vocabulary", "The Grand Bazaar is very near, so we often go ____ after class.", "shopping", ["sleeping", "swimming", "skiing"],
     "Kapalıçarşı'ya alışverişe gidilir: 'go shopping'."),
    ("A2", "Restatement", "The library opens at eight and closes at ten in the evening.",
     "The library is open for fourteen hours a day.",
     ["The library is open for ten hours a day.", "The library opens in the evening only.", "The library closes at eight in the morning."],
     "08.00–22.00 arası on dört saattir."),
    ("A2", "Sentence Completion", "The Beyazıt campus is very crowded at lunchtime, so ____.", "I usually eat a little earlier",
     ["it is always completely empty then", "nobody eats lunch on the campus", "the canteen is closed every day"],
     "Öğlen kalabalık olduğu için mantıklı sonuç daha erken yemektir."),
    ("A2", "Grammar", "This is the oldest building ____ I have ever seen.", "that", ["who", "where", "whose"],
     "Üstünlük derecesinden sonra 'that' tercih edilir: 'the oldest building that I have ever seen'."),
    ("A2", "Vocabulary", "The professor ____ us to read two chapters before next week.", "asked", ["said", "spoke", "talked"],
     "'ask someone to do' kalıbı; 'say/speak/talk' bu yapıyla kullanılmaz."),
    ("B2", "Restatement", "Despite its long history, the university continues to modernise its programmes.",
     "Although the university is very old, it keeps updating its programmes.",
     ["Because the university is very old, it refuses to change its programmes.",
      "The university's programmes are as old as the university's history itself.",
      "The university only recently started teaching any of its programmes."],
     "'Despite' = -e rağmen; köklü olmasına rağmen programlarını yeniliyor."),
    ("B2", "Restatement", "No sooner had the lecture begun than the fire alarm went off.",
     "The fire alarm went off immediately after the lecture started.",
     ["The lecture began a long time after the fire alarm had gone off.", "The fire alarm went off before anyone had arrived for the lecture.",
      "Nobody heard the fire alarm because the lecture had already begun."],
     "'No sooner ... than' = … olur olmaz."),
    ("B2", "Sentence Completion", "Had the manuscripts not been stored in such a dry place, ____.",
     "they would have been damaged long ago",
     ["they were in perfect condition all along", "they will be kept there for many years", "nobody would ever want to read them"],
     "Devrik üçüncü tip koşul; temel cümle 'would have + V3' olmalı."),
    ("B2", "Vocabulary", "The library holds a large collection of ____ manuscripts written in Ottoman Turkish, Arabic and Persian.",
     "handwritten", ["digital", "printed", "recorded"],
     "Manuscript elle yazılmış eserdir: 'handwritten'."),
    ("C2", "Restatement", "Scholars have yet to reach a consensus on the exact date the manuscript was copied.",
     "Scholars still do not agree on precisely when the manuscript was copied.",
     ["Scholars have finally agreed on the exact date the manuscript was copied.",
      "Scholars are not interested in finding out when the manuscript was copied.",
      "The manuscript was copied by a group of scholars who disagreed with each other."],
     "'have yet to' = henüz … değil; kesin tarih konusunda hâlâ uzlaşma yok."),
    ("C2", "Restatement", "Only by comparing several copies were the historians able to reconstruct the original text.",
     "The historians could reconstruct the original text only after comparing several copies.",
     ["The historians reconstructed the original text without comparing any copies.",
      "The historians compared several copies but failed to reconstruct the text.",
      "Several copies of the text were made by the historians themselves."],
     "'Only by -ing' devrik yapı: ancak birkaç nüshayı karşılaştırarak özgün metni yeniden kurabildiler."),
    ("C2", "Sentence Completion", "Much as the students admired the historic buildings, ____.",
     "they complained that the old classrooms were poorly heated",
     ["they found the old buildings truly beautiful and admirable", "they thought the buildings were the most historic in the city",
      "they agreed that the buildings deserved their admiration"],
     "'Much as' = -e rağmen; hayranlığın karşısına bir şikâyet gelmeli."),
    ("C2", "Vocabulary", "The restoration revealed ____ frescoes that had been hidden beneath layers of plaster for centuries.",
     "exquisite", ["mundane", "shoddy", "crude"],
     "Yüzyıllarca gizlenip ortaya çıkarılan freskler 'nefis, zarif': 'exquisite'."),
]
CLOZE = (
    "Istanbul University is one of the oldest institutions of higher education in Türkiye. Its main campus is in Beyazıt, (1) ____ "
    "the famous Grand Bazaar and the Süleymaniye Mosque. The large gate at the entrance (2) ____ a symbol of the university for more "
    "than a century. Every day, thousands of students walk (3) ____ this gate on their way to lectures. The university library also "
    "keeps rare manuscripts that researchers from (4) ____ the world come to study.",
    [
        ("near", ["among", "between", "towards"], "Kapalıçarşı ve Süleymaniye'ye yakın: 'near'."),
        ("has been", ["is", "was being", "had"], "'for more than a century' şimdiye uzanan süre: Present Perfect."),
        ("through", ["across", "over", "along"], "Bir kapıdan geçmek: 'walk through the gate'."),
        ("all over", ["all along", "all about", "all through"], "Dünyanın her yerinden: 'from all over the world'."),
    ],
)
READING = (
    "Reading the Past\n\nHistorians who study handwritten manuscripts face problems that modern readers rarely consider. Before "
    "printing became widespread, every copy of a text was made by hand, and copyists inevitably introduced errors. Some mistakes were "
    "accidental: a skipped line, a misread word. Others were deliberate, as copyists 'corrected' passages they believed to be wrong or "
    "updated old-fashioned spellings.\n\nAs a result, two copies of the same work may differ in hundreds of places. To establish what "
    "the author originally wrote, scholars compare all surviving copies and try to work out how they are related. If several copies "
    "share the same unusual error, they were probably copied from a common source. This method, known as textual criticism, can reveal "
    "the history of a text as well as its original form.\n\nDigital tools have transformed this work. High-resolution images allow "
    "scholars in different countries to examine the same manuscript simultaneously, and software can detect differences between copies "
    "far faster than a human reader.",
    [
        ("Why do copies of the same manuscript often differ?", "Copyists made both accidental and deliberate changes.",
         ["Authors wrote different versions for different readers.", "Printing machines often damaged the original pages.",
          "Historians changed the texts when they studied them."],
         "Kopyacılar hem kazara hem bilerek değişiklik yaptı."),
        ("According to the passage, what does a shared unusual error suggest?", "The copies probably came from the same source.",
         ["The copies were all made by the original author.", "The error was deliberately added by modern historians.",
          "The copies were made in the same year and city."],
         "Aynı sıra dışı hatayı paylaşan kopyalar muhtemelen ortak bir kaynaktan kopyalanmıştır."),
        ("Textual criticism helps scholars to ____.", "discover the original text and its history",
         ["print modern editions without any changes", "decide which copyists were the most skilled", "translate manuscripts into modern languages"],
         "Yöntem hem metnin özgün biçimini hem tarihini ortaya koyar."),
        ("Which of the following is mentioned as a benefit of digital tools?", "Scholars in different places can study a manuscript at the same time.",
         ["Original manuscripts no longer need to be stored in special libraries.", "Copyists' errors can now be corrected automatically.",
          "Scholars no longer need to compare different copies."],
         "Yüksek çözünürlüklü görüntüler farklı ülkelerdeki araştırmacılara aynı anda inceleme imkânı verir."),
    ],
)
