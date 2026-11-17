"""
Gerçek yeterlik sınavlarının (ODTÜ EPE, BUEPT, Bilkent PAE, İTÜ Yeterlik ve YDS tipi devlet
üniversitesi sınavları) soru TİPLERİNE göre yazılmış ÖZGÜN sorular (15.11.2026).

Hiçbir soru gerçek bir sınavdan kopyalanmamıştır (telif). Metinler ve sorular sıfırdan yazıldı;
yalnızca biçim örnek alındı: dil bilgisi, kelime, metin içi boşluk doldurma (cloze), cümle tamamlama,
anlamca en yakın cümle (restatement), diyalog tamamlama, paragraf tamamlama ve akademik okuma
(ana fikir, ayrıntı, çıkarım, gönderim, bağlamda kelime).

Sorular genel havuza (university_id="general") eklenir; her üniversitenin "Okul + Genel Havuz"
seçeneğinde ve deneme sınavlarında görünür.

Kullanım:  python scripts/add_original_questions.py          (kuru çalıştırma, yalnız denetler)
           python scripts/add_original_questions.py --write  (data/ ve mobile/assets/data/ yazar)
Tekrar çalıştırmak güvenlidir: önce eski "q-orj-*" kayıtlarını siler, sonra yeniden ekler.
Şıkların sırası soru kimliğinden türeyen tohumla karıştırılır (her çalıştırmada aynı sonuç).
"""
import collections
import json
import random
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LETTERS = "ABCD"
PREFIX = "q-orj-"

QUESTIONS = []  # (level, category, question, correct, [distractors], tr, en, passage)


def Q(level, category, question, correct, distractors, tr, en, passage=None):
    QUESTIONS.append((level, category, question, correct, distractors, tr, en, passage))


GR = "Choose the option that best completes the sentence."
VO = "Choose the word or phrase that best completes the sentence."
SC = "Choose the option that best completes the sentence."
RS = "Choose the sentence that is closest in meaning to the given sentence."
DI = "Choose the option that best completes the dialogue."
PC = "Choose the sentence that best fills the gap in the paragraph."


def cloze_q(n):
    return f"Choose the option that best fills blank ({n}) in the text."


# =====================================================================================  A1
Q("A1", "Grammar", f"{GR}\n\nMy sister ____ in a small flat near the campus.",
  "lives", ["live", "living", "is live"],
  "Özne 'my sister' tekil (she) ve cümle sürekli bir durumu anlatıyor; geniş zamanda fiile -s eklenir: 'lives'.",
  "The subject 'my sister' is third person singular, so the present simple verb takes -s: 'lives'.")
Q("A1", "Grammar", f"{GR}\n\nThere ____ two computers in the library study room.",
  "are", ["is", "be", "am"],
  "'two computers' çoğul olduğu için 'there are' kullanılır.",
  "'Two computers' is plural, so we use 'there are'.")
Q("A1", "Grammar", f"{GR}\n\nWe didn't go out yesterday because it ____ very cold.",
  "was", ["is", "were", "be"],
  "'yesterday' geçmiş zamanı gösterir; tekil 'it' ile geçmişte 'was' kullanılır.",
  "'Yesterday' signals the past, and the singular subject 'it' takes 'was'.")
Q("A1", "Grammar", f"{GR}\n\nCan you help me? I can't find ____ keys.",
  "my", ["me", "I", "mine"],
  "İsimden ('keys') önce iyelik sıfatı gelir: 'my keys'. 'mine' isimden önce kullanılmaz.",
  "A possessive adjective comes before a noun: 'my keys'. 'Mine' cannot be followed by a noun.")
Q("A1", "Vocabulary", f"{VO}\n\nI'm hungry. Let's go to the ____ and get some lunch.",
  "cafeteria", ["library", "classroom", "car park"],
  "Öğle yemeği yenecek yer 'cafeteria'dır (yemekhane / kafeterya).",
  "You get lunch in a 'cafeteria'.")
Q("A1", "Vocabulary", f"{VO}\n\nThe exam starts at nine o'clock, so please don't be ____.",
  "late", ["early", "busy", "quiet"],
  "Sınav belli bir saatte başlıyor; uyarı 'geç kalma' (late) anlamına gelir.",
  "The exam starts at a fixed time, so the warning is not to be 'late'.")
Q("A1", "Vocabulary", f"{VO}\n\nTom isn't at school today because he is ____. He has a high temperature.",
  "ill", ["happy", "hungry", "ready"],
  "Ateşi olan biri hastadır: 'ill'. Diğer seçenekler okula gelmemeyi açıklamaz.",
  "Someone with a high temperature is 'ill'; the other options do not explain his absence.")
A1_CLOZE = ("My name is Elif and I am a new student at the preparatory school. Every morning I (1) ____ "
            "the bus to the campus at eight o'clock. My classes start at nine and finish (2) ____ three "
            "o'clock. After class, I usually study in the library (3) ____ my friends.")
Q("A1", "Cloze Test", cloze_q(1), "take", ["takes", "taking", "took"],
  "Özne 'I' ve 'every morning' alışkanlık bildirir; geniş zamanda yalın fiil gelir: 'I take the bus'.",
  "With 'I' and the habit marker 'every morning', the present simple base form is needed: 'I take'.", A1_CLOZE)
Q("A1", "Cloze Test", cloze_q(2), "at", ["in", "on", "for"],
  "Saatlerden önce 'at' kullanılır: 'at three o'clock'.",
  "We use 'at' with clock times: 'at three o'clock'.", A1_CLOZE)
Q("A1", "Cloze Test", cloze_q(3), "with", ["for", "of", "about"],
  "Birisiyle birlikte ders çalışmak 'study with my friends' şeklinde ifade edilir.",
  "To study together with someone is 'study with my friends'.", A1_CLOZE)
Q("A1", "Sentence Completion", f"{SC}\n\nI want to improve my English, so ____.",
  "I read a short story in English every evening", ["my brother speaks German and French very well",
                                                    "the weather is very nice and sunny today", "I don't like reading books in any language"],
  "'so' bir sonuç bildirir; İngilizcesini geliştirmek isteyen birinin her akşam İngilizce hikâye okuması mantıklı sonuçtur.",
  "'So' introduces a result; reading an English story every evening is a logical result of wanting to improve.")
Q("A1", "Sentence Completion", f"{SC}\n\nAli couldn't answer the question because ____.",
  "he didn't understand it", ["it was very easy", "he answered it correctly", "the teacher was happy"],
  "'because' bir neden ister; soruyu cevaplayamamanın mantıklı nedeni soruyu anlamamaktır.",
  "'Because' needs a reason; not understanding the question explains why he couldn't answer it.")
Q("A1", "Restatement", f"{RS}\n\nThe library opens at 8 a.m. and closes at 10 p.m.",
  "The library is open for fourteen hours a day.", ["The library is open only in the evening.",
                                                     "The library closes at 8 a.m.", "The library is open all day and all night."],
  "Sabah 8'den akşam 10'a kadar 14 saat eder; anlamca en yakın cümle budur.",
  "From 8 a.m. to 10 p.m. is fourteen hours, so this sentence has the same meaning.")
Q("A1", "Restatement", f"{RS}\n\nMert is taller than his brother.",
  "Mert's brother is shorter than Mert.", ["Mert and his brother are the same height.",
                                          "Mert's brother is taller than Mert.", "Mert is the shortest person in his family."],
  "Mert kardeşinden uzunsa kardeşi Mert'ten kısadır; aynı bilgi ters yönden ifade edilmiştir.",
  "If Mert is taller, his brother is shorter; the same fact is expressed from the other side.")
Q("A1", "Dialogue", f"{DI}\n\nStudent: Excuse me, where is the language laboratory?\nStaff: ____",
  "It's on the second floor.", ["It opens at nine o'clock.",
                                                     "Yes, I like learning languages.", "I have two lab classes today."],
  "Öğrenci 'nerede' (where) diye soruyor; yer bildiren tek cevap ikinci kattaki konumu söyleyendir.",
  "The student asks 'where', and only this answer gives a location.")
Q("A1", "Paragraph Completion", f"{PC}\n\nOur school has a big sports centre. ____. Many students go there after class to relax and do exercise.",
  "It has a swimming pool, a gym and two tennis courts", ["The bus to the city centre is very slow in the morning",
                                                         "I don't like my mathematics teacher very much", "Our exams are on Friday and Saturday this week"],
  "Paragraf spor merkezini anlatıyor; boşluğa merkezde neler olduğunu söyleyen cümle gelir. Diğerleri konudan kopuktur.",
  "The paragraph is about the sports centre, so the gap needs a sentence describing what it has.")
A1_READ = ("Kerem is a first-year student. He lives in a student dormitory with three other students. His room "
           "is small, but it is clean and quiet. Kerem gets up at seven o'clock every day. He has breakfast in "
           "the dormitory and then walks to his English class. The walk takes fifteen minutes.\n\nAt the weekend, "
           "Kerem works in a bookshop near the campus. He likes the job because he can read new books in his free time.")
Q("A1", "Reading", "How does Kerem go to his English class?", "on foot", ["by bus", "by bike", "by car"],
  "Metinde 'then walks to his English class' (sonra İngilizce dersine yürür) denmektedir.",
  "The text says he 'walks to his English class'.", A1_READ)
Q("A1", "Reading", "What time does Kerem get up every day?", "at seven o'clock",
  ["at six o'clock", "at eight o'clock", "at fifteen past seven"],
  "Metinde 'Kerem gets up at seven o'clock every day' yazıyor. 'fifteen' yürüyüşün süresidir, saat değil.",
  "The text says he gets up at seven o'clock; 'fifteen minutes' is the length of the walk.", A1_READ)
Q("A1", "Reading", "Where does Kerem work at the weekend?", "in a bookshop near the campus",
  ["in the dormitory where he lives", "in the library on the campus", "in a café in the city centre"],
  "Metin: 'At the weekend, Kerem works in a bookshop near the campus.'",
  "The text states that he works in a bookshop near the campus.", A1_READ)
Q("A1", "Reading", "Why does Kerem like his job?", "He can read new books in his free time.",
  ["It is very close to his home town.", "It pays a lot of money.", "He works with his roommates."],
  "Metnin son cümlesi nedeni verir: 'because he can read new books in his free time'.",
  "The last sentence gives the reason: he can read new books in his free time.", A1_READ)

# =====================================================================================  A2
Q("A2", "Grammar", f"{GR}\n\nI ____ to İzmir three times since last summer.",
  "have been", ["went", "go", "am going"],
  "'since' ile geçmişte başlayıp şimdiye uzanan dönem anlatılır; Present Perfect gerekir: 'have been'.",
  "'Since last summer' describes a period up to now, which requires the present perfect: 'have been'.")
Q("A2", "Grammar", f"{GR}\n\nOur new classroom is ____ than the old one.",
  "bigger", ["more big", "biggest", "big"],
  "Tek heceli sıfatlarda karşılaştırma '-er' ile yapılır ve 'than' ile kullanılır: 'bigger than'.",
  "One-syllable adjectives form the comparative with -er: 'bigger than'.")
Q("A2", "Grammar", f"{GR}\n\nWhen the teacher came in, the students ____ a video about volcanoes.",
  "were watching", ["watch", "are watching", "have watched"],
  "Geçmişte devam eden bir eylem (video izleme) başka bir kısa eylemle (öğretmenin girmesi) kesiliyor: Past Continuous.",
  "An action in progress in the past (watching) is interrupted by a shorter action, so we use the past continuous.")
Q("A2", "Grammar", f"{GR}\n\nYou ____ use your phone during the exam. It is against the rules.",
  "mustn't", ["don't have to", "can", "should"],
  "Kurallara aykırı olan şey yasaktır: 'mustn't'. 'don't have to' yalnızca 'gerekli değil' demektir.",
  "Something against the rules is forbidden: 'mustn't'. 'Don't have to' only means it isn't necessary.")
Q("A2", "Vocabulary", f"{VO}\n\nPlease ____ this form and give it to the secretary before Friday.",
  "fill in", ["look after", "turn off", "give up"],
  "Form doldurmak 'fill in a form' şeklinde ifade edilir.",
  "The collocation is 'fill in a form'.")
Q("A2", "Vocabulary", f"{VO}\n\nThe lecture was so ____ that half of the students fell asleep.",
  "boring", ["exciting", "bored", "useful"],
  "Bir şeyin özelliği '-ing' sıfatıyla anlatılır: ders sıkıcıydı = 'boring'. 'bored' kişinin hissidir.",
  "An '-ing' adjective describes the thing: the lecture was 'boring'. 'Bored' describes how a person feels.")
Q("A2", "Vocabulary", f"{VO}\n\nI'd like to ____ this book from the library for two weeks.",
  "borrow", ["lend", "sell", "pay"],
  "Kütüphaneden ödünç ALMAK 'borrow from' ile ifade edilir; 'lend' ödünç VERMEK demektir.",
  "To take something temporarily is to 'borrow' it; 'lend' means to give it temporarily.")
A2_CLOZE = ("Last summer, I (1) ____ a two-week English course in Brighton. I stayed with a host family, and "
            "they were very friendly. Every day we had lessons in the morning, and in the afternoon we visited "
            "museums (2) ____ walked along the beach. It was my first time abroad alone, so I felt a bit "
            "(3) ____ at the beginning, but I soon made friends.")
Q("A2", "Cloze Test", cloze_q(1), "attended", ["attend", "attends", "attending"],
  "'Last summer' geçmişte bitmiş bir zamandır; Past Simple gerekir: 'attended'.",
  "'Last summer' is a finished past time, so the past simple 'attended' is needed.", A2_CLOZE)
Q("A2", "Cloze Test", cloze_q(2), "or", ["but", "so", "because"],
  "Öğleden sonra yapılan iki seçenek etkinlik sıralanıyor (müze ya da sahil): 'or'.",
  "Two alternative afternoon activities are listed (museums or the beach), so 'or' fits.", A2_CLOZE)
Q("A2", "Cloze Test", cloze_q(3), "nervous", ["boring", "crowded", "expensive"],
  "İlk kez yalnız yurt dışında olan biri başta gergin hisseder: 'nervous'. 'but I soon made friends' da bunu destekler.",
  "Being abroad alone for the first time makes someone 'nervous'; 'but I soon made friends' supports this.", A2_CLOZE)
Q("A2", "Sentence Completion", f"{SC}\n\nIf it rains tomorrow, ____.",
  "we will have the picnic in the classroom", ["we had the picnic in the park last weekend",
                                               "we would have gone to the beach instead", "the sun is shining and it is warm"],
  "Birinci tip koşul cümlesi: 'If + present simple, will + fiil'. Tek uygun yapı 'we will have'.",
  "This is a first conditional: 'If + present simple, will + verb'.")
Q("A2", "Sentence Completion", f"{SC}\n\nAlthough the exam was difficult, ____.",
  "most students passed it", ["many students failed it", "the students didn't study for it",
                              "it had a lot of hard questions"],
  "'Although' beklenmedik bir zıtlık ister: sınav zordu AMA çoğu öğrenci geçti.",
  "'Although' requires an unexpected contrast: the exam was difficult, yet most students passed.")
Q("A2", "Restatement", f"{RS}\n\nI started learning English six years ago.",
  "I have been learning English for six years.", ["Six years ago I stopped learning English.",
                                                 "I will start learning English in six years.", "I learned English in six months."],
  "Altı yıl önce başlayan ve süren eylem Present Perfect Continuous ile 'for six years' olarak anlatılır.",
  "An action that started six years ago and continues is expressed as 'have been learning for six years'.")
Q("A2", "Restatement", f"{RS}\n\nIt isn't necessary to bring your dictionary to class.",
  "You don't have to bring your dictionary to class.", ["You mustn't bring your dictionary to class.",
                                                       "You must bring your dictionary to class.", "You can't use a dictionary in class."],
  "'Gerekli değil' = 'don't have to'. 'mustn't' yasak bildirir, anlam farklıdır.",
  "'Not necessary' means 'don't have to'; 'mustn't' would mean it is forbidden.")
Q("A2", "Dialogue", f"{DI}\n\nA: I've lost my student ID card. What should I do?\nB: ____",
  "Go to the student affairs office for a new one.",
  ["I usually keep my card in my wallet.", "Oh no, I think I lost my ID card last year too.", "No, it isn't very expensive to eat here."],
  "A ne yapması gerektiğini soruyor; tavsiye veren tek cevap öğrenci işlerine gitmesini söyleyendir.",
  "A asks for advice, and only this option gives advice about what to do.")
Q("A2", "Paragraph Completion",
  f"{PC}\n\nMany students find it hard to wake up for early classes. ____. Experts say that teenagers and young adults naturally feel sleepy later at night, so they also need to sleep later in the morning.",
  "One reason for this is biological, not laziness",
  ["Breakfast is the most important meal of the day for students", "Most universities have large libraries open until midnight",
   "Some students prefer online exams to paper ones"],
  "Sonraki cümle biyolojik bir açıklama (vücut saati) veriyor; boşluğa bu açıklamayı başlatan cümle gelir.",
  "The next sentence gives a biological explanation, so the gap must introduce that reason.")
A2_READ = ("Libraries Are Changing\n\nTwenty years ago, a university library was a quiet place full of books. "
           "Students went there to find information and to study alone. Today, many libraries look very different. "
           "Most of the information students need is online, so libraries have fewer printed books and more computers. "
           "Some libraries also have group study rooms where students can talk and work together, and a few even have cafés.\n\n"
           "However, libraries still have quiet areas for students who want to study without noise. Librarians say that "
           "the number of visitors has not gone down; in fact, many libraries are busier than before.")
Q("A2", "Reading", "What is the text mainly about?", "how university libraries have changed",
  ["why students don't like libraries", "how to find a book in a library", "why many libraries are closing"],
  "Metin yirmi yıl önceki ve bugünkü kütüphaneleri karşılaştırıyor; ana fikir kütüphanelerin değişimidir.",
  "The text compares libraries twenty years ago and today; its main idea is how they have changed.", A2_READ)
Q("A2", "Reading", "Why do libraries have fewer printed books today?", "Students can find most information online.",
  ["Books have become too expensive to buy.", "Students don't enjoy reading printed books.", "Libraries need more space for their cafés."],
  "Metin: 'Most of the information students need is online, so libraries have fewer printed books'.",
  "The text says most information is online, so libraries have fewer printed books.", A2_READ)
Q("A2", "Reading", "Which of the following is TRUE according to the text?", "Libraries still offer places to study in silence.",
  ["Students can't talk in any part of the library.", "All libraries now have cafés.", "Fewer students visit libraries than before."],
  "Metin 'libraries still have quiet areas' diyor. Kafe yalnızca 'a few' kütüphanede var; ziyaretçi sayısı düşmemiş.",
  "The text says libraries still have quiet areas; only a few have cafés and visitor numbers have not fallen.", A2_READ)
Q("A2", "Reading", "What do librarians say about the number of visitors?", "Many libraries are busier now than in the past.",
  ["Visitors only come to use the cafés and computers.", "There are fewer and fewer visitors every year.", "Most visitors are not students but local people."],
  "Son cümle: 'many libraries are busier than before'.",
  "The last sentence says many libraries are busier than before.", A2_READ)

# =====================================================================================  B1
Q("B1", "Grammar", f"{GR}\n\nBy the time the lecturer arrived, most of the students ____ the room.",
  "had left", ["have left", "leave", "would leave"],
  "Geçmişteki bir olaydan (öğretmenin gelmesi) DAHA ÖNCE tamamlanan eylem Past Perfect ile anlatılır: 'had left'.",
  "An action completed before another past event takes the past perfect: 'had left'.")
Q("B1", "Grammar", f"{GR}\n\nThe new research centre, ____ was opened last month, has already attracted international funding.",
  "which", ["that", "who", "where"],
  "Virgüllerle ayrılmış (non-defining) sıfat cümlesinde nesneler için 'which' kullanılır; 'that' bu yapıda kullanılmaz.",
  "In a non-defining relative clause (between commas) we use 'which' for things; 'that' is not possible.")
Q("B1", "Grammar", f"{GR}\n\nIf I ____ more free time, I would join the university debate club.",
  "had", ["have", "will have", "would have"],
  "İkinci tip koşul (şu anki gerçek dışı durum): 'If + past simple, would + fiil'.",
  "Second conditional for an unreal present situation: 'If + past simple, would + verb'.")
Q("B1", "Grammar", f"{GR}\n\nThe exam results ____ to all candidates by email next week.",
  "will be sent", ["will send", "are sending", "have sent"],
  "Sonuçlar kendileri göndermez, gönderilir; gelecek zaman edilgen yapı gerekir: 'will be sent'.",
  "Results do not send anything; they are sent. The future passive 'will be sent' is needed.")
Q("B1", "Vocabulary", f"{VO}\n\nThe professor asked us to ____ the main points of the article in no more than 150 words.",
  "summarise", ["postpone", "interrupt", "borrow"],
  "Ana noktaları kısa biçimde yazmak 'summarise' (özetlemek) demektir.",
  "Writing the main points briefly is to 'summarise'.")
Q("B1", "Vocabulary", f"{VO}\n\nRegular exercise can significantly ____ the risk of heart disease.",
  "reduce", ["increase", "attend", "solve"],
  "Düzenli egzersiz kalp hastalığı riskini azaltır: 'reduce the risk'. 'increase' anlamca ters düşer.",
  "Exercise lowers the risk: 'reduce the risk'. 'Increase' would contradict the meaning.")
Q("B1", "Vocabulary", f"{VO}\n\nBecause of the heavy snow, the university decided to ____ the exam until the following week.",
  "postpone", ["cancel", "arrange", "promote"],
  "'until the following week' ertelemeyi gösterir: 'postpone'. 'cancel ... until' kullanılmaz; iptal edilen sınav ertelenmiş olmaz.",
  "'Until the following week' shows a delay: 'postpone'. 'Cancel' means it will not happen at all.")
B1_CLOZE = ("Social media has changed the way young people follow the news. (1) ____ previous generations relied on "
            "newspapers and television, many students today learn about world events through short videos and posts. "
            "This has clear advantages: news spreads quickly and is usually free. (2) ____, it also carries risks, "
            "because false information can spread just as fast as true stories. For this reason, teachers increasingly "
            "encourage students to (3) ____ the source of any information before sharing it.")
Q("B1", "Cloze Test", cloze_q(1), "Whereas", ["Because", "Unless", "So that"],
  "Önceki nesiller ile bugünkü öğrenciler karşılaştırılıyor; zıtlık bağlacı 'Whereas' gerekir.",
  "Previous generations are contrasted with students today, so the contrast linker 'whereas' is needed.", B1_CLOZE)
Q("B1", "Cloze Test", cloze_q(2), "However", ["Therefore", "For example", "Similarly"],
  "Önce avantajlar, sonra riskler anlatılıyor; iki cümle arasında zıtlık var: 'However'.",
  "The text moves from advantages to risks, which is a contrast: 'However'.", B1_CLOZE)
Q("B1", "Cloze Test", cloze_q(3), "check", ["ignore", "avoid", "delete"],
  "Yanlış bilgiye karşı öğrencilerin kaynağı kontrol etmesi öneriliyor: 'check the source'.",
  "Because of false information, students are encouraged to 'check the source'.", B1_CLOZE)
Q("B1", "Sentence Completion", f"{SC}\n\nMany students prefer studying in groups ____.",
  "because they can explain difficult topics to each other",
  ["although they usually learn more effectively this way", "so that they will not have to talk to anyone at all",
   "unless the library is open late in the evening"],
  "Grup çalışmasını tercih etmenin mantıklı nedeni zor konuları birbirine anlatabilmektir.",
  "The logical reason for preferring group study is being able to explain difficult topics to each other.")
Q("B1", "Sentence Completion", f"{SC}\n\n____, the experiment had to be repeated.",
  "As some of the measurements were inaccurate",
  ["Even though all the data were completely correct", "In order to avoid unnecessary extra work", "Since the results were perfect the first time"],
  "Deneyin tekrarlanmasının nedeni bazı ölçümlerin hatalı olmasıdır; 'As' burada 'çünkü' anlamındadır.",
  "The experiment was repeated because some measurements were inaccurate; 'as' means 'because' here.")
Q("B1", "Restatement", f"{RS}\n\nThe bridge was so old that it had to be closed to traffic.",
  "The bridge was too old to remain open to traffic.",
  ["Although the bridge was old, traffic continued to use it.", "Traffic was so heavy that the old bridge collapsed.",
   "The bridge was not old enough to be closed to traffic."],
  "'so ... that' yapısı 'too ... to' ile aynı anlamda yeniden yazılabilir: köprü trafiğe açık kalamayacak kadar eskiydi.",
  "'So old that it had to be closed' is equivalent to 'too old to remain open'.")
Q("B1", "Restatement", f"{RS}\n\nUnless you register online by Friday, you can't take the exam.",
  "You can only take the exam if you register online by Friday.",
  ["If you register online by Friday, you can't take the exam.", "You can take the exam even if you don't register.",
   "Registering online on Friday is not allowed."],
  "'Unless' = 'if not'. Cuma'ya kadar kayıt olmazsan giremezsin = ancak kayıt olursan girebilirsin.",
  "'Unless' means 'if not', so you can only take the exam if you register by Friday.")
Q("B1", "Dialogue",
  f"{DI}\n\nStudent: I'm thinking of dropping my statistics course. It's much harder than I expected.\nAdvisor: ____\nStudent: That's a good idea. I'll go to her office hours tomorrow.",
  "Before you decide, why don't you talk to your instructor about it?",
  ["Statistics is a compulsory course for all first-year students.", "I took the same course when I was a student.",
   "You can drop it, but you won't get a refund."],
  "Öğrencinin cevabı ('iyi fikir, yarın onun ofis saatine gideceğim') bir öneriye ve bir kişiye (her) gönderme yapıyor; bu yalnızca hocayla konuşma önerisine uyar.",
  "The student's reply ('That's a good idea... her office hours') requires a suggestion involving a woman instructor.")
Q("B1", "Paragraph Completion",
  f"{PC}\n\nWorking while studying has both benefits and drawbacks. On the one hand, a part-time job helps students pay their expenses and gain useful experience. ____. As a result, some students who work more than twenty hours a week find that their grades begin to fall.",
  "On the other hand, it leaves them less time and energy for studying",
  ["Many employers also offer free training courses to new part-time workers", "Part-time jobs are especially common in cafés, restaurants and shops",
   "Students who work usually learn to manage their money very well"],
  "'On the one hand' yapısı 'On the other hand' ile tamamlanır; ardından gelen 'notlar düşer' sonucu da dezavantajı gerektirir.",
  "'On the one hand' is completed by 'On the other hand', and the falling grades need a drawback.")
B1_READ = ("The 'Two-Minute Rule'\n\nMany university students complain that they never have enough time. Yet "
           "time-management researchers argue that the problem is often not the amount of time but the way small "
           "tasks pile up. One popular solution is the 'two-minute rule': if a task takes less than two minutes, such "
           "as replying to a short email or putting notes in a folder, you should do it immediately instead of writing "
           "it on a to-do list. Supporters say this prevents small jobs from becoming a source of stress.\n\n"
           "Critics, however, point out that the rule can be counterproductive for students who are constantly "
           "interrupted. If a student stops writing an essay every few minutes to deal with 'quick' tasks, their "
           "concentration may suffer. Most experts therefore recommend combining the rule with fixed periods of "
           "uninterrupted study.")
Q("B1", "Reading", "According to the researchers, what is often the real cause of students' time problems?",
  "small tasks that accumulate", ["having too few hours in the day", "writing to-do lists that are too long",
                                  "spending too much time on essays"],
  "Metin: 'the problem is often not the amount of time but the way small tasks pile up' (küçük işlerin birikmesi).",
  "The text says the problem is the way small tasks pile up, not the amount of time.", B1_READ)
Q("B1", "Reading", "Which of the following actions follows the two-minute rule?",
  "filing a handout at once rather than listing it",
  ["writing an essay in short two-minute sections", "checking your email every two minutes", "putting every small task on a to-do list"],
  "Kural, iki dakikadan kısa sürecek işi listeye yazmak yerine hemen yapmayı söyler; ders notunu hemen dosyalamak buna örnektir.",
  "The rule says to do any task under two minutes immediately rather than listing it; filing a handout is such a task.", B1_READ)
Q("B1", "Reading", "What concern do critics raise about the rule?", "It may break students' concentration on longer tasks.",
  ["It makes to-do lists too short.", "It takes too long to learn.", "It increases the number of emails students receive."],
  "Eleştirmenler, sürekli kısa işlerle uğraşmanın ödev yazarken konsantrasyonu bozabileceğini söylüyor.",
  "Critics say stopping for 'quick' tasks can damage concentration on an essay.", B1_READ)
Q("B1", "Reading", "The word 'counterproductive' in the second paragraph is closest in meaning to ____.",
  "having the opposite of the intended effect", ["taking an extremely long time to complete", "simple and easy for most students to follow", "widely popular among university students"],
  "'Counterproductive' amaçlananın tersi sonuç doğuran demektir; kural zaman kazandırmak yerine konsantrasyonu bozabilir.",
  "'Counterproductive' means producing the opposite of the intended result.", B1_READ)

# =====================================================================================  B2
Q("B2", "Grammar", f"{GR}\n\nHad the committee reviewed the data more carefully, it ____ the error before publication.",
  "would have noticed", ["would notice", "will have noticed", "had noticed"],
  "Devrik üçüncü tip koşul ('Had + özne + V3') geçmişe yöneliktir; ana cümle 'would have + V3' olur.",
  "An inverted third conditional ('Had the committee reviewed...') takes 'would have + past participle'.")
Q("B2", "Grammar", f"{GR}\n\nNot only ____ the deadline, but they also exceeded the project's original goals.",
  "did the team meet", ["the team met", "met the team", "the team did meet"],
  "Cümle başında 'Not only' olduğunda devrik yapı gerekir: yardımcı fiil + özne + fiil ('did the team meet').",
  "Sentence-initial 'Not only' requires inversion: auxiliary + subject + verb.")
Q("B2", "Grammar", f"{GR}\n\nThe proposal, ____ details are still being discussed, is expected to be approved next month.",
  "whose", ["which", "that", "whom"],
  "'details' önerinin detaylarıdır; iyelik bildiren sıfat cümlesi zamiri 'whose' kullanılır.",
  "The details belong to the proposal, so the possessive relative pronoun 'whose' is required.")
Q("B2", "Grammar", f"{GR}\n\nIt is high time the government ____ serious measures to reduce air pollution in large cities.",
  "took", ["takes", "will take", "has taken"],
  "'It is high time' kalıbından sonra şimdiki zamanı kastetse de Past Simple kullanılır: 'took'.",
  "After 'It is high time', the past simple is used with present meaning: 'took'.")
Q("B2", "Vocabulary", f"{VO}\n\nThe study's findings were ____ because the sample consisted of only twelve participants.",
  "inconclusive", ["comprehensive", "unanimous", "compulsory"],
  "Yalnızca on iki katılımcı kesin sonuca varmak için yetersizdir; bulgular 'inconclusive' (kesin olmayan) olur.",
  "With only twelve participants, the findings cannot be definite: they are 'inconclusive'.")
Q("B2", "Vocabulary", f"{VO}\n\nResearchers are trying to ____ the factors that cause students to drop out of university.",
  "identify", ["abandon", "postpone", "contradict"],
  "Okulu bırakmaya yol açan etkenleri belirlemek 'identify the factors' şeklinde ifade edilir.",
  "To find out and name the causes is to 'identify the factors'.")
Q("B2", "Vocabulary", f"{VO}\n\nDespite decades of research, a cure for the disease remains ____.",
  "elusive", ["abundant", "evident", "redundant"],
  "'Despite' zıtlık bildirir: onca araştırmaya rağmen tedavi hâlâ bulunamıyor = 'elusive' (ele geçmeyen).",
  "'Despite' signals contrast: in spite of research, a cure is still 'elusive' (hard to find).")
B2_CLOZE = ("Urban green spaces are often seen as a luxury, (1) ____ a growing body of research suggests that they are "
            "essential to public health. Studies have shown that people living near parks report lower levels of stress "
            "and are more likely to exercise regularly. Trees also help cities cope with rising temperatures (2) ____ "
            "providing shade and releasing moisture into the air. (3) ____ these benefits, many municipalities continue to "
            "approve construction projects that reduce the amount of green space available to residents.")
Q("B2", "Cloze Test", cloze_q(1), "yet", ["so", "for", "as"],
  "'lüks olarak görülür' ile 'temel bir gereksinimdir' arasında zıtlık var: 'yet' (ama, yine de).",
  "There is a contrast between 'a luxury' and 'essential', so 'yet' is needed.", B2_CLOZE)
Q("B2", "Cloze Test", cloze_q(2), "by", ["despite", "instead of", "in spite"],
  "Ağaçların sıcakla başa çıkmaya yardım etme YOLU anlatılıyor: 'by + V-ing' (… yaparak).",
  "The way trees help is described with 'by + -ing' (by providing shade).", B2_CLOZE)
Q("B2", "Cloze Test", cloze_q(3), "Despite", ["Owing to", "Thanks to", "Because of"],
  "Faydalara RAĞMEN yeşil alanları azaltan projeler onaylanıyor; zıtlık bildiren 'Despite' gerekir. Diğerleri neden bildirir.",
  "Projects are approved in spite of the benefits, so 'Despite' is needed; the others express cause.", B2_CLOZE)
Q("B2", "Sentence Completion", f"{SC}\n\nNo sooner had the results been announced ____.",
  "than journalists started asking about the methodology",
  ["when journalists started asking about the methodology", "so journalists started asking about the methodology",
   "before journalists had started asking about the methodology"],
  "'No sooner ... than' sabit bir kalıptır (… yapar yapmaz). 'when' ile kullanılmaz.",
  "'No sooner ... than' is a fixed structure; 'when' cannot be used with it.")
Q("B2", "Sentence Completion", f"{SC}\n\nWhile renewable energy sources are becoming cheaper, ____.",
  "storing the energy they produce remains a major technical challenge",
  ["they are also becoming less expensive with every passing year", "solar panels convert sunlight directly into usable electricity",
   "their prices have fallen steadily over the last two decades"],
  "Buradaki 'While' zıtlık bildirir; ucuzlamaya karşın hâlâ var olan bir sorun (enerjinin depolanması) gerekir.",
  "'While' expresses contrast here, so the clause must present a remaining problem (energy storage).")
Q("B2", "Restatement", f"{RS}\n\nThe museum is unlikely to reopen before the end of the year.",
  "It is doubtful whether the museum will reopen before the year ends.",
  ["The museum will definitely reopen well before the end of the year.", "The museum first closed to visitors at the end of last year.",
   "It seems likely that the museum will reopen early in the new year."],
  "'unlikely' = muhtemel değil; 'It is doubtful whether' (… şüpheli) aynı anlamı verir.",
  "'Unlikely' corresponds to 'it is doubtful whether'.")
Q("B2", "Restatement", f"{RS}\n\nHad it not been for her supervisor's support, she would never have completed her thesis.",
  "She was only able to complete her thesis thanks to her supervisor's support.",
  ["She completed her thesis without any support from her supervisor.", "Her supervisor completed the thesis for her.",
   "She didn't complete her thesis although her supervisor supported her."],
  "'Had it not been for X' = X olmasaydı. Danışmanının desteği olmasaydı bitiremezdi = ancak onun sayesinde bitirebildi.",
  "'Had it not been for her supervisor's support' means the support was what made completion possible.")
Q("B2", "Dialogue",
  f"{DI}\n\nLecturer: Your essay raises some interesting points, but the argument isn't very well organised.\nStudent: ____\nLecturer: Try writing a short outline first, with one main idea for each paragraph.",
  "What would you suggest I do to make it clearer?",
  ["Thank you, I worked very hard on the conclusion.", "Could I submit it a week after the deadline?",
   "I think the topic was too easy for this course."],
  "Hocanın cevabı bir öneridir (önce taslak yaz); bu yüzden öğrenci öneri istemiş olmalıdır.",
  "The lecturer's reply is a piece of advice, so the student must have asked for a suggestion.")
Q("B2", "Paragraph Completion",
  f"{PC}\n\nFor decades, scientists assumed that the adult human brain could not produce new neurons. ____. Researchers now believe that this process, known as neurogenesis, may play a role in learning and memory. Nevertheless, how much it continues in older adults is still hotly debated.",
  "Since the late 1990s, however, studies have found new cells forming in areas such as the hippocampus",
  ["As a result, most neuroscientists stopped studying the adult brain altogether and turned to children",
   "The human brain weighs, on average, around 1.4 kilograms and uses about a fifth of the body's energy",
   "Children, by contrast, learn new languages and motor skills far more easily than adults"],
  "Önce eski varsayım, ardından 'this process, known as neurogenesis' geliyor; boşluğa varsayımı çürüten ve yeni hücre oluşumunu anlatan cümle gelmelidir.",
  "The gap must contradict the old assumption and introduce new cells forming, which 'this process' then refers to.")
B2_READ = ("The Myth of Multitasking\n\nMany students believe they can study effectively while checking messages, "
           "listening to podcasts or watching videos. Cognitive scientists, however, argue that what we call multitasking "
           "is usually 'task switching': the brain rapidly moves its attention from one activity to another rather than "
           "processing them simultaneously. Each switch carries a small cost, as the brain must reorient itself to the new "
           "task's rules and goals. Over an hour of study, these costs can add up to a significant loss of time and accuracy.\n\n"
           "Interestingly, people who multitask most often tend to be worse at it. In one frequently cited experiment, heavy "
           "media multitaskers performed more poorly than light multitaskers on tests that required them to ignore irrelevant "
           "information. The researchers suggested that frequent multitasking may train the brain to be more easily "
           "distracted, although it is also possible that people who are naturally distractible are drawn to multitasking "
           "in the first place.\n\nThis does not mean that all combinations of activities are harmful. Tasks that are highly "
           "automatic, such as walking, can often be paired with more demanding ones without much difficulty. The problem "
           "arises when two tasks compete for the same mental resources, such as reading an article while following a conversation.")
Q("B2", "Reading", "According to the passage, what actually happens when people 'multitask'?",
  "Their attention shifts quickly between tasks.",
  ["They process two tasks at exactly the same time.", "They complete each task more slowly but more accurately.",
   "Their brain ignores the less important task."],
  "Metin: 'the brain rapidly moves its attention from one activity to another rather than processing them simultaneously'.",
  "The passage says the brain moves its attention rapidly between activities rather than processing them at once.", B2_READ)
Q("B2", "Reading", "The researchers' explanation in the second paragraph is presented as ____.",
  "one of two possible interpretations of the results",
  ["a fact proven by several experiments", "a view rejected by most cognitive scientists",
   "the reason why light multitaskers performed poorly"],
  "Yazar 'although it is also possible that...' diyerek ikinci bir olası açıklama sunuyor; yani araştırmacıların görüşü kesin değil, iki yorumdan biridir.",
  "'Although it is also possible that...' offers an alternative, so the explanation is one of two interpretations.", B2_READ)
Q("B2", "Reading", "It can be inferred from the passage that listening to a lecture while walking is ____.",
  "less problematic than reading while following a conversation",
  ["impossible for most students to manage without losing focus", "the most efficient way of learning new academic material",
   "harmful because both tasks demand a great deal of attention"],
  "Yürümek otomatik bir iş olduğu için zihinsel kaynak için yarışmaz; sorun aynı kaynağı kullanan iki zorlu işte çıkar.",
  "Walking is automatic and does not compete for the same resources, unlike reading while following a conversation.", B2_READ)
Q("B2", "Reading", "The word 'it' in 'tend to be worse at it' (paragraph 2) refers to ____.",
  "multitasking", ["studying", "the brain", "attention"],
  "Cümle 'people who multitask most often tend to be worse at it' — en çok çoklu görev yapanların bu işte (multitasking) daha kötü olduğu söyleniyor.",
  "People who multitask most are worse at multitasking; 'it' refers back to multitasking.", B2_READ)

# =====================================================================================  C1
Q("C1", "Grammar", f"{GR}\n\nLittle ____ that the minor coding error would eventually cost the company millions.",
  "did the engineers realise", ["the engineers realised", "had realised the engineers", "the engineers did realise"],
  "Olumsuz anlamlı 'Little' cümle başına geldiğinde devrik yapı gerekir: 'Little did + özne + fiil'.",
  "Negative 'Little' at the start of a sentence requires inversion: 'Little did the engineers realise'.")
Q("C1", "Grammar", f"{GR}\n\n____ extensive testing, the software still contained several critical bugs when it was released.",
  "Notwithstanding", ["Owing to", "Provided that", "In the event of"],
  "Kapsamlı teste RAĞMEN hata var; zıtlık bildiren edat 'Notwithstanding' gerekir. 'Owing to' neden bildirir.",
  "There were bugs in spite of testing, so the concessive 'notwithstanding' is required; 'owing to' expresses cause.")
Q("C1", "Grammar", f"{GR}\n\nThe new policy is likely to be unpopular, ____ it requires staff to work longer hours without additional pay.",
  "in that", ["so that", "in case", "whereas"],
  "'in that' = 'şu bakımdan / çünkü'; politikanın neden sevilmeyeceğini açıklar.",
  "'In that' means 'because' or 'in the sense that', explaining why the policy is unpopular.")
Q("C1", "Grammar", f"{GR}\n\nScarcely ____ the conference begun when the fire alarm went off.",
  "had", ["did", "has", "was"],
  "'Scarcely ... when' kalıbı devrik Past Perfect ile kullanılır: 'Scarcely had the conference begun when...'.",
  "'Scarcely ... when' takes an inverted past perfect: 'Scarcely had the conference begun'.")
Q("C1", "Vocabulary", f"{VO}\n\nThe government's response to the crisis was criticised as ____, coming months after the problem had first been reported.",
  "belated", ["premature", "meticulous", "tentative"],
  "Sorun bildirildikten aylar sonra gelen tepki gecikmiştir: 'belated'. 'premature' ise erken demektir.",
  "A response that came months later is 'belated' (late); 'premature' means too early.")
Q("C1", "Vocabulary", f"{VO}\n\nThe author's argument is ____ by her failure to consider evidence that contradicts it.",
  "undermined", ["reinforced", "alleviated", "substantiated"],
  "Karşıt kanıtları ele almamak argümanı zayıflatır: 'undermined'. 'reinforced' ve 'substantiated' güçlendirmek anlamındadır.",
  "Ignoring contrary evidence weakens an argument: it is 'undermined'.")
Q("C1", "Vocabulary", f"{VO}\n\nCritics argue that the new regulations will merely ____ the problem to another region rather than solve it.",
  "displace", ["eradicate", "alleviate", "ascertain"],
  "Sorunu çözmek yerine başka bir bölgeye kaydırmak 'displace ... to another region' ile anlatılır.",
  "Moving a problem elsewhere instead of solving it is to 'displace' it.")
C1_CLOZE = ("The notion that languages shape the way their speakers think has a long and contentious history. In its "
            "strongest form, the hypothesis claims that language (1) ____ thought, making certain concepts literally "
            "unthinkable for speakers who lack the relevant words. This version has been largely discredited. (2) ____, a "
            "weaker version, which holds that language merely influences habits of attention and memory, has found "
            "considerable experimental support. Speakers of languages that describe directions in absolute terms, such as "
            "'north' and 'south', (3) ____ perform better on certain orientation tasks than those who rely on 'left' and 'right'.")
Q("C1", "Cloze Test", cloze_q(1), "determines", ["resembles", "follows", "precedes"],
  "Hipotezin 'en güçlü hâli' dilin düşünceyi BELİRLEDİĞİNİ (determines) söyler; bu yüzden bazı kavramlar düşünülemez hâle gelir.",
  "The strongest form claims that language 'determines' thought, which is why some concepts become unthinkable.", C1_CLOZE)
Q("C1", "Cloze Test", cloze_q(2), "By contrast", ["Consequently", "Likewise", "In other words"],
  "Çürütülmüş güçlü versiyon ile destek bulan zayıf versiyon karşılaştırılıyor: 'By contrast'.",
  "The discredited strong version is contrasted with the supported weak version: 'By contrast'.", C1_CLOZE)
Q("C1", "Cloze Test", cloze_q(3), "tend to", ["refuse to", "cease to", "pretend to"],
  "Deneysel bir eğilim anlatılıyor: bu dilleri konuşanlar yön görevlerinde daha başarılı olma EĞİLİMİNDEDİR ('tend to').",
  "An experimental tendency is described: these speakers 'tend to' perform better.", C1_CLOZE)
Q("C1", "Sentence Completion", f"{SC}\n\nMuch as the committee appreciated the proposal's ambition, ____.",
  "it ultimately rejected the plan on financial grounds",
  ["it was therefore approved unanimously", "the proposal was ambitious and well researched",
   "it encouraged the authors to make it even larger"],
  "'Much as' = 'although'. Kurul hırsı takdir etse de planı REDDETTİ; zıtlık gerekir.",
  "'Much as' means 'although', so a contrasting result is needed: the plan was rejected.")
Q("C1", "Sentence Completion", f"{SC}\n\n____, the treatment has been approved only for patients who have not responded to conventional therapy.",
  "Because its long-term side effects are not yet fully understood",
  ["Since it has proved completely safe in all clinical trials so far", "Even though doctors have no concerns at all about its safety",
   "In order that as many patients as possible can benefit from it"],
  "Tedavinin yalnızca sınırlı hastalara onaylanmasının mantıklı nedeni uzun vadeli yan etkilerinin bilinmemesidir.",
  "Restricting approval makes sense because long-term side effects are not yet understood.")
Q("C1", "Restatement", f"{RS}\n\nWere the funding to be withdrawn, the project would have to be abandoned.",
  "The project can only continue as long as the funding is not withdrawn.",
  ["The funding was withdrawn last year, so the project was abandoned.", "Even if the funding is withdrawn, the project will still continue as planned.",
   "The project had already been abandoned before the funding was withdrawn."],
  "'Were the funding to be withdrawn' = 'If the funding were withdrawn' (varsayımsal). Destek kesilirse proje biter = ancak destek sürdükçe devam eder.",
  "'Were the funding to be withdrawn' is a hypothetical condition, so the project depends on continued funding.")
Q("C1", "Restatement", f"{RS}\n\nThere is no denying that the reform has had some unintended consequences.",
  "It cannot be disputed that the reform has had some unforeseen effects.",
  ["It is unclear whether the reform has had any consequences at all.",
   "The reform's consequences were exactly what its designers intended.",
   "Nobody has yet publicly admitted that the reform was a serious mistake."],
  "'There is no denying' = inkâr edilemez; 'unintended consequences' = öngörülmemiş sonuçlar.",
  "'There is no denying' equals 'it cannot be disputed', and 'unintended' corresponds to 'unforeseen'.")
Q("C1", "Dialogue",
  f"{DI}\n\nResearcher A: The survey response rate was only twelve percent, so I'm not sure we can generalise the results.\nResearcher B: ____\nResearcher A: That's true, but we still need to acknowledge it as a limitation in the paper.",
  "Admittedly it's low, but it's in line with similar studies in our field.",
  ["Exactly, which is why we should publish the results immediately.", "The survey had twenty-five questions in total.",
   "I agree that twelve percent is an excellent response rate."],
  "A'nın cevabı ('Doğru, ama yine de sınırlılık olarak belirtmeliyiz') B'nin oranı kısmen savunduğunu gösterir.",
  "A's reply ('That's true, but...') shows B partly defended the low rate, which only this option does.")
Q("C1", "Paragraph Completion",
  f"{PC}\n\nMicroplastics, fragments of plastic smaller than five millimetres, have been detected in environments as remote as Arctic sea ice and deep-ocean sediments. ____. What remains far less clear is whether the quantities to which people are typically exposed pose a significant risk to human health. Toxicologists caution that answering this question will require long-term studies that are only now beginning.",
  "They have also been found in drinking water, food and even human blood",
  ["Plastic production first began on an industrial scale in the 1950s",
   "Consequently, the health risks of microplastics are now fully understood",
   "Arctic sea ice has declined significantly over the past four decades"],
  "Sonraki cümle insanların maruziyet düzeyinden söz ediyor; boşluğa mikroplastiklerin insan vücudunda/besinlerde bulunduğunu söyleyen cümle gelir.",
  "The next sentence discusses how much people are exposed to, so the gap must link microplastics to humans.")
C1_READ = ("The Paradox of Choice in Higher Education\n\nOver the past three decades, universities in many countries have "
           "expanded the range of courses available to undergraduates, often allowing students to design highly "
           "individualised programmes. The rationale seems self-evident: greater choice should enable students to pursue "
           "their genuine interests and thereby increase both satisfaction and achievement.\n\nYet a growing body of evidence "
           "complicates this assumption. Behavioural economists have long observed that an abundance of options can lead to "
           "decision paralysis, in which individuals postpone or avoid choices altogether, and to post-decision regret, as the "
           "attractiveness of rejected alternatives looms larger in hindsight. In the academic context, students confronted "
           "with dozens of elective modules may default to those that seem least demanding, or may accumulate credits that "
           "fail to cohere into a meaningful qualification. Community colleges in the United States that replaced "
           "'cafeteria-style' course catalogues with structured 'guided pathways' have reported modest but consistent "
           "improvements in completion rates.\n\nNone of this implies that choice is inherently harmful. Rather, the evidence "
           "suggests that choice is most beneficial when accompanied by adequate guidance: clear information about how courses "
           "relate to one another and to career outcomes, and access to advisers who can help students translate vague "
           "interests into coherent plans. The challenge for institutions, then, is not to eliminate options but to make them navigable.")
Q("C1", "Reading", "The author's main purpose in the passage is to ____.",
  "argue that course choice works best when it is supported by structure and guidance",
  ["show that students should not be allowed to choose their courses",
   "explain why universities have reduced the number of courses they offer",
   "compare higher education in the United States with that in other countries"],
  "Son paragraf ana fikri verir: amaç seçenekleri kaldırmak değil, rehberlikle 'navigable' (yönetilebilir) kılmaktır.",
  "The final paragraph states the thesis: options should be made navigable through guidance, not eliminated.", C1_READ)
Q("C1", "Reading", "According to the passage, 'post-decision regret' occurs when ____.",
  "rejected options seem more attractive after a choice has been made",
  ["students are forced to take courses that they did not choose themselves", "students keep postponing the choice of their elective courses",
   "advisers recommend only the least demanding courses to students"],
  "Metin: 'the attractiveness of rejected alternatives looms larger in hindsight' (reddedilen seçenekler sonradan daha çekici görünür).",
  "The passage says rejected alternatives look more attractive in hindsight.", C1_READ)
Q("C1", "Reading", "The example of community colleges in the United States is used to ____.",
  "provide evidence that more structured programmes can improve outcomes",
  ["illustrate the problem of decision paralysis among advisers", "show that guided pathways remove all student choice",
   "suggest that completion rates are unrelated to course design"],
  "Yapılandırılmış 'guided pathways' sistemine geçen okulların mezuniyet oranları artmış; örnek, yapının faydasına kanıt olarak verilmiştir.",
  "Colleges that adopted guided pathways improved completion rates, which is evidence for structure.", C1_READ)
Q("C1", "Reading", "The word 'navigable' in the last sentence is closest in meaning to ____.",
  "easy to understand and find one's way through", ["limited to a small number of options", "available to students free of charge", "attractive to future employers and companies"],
  "Bağlamda seçenekleri kaldırmak değil, öğrencinin içinde yolunu bulabileceği hâle getirmek kastediliyor.",
  "In context, options should be made easy to understand and find one's way through.", C1_READ)

# =====================================================================================  C2
Q("C2", "Grammar", f"{GR}\n\nSo compelling was the evidence ____ even the most sceptical members of the panel were persuaded.",
  "that", ["which", "as", "than"],
  "Devrik 'So + sıfat + was + özne' yapısı da 'that' ile sonuç cümlesine bağlanır.",
  "The inverted 'So compelling was the evidence' is still followed by a result clause with 'that'.")
Q("C2", "Grammar", f"{GR}\n\nRarely ____ such a degree of consensus among economists on so contentious an issue.",
  "has there been", ["there has been", "there was being", "had been there"],
  "Cümle başındaki 'Rarely' devrik yapı ister: yardımcı fiil + 'there' + fiil ('has there been').",
  "Sentence-initial 'Rarely' requires inversion: 'has there been'.")
Q("C2", "Grammar", f"{GR}\n\nWere it not for the tireless efforts of a handful of volunteers, the archive ____ irretrievably lost decades ago.",
  "would have been", ["would be", "had been", "will have been"],
  "'decades ago' sonucu geçmişe yerleştirir; gerçek dışı geçmiş sonuç 'would have been' ile anlatılır.",
  "'Decades ago' places the hypothetical result in the past, so 'would have been' is required.")
Q("C2", "Grammar", f"{GR}\n\nThe report recommends that the scheme ____ until its environmental impact has been fully assessed.",
  "be suspended", ["suspends", "is suspending", "would suspend"],
  "'recommend that' sonrasında subjunctive (yalın fiil) kullanılır; plan askıya alınacağı için edilgen: 'be suspended'.",
  "After 'recommend that', the subjunctive base form is used; the scheme is acted upon, so 'be suspended'.")
Q("C2", "Vocabulary", f"{VO}\n\nThe biography, though meticulously researched, is marred by a ____ tone that reads more like hagiography than history.",
  "sycophantic", ["acerbic", "impartial", "laconic"],
  "'hagiography' bir kişiyi aşırı övgüyle anlatan yazıdır; buna uygun ton 'sycophantic' (dalkavukça) olur.",
  "Hagiography is excessively flattering, which matches a 'sycophantic' tone.")
Q("C2", "Vocabulary", f"{VO}\n\nThe negotiations reached an ____, with neither side willing to make further concessions.",
  "impasse", ["accolade", "epiphany", "anomaly"],
  "Hiçbir tarafın taviz vermediği durum çıkmazdır: 'impasse'.",
  "When neither side will make concessions, talks reach an 'impasse' (deadlock).")
Q("C2", "Vocabulary", f"{VO}\n\nHer ____ remarks, which seemed casual at the time, turned out to anticipate the crisis with remarkable accuracy.",
  "prescient", ["perfunctory", "pedantic", "gratuitous"],
  "Krizi doğru biçimde önceden görmüş sözler 'prescient' (ileriyi gören) olarak nitelenir.",
  "Remarks that accurately anticipated the crisis were 'prescient'.")
C2_CLOZE = ("Few scientific ideas have been as (1) ____ misunderstood as the theory of evolution by natural selection. A "
            "common misconception holds that evolution is goal-directed, as though organisms strive to become more complex "
            "or better adapted. In reality, natural selection is a blind process: variations arise without regard to their "
            "usefulness, and those that (2) ____ to confer a reproductive advantage in a given environment become more common "
            "over generations. 'Fitness', in this sense, is entirely contingent on circumstance; a trait that is advantageous "
            "in one setting may prove a liability in another. It is precisely this contingency that renders evolutionary "
            "outcomes so (3) ____ to prediction.")
Q("C2", "Cloze Test", cloze_q(1), "persistently", ["scarcely", "deliberately", "marginally"],
  "'Few ideas have been as ... misunderstood' yapısı, kuramın sürekli ve yaygın biçimde yanlış anlaşıldığını vurgular: 'persistently'.",
  "The sentence stresses a widespread, ongoing misunderstanding, so 'persistently' fits.", C2_CLOZE)
Q("C2", "Cloze Test", cloze_q(2), "happen", ["aim", "intend", "strive"],
  "Metin evrimin amaçsız olduğunu söylüyor; varyasyonlar avantaj sağlamayı 'amaçlamaz', yalnızca tesadüfen sağlar: 'happen to'.",
  "The text insists evolution has no goals, so variants merely 'happen to' confer an advantage.", C2_CLOZE)
Q("C2", "Cloze Test", cloze_q(3), "resistant", ["amenable", "conducive", "susceptible"],
  "Uygunluğun koşullara bağlı olması sonuçları öngörülemez kılar: 'resistant to prediction'. 'amenable' tersini söyler.",
  "Contingency makes outcomes hard to predict: 'resistant to prediction'; 'amenable' would mean the opposite.", C2_CLOZE)
Q("C2", "Sentence Completion", f"{SC}\n\nFar from settling the debate, ____.",
  "the new findings have only deepened the disagreement among specialists",
  ["the new findings have finally brought the long controversy to an end", "the debate was finally settled once and for all by the new findings",
   "specialists have long been in complete agreement on the issue"],
  "'Far from settling' = tartışmayı bitirmek şöyle dursun; ana cümle tam tersini, yani tartışmanın derinleştiğini söylemeli. Ayrıca özne 'findings' olmalı.",
  "'Far from settling the debate' requires the opposite outcome, with 'the findings' as subject.")
Q("C2", "Sentence Completion", f"{SC}\n\nInasmuch as the original data are no longer available, ____.",
  "the study's conclusions cannot be independently verified",
  ["the conclusions have been confirmed by several replications", "the data were collected over a ten-year period",
   "researchers will easily be able to reanalyse them"],
  "'Inasmuch as' = 'since / because'. Veri yoksa sonuçlar bağımsız olarak doğrulanamaz.",
  "'Inasmuch as' means 'since'; without the data, the conclusions cannot be verified.")
Q("C2", "Restatement", f"{RS}\n\nIt was not until the archives were opened that the full extent of the scandal came to light.",
  "Only once the archives had been opened did the true scale of the scandal become known.",
  ["The scandal was fully known to the public long before the archives were opened.", "The archives were deliberately opened in order to hide the scandal from the public.",
   "Opening the archives finally revealed that there had never been any scandal."],
  "'It was not until X that Y' = Y ancak X'ten sonra oldu. 'Only once ... did ...' aynı anlamı devrik yapıyla verir.",
  "'Not until X did Y happen' is equivalent to 'Only once X had happened did Y'.")
Q("C2", "Restatement", f"{RS}\n\nThe proposal, for all its merits, is unlikely to win the support it needs.",
  "Despite its strengths, the proposal will probably not gain enough backing.",
  ["Because of its many merits, the proposal is certain to be approved by everyone.", "The proposal has no real merits and has therefore already been rejected.",
   "The proposal needs considerably more merits before it can even be considered."],
  "'for all its merits' = tüm erdemlerine rağmen; 'unlikely to win the support' = muhtemelen yeterli desteği alamayacak.",
  "'For all its merits' means 'despite its strengths', and 'unlikely to win support' means it probably won't gain backing.")
Q("C2", "Dialogue",
  f"{DI}\n\nEditor: The reviewers felt that your conclusion overstates what the data can actually show.\nAuthor: ____\nEditor: That would help, yes, and perhaps add a paragraph on limitations as well.",
  "Would it help if I presented the claims as tentative rather than definitive?",
  ["I'm afraid I've already submitted the article to another journal instead.", "The data were collected over a period of eighteen months at three different sites.",
   "I'm glad they agreed that the conclusion is fully justified by the data."],
  "Editörün 'That would help' cevabı yazarın bir çözüm önerdiğini gösterir; iddiaları temkinli biçimde yeniden ifade etmek eleştiriye doğrudan yanıttır.",
  "'That would help' shows the author proposed a fix; softening the claims directly answers the criticism.")
Q("C2", "Paragraph Completion",
  f"{PC}\n\nHistorians have traditionally portrayed the printing press as the catalyst of a sudden intellectual revolution in early modern Europe. ____. Manuscript copying persisted for well over a century after Gutenberg, literacy rates rose only gradually, and many early printed books simply reproduced medieval texts rather than spreading new ideas. The 'revolution', in other words, was considerably slower and more uneven than the conventional narrative suggests.",
  "More recent scholarship, however, has questioned how abrupt this transformation really was",
  ["Gutenberg's press was therefore immediately adopted in every European city and town",
   "The printing press was invented in the mid-fifteenth century in the German city of Mainz",
   "Most historians agree that this revolution happened almost overnight across the continent"],
  "Paragraf geleneksel görüşü verip ardından onu çürüten kanıtlar sıralıyor; boşluğa 'yeni araştırmalar bunu sorguladı' diyen geçiş cümlesi gelir.",
  "The paragraph moves from the traditional view to counter-evidence, so the gap must introduce that challenge.")
C2_READ = ("Against Metrics\n\nIn recent decades, institutions ranging from hospitals to universities have increasingly "
           "sought to evaluate performance through quantitative indicators: waiting times, citation counts, graduation "
           "rates. The appeal is understandable. Numbers promise transparency and comparability, and they appear to "
           "insulate judgements from personal bias. Yet critics contend that this enthusiasm rests on a category error, "
           "namely the assumption that whatever is measurable is also what matters most.\n\nThe difficulty is compounded by "
           "a phenomenon often associated with the economist Charles Goodhart: when a measure becomes a target, it ceases to "
           "be a good measure. Once individuals know that they will be judged by a particular indicator, they have every "
           "incentive to improve the indicator itself rather than the underlying quality it was intended to capture. "
           "Hospitals may reclassify patients to shorten recorded waiting times; academics may divide a single study into "
           "several smaller publications to inflate their output. In each case the number improves while the reality it "
           "purports to describe stagnates or even deteriorates.\n\nTo acknowledge these distortions is not to reject "
           "measurement wholesale. Indicators can serve as valuable prompts for inquiry, signalling where closer attention "
           "might be warranted. The error lies in treating them as substitutes for judgement rather than as aids to it.")
Q("C2", "Reading", "The 'category error' mentioned in the first paragraph refers to ____.",
  "equating what can be counted with what is most important",
  ["using numbers to compare different types of institutions", "allowing personal bias to influence evaluations",
   "measuring hospitals and universities with the same indicators"],
  "Metin hatayı açıkça tanımlıyor: 'the assumption that whatever is measurable is also what matters most'.",
  "The passage defines it as assuming that whatever is measurable is also what matters most.", C2_READ)
Q("C2", "Reading", "The examples of hospitals and academics in the second paragraph serve to illustrate ____.",
  "how people may improve an indicator without improving actual performance",
  ["why quantitative indicators are always manipulated deliberately", "that waiting times and publication counts are unrelated",
   "how Goodhart first developed his theory"],
  "Her iki örnekte de sayı iyileşiyor ama gerçeklik iyileşmiyor: 'the number improves while the reality ... stagnates'.",
  "In both examples the number improves while the underlying reality does not.", C2_READ)
Q("C2", "Reading", "The author's attitude towards quantitative indicators can best be described as ____.",
  "qualified acceptance: useful as aids to judgement, not as substitutes for it",
  ["wholehearted endorsement of their objectivity and reliability in every field",
   "outright rejection of all forms of measurement as fundamentally misleading",
   "complete indifference to how institutions choose to use such indicators"],
  "Yazar ölçümü tümden reddetmiyor ('not to reject measurement wholesale') ama yargının yerine konmasına karşı çıkıyor: koşullu kabul.",
  "The author does not reject measurement wholesale but objects to using it as a substitute for judgement.", C2_READ)
Q("C2", "Reading", "The word 'purports' in the second paragraph is closest in meaning to ____.",
  "claims", ["fails", "refuses", "happens"],
  "'the reality it purports to describe' = sayının betimlediğini İDDİA ETTİĞİ gerçeklik; 'purport' = iddia etmek.",
  "'Purports to describe' means 'claims to describe'.", C2_READ)


# =====================================================================================  derleme
# Şıklar karıştırıldığı için açıklamalar "option B", "(C)", "D şıkkı" gibi harf atıfları içermemeli.
LETTER_REF = re.compile(r"(?i:\b(?:option|choice|answer|seçenek|cevap)\s+)[A-D]\b|\([A-D]\)|\b[A-D]\s+(?:şık|seçene)")


def build():
    out, per_level = [], collections.Counter()
    for level, cat, question, correct, distractors, tr, en, passage in QUESTIONS:
        per_level[level] += 1
        qid = f"{PREFIX}{level.lower()}-{per_level[level]:02d}"
        texts = [correct] + list(distractors)
        assert len(texts) == 4 and len({t.strip().lower() for t in texts}) == 4, qid
        for f in (tr, en):
            assert not LETTER_REF.search(f), f"{qid}: açıklama şık harfine atıf yapıyor"
        for s in (question, passage or "", *texts, tr, en):
            assert "<" not in s and ">" not in s and "&" not in s, f"{qid}: HTML karakteri"
        rng = random.Random("prepmaster-ozgun-v1:" + qid)
        order = list(range(4))
        rng.shuffle(order)
        options = [{"key": LETTERS[i], "text": texts[j]} for i, j in enumerate(order)]
        item = {
            "id": qid, "university_id": "general", "level": level, "category": cat,
            "question": question, "options": options,
            "correct_answer": LETTERS[order.index(0)],
            "explanation_tr": tr, "explanation_en": en,
        }
        if passage:
            item["passage"] = passage
        out.append(item)
    return out


def main(write):
    new = build()
    path = ROOT / "data" / "questions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data = [q for q in data if not q["id"].startswith(PREFIX)]
    ids = {q["id"] for q in data}
    assert not ids & {q["id"] for q in new}
    data.extend(new)

    print("Eklenen özgün soru:", len(new))
    print("Seviye:", dict(sorted(collections.Counter(q["level"] for q in new).items())))
    print("Kategori:", dict(collections.Counter(q["category"] for q in new)))
    print("Doğru şık dağılımı:", dict(sorted(collections.Counter(q["correct_answer"] for q in new).items())))
    longest = sum(1 for q in new if max(q["options"], key=lambda o: len(o["text"]))["key"] == q["correct_answer"])
    print(f"Doğru şıkkın en uzun şık olduğu soru: {longest}/{len(new)}")
    print("Toplam soru:", len(data))
    if write:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        shutil.copyfile(path, ROOT / "mobile" / "assets" / "data" / path.name)
        print("Yazıldı: data/questions.json ve mobile/assets/data/questions.json")


if __name__ == "__main__":
    main("--write" in sys.argv)
