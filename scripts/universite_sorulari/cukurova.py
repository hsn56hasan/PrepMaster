# Çukurova: Grammar & Vocabulary %30, Reading %35, Listening %15, Writing %20
UNI = "cukurova"
ITEMS = [
    ("A1", "Grammar", "The Balcalı campus ____ next to a big lake.", "is", ["are", "am", "be"],
     "Özne tekil: 'is'."),
    ("A1", "Grammar", "Farmers in Adana ____ cotton and oranges.", "grow", ["grows", "growing", "is grow"],
     "Özne 'farmers' çoğul: 'grow'."),
    ("A1", "Vocabulary", "In July it is very hot, so I always carry a bottle of ____.", "water", ["paper", "sand", "salt"],
     "Sıcakta su taşınır: 'water'."),
    ("A1", "Vocabulary", "Adana is famous for its delicious ____.", "kebab", ["snow", "chair", "window"],
     "Adana kebabıyla ünlüdür: 'kebab'."),
    ("A2", "Grammar", "Çukurova is one of the ____ agricultural regions in Türkiye.", "most important",
     ["more important", "importantest", "important"],
     "'one of the' + üstünlük derecesi: 'the most important'."),
    ("A2", "Grammar", "I ____ my homework when my friend called.", "was doing", ["am doing", "did", "have done"],
     "Geçmişte devam eden eylem kısa bir olayla kesildi: Past Continuous."),
    ("A2", "Dialogue", "A: Shall we sit outside in the garden?\nB: ____\nA: You're right. Let's find a table inside.",
     "It's a bit too hot out there, isn't it?",
     ["I'd like a glass of orange juice, please.", "The garden is very beautiful in spring.", "Yes, I've already finished my lunch."],
     "A 'haklısın, içeride masa bulalım' diyor; B dışarının çok sıcak olduğunu söylemiş olmalı."),
    ("A2", "Vocabulary", "The Seyhan River gives ____ to the fields, so farmers can grow crops in summer.", "water",
     ["noise", "money", "smoke"],
     "Nehir tarlalara su sağlar: 'water'."),
    ("B2", "Grammar", "Cotton ____ in the Çukurova region for centuries.", "has been grown",
     ["has grown", "is growing", "had being grown"],
     "'for centuries' şimdiye uzanır; edilgen Present Perfect: 'has been grown'."),
    ("B2", "Grammar", "The farmers wish they ____ more water during the dry summer last year.", "had had",
     ["have had", "had", "would have"],
     "Geçmişe dair dilek: 'wish + Past Perfect'."),
    ("B2", "Vocabulary", "Modern irrigation methods help farmers use water more ____.", "efficiently",
     ["wastefully", "carelessly", "rarely"],
     "Suyu daha verimli kullanmak: 'efficiently'."),
    ("B2", "Sentence Completion", "Since the dam was built, ____.", "the region has had a more reliable water supply",
     ["the river has had no water flowing in it at all", "farmers have stopped growing any crops", "it has never rained once in the region"],
     "Baraj yapıldığından beri bölgenin su kaynağı daha güvenilir hâle geldi."),
    ("C2", "Grammar", "Were it not for the dam, the plain ____ by floods every spring.", "would be hit",
     ["will be hit", "had been hit", "would hit"],
     "'Were it not for' = 'If it weren't for'; şimdiki duruma dair: 'would be hit' (edilgen)."),
    ("C2", "Vocabulary", "Excessive use of fertilisers can ____ groundwater supplies.", "contaminate",
     ["purify", "replenish", "filter"],
     "Aşırı gübre yer altı suyunu kirletebilir: 'contaminate'."),
    ("C2", "Restatement", "The drought did far less damage to the harvest than farmers had feared.",
     "The drought harmed the harvest much less than farmers had expected.",
     ["The drought destroyed the harvest just as the farmers had feared.", "Farmers were not worried about the drought at all.",
      "The harvest was damaged more than farmers had expected."],
     "Kuraklık hasada, çiftçilerin korktuğundan çok daha az zarar verdi."),
    ("C2", "Paragraph Completion",
     "Drip irrigation delivers water directly to the roots of plants through a network of pipes. ____. It can therefore reduce water consumption considerably compared with flooding the fields.",
     "As a result, very little water is lost to evaporation or runoff",
     ["Cotton was first grown in Anatolia thousands of years ago", "However, it uses far more water than traditional methods",
      "Many farmers prefer to harvest their crops by hand"],
     "'therefore' su tasarrufunu sonuç olarak veriyor; neden buharlaşma ve akışla az su kaybıdır."),
]
CLOZE = (
    "Çukurova University was founded in Adana in 1973. Its Balcalı campus is (1) ____ the largest in Türkiye and lies on the shore of "
    "a lake formed by the Seyhan Dam. Because the region is (2) ____ for agriculture, the university's Faculty of Agriculture plays an "
    "important role in research on crops such as cotton, citrus fruits and wheat. Summers in Adana are long and hot, (3) ____ many "
    "students prefer to study in air-conditioned libraries. In spring, (4) ____, the campus is green and pleasant.",
    [
        ("among", ["between", "within", "beside"], "En büyükler arasında: 'among the largest'."),
        ("famous", ["famously", "fame", "famed for"], "'be famous for' kalıbı."),
        ("so", ["because", "although", "unless"], "Sonuç bildirir: sıcak olduğu için kütüphanede çalışırlar."),
        ("however", ["therefore", "moreover", "for example"], "Yazla karşıtlık: 'In spring, however, ...'."),
    ],
)
READING = (
    "The Cost of a T-shirt\n\nCotton is one of the world's most widely used natural fibres, but growing it can require large amounts "
    "of water. Estimates vary greatly depending on the climate and farming methods, but the cotton in a single T-shirt may need "
    "thousands of litres of water to grow in some regions. In areas where irrigation draws on rivers and underground supplies, this "
    "demand can contribute to falling water tables and shrinking lakes.\n\nFarmers and researchers have developed several ways to reduce "
    "this footprint. Drip irrigation delivers water precisely where it is needed, while improved crop varieties can tolerate dry "
    "conditions better. In regions with sufficient rainfall, cotton can be grown with little or no irrigation at all.\n\nConsumers also "
    "have a role to play. Clothes that are worn for longer and recycled at the end of their life reduce the need for new cotton. Some "
    "analysts argue that the greatest environmental gains will come not from changing how cotton is grown but from changing how many "
    "clothes people buy.",
    [
        ("According to the passage, why do estimates of cotton's water use vary?", "They depend on climate and farming methods.",
         ["Scientists use very different measuring tools.", "Some T-shirts contain much more cotton than others.", "Cotton farmers rarely report their actual water use."],
         "Tahminler iklime ve tarım yöntemlerine göre büyük ölçüde değişir."),
        ("What can happen when cotton irrigation relies on rivers and underground water?", "Water tables may fall and lakes may shrink.",
         ["Rivers may flood the surrounding fields more often.", "Cotton plants may grow much faster than expected.", "Farmers may need fewer workers during the harvest."],
         "Su tablaları düşebilir ve göller küçülebilir."),
        ("Which method of reducing water use is NOT mentioned?", "growing cotton indoors in greenhouses",
         ["using drip irrigation systems", "planting drought-tolerant varieties", "growing cotton where it rains enough"],
         "Seralarda yetiştirmekten söz edilmiyor."),
        ("What do some analysts believe?", "Buying fewer clothes would help the environment most.",
         ["Cotton should be replaced by synthetic fibres.", "Farmers should stop using irrigation completely.", "Recycling clothes has no environmental benefit."],
         "En büyük kazanç, insanların ne kadar kıyafet aldığını değiştirmekten gelecek."),
    ],
)
