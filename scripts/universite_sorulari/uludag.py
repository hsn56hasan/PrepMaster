# Bursa Uludağ: Use of English %30, Grammar %20, Vocabulary %20, Reading %30
UNI = "uludag"
ITEMS = [
    ("A1", "Grammar", "There ____ a lot of snow on the mountain in winter.", "is", ["are", "be", "am"],
     "'snow' sayılamaz: 'there is'."),
    ("A1", "Grammar", "We ____ skiing on Uludağ every January.", "go", ["goes", "going", "gone"],
     "Özne 'we', alışkanlık: 'go'."),
    ("A1", "Vocabulary", "Bursa is famous for its green ____ and parks.", "trees", ["cars", "phones", "shoes"],
     "'Yeşil Bursa' ağaçları ve parklarıyla bilinir: 'trees'."),
    ("A1", "Vocabulary", "I wear a warm ____ because it is cold today.", "coat", ["sandal", "swimsuit", "T-shirt"],
     "Soğukta kalın mont giyilir: 'coat'."),
    ("A2", "Grammar", "The Görükle campus is ____ from the city centre, so I take the metro.", "far", ["near", "close", "next"],
     "Metroya binmenin nedeni uzaklıktır: 'far from'."),
    ("A2", "Grammar", "I have lived in Bursa ____ three years.", "for", ["since", "ago", "during"],
     "Süre bildirirken 'for': 'for three years'."),
    ("A2", "Vocabulary", "Bursa was once an important centre of the ____ trade.", "silk", ["oil", "coal", "gold"],
     "Bursa tarihte ipek ticaretinin merkezlerindendi: 'silk'."),
    ("A2", "Vocabulary", "We ____ the cable car to the top of the mountain.", "took", ["made", "did", "drove"],
     "Teleferiğe binmek: 'take the cable car'."),
    ("B2", "Grammar", "The ski season ____ shorter in recent years because of warmer winters.", "has become",
     ["became", "becomes", "is becoming to"],
     "'in recent years' şimdiye uzanır: Present Perfect 'has become'."),
    ("B2", "Grammar", "Silk ____ in Bursa for more than five hundred years.", "has been produced",
     ["has produced", "is being producing", "produced"],
     "İpek üretildi (edilgen) ve süre şimdiye uzanıyor: 'has been produced'."),
    ("B2", "Vocabulary", "Snow-making machines are used to ____ for the lack of natural snow.", "compensate",
     ["complain", "compete", "comply"],
     "Bir eksikliği telafi etmek: 'compensate for'."),
    ("B2", "Vocabulary", "The old silk market, Koza Han, ____ thousands of visitors every year.", "attracts",
     ["avoids", "rejects", "loses"],
     "Tarihi han her yıl binlerce ziyaretçi çeker: 'attracts'."),
    ("C2", "Grammar", "Seldom ____ such heavy snowfall in early November.", "has the region seen",
     ["the region has seen", "the region saw", "saw the region"],
     "'Seldom' cümle başında devrik yapı ister: 'has the region seen'."),
    ("C2", "Vocabulary", "The decline in snowfall poses a serious ____ to the local tourism industry.", "threat",
     ["benefit", "relief", "reward"],
     "Kar azalması turizme ciddi bir tehdit oluşturur: 'pose a threat'."),
    ("C2", "Vocabulary", "Traditional silk weaving is a ____ craft, practised today by only a handful of artisans.", "dwindling",
     ["flourishing", "booming", "thriving"],
     "Yalnızca birkaç ustanın sürdürdüğü zanaat giderek azalmaktadır: 'dwindling'."),
    ("C2", "Restatement", "Unless winters become colder again, the ski resort may have to rethink its entire business model.",
     "If winters stay warm, the ski resort may need to change the way it does business.",
     ["The ski resort will close soon because winters in the region are becoming much colder.", "Warmer winters will help the ski resort attract more skiers.",
      "The ski resort has already changed its business model completely."],
     "'Unless' = 'if not': kışlar yeniden soğumazsa tesis iş modelini değiştirmek zorunda kalabilir."),
]
CLOZE = (
    "Bursa Uludağ University was founded in 1975 and takes its name from the mountain (1) ____ rises above the city. Its main campus "
    "is in Görükle, about twenty kilometres from the city centre, and students can reach it (2) ____ metro or bus. Bursa was the first "
    "capital of the Ottoman Empire, so the city is full of historic mosques, baths and markets. In winter, many students go to the "
    "mountain (3) ____ skiing, and in summer they enjoy (4) ____ in its forests.",
    [
        ("that", ["who", "where", "whose"], "Dağı niteleyen sıfat cümlesi: 'the mountain that rises'."),
        ("by", ["on", "with", "in"], "Ulaşım aracı: 'by metro or bus'."),
        ("for", ["to", "at", "on"], "Bir etkinlik amacıyla gitmek: 'go to the mountain for skiing'."),
        ("walking", ["walk", "to walking", "walked"], "'enjoy' fiilinden sonra -ing: 'enjoy walking'."),
    ],
)
READING = (
    "When the Snow Stops Falling\n\nSki resorts around the world are confronting an uncomfortable reality: winters are becoming "
    "warmer and snowfall less reliable. Resorts at lower altitudes are particularly affected, as rising temperatures cause more "
    "precipitation to fall as rain rather than snow. Some have already closed, and many others depend increasingly on artificial snow.\n\n"
    "Snow-making, however, is an imperfect solution. It requires large amounts of water and energy, and it works only when "
    "temperatures are below freezing. As warm spells become more frequent, the window of time in which machines can operate shrinks. "
    "The cost of producing snow is eventually passed on to skiers through higher ticket prices.\n\nA growing number of mountain resorts "
    "are therefore trying to reduce their dependence on winter sports altogether. They are investing in hiking trails, mountain biking, "
    "conferences and wellness tourism in an effort to attract visitors throughout the year. Such diversification is not easy, but it "
    "may be the only way for these communities to secure their economic future.",
    [
        ("Why are low-altitude resorts particularly affected?", "More precipitation falls as rain instead of snow.",
         ["They receive too much snow during the winter.", "They are too far from major cities for tourists.", "They cannot afford to buy snow-making machines."],
         "Sıcaklık arttıkça yağış kar yerine yağmur olarak düşüyor."),
        ("According to the passage, which is a limitation of artificial snow?", "It can only be made when it is below freezing.",
         ["It melts faster than natural snow on the slopes.", "It is dangerous for skiers to use it at all.", "It needs no water but uses a lot of energy."],
         "Yapay kar yalnızca sıcaklık donma noktasının altındayken üretilebilir."),
        ("Who eventually pays the cost of making snow?", "skiers, through more expensive tickets",
         ["local governments, through higher taxes", "hotel owners, through lower profits", "environmental groups, through donations"],
         "Kar üretiminin maliyeti bilet fiyatlarıyla kayakçılara yansıtılır."),
        ("What is the main purpose of the resorts' new investments?", "to attract visitors all year round",
         ["to build more ski slopes at higher altitudes", "to produce artificial snow more cheaply", "to stop tourists from visiting in winter"],
         "Yürüyüş, bisiklet, kongre gibi yatırımlarla yıl boyu ziyaretçi çekmek amaçlanıyor."),
    ],
)
