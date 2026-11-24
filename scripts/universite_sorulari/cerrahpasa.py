# İÜ-Cerrahpaşa: Use of English %30, Grammar %20, Vocabulary %20, Reading %30
UNI = "cerrahpasa"
ITEMS = [
    ("A1", "Grammar", "The nurses ____ very busy in the morning.", "are", ["is", "am", "be"],
     "Özne 'the nurses' çoğul: 'are'."),
    ("A1", "Grammar", "Please don't ____ in the hospital corridors.", "run", ["runs", "running", "ran"],
     "Olumsuz emir cümlesi 'don't + yalın fiil': 'don't run'."),
    ("A1", "Vocabulary", "A doctor uses a ____ to listen to your heart.", "stethoscope", ["hammer", "brush", "kettle"],
     "Kalp sesi stetoskopla dinlenir: 'stethoscope'."),
    ("A1", "Vocabulary", "I have a high temperature. I think I have a ____.", "fever", ["holiday", "garden", "ticket"],
     "Yüksek ateş: 'fever'."),
    ("A2", "Grammar", "The patient ____ his medicine three times a day.", "takes", ["take", "taking", "is take"],
     "Özne tekil, alışkanlık: 'takes'."),
    ("A2", "Grammar", "You ____ smoke in the hospital. It's against the rules.", "mustn't", ["don't have to", "needn't", "can"],
     "Yasak bildiren: 'mustn't'. 'don't have to' gereklilik olmadığını anlatır."),
    ("A2", "Vocabulary", "The ____ carried the injured man to the ambulance.", "paramedics", ["pilots", "chefs", "lawyers"],
     "Yaralıyı ambulansa sağlık görevlileri taşır: 'paramedics'."),
    ("A2", "Vocabulary", "Before the operation, the surgeon ____ her hands carefully.", "washed", ["cooked", "painted", "sold"],
     "Cerrah ameliyattan önce ellerini yıkar: 'washed'."),
    ("B2", "Grammar", "The patient is believed ____ from the infection completely.", "to have recovered",
     ["recovering", "to recover", "having recovered"],
     "Geçmişte tamamlanmış eylem için 'be believed + to have + V3'."),
    ("B2", "Grammar", "The new surgical technique, ____ was developed in the 1990s, reduces recovery time.", "which",
     ["who", "what", "whose"],
     "Teknik nesne; virgüllü sıfat cümlesinde 'which'."),
    ("B2", "Vocabulary", "The doctor ____ antibiotics for the infection.", "prescribed", ["described", "subscribed", "inscribed"],
     "İlaç yazmak: 'prescribe'."),
    ("B2", "Vocabulary", "Early ____ of the disease greatly increases the chances of successful treatment.", "diagnosis",
     ["prognosis", "surgery", "recovery"],
     "Hastalığın erken teşhisi: 'diagnosis'. 'prognosis' seyrin tahminidir."),
    ("C2", "Grammar", "So severe ____ the injuries that the patient had to be transferred to intensive care.", "were",
     ["was", "had", "did"],
     "'So + sıfat + be + özne' devrik yapısı; özne 'the injuries' çoğul: 'were'."),
    ("C2", "Vocabulary", "The virus is highly ____, spreading rapidly from person to person.", "contagious",
     ["benign", "dormant", "inert"],
     "Kişiden kişiye hızla yayılan virüs bulaşıcıdır: 'contagious'."),
    ("C2", "Vocabulary", "The symptoms ____ after a few days of treatment, and the patient was sent home.", "subsided",
     ["escalated", "intensified", "flared up"],
     "Tedaviyle belirtiler geriledi ve hasta eve gönderildi: 'subsided'."),
    ("C2", "Restatement", "The new drug, while effective, is prohibitively expensive for most hospitals.",
     "Although the new drug works, most hospitals cannot afford it.",
     ["The new drug is cheap but does not work in most cases.", "Most hospitals buy the new drug because it is effective.",
      "The new drug is banned in most hospitals because it is dangerous."],
     "'prohibitively expensive' = karşılanamayacak kadar pahalı; ilaç etkili ama çoğu hastane alamıyor."),
]
CLOZE = (
    "Cerrahpaşa Faculty of Medicine has trained doctors in Istanbul for more (1) ____ a century. In 2018, it became part of a new "
    "university, Istanbul University-Cerrahpaşa, (2) ____ also includes faculties of engineering, forestry and health sciences. The "
    "medical faculty is (3) ____ for its hospital, where students gain practical experience under the supervision of senior doctors. "
    "Many graduates later (4) ____ in hospitals all over Türkiye.",
    [
        ("than", ["then", "that", "as"], "'more than a century' = bir asırdan fazla."),
        ("which", ["who", "where", "whose"], "Üniversiteyi niteleyen virgüllü sıfat cümlesi: 'which'."),
        ("known", ["knowing", "know", "knew"], "Bir şeyle tanınmak: 'be known for'."),
        ("work", ["working", "worked", "to work"], "'Many graduates later' + geniş zaman: 'work'."),
    ],
)
READING = (
    "Hand Hygiene\n\nIn the 1840s, a Hungarian doctor working in Vienna noticed that women who gave birth in a ward run by doctors "
    "died of fever far more often than those in a ward run by midwives. He observed that doctors frequently came directly from "
    "dissecting bodies to examine patients. When he required staff to wash their hands in a chlorine solution, the death rate fell "
    "dramatically. Yet his colleagues largely rejected his conclusions, partly because the role of germs in disease had not yet been "
    "established.\n\nToday, hand hygiene is recognised as one of the most effective ways to prevent infections in hospitals. Even so, "
    "studies regularly find that health workers clean their hands far less often than guidelines recommend, particularly when wards are "
    "busy. Reasons include time pressure, skin irritation from frequent washing and the simple belief that gloves offer enough "
    "protection.\n\nHospitals that have improved compliance usually combine several approaches: placing alcohol-based hand rub at every "
    "bedside, giving staff regular feedback on their performance and encouraging patients to remind workers to clean their hands.",
    [
        ("What did the doctor in Vienna notice?", "More women died in the doctors' ward than in the midwives' ward.",
         ["Midwives washed their hands less often than the doctors did.", "Women who gave birth at home were more likely to die.",
          "Fever was more common among doctors than among patients."],
         "Doktorların yönettiği koğuşta ateşten ölüm, ebelerinkine göre çok daha sıktı."),
        ("Why did many colleagues reject his conclusions?", "The link between germs and disease was not yet known.",
         ["Chlorine was too expensive for most hospitals.", "The death rate did not change after hand washing.", "Midwives refused to follow his instructions."],
         "Mikropların hastalıktaki rolü henüz ortaya konmamıştı."),
        ("Which is NOT mentioned as a reason why health workers clean their hands too rarely?", "a shortage of water in hospitals",
         ["time pressure on busy wards", "skin irritation caused by frequent washing", "the belief that gloves are enough protection"],
         "Metinde su kıtlığından söz edilmiyor; diğer üçü sayılıyor."),
        ("According to the last paragraph, successful hospitals ____.", "use a combination of different methods",
         ["ban gloves on all of their wards", "rely only on patients to remind staff", "punish workers who forget to wash"],
         "Başarılı hastaneler genellikle birkaç yaklaşımı bir arada kullanır."),
    ],
)
