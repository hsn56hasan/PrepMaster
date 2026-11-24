# Bahçeşehir: Grammar & Vocabulary %25, Reading %30, Listening %25, Writing %20
UNI = "bahcesehir"
ITEMS = [
    ("A1", "Grammar", "The main campus ____ next to the Bosphorus in Beşiktaş.", "is", ["are", "am", "be"],
     "Özne tekil: 'is'."),
    ("A1", "Grammar", "Look! The ships ____ under the bridge.", "are passing", ["is passing", "passes", "pass"],
     "'Look!' şu anki eylem; özne çoğul: 'are passing'."),
    ("A1", "Vocabulary", "From the classroom window, we can see the ____ of the Bosphorus.", "view", ["noise", "taste", "smell"],
     "Pencereden Boğaz manzarası görülür: 'view'."),
    ("A1", "Vocabulary", "I ____ my friends a message after class.", "send", ["listen", "arrive", "sleep"],
     "Mesaj göndermek: 'send a message'."),
    ("A2", "Grammar", "I ____ a video for my media class at the moment.", "am editing", ["edit", "edited", "have edit"],
     "'at the moment' şimdiki zaman: 'am editing'."),
    ("A2", "Grammar", "This game is ____ interesting than the one we played last week.", "more", ["most", "much", "very"],
     "Uzun sıfat karşılaştırması: 'more interesting than'."),
    ("A2", "Vocabulary", "Game design students learn how to ____ characters for video games.", "create",
     ["destroy", "forget", "borrow"],
     "Karakter tasarlamak/yaratmak: 'create characters'."),
    ("A2", "Dialogue", "A: Have you seen the news about the new metro line?\nB: ____\nA: It says it will open next month.",
     "No, I haven't. What does it say?",
     ["Yes, I take the bus every morning.", "I'm reading a book about history.", "The metro is very crowded today."],
     "A haberin içeriğini anlatıyor; B görmediğini söyleyip ne yazdığını sormuş olmalı."),
    ("B2", "Grammar", "The video was shared so widely that it ____ by millions of people within a day.", "had been watched",
     ["has watched", "would be watching", "had watched"],
     "İzlendi (edilgen) ve bir gün içinde tamamlanmıştı: Past Perfect Passive."),
    ("B2", "Vocabulary", "Before sharing a news story online, you should ____ whether it comes from a reliable source.", "check",
     ["ignore", "forget", "hide"],
     "Kaynağın güvenilirliğini kontrol etmek: 'check'."),
    ("B2", "Vocabulary", "The journalist was accused of ____ the facts to support her opinion.", "distorting",
     ["verifying", "reporting", "confirming"],
     "Gerçekleri çarpıtmakla suçlanmak: 'distorting'."),
    ("B2", "Sentence Completion", "False stories often spread faster than true ones because ____.",
     "they are usually more surprising and emotional",
     ["they are always checked by many journalists", "people never share any surprising stories", "true stories are always far more exciting"],
     "Yanlış haberler genelde daha şaşırtıcı ve duygusal olduğu için hızla yayılır."),
    ("C2", "Grammar", "Had the editors checked the source more carefully, the false report ____.", "would never have been published",
     ["would never be published", "had never been published", "will never have been published"],
     "Devrik üçüncü tip koşul: 'would have + been + V3' (edilgen)."),
    ("C2", "Vocabulary", "The documentary gives a ____ account of the events, presenting all sides fairly.", "balanced",
     ["biased", "one-sided", "partisan"],
     "Tüm tarafları adilce sunan anlatım dengelidir: 'balanced'."),
    ("C2", "Restatement", "The platform's algorithm tends to show users content that reinforces their existing views.",
     "Users of the platform mostly see content that matches their existing beliefs.",
     ["The platform's algorithm actively encourages users to change their political opinions.", "Users of the platform see a wide range of opposing views.",
      "The algorithm hides content that users already agree with."],
     "Algoritma mevcut görüşleri pekiştiren içerik gösterir."),
    ("C2", "Paragraph Completion",
     "Media literacy programmes teach students to evaluate information critically. ____. Early studies suggest that students who complete such programmes are better at identifying misleading headlines.",
     "Participants learn to check sources and recognise manipulated images",
     ["Most students use social media for several hours every single day", "Therefore, students no longer need to read any news",
      "Newspapers were the main source of information in the past"],
     "Programın neler öğrettiğini anlatan cümle gerekir; sonra etkisi geliyor."),
]
CLOZE = (
    "Bahçeşehir University's main campus is in Beşiktaş, on the European shore of the Bosphorus. Students (1) ____ classrooms face the "
    "water can watch ships pass between the Black Sea and the Sea of Marmara. The university is well known for its programmes in "
    "communication, (2) ____ students learn about film, journalism and digital media. It also offers a popular game design programme, "
    "and many students (3) ____ their own games before they graduate. Because Beşiktaş is a lively district, students have plenty of "
    "opportunities to (4) ____ cultural events.",
    [
        ("whose", ["who", "which", "where"], "Sınıflar öğrencilere ait: 'Students whose classrooms face'."),
        ("where", ["which", "who", "when"], "Programları niteleyen yer bildiren sıfat cümlesi: 'where'."),
        ("develop", ["developing", "developed", "to develop"], "Özne 'many students' + geniş zaman: 'develop'."),
        ("attend", ["attending", "attended", "attends"], "'opportunities to + yalın fiil': 'to attend'."),
    ],
)
READING = (
    "Why False News Travels Fast\n\nA large study of stories shared on a major social media platform found that false news spread "
    "significantly further and faster than true news. Contrary to popular belief, automated accounts were not the main cause; they "
    "spread true and false stories at similar rates. Instead, the difference was driven largely by ordinary human users.\n\nThe "
    "researchers suggested that novelty plays a key role. False stories were more likely to contain surprising information, and people "
    "tend to share content that seems new because it makes them appear well informed. False stories also provoked stronger emotional "
    "reactions, such as surprise and disgust, which are known to encourage sharing.\n\nThese findings have implications for efforts to "
    "combat misinformation. If people rather than machines are the main channel, removing automated accounts will not be enough. "
    "Some experts argue that simple 'friction', such as asking users whether they have read an article before sharing it, can reduce the "
    "spread of false stories without restricting free expression.",
    [
        ("According to the study, who was mainly responsible for spreading false news?", "ordinary human users",
         ["automated accounts", "professional journalists", "the platform itself"],
         "Fark büyük ölçüde sıradan insan kullanıcılardan kaynaklanıyordu."),
        ("Why might people share surprising stories?", "Sharing new information makes them seem well informed.",
         ["They are paid by the platform for every story they share.", "Surprising stories are always checked before being posted.",
          "They want to warn others that the stories are false."],
         "Yeni görünen içerik paylaşmak insanı iyi bilgilenmiş gösterir."),
        ("Which emotions are mentioned as encouraging people to share?", "surprise and disgust",
         ["fear and sadness", "joy and trust", "jealousy and boredom"],
         "Şaşkınlık ve tiksinti gibi güçlü tepkiler paylaşımı artırır."),
        ("What is meant by 'friction' in the last paragraph?", "small steps that make users pause before sharing",
         ["arguments between users with different opinions", "laws that punish people for sharing news", "technical problems that slow down the platform"],
         "Paylaşmadan önce durup düşünmeyi sağlayan küçük adımlar (ör. 'makaleyi okudunuz mu?')."),
    ],
)
