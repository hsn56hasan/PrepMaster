# İTÜ Proficiency: Restatement %15, Reading %35, Use of English & Cloze %20 -> restatement ağırlıklı
UNI = "itu"
ITEMS = [
    ("A1", "Grammar", "Our classes ____ on the Maslak campus every morning.", "start", ["starts", "starting", "is start"],
     "Özne 'our classes' çoğul ve geniş zaman kullanılıyor; fiil yalın hâlde kalır: 'start'."),
    ("A1", "Grammar", "There ____ a big library near the mechanical engineering building.", "is", ["are", "be", "am"],
     "'a big library' tekil olduğu için 'there is' kullanılır."),
    ("A1", "Vocabulary", "My robotics lesson is very ____; we build small robots and test them.", "interesting", ["hungry", "late", "cheap"],
     "Robot yapıp denemek bir dersi ilginç kılar: 'interesting'. Diğerleri derse anlamca uymaz."),
    ("A1", "Vocabulary", "The lecture ____ is on the second floor of the faculty building.", "hall", ["kitchen", "garden", "shower"],
     "Derslerin yapıldığı büyük salon 'lecture hall' olarak adlandırılır."),
    ("A2", "Grammar", "Last year, an İTÜ team ____ first prize in a solar car race.", "won", ["wins", "has win", "winning"],
     "'Last year' geçmişte bitmiş zamanı gösterir; Past Simple 'won' gerekir."),
    ("A2", "Vocabulary", "The naval architecture students tested their model ship in a large water ____.", "tank", ["glass", "bottle", "bag"],
     "Model gemiler büyük bir su havuzunda/tankında denenir: 'water tank'."),
    ("A2", "Sentence Completion", "The lab was closed on Monday, so ____.", "we did the experiment on Tuesday instead",
     ["we finished the experiment in the lab on Monday", "the lab is always open on Mondays", "we did not need any of the equipment"],
     "'so' sonuç bildirir: laboratuvar kapalı olduğu için deney salıya kaldı."),
    ("A2", "Restatement", "The new dormitory is closer to the campus than the old one.",
     "The old dormitory is farther from the campus than the new one.",
     ["The new dormitory is as far from the campus as the old one.", "The old dormitory is closer to the campus than the new one.",
      "Both dormitories are a long way outside the city centre."],
     "Yeni yurt kampüse daha yakınsa eski yurt daha uzaktır; aynı bilgi ters yönden söylenmiştir."),
    ("B2", "Restatement", "Unless the funding is renewed, the drone project will be suspended next term.",
     "The drone project will be suspended next term if the funding is not renewed.",
     ["The drone project will continue next term even without any new funding.", "The funding was renewed, so the drone project was suspended last term.",
      "If the funding is renewed, the drone project will be suspended next term."],
     "'Unless' = 'if ... not'. Destek yenilenmezse proje durdurulacak."),
    ("B2", "Restatement", "No sooner had the students submitted their design than the deadline was extended.",
     "The deadline was extended immediately after the students had submitted their design.",
     ["The students submitted their design long after the deadline had been extended.", "The deadline was extended so that the students could start their design.",
      "The students did not submit their design because the deadline had been extended."],
     "'No sooner ... than' = '... yapar yapmaz'. Tasarım teslim edilir edilmez süre uzatıldı."),
    ("B2", "Grammar", "The bridge model, ____ was designed by second-year civil engineering students, survived the load test.", "which", ["who", "whose", "what"],
     "Virgüllü (non-defining) sıfat cümlesinde nesneler için 'which' kullanılır."),
    ("B2", "Sentence Completion", "Although the prototype performed well in the laboratory, ____.", "it failed several tests in real traffic conditions",
     ["it was approved at once without any further testing", "the laboratory results were very encouraging indeed", "the engineers were pleased with how it performed"],
     "'Although' zıtlık ister: laboratuvarda iyiydi AMA gerçek trafikte başarısız oldu."),
    ("C2", "Restatement", "Had the simulation been run with more realistic data, the design flaw would have come to light much earlier.",
     "The design flaw was discovered late because the simulation did not use sufficiently realistic data.",
     ["The design flaw was found early thanks to the realistic data used in the simulation.", "The simulation was never run, so the design flaw remains hidden even today.",
      "Using realistic data in the simulation would have created a completely new design flaw."],
     "Devrik üçüncü tip koşul geçmişteki gerçeğin tersini anlatır: veri gerçekçi değildi, kusur geç fark edildi."),
    ("C2", "Restatement", "It is by no means certain that the new material will withstand the extreme temperatures of a deep-sea environment.",
     "Whether the new material can endure the extreme temperatures of the deep sea remains uncertain.",
     ["The new material has been proven to endure the extreme temperatures of a deep-sea environment.", "The new material is certain to fail in the extreme temperatures of a deep-sea environment.",
      "Deep-sea environments are no longer considered to have extreme temperatures at all."],
     "'by no means certain' = hiç de kesin değil; malzemenin dayanıp dayanmayacağı belirsiz."),
    ("C2", "Paragraph Completion",
     "Istanbul's position on an active fault line makes earthquake engineering a central concern for local researchers. ____. Consequently, many recent projects focus not on new construction but on reinforcing ageing residential buildings.",
     "Studies suggest that much of the city's existing housing was built before modern seismic codes",
     ["Istanbul is also famous for its historical architecture and its rich culinary traditions", "As a result, new buildings in the city are rarely affected by building regulations",
      "Earthquakes, however, have never caused any significant damage in the region"],
     "Sonraki cümle eski binaların güçlendirilmesine odaklanıldığını söylüyor; boşluğa bunun nedeni (eski yapı stoku) gelir."),
    ("C2", "Vocabulary", "The committee's report was criticised for ____ the risks of the tunnel project, presenting them as far smaller than they really were.",
     "downplaying", ["exaggerating", "dramatising", "itemising"],
     "Riskleri olduğundan küçük göstermek 'downplay' (önemsizleştirmek) demektir; 'exaggerate' tersidir."),
]
CLOZE = (
    "İTÜ is one of the oldest technical universities in the world; its history (1) ____ back to 1773. Today, most of its "
    "engineering programmes are on the Ayazağa campus in Maslak. Students who (2) ____ the English proficiency exam can start "
    "their departments directly; (3) ____, others spend a year in the preparatory school. Many graduates later work (4) ____ "
    "engineers in Türkiye and abroad.",
    [
        ("goes", ["go", "going", "gone"], "Özne 'its history' tekil, geniş zaman: 'goes back to' (… yılına uzanır)."),
        ("pass", ["lose", "forget", "miss"], "Sınavı geçenler doğrudan bölüme başlar: 'pass the exam'."),
        ("however", ["therefore", "for example", "similarly"], "Geçenler ile diğerleri karşılaştırılıyor; zıtlık: 'however'."),
        ("as", ["by", "on", "of"], "Bir meslekte çalışmak 'work as an engineer' kalıbıyla anlatılır."),
    ],
)
READING = (
    "Universities and the Innovation Economy\n\nFor much of the twentieth century, Turkish engineering faculties saw their "
    "mission mainly as training competent professionals. Research was carried out, but its results rarely left the laboratory. "
    "This began to change in the early 2000s, when technology development zones were established next to several campuses, "
    "including İTÜ's ARI Teknokent in Maslak. The idea was simple: if start-up companies worked within walking distance of "
    "researchers, ideas would move more easily from academic papers to marketable products.\n\nThe results have been mixed. "
    "Supporters point to hundreds of firms that have grown out of these zones, some of which now export software and defence "
    "technologies. Critics, however, argue that tax incentives rather than genuine collaboration attracted many companies, and "
    "that only a minority of firms actually employ university researchers. A recent study of one zone found that fewer than one "
    "in five companies had a joint project with the neighbouring faculty.\n\nThe challenge, then, is not physical proximity but "
    "institutional culture. Unless academic promotion rewards patents and partnerships as well as publications, researchers have "
    "little reason to spend time on commercial work.",
    [
        ("What is the main point of the passage?", "Placing companies near universities has not by itself guaranteed real collaboration.",
         ["Technology zones have completely failed to produce any successful firms.", "Turkish universities stopped training engineers after the early 2000s.",
          "Tax incentives are by far the most effective way to encourage academic research."],
         "Metin, yakınlığın tek başına iş birliği getirmediğini ve asıl sorunun kurum kültürü olduğunu savunuyor."),
        ("According to the critics, why did many companies move to technology zones?", "to benefit from tax advantages",
         ["to hire large numbers of researchers", "to be closer to their foreign customers", "to publish more academic papers"],
         "Eleştirmenler şirketleri asıl çekenin vergi teşvikleri olduğunu söylüyor."),
        ("The study mentioned in the second paragraph suggests that ____.", "most companies in the zone did not work with the nearby faculty",
         ["most companies had at least one joint project with the faculty", "the zone had fewer than five companies in total", "university researchers preferred to work abroad"],
         "Şirketlerin beşte birinden azının fakülteyle ortak projesi var; yani çoğunluğun yok."),
        ("According to the last paragraph, researchers would be more willing to work with companies if ____.",
         "promotion rewarded patents and partnerships",
         ["companies moved further away from campuses", "they were allowed to publish fewer papers", "technology zones offered more tax incentives"],
         "Son paragraf: akademik yükselme patent ve ortaklıkları da ödüllendirirse araştırmacılar ticari işe zaman ayırır."),
    ],
)
