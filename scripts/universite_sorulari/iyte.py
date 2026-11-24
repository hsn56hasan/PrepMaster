# İYTE: Grammar & Vocabulary %25, Reading %35, Listening %20, Writing %20 (mühendislik ağırlıklı)
UNI = "iyte"
ITEMS = [
    ("A1", "Grammar", "The İYTE campus ____ in Urla, near the sea.", "is", ["are", "am", "be"],
     "Özne tekil: 'is'."),
    ("A1", "Grammar", "There ____ a lot of wind turbines on the hills.", "are", ["is", "be", "am"],
     "'a lot of wind turbines' çoğul: 'there are'."),
    ("A1", "Vocabulary", "It is often very ____ on the campus, so the trees bend.", "windy", ["sleepy", "hungry", "quiet"],
     "Ağaçları eğen hava rüzgârlıdır: 'windy'."),
    ("A1", "Vocabulary", "Engineering students use ____ to solve problems in the lab.", "computers", ["pillows", "flowers", "sandwiches"],
     "Laboratuvarda problem çözmek için bilgisayar kullanılır: 'computers'."),
    ("A2", "Grammar", "The campus is ____ from the city centre than I expected.", "further", ["far", "furthest", "more far"],
     "'than' karşılaştırma ister: 'further than'."),
    ("A2", "Grammar", "We ____ the experiment twice, but it didn't work.", "tried", ["try", "tries", "trying"],
     "Geçmişte tamamlanmış eylem: 'tried'."),
    ("A2", "Vocabulary", "Solar panels ____ sunlight into electricity.", "turn", ["bring", "keep", "hold"],
     "Bir şeyi başka bir şeye dönüştürmek: 'turn into'."),
    ("A2", "Sentence Completion", "The bus to the campus was full, so ____.", "I had to wait for the next one",
     ["I got on it and found an empty seat", "it was easy to find a free seat", "nobody was on the bus that morning"],
     "Otobüs dolu olduğu için mantıklı sonuç bir sonrakini beklemektir."),
    ("B2", "Grammar", "If the turbine blades ____ longer, they would generate more electricity.", "were",
     ["are", "had", "will be"],
     "İkinci tip koşul: 'If + past (were), would + V1'."),
    ("B2", "Grammar", "The prototype ____ by a team of four students over six months.", "was designed",
     ["designed", "was designing", "has designing"],
     "Prototip tasarlandı (edilgen, geçmiş): 'was designed'."),
    ("B2", "Vocabulary", "Wind energy is a ____ source of power because the wind never runs out.", "renewable",
     ["finite", "costly", "polluting"],
     "Tükenmeyen kaynak yenilenebilirdir: 'renewable'."),
    ("B2", "Vocabulary", "The engineers ____ a solution to reduce the noise from the turbines.", "came up with",
     ["came across as", "came down with", "came in for"],
     "Çözüm bulmak: 'come up with'."),
    ("C2", "Grammar", "Not only ____ the new material lighter, but it is also more resistant to corrosion.", "is",
     ["does", "has", "it is"],
     "'Not only' devrik yapı: 'Not only is the new material lighter'."),
    ("C2", "Vocabulary", "The results of the stress test were ____, so the team had to repeat it.", "inconclusive",
     ["definitive", "decisive", "conclusive"],
     "Testin tekrarlanması sonuçların belirsiz olduğunu gösterir: 'inconclusive'."),
    ("C2", "Restatement", "The turbine's efficiency hinges on the precise angle of its blades.",
     "How efficient the turbine is depends on the exact angle of its blades.",
     ["The angle of the blades has nothing to do with the turbine's efficiency.", "The blades of the turbine are attached with special hinges.",
      "The turbine becomes less efficient when the blades are measured precisely."],
     "'hinge on' = -e bağlı olmak; verim kanat açısına bağlıdır."),
    ("C2", "Paragraph Completion",
     "Offshore wind farms can produce more electricity than those on land because winds at sea are stronger and steadier. ____. Engineers are therefore developing floating turbines that can be anchored in deeper water.",
     "However, fixed foundations are only practical in shallow coastal areas",
     ["Wind farms on land were first built in the 1980s", "Consequently, offshore wind farms are cheaper to build than any other",
      "Many people enjoy watching turbines turn on windy days"],
     "Sonraki cümle derin sulara yüzen türbin geliştirilmesini anlatıyor; neden sabit temellerin sığ suyla sınırlı olmasıdır."),
]
CLOZE = (
    "The İzmir Institute of Technology, also known as İYTE, was founded in 1992. Its campus is located in Gülbahçe, (1) ____ the "
    "town of Urla. The area is famous for its strong winds, (2) ____ make it ideal for research on wind energy. Most students at İYTE "
    "study engineering, architecture or science, and they often work (3) ____ projects with local industry. Since the campus is far "
    "from the city, many students live in dormitories or in Urla (4) ____.",
    [
        ("near", ["between", "among", "through"], "Urla'ya yakın: 'near'."),
        ("which", ["who", "what", "where"], "Rüzgârları niteleyen virgüllü sıfat cümlesi: 'which'."),
        ("on", ["at", "in", "for"], "Bir proje üzerinde çalışmak: 'work on projects'."),
        ("itself", ["himself", "themselves", "herself"], "Urla'nın kendisinde: 'in Urla itself'."),
    ],
)
READING = (
    "Turbines and Birds\n\nAs wind farms spread across hillsides and coastlines, concerns have grown about their impact on birds. "
    "Large birds of prey, which often glide along the same ridges where winds are strongest, appear to be particularly at risk of "
    "colliding with rotating blades. Studies at some sites have recorded significant numbers of deaths, prompting calls for stricter "
    "planning rules.\n\nTo put these figures in perspective, researchers point out that far more birds are killed each year by "
    "collisions with glass buildings, by domestic cats and by habitat loss linked to fossil fuel extraction. Nevertheless, because some "
    "affected species breed slowly, even a small number of additional deaths can threaten local populations.\n\nSeveral measures can "
    "reduce the risk. Careful site selection, avoiding major migration routes, is the most effective. Some operators now use cameras "
    "that detect approaching birds and automatically slow the turbines. In one trial, painting one of the three blades black made the "
    "rotor more visible to birds and substantially reduced collisions.",
    [
        ("Why are large birds of prey especially at risk?", "They glide along ridges where turbines are often placed.",
         ["They are attracted to the noise made by turbines.", "They usually fly at night when turbines are hard to see.",
          "They build their nests on the towers of wind turbines."],
         "Yırtıcı kuşlar rüzgârın en güçlü olduğu sırtlarda süzülür; türbinler de oraya kurulur."),
        ("Why does the author mention glass buildings and cats?", "to show that other causes kill many more birds",
         ["to suggest that turbines should be built near cities", "to prove that turbines cause no deaths at all", "to explain how birds learn to avoid danger"],
         "Rakamları bağlama oturtmak için: cam binalar ve kediler çok daha fazla kuş öldürüyor."),
        ("According to the passage, why can a small number of deaths still be serious?", "Some species reproduce slowly.",
         ["Turbines are being built very quickly.", "Most birds cannot see moving objects.", "Dead birds are rarely found by researchers."],
         "Bazı türler yavaş ürediği için az sayıda ek ölüm bile yerel nüfusu tehdit edebilir."),
        ("Which measure is described as the most effective?", "choosing locations away from migration routes",
         ["painting all the blades of turbines black", "slowing turbines down whenever it is windy", "using cameras to count the dead birds"],
         "En etkili önlem: büyük göç yollarından kaçınarak dikkatli yer seçimi."),
    ],
)
