# YTÜ İYS: Use of English & Grammar %25, Vocabulary in Context %20, Reading %30, Essay %25
UNI = "ytu"
ITEMS = [
    ("A1", "Grammar", "The Davutpaşa campus ____ very big and green.", "is", ["are", "be", "am"],
     "Özne 'the campus' tekil: 'is'."),
    ("A1", "Grammar", "Where ____ you study last night?", "did", ["do", "were", "are"],
     "'last night' geçmiş zaman; soru 'Where did you study' ile kurulur."),
    ("A1", "Vocabulary", "I write my notes in a ____ during the lesson.", "notebook", ["pillow", "window", "bottle"],
     "Ders notları deftere yazılır: 'notebook'."),
    ("A1", "Vocabulary", "The architecture students ____ pictures of old buildings.", "draw", ["drink", "sleep", "swim"],
     "Mimarlık öğrencileri bina resimleri çizer: 'draw pictures'."),
    ("A2", "Grammar", "The Yıldız campus is in Beşiktaş, ____ the Davutpaşa campus is in Esenler.", "while", ["because", "so", "if"],
     "İki kampüsün yeri karşılaştırılıyor; karşıtlık bağlacı 'while'."),
    ("A2", "Vocabulary", "Please ____ off your phones before the exam begins.", "turn", ["take", "look", "give"],
     "Telefonu kapatmak 'turn off' ile anlatılır."),
    ("A2", "Vocabulary", "The library is very ____; you can hear every page you turn.", "quiet", ["crowded", "noisy", "busy"],
     "Sayfa sesinin bile duyulduğu yer çok sessizdir: 'quiet'."),
    ("A2", "Sentence Completion", "I couldn't attend the morning lecture because ____.", "my train from Esenler was cancelled",
     ["I arrived at the lecture hall very early", "the lecture was really very interesting", "I took very good notes in the lecture"],
     "Derse katılamamanın mantıklı nedeni trenin iptal edilmesidir."),
    ("B2", "Grammar", "If the students ____ the safety rules, the accident in the chemistry lab would not have happened.", "had followed",
     ["followed", "would follow", "have followed"],
     "Üçüncü tip koşul (geçmişe pişmanlık): 'If + had + V3, would have + V3'."),
    ("B2", "Grammar", "The architect, ____ designs have won several awards, will give a talk on Friday.", "whose", ["who", "which", "whom"],
     "Tasarımlar mimara ait; iyelik bildiren 'whose' kullanılır."),
    ("B2", "Vocabulary", "Because the old building could ____ collapse in an earthquake, the faculty moved to a new block.", "potentially",
     ["deliberately", "reluctantly", "punctually"],
     "Depremde 'olası olarak' çökebilecek bina: 'potentially'."),
    ("B2", "Vocabulary", "The city council ____ the university to use the historic palace grounds for teaching.", "permitted",
     ["prevented", "prohibited", "refused"],
     "'permit someone to do' = izin vermek; diğerleri bu yapıyla kullanılmaz ya da anlamca ters düşer."),
    ("C2", "Grammar", "Not until the final inspection ____ that the foundations were cracked.", "did the engineers discover",
     ["the engineers discovered", "discovered the engineers", "the engineers did discover"],
     "'Not until ...' cümle başında olunca ana cümle devrik olur: 'did the engineers discover'."),
    ("C2", "Vocabulary", "The restoration project aims to ____ the palace's original features while adding modern facilities.", "preserve",
     ["obliterate", "dismantle", "forsake"],
     "Restorasyon özgün özellikleri korumayı amaçlar: 'preserve'."),
    ("C2", "Vocabulary", "The new regulations are ____ with international building standards, so no further changes are needed.", "consistent",
     ["incompatible", "inconsistent", "unfamiliar"],
     "'Başka değişiklik gerekmiyor' ifadesi uyumluluğu gösterir: 'consistent with'."),
    ("C2", "Restatement", "The building's energy consumption was cut by almost half, an achievement few had thought possible.",
     "Few people thought the building's energy use could be nearly halved, but it was.",
     ["Most people expected the building's energy use to double, and it eventually did.", "The building's energy consumption stayed the same despite everyone's expectations.",
      "Nobody ever tried to reduce the building's energy consumption in any way at all."],
     "Enerji tüketimi neredeyse yarıya indi ve bu, pek az kişinin mümkün gördüğü bir başarıydı."),
]
CLOZE = (
    "Yıldız Technical University has two main campuses in Istanbul. The historic Yıldız campus is located in the gardens of an old "
    "Ottoman (1) ____, while most engineering faculties are at Davutpaşa. Every year, thousands of students take the YTÜ proficiency "
    "exam, (2) ____ tests grammar, vocabulary, reading and writing. Students who get a score (3) ____ than the pass mark can start "
    "their departments. The others improve their English in the preparatory programme (4) ____ the following year.",
    [
        ("palace", ["market", "ship", "bridge"], "Yıldız kampüsü eski bir Osmanlı sarayının bahçelerindedir: 'palace'."),
        ("which", ["who", "what", "where"], "Virgüllü sıfat cümlesi sınavı niteliyor: 'which'."),
        ("higher", ["high", "highest", "more high"], "'than' karşılaştırma ister: 'higher than'."),
        ("during", ["since", "ago", "among"], "Bir süre boyunca: 'during the following year'."),
    ],
)
READING = (
    "Adaptive Reuse\n\nWhen a historic building outlives its original purpose, cities face a difficult choice: demolish it, preserve "
    "it as a museum, or adapt it for a new use. The third option, known as adaptive reuse, has become increasingly popular among "
    "architects. Supporters argue that it conserves the energy already 'embodied' in existing materials; constructing a new building "
    "of the same size can produce more carbon emissions than decades of operating an old one.\n\nAdaptive reuse is not without "
    "difficulties, however. Historic structures were rarely designed for modern loads, accessibility requirements or earthquake "
    "resistance, and bringing them up to current standards can be more expensive than building from scratch. Conservationists also "
    "worry that excessive alterations may erase the very features that made a building worth saving.\n\nSuccessful projects, therefore, "
    "tend to follow a principle of minimum intervention: new elements are added in a way that is clearly distinguishable from the "
    "original fabric and, ideally, could be removed in the future without damaging it.",
    [
        ("What is the main environmental argument for adaptive reuse?", "It avoids the emissions caused by constructing new buildings.",
         ["It makes old buildings use less electricity than new ones.", "It allows architects to use only modern building materials.",
          "It turns every historic building into a public museum."],
         "Yeni bina yapmak, eski binayı onlarca yıl işletmekten fazla karbon salımına yol açabilir."),
        ("According to the passage, why can adaptive reuse be costly?", "Old buildings must be upgraded to meet modern standards.",
         ["Historic materials cost more than modern ones.", "Architects charge more for working on museums.", "Old buildings use far more energy than modern new ones do."],
         "Tarihi yapıları güncel yük, erişilebilirlik ve deprem standartlarına getirmek pahalıdır."),
        ("Conservationists are concerned that ____.", "too many changes may destroy a building's valuable features",
         ["historic buildings cannot be adapted for any new use", "new buildings are always more beautiful than old ones", "minimum intervention costs more than demolition"],
         "Aşırı değişiklik, binayı korunmaya değer kılan özellikleri silebilir."),
        ("The principle of 'minimum intervention' suggests that new elements should be ____.", "clearly different from the original and removable",
         ["identical in style to the original building", "permanent so that the building stays strong", "hidden completely inside the original walls"],
         "Yeni öğeler özgün yapıdan açıkça ayırt edilebilmeli ve ileride zarar vermeden sökülebilmeli."),
    ],
)
