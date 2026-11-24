# Eskişehir Teknik: Grammar & Vocabulary %30, Reading %35, Listening %15, Writing %20 (havacılık ve raylı sistemler)
UNI = "eskisehir_teknik"
ITEMS = [
    ("A1", "Grammar", "The planes ____ very loud when they take off.", "are", ["is", "am", "be"],
     "Özne 'the planes' çoğul: 'are'."),
    ("A1", "Grammar", "My brother wants to ____ a pilot.", "be", ["is", "being", "been"],
     "'want to' + yalın fiil: 'to be'."),
    ("A1", "Vocabulary", "We go from Eskişehir to Ankara by fast ____.", "train", ["boat", "horse", "bicycle"],
     "Eskişehir–Ankara arasında hızlı tren vardır: 'train'."),
    ("A1", "Vocabulary", "A pilot flies a ____.", "plane", ["bus", "car", "ship"],
     "Pilot uçak uçurur: 'plane'."),
    ("A2", "Grammar", "The high-speed train is ____ than the bus.", "faster", ["fast", "fastest", "more fast"],
     "'than' karşılaştırma: 'faster than'."),
    ("A2", "Grammar", "When I was a child, I ____ to be an astronaut.", "wanted", ["want", "wants", "am wanting"],
     "'When I was a child' geçmiş zaman: 'wanted'."),
    ("A2", "Vocabulary", "Please fasten your seat ____ before the plane takes off.", "belt", ["shoe", "glove", "scarf"],
     "Emniyet kemeri: 'seat belt'."),
    ("A2", "Vocabulary", "The train ____ at the station at exactly 10.15.", "arrived", ["opened", "slept", "painted"],
     "Tren istasyona varır: 'arrive at'."),
    ("B2", "Grammar", "The aircraft must ____ thoroughly before every flight.", "be checked", ["check", "checking", "have check"],
     "Uçak kontrol edilmeli (edilgen): 'must be checked'."),
    ("B2", "Grammar", "Students ____ aircraft maintenance must complete a long internship.", "studying",
     ["studied", "who studies", "are studying"],
     "İndirgenmiş sıfat cümlesi: 'Students (who are) studying'."),
    ("B2", "Vocabulary", "Air traffic controllers must stay ____ throughout their shift to avoid mistakes.", "alert",
     ["drowsy", "careless", "distracted"],
     "Hata yapmamak için tetikte kalmak: 'alert'."),
    ("B2", "Sentence Completion", "The flight was delayed for three hours because ____.", "thick fog made it unsafe to take off",
     ["the passengers arrived at the airport very early", "the weather was perfect for flying all day long", "the plane took off exactly on time that day"],
     "Gecikmenin mantıklı nedeni yoğun sistir."),
    ("C2", "Grammar", "Under no circumstances ____ the cockpit door during the flight.", "should passengers open",
     ["passengers should open", "passengers open", "open passengers should"],
     "'Under no circumstances' devrik yapı ister: 'should passengers open'."),
    ("C2", "Vocabulary", "The engine failure was attributed to a tiny crack that had gone ____ during routine inspections.", "undetected",
     ["unharmed", "untouched", "unnoticeable"],
     "Rutin kontrollerde fark edilmeden kalmak: 'go undetected'."),
    ("C2", "Restatement", "Rail travel between the two cities has become so fast that flying no longer makes sense for most passengers.",
     "Trains between the two cities are now so fast that most passengers no longer fly.",
     ["Most passengers still prefer flying because the trains between the cities are too slow.", "Flights between the two cities have become faster than trains.",
      "Rail travel between the two cities has been stopped completely."],
     "Tren o kadar hızlandı ki çoğu yolcu için uçmak artık anlamlı değil."),
    ("C2", "Paragraph Completion",
     "Aircraft noise is a major concern for people living near airports. ____. Modern engines are therefore designed with larger fans that move more air at lower speeds.",
     "Much of this noise is produced by the high-speed jet of air leaving the engine",
     ["Airports are usually built far away from the sea", "Consequently, modern aircraft are much louder than older ones ever were",
      "Many passengers enjoy watching planes take off and land"],
     "Sonraki cümle düşük hızda daha çok hava taşıyan fanlardan söz ediyor; gürültünün kaynağı yüksek hızlı hava jetidir."),
]
CLOZE = (
    "Eskişehir Technical University was established in 2018, when the engineering and aviation faculties of Anadolu University "
    "became (1) ____ independent university. Its Faculty of Aeronautics and Astronautics is one of the few in Türkiye (2) ____ trains "
    "pilots as well as engineers. The university also does research on railway systems, an important field for Eskişehir, (3) ____ has "
    "a long history of train manufacturing. Students can reach Ankara and Istanbul easily (4) ____ high-speed train.",
    [
        ("an", ["a", "the", "some"], "Sesli harfle başlayan 'independent' öncesi: 'an'."),
        ("that", ["what", "whose", "where"], "Fakülteyi niteleyen sıfat cümlesi: 'one of the few that trains'."),
        ("which", ["who", "where", "what"], "Eskişehir'i niteleyen virgüllü sıfat cümlesi, özne görevinde: 'which'."),
        ("by", ["on", "with", "in"], "Ulaşım aracı: 'by high-speed train'."),
    ],
)
READING = (
    "Electric Flight\n\nElectric cars have become a familiar sight, so why are electric aircraft still so rare? The main obstacle is "
    "weight. Batteries store far less energy per kilogram than jet fuel, perhaps one-fortieth as much. A car can carry a heavy battery "
    "without great difficulty, but for an aircraft every additional kilogram requires more lift and therefore more energy.\n\nThere is "
    "a further complication. As an ordinary aircraft burns fuel, it becomes lighter and more efficient during the flight. A battery, "
    "by contrast, weighs the same whether it is full or empty. For these reasons, experts expect fully electric aircraft to be limited "
    "for the foreseeable future to small planes on short routes, such as flights between islands or training flights for pilots.\n\n"
    "Longer journeys may instead rely on hybrid systems, which combine batteries with conventional engines, or on fuels produced from "
    "renewable sources. Each option has drawbacks, but together they represent the industry's most realistic path towards lower emissions.",
    [
        ("According to the passage, what is the main problem with electric aircraft?", "Batteries are very heavy for the energy they store.",
         ["Electric engines are much louder than jet engines.", "Pilots do not know how to fly electric aircraft.", "Passengers are afraid of travelling on electric planes."],
         "Piller jet yakıtına göre kilogram başına çok daha az enerji depolar."),
        ("Why is a battery less convenient than fuel during a flight?", "It does not get lighter as its energy is used.",
         ["It cannot be recharged during a long flight.", "It produces more emissions than burning fuel.", "It must be replaced before every single flight."],
         "Yakıt yandıkça uçak hafifler; pil ise dolu da boş da aynı ağırlıktadır."),
        ("Experts believe fully electric aircraft will mainly be used for ____.", "short flights in small planes",
         ["long flights across oceans", "carrying heavy cargo loads", "military operations only"],
         "Küçük uçaklar ve kısa hatlarla sınırlı kalması bekleniyor."),
        ("What does the last paragraph suggest about longer flights?", "They may depend on hybrid systems or renewable fuels.",
         ["They will become fully electric within a few years.", "They will be replaced by high-speed trains everywhere.", "They will no longer produce any emissions at all."],
         "Uzun yolculuklar hibrit sistemlere ya da yenilenebilir yakıtlara dayanabilir."),
    ],
)
