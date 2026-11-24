# Ankara Üniversitesi: Grammar & Structure %25, Vocabulary & Collocations %20, Reading %35, Essay %20
UNI = "ankara"
ITEMS = [
    ("A1", "Grammar", "My sister ____ at Ankara University.", "studies", ["study", "studying", "is study"],
     "Özne 'my sister' tekil; geniş zamanda fiile -es eklenir: 'studies'."),
    ("A1", "Grammar", "I ____ to the campus by bus every day.", "go", ["goes", "going", "gone"],
     "Özne 'I', alışkanlık: 'I go'."),
    ("A1", "Vocabulary", "We look at the stars with a big ____ at the observatory.", "telescope", ["spoon", "blanket", "pillow"],
     "Gözlemevinde yıldızlara teleskopla bakılır: 'telescope'."),
    ("A1", "Vocabulary", "The canteen sells cheap food, so it is very ____ with students.", "popular", ["angry", "tired", "empty"],
     "Ucuz yemek satan kantin öğrenciler arasında sevilir: 'popular with'."),
    ("A2", "Grammar", "Ankara University is one of the ____ universities in Türkiye.", "oldest", ["old", "older", "most old"],
     "'one of the' yapısından sonra üstünlük derecesi gelir: 'the oldest'."),
    ("A2", "Grammar", "We ____ our project when the electricity went off.", "were finishing", ["finish", "have finished", "are finishing"],
     "Geçmişte devam eden eylem (proje) kısa bir olayla (elektrik kesintisi) kesildi: Past Continuous."),
    ("A2", "Vocabulary", "I always ____ notes during my history lectures.", "take", ["do", "get", "say"],
     "Not almak İngilizcede 'take notes' kalıbıyla söylenir."),
    ("A2", "Vocabulary", "You should ____ attention to the professor's examples.", "pay", ["make", "take", "keep"],
     "Dikkat etmek: 'pay attention to'."),
    ("B2", "Grammar", "The students ____ outside; the exam hall had been open all along.", "needn't have waited",
     ["mustn't have waited", "can't have to wait", "didn't need wait"],
     "Gereksiz yere yapılmış geçmiş eylem 'needn't have + V3' ile anlatılır: beklemelerine gerek yoktu."),
    ("B2", "Grammar", "It was the observatory's old telescope ____ first captured an image of the comet.", "that",
     ["what", "where", "when"],
     "Vurgulu (cleft) yapı: 'It was X that ...'."),
    ("B2", "Vocabulary", "The government has ____ a decision to build a new metro line to the Gölbaşı campus.", "made",
     ["done", "given", "had"],
     "Karar vermek: 'make a decision'."),
    ("B2", "Vocabulary", "Many students ____ part-time jobs to cover their living costs.", "take on", ["take off", "take after", "take over"],
     "'take on a job' = bir işi üstlenmek. 'take after' benzemek, 'take over' devralmak demektir."),
    ("C2", "Grammar", "Such ____ the demand for the course that a second section had to be opened.", "was", ["is being", "has", "were"],
     "'Such + be + özne + that' devrik yapısı; özne 'the demand' tekil ve geçmişte: 'was'."),
    ("C2", "Vocabulary", "The report ____ serious doubts on the reliability of the survey.", "casts", ["makes", "puts", "sets"],
     "Şüphe düşürmek: 'cast doubt on'."),
    ("C2", "Vocabulary", "The findings ____ the way for a new treatment of the disease.", "pave", ["draw", "lay", "cut"],
     "Yol açmak: 'pave the way for'."),
    ("C2", "Paragraph Completion",
     "Ankara University's Faculty of Language, History and Geography was founded in 1936 as part of an effort to build a national academic tradition. ____. Its graduates went on to staff archives, museums and schools across the young republic.",
     "Its scholars pioneered research on Anatolian history and languages",
     ["Ankara became the capital of the Turkish Republic in October 1923", "As a result, no history courses were taught in Ankara for many years",
      "Many students today prefer to study engineering instead of history"],
     "Fakültenin akademik katkısını anlatan cümle gerekir; mezunların arşiv ve müzelerde çalışması da bunu izler."),
]
CLOZE = (
    "Ankara University was officially founded in 1946, but some of its faculties are older. The Faculty of Language, History and "
    "Geography, for example, (1) ____ in 1936. Today the university has campuses in many parts of the city, (2) ____ Cebeci, Tandoğan "
    "and Gölbaşı. Its observatory is one of the oldest in the country, and students can visit it (3) ____ clear nights. The university "
    "also has a large hospital (4) ____ thousands of patients are treated every year.",
    [
        ("was founded", ["founded", "is founded", "has founded"], "Fakülte kuruldu (edilgen, 1936): 'was founded'."),
        ("including", ["include", "included", "includes"], "Örnek sıralarken 'including' kullanılır."),
        ("on", ["in", "at", "by"], "Belirli gece/günlerde 'on' kullanılır: 'on clear nights'."),
        ("where", ["which", "who", "when"], "Yer bildiren sıfat cümlesi: 'a hospital where patients are treated'."),
    ],
)
READING = (
    "Losing the Night Sky\n\nWhen Ankara University's observatory was built in the 1960s, the hills south of the city were dark "
    "enough for detailed astronomical work. Today, the glow of street lights, billboards and illuminated buildings has spread across "
    "much of the horizon. Astronomers call this phenomenon light pollution, and it affects far more than scientific research. Studies "
    "indicate that around a third of humanity can no longer see the Milky Way from where they live.\n\nThe consequences extend to "
    "wildlife and human health. Migrating birds, which navigate partly by starlight, can become disoriented by brightly lit towers, "
    "and artificial light at night has been linked to disrupted sleep patterns in humans. Unlike many forms of pollution, however, "
    "light pollution is relatively easy to reverse. Shielding street lamps so that they shine downwards, using warmer colours and "
    "switching off unnecessary lighting after midnight can reduce sky glow substantially without compromising safety. Several European "
    "cities have adopted such measures and report energy savings as well as darker skies.",
    [
        ("What is the main idea of the passage?", "Light pollution has wide effects but can be reduced fairly easily.",
         ["Observatories should be moved far away from all cities.", "Most people prefer bright cities to dark night skies.",
          "Light pollution mainly affects the work of professional astronomers."],
         "Metin ışık kirliliğinin geniş etkilerini anlatıp görece kolay azaltılabildiğini söylüyor."),
        ("Why does the author mention migrating birds?", "to show that light pollution also harms animals",
         ["to explain how observatories were built", "to prove that birds prefer lit cities", "to describe how migrating birds affect human sleep"],
         "Göçmen kuşların yön şaşırması, ışık kirliliğinin hayvanlara da zarar verdiğini gösterir."),
        ("According to the passage, what makes light pollution different from many other kinds of pollution?",
         "It can be reversed relatively easily.",
         ["It affects only a small number of people.", "It cannot be measured by scientists.", "It has no effect on human health."],
         "'Unlike many forms of pollution, light pollution is relatively easy to reverse.'"),
        ("The European cities mentioned in the last paragraph have experienced ____.", "lower energy use as well as darker skies",
         ["more accidents because the streets are darker", "higher costs because of the new street lamps", "complaints from astronomers about the changes"],
         "Bu şehirler hem enerji tasarrufu hem daha karanlık gökyüzü bildiriyor."),
    ],
)
