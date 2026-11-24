# Akdeniz: Use of English %30, Grammar %20, Vocabulary %20, Reading %30 (turizm ağırlıklı bağlam)
UNI = "akdeniz"
ITEMS = [
    ("A1", "Grammar", "Antalya ____ famous for its beaches.", "is", ["are", "am", "be"],
     "Özne 'Antalya' tekil: 'is'."),
    ("A1", "Grammar", "Tourists ____ to Antalya every summer.", "come", ["comes", "coming", "is come"],
     "Özne 'tourists' çoğul, alışkanlık: 'come'."),
    ("A1", "Vocabulary", "We stay in a ____ near the beach during the holiday.", "hotel", ["school", "factory", "bank"],
     "Tatilde otelde kalınır: 'hotel'."),
    ("A1", "Vocabulary", "In summer it is very ____ in Antalya.", "hot", ["cold", "snowy", "icy"],
     "Antalya'da yazın hava sıcaktır: 'hot'."),
    ("A2", "Grammar", "Last summer, we ____ the ancient city of Perge.", "visited", ["visit", "visits", "are visiting"],
     "'Last summer' geçmiş zaman: 'visited'."),
    ("A2", "Grammar", "The beach is ____ crowded in August than in May.", "more", ["most", "much", "very"],
     "Uzun sıfatlarda karşılaştırma: 'more crowded than'."),
    ("A2", "Vocabulary", "Tourism students learn how to ____ guests at the hotel reception.", "welcome",
     ["forget", "ignore", "punish"],
     "Resepsiyonda misafir karşılanır: 'welcome guests'."),
    ("A2", "Vocabulary", "Sea turtles ____ their eggs on the sandy beaches at night.", "lay", ["cook", "sell", "throw"],
     "Kaplumbağalar yumurta bırakır: 'lay eggs'."),
    ("B2", "Grammar", "The hotel, ____ was built in the 1990s, has recently been renovated.", "which",
     ["who", "where", "what"],
     "Oteli niteleyen virgüllü sıfat cümlesi: 'which'."),
    ("B2", "Grammar", "If tourists ____ more careful, fewer turtle nests would be destroyed.", "were",
     ["are", "will be", "had"],
     "İkinci tip koşul: 'If + were, would + V1'."),
    ("B2", "Vocabulary", "Mass tourism can ____ local resources such as water and energy.", "put pressure on",
     ["put up with", "put the blame on", "put forward"],
     "Kaynaklar üzerinde baskı oluşturmak: 'put pressure on'."),
    ("B2", "Vocabulary", "Beaches where turtles nest are ____ areas, so building is not allowed.", "protected",
     ["polluted", "crowded", "abandoned"],
     "İnşaata izin verilmeyen alanlar koruma altındadır: 'protected'."),
    ("C2", "Grammar", "Only when the hotels agreed to dim their lights at night ____ to return to the beach.", "did the turtles begin",
     ["the turtles began", "began the turtles", "the turtles did begin"],
     "'Only when' cümle başında olunca ana cümle devrik: 'did the turtles begin'."),
    ("C2", "Vocabulary", "The region's economy is heavily ____ on tourism, which makes it vulnerable to sudden crises.", "reliant",
     ["independent", "indifferent", "immune"],
     "Turizme büyük ölçüde bağımlı: 'reliant on'."),
    ("C2", "Restatement", "Tourism brings considerable income to the region, but at a significant environmental cost.",
     "Tourism earns the region a lot of money but also harms the environment.",
     ["Tourism brings little income to the region and does not affect the environment.",
      "The region spends a lot of money protecting the environment from tourists.",
      "The environment benefits greatly from the income that tourism brings."],
     "Turizm bölgeye ciddi gelir getiriyor, ancak önemli bir çevresel bedelle."),
    ("C2", "Paragraph Completion",
     "Some Mediterranean destinations now attract more visitors than they can comfortably handle. ____. In response, several cities have introduced daily visitor limits and higher taxes on short-term rentals.",
     "Residents complain of rising rents, crowded streets and overloaded public services",
     ["Most visitors arrive in the region by plane during the summer months", "As a result, local residents have welcomed even more tourists every year",
      "The Mediterranean Sea is home to many different species of fish"],
     "Sonraki cümle ziyaretçi sınırı ve vergileri anlatıyor; boşluk aşırı turizmin sorunlarını vermeli."),
]
CLOZE = (
    "Akdeniz University is located in Antalya, one of the most popular tourist (1) ____ in Türkiye. Its campus is close to the city "
    "centre and only a short distance (2) ____ the sea. Because tourism is so important to the regional economy, the university has a "
    "large Faculty of Tourism, (3) ____ students learn about hotel management, travel and gastronomy. Many students also find summer "
    "jobs in hotels, which helps them (4) ____ their English.",
    [
        ("destinations", ["destination", "destined", "destiny"], "'one of the' + çoğul isim: 'destinations'."),
        ("from", ["of", "to", "at"], "Bir yerden kısa mesafe: 'a short distance from'."),
        ("where", ["which", "who", "when"], "Fakülteyi niteleyen yer bildiren sıfat cümlesi: 'where'."),
        ("improve", ["improving", "improved", "improves"], "'help someone (to) + yalın fiil': 'help them improve'."),
    ],
)
READING = (
    "Turtles and Tourists\n\nEvery summer, loggerhead sea turtles return to the beaches of Türkiye's Mediterranean coast to lay their "
    "eggs. The females crawl ashore at night, dig a nest in the sand and deposit around a hundred eggs before returning to the sea. "
    "About two months later, the hatchlings emerge and instinctively head towards the brightest horizon, which on a natural beach is "
    "the moonlit sea.\n\nThe growth of coastal tourism has made this journey increasingly hazardous. Bright lights from hotels and "
    "restaurants can lead hatchlings inland, where they die from exhaustion or are caught by predators. Sunbeds and umbrellas left on "
    "the sand overnight may block the path of nesting females, and heavy vehicles compact the sand above the nests.\n\nConservation "
    "groups, often working with university volunteers, now mark nests and protect them with cages. Several beaches have introduced "
    "rules requiring hotels to switch off or shield lights facing the sea and to remove beach furniture at night. Where such rules are "
    "enforced, hatchling survival has improved noticeably.",
    [
        ("How do hatchlings normally find the sea?", "They move towards the brightest horizon.",
         ["They follow their mothers back to the water.", "They listen to the sound of the waves.", "They use the smell of the salty water."],
         "Yavrular içgüdüsel olarak en parlak ufka yönelir; doğal kumsalda bu, ay ışıklı denizdir."),
        ("According to the passage, why are hotel lights dangerous for hatchlings?", "They can lead hatchlings away from the sea.",
         ["They warm the sand and damage the eggs.", "They attract tourists who disturb the nests.", "They prevent females from laying any eggs."],
         "Parlak ışıklar yavruları karaya doğru yönlendirebilir."),
        ("Which of the following is NOT mentioned as a threat?", "fishing boats near the coast",
         ["sunbeds left on the beach", "vehicles driving over the sand", "lights from hotels and restaurants"],
         "Balıkçı teknelerinden söz edilmiyor."),
        ("What does the final paragraph show?", "Enforcing simple rules can help more hatchlings survive.",
         ["Conservation groups have failed to protect nests.", "Tourists are no longer allowed on most beaches.", "Hotels have refused to follow the new rules."],
         "Kuralların uygulandığı yerlerde yavruların hayatta kalma oranı belirgin şekilde arttı."),
    ],
)
