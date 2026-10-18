# -*- coding: utf-8 -*-
"""
Expand data/writing_guides.json so that every CEFR level (A1, A2, B1, B2, C1, C2)
has multiple comprehensive writing guides with models, tips, structures, and band analysis.
"""

import json
from pathlib import Path

TARGET_FILE = Path("data/writing_guides.json")

with open(TARGET_FILE, "r", encoding="utf-8") as f:
    existing_guides = json.load(f)

existing_ids = {g["id"] for g in existing_guides}

NEW_GUIDES = [
    {
        "id": "a1-personal-intro",
        "title": "Personal Introduction & Student Profile",
        "description": "A1 seviyesindeki öğrenciler için temel kendini tanıtma, bölüm, ilgi alanları ve akademik hedefleri anlatan 80-100 kelimelik kısa paragraf rehberi.",
        "level": "A1",
        "structure": [
            {
                "section": "Greeting & Identity (Giriş & Kimlik)",
                "elements": [
                    "Adınızı, memleketinizi ve üniversite bölümünüzü belirtin.",
                    "Örnek: My name is Deniz and I am an undergraduate student in Computer Engineering at Ankara University."
                ]
            },
            {
                "section": "Background & Hobbies (Arka Plan ve Hobiler)",
                "elements": [
                    "Haftalık rutinlerinizi ve boş zaman aktivitelerinizi yazın.",
                    "Örnek: In my free time, I enjoy reading science fiction books and practicing coding."
                ]
            },
            {
                "section": "Academic Goals (Akademik Hedefler)",
                "elements": [
                    "İngilizce hazırlık okulunu neden bitirmek istediğinizi özetleyin.",
                    "Örnek: My main goal this year is to pass the English proficiency exam with high marks."
                ]
            }
        ],
        "key_transitions": [
            "My name is ...",
            "I study at ...",
            "In my free time, ...",
            "Furthermore, ...",
            "My goal is to ..."
        ],
        "sample_topic": "Introduce yourself, describe your major, and explain why learning English is important for your future.",
        "band_score_tip": "Basit Present Tense kalıplarını (am/is/are ve he/she/it -s takısı) hatasız kullanmaya özen gösterin.",
        "model_band_score": 88,
        "model_essay": "My name is Deniz and I am eighteen years old. I am currently a first-year student in the Department of Computer Engineering at Ankara University. I come from Izmir, but I live in an on-campus dormitory in Ankara now. In my free time, I like playing chess and developing simple software applications. I believe that English is very important because all modern programming languages and documentation are written in English. My primary objective this year is to successfully finish the preparatory English program and achieve academic fluency.",
        "annotated_strengths": [
            "Özne-yüklem uyumu (Subject-Verb agreement) ve Present Simple doğru kullanılmış.",
            "Giriş, arka plan ve gelecek hedefleri dengeli aktarılmış.",
            "Gereksiz karmaşıklıktan kaçınılarak net ve temiz cümleler kurulmuş."
        ],
        "common_pitfalls": [
            "Fiilleri yalın halde bırakıp özne zamirlerini unutmak.",
            "Türkçedeki 'benim adım ... vardır' gibi doğrudan çeviri hataları yapmak."
        ]
    },
    {
        "id": "a1-simple-email",
        "title": "Formal Inquiry Email to Academic Advisor",
        "description": "A1 seviyesindeki öğrencilerin ders kaydı, danışman görüşmesi veya devamsızlık bildirimi için üniversite hocalarına yazacağı kısa resmi e-posta formatı.",
        "level": "A1",
        "structure": [
            {
                "section": "Salutation (Hitap)",
                "elements": [
                    "Saygılı ve resmi hitap: Dear Professor [Soyadı] veya Dear Dr. [Soyadı]"
                ]
            },
            {
                "section": "Purpose of Email (Yazma Amacı)",
                "elements": [
                    "E-postayı neden yazdığınızı ilk cümlede açıkça belirtin.",
                    "Örnek: I am writing to ask about the appointment hours for our course syllabus."
                ]
            },
            {
                "section": "Specific Question / Request (Soru veya Talep)",
                "elements": [
                    "Talep ettiğiniz bilgi veya randevu tarihini netleştirin."
                ]
            },
            {
                "section": "Polite Sign-off (Kapanış)",
                "elements": [
                    "Teşekkür ve isim: Thank you for your time. Sincerely, [Adınız Soyadınız] [Öğrenci Numaranız]"
                ]
            }
        ],
        "key_transitions": [
            "Dear Professor ...",
            "I am writing to ...",
            "Could you please ...",
            "Thank you for your assistance.",
            "Best regards, ..."
        ],
        "sample_topic": "Write an email to your English instructor asking for clarification on next week's vocabulary quiz date.",
        "band_score_tip": "Konu başlığını (Subject line) boş bırakmayın ve gayriresmi ifadelerden ('Hey', 'Bye') kaçının.",
        "model_band_score": 90,
        "model_essay": "Subject: Inquiry Regarding Vocabulary Quiz Date - Deniz Yilmaz (ID: 20240182)\n\nDear Professor Demir,\n\nI hope this email finds you well. I am a student in your Monday morning English preparatory class (Section 3). I am writing to ask for clarification regarding the date of our second vocabulary quiz. The course syllabus states Wednesday, but the portal shows Friday. Could you please confirm the correct day? Thank you very much for your time and assistance.\n\nSincerely,\nDeniz Yilmaz\nStudent ID: 20240182",
        "annotated_strengths": [
            "Net ve anlaşılır konu satırı (Subject line) kullanılmış.",
            "Kibar ve akademik bir açılış ve kapanış kalıbı tercih edilmiş.",
            "Talep edilen bilgi doğrudan ve saygılı bir dille ifade edilmiş."
        ],
        "common_pitfalls": [
            "Öğrenci numarası veya sınıf şubesini belirtmemek.",
            "Büyük/küçük harf kurallarına dikkat etmemek."
        ]
    },
    {
        "id": "a2-narrative-paragraph",
        "title": "Short Narrative & Personal Experience",
        "description": "A2 seviyesinde Past Simple ve Past Continuous kullanarak geçmişte yaşanmış önemli bir okul deneyimini kronolojik sırayla anlatan anlatı paragrafı.",
        "level": "A2",
        "structure": [
            {
                "section": "Orientation (Zaman & Mekan Girişi)",
                "elements": [
                    "Olayın ne zaman, nerede ve kimlerle başladığını anlatın."
                ]
            },
            {
                "section": "Chronological Sequence (Olaylar Dizisi)",
                "elements": [
                    "First, Then, After that, Suddenly gibi zaman bağlaçlarıyla gelişmeleri sıralayın."
                ]
            },
            {
                "section": "Reflection (Ders & Sonuç)",
                "elements": [
                    "Bu deneyimden ne öğrendiğinizi özetleyin."
                ]
            }
        ],
        "key_transitions": [
            "Last semester, ...",
            "At first, ...",
            "Suddenly, ...",
            "After a few hours, ...",
            "In the end, ..."
        ],
        "sample_topic": "Describe your first day on the university campus and how you overcame feeling lost.",
        "band_score_tip": "Geçmiş zaman fiil çekimlerine (regular -ed ve irregular fiiller) dikkat edin.",
        "model_band_score": 87,
        "model_essay": "My first day at Hacettepe University was both exciting and challenging. Early in the morning, I arrived at the massive Beytepe campus to register for my preparatory English classes. At first, I felt completely overwhelmed because the campus was enormous and crowded with thousands of new students. When I was looking for the Foreign Languages building, I accidentally entered the engineering faculty. Fortunately, a senior medical student noticed my confusion and kindly guided me to the correct office. By the afternoon, I met several friendly classmates and registered for all my lectures without further issues. This experience taught me that university students are always willing to help newcomers.",
        "annotated_strengths": [
            "Zaman bağlaçları (At first, When, Fortunately, By the afternoon) akıcı kullanılmış.",
            "Past Continuous (When I was looking...) ve Past Simple bir arada doğru uygulanmış."
        ],
        "common_pitfalls": [
            "Zamanlar arası gereksiz geçişler yapmak (Past'tan Present'a kaymak).",
            "Olay akışını bağlaçsız art arda yazmak."
        ]
    },
    {
        "id": "b1-descriptive-informative",
        "title": "Informative & Expository Essay",
        "description": "B1 seviyesinde belirli bir bilimsel veya toplumsal konuyu tarafsız, bilgilendirici ve organize bir 300 kelimelik essay formatında sunma rehberi.",
        "level": "B1",
        "structure": [
            {
                "section": "Introduction (Giriş Paragrafı)",
                "elements": [
                    "Genel bağlam, konunun tanımı ve iki ana alt başlığı belirten Thesis Statement."
                ]
            },
            {
                "section": "Body Paragraph 1 (İlk Bilgilendirici Boyut)",
                "elements": [
                    "Birinci faktör ve somut bir örnek."
                ]
            },
            {
                "section": "Body Paragraph 2 (İkinci Bilgilendirici Boyut)",
                "elements": [
                    "İkinci faktör ve pratik etkileri."
                ]
            },
            {
                "section": "Conclusion (Sonuç Paragrafı)",
                "elements": [
                    "Ana noktaların özeti ve geleceğe yönelik genel değerlendirme."
                ]
            }
        ],
        "key_transitions": [
            "In recent decades, ...",
            "The primary factor is ...",
            "Furthermore, ...",
            "In contrast, ...",
            "In conclusion, ..."
        ],
        "sample_topic": "Explain the major benefits of integrating renewable solar energy into modern urban buildings.",
        "band_score_tip": "Kişisel hisler yerine nesnel gerçeklere ve 'This leads to...', 'As a result...' gibi neden-sonuç ifadelerine ağırlık verin.",
        "model_band_score": 88,
        "model_essay": "In recent years, the transition toward renewable energy has become a central priority for sustainable urban architecture. Among alternative power sources, solar photovoltaics offer two significant advantages for modern city dwellers: substantial reduction in municipal greenhouse gas emissions and long-term financial savings on household electricity bills.\n\nFirst and foremost, utilizing rooftop solar panels significantly diminishes an urban area's reliance on fossil-fuel power stations. When residential complexes generate their own clean solar energy, the consumption of coal and natural gas decreases proportionally. As a consequence, air pollutants such as sulfur dioxide and particulate matter decline, creating healthier metropolitan environments for residents. For example, recent municipal pilot projects in Izmir demonstrated a twenty percent drop in neighborhood power grid strain during peak summer cooling hours.\n\nIn addition to environmental benefits, solar infrastructure provides considerable economic relief for families and municipal budgets over time. Although the initial installation costs of photovoltaic panels require capital investment, solar technology typically pays for itself within five to seven years. After this payback horizon, the electricity produced is practically free, shielding consumers from volatile global fuel prices. Moreover, excess power generated on sunny days can be sold back to the local utility grid.\n\nIn conclusion, integrating solar energy into metropolitan building design addresses both atmospheric contamination and escalating household energy expenditures. Therefore, local municipalities should continue encouraging rooftop solar adoption through tax credits and educational outreach.",
        "annotated_strengths": [
            "Güçlü ve açık iki odak noktası içeren Thesis Statement.",
            "Body paragraflarında net Topic Sentences ve somut destekleyici detaylar.",
            "Akademik geçiş bağlaçları (First and foremost, As a consequence, Moreover) dengeli."
        ],
        "common_pitfalls": [
            "Konudan saparak rüzgar veya nükleer gibi ilgisiz enerjilere fazla yer vermek.",
            "Örnek vermeden soyut iddialarda bulunmak."
        ]
    },
    {
        "id": "b2-cause-effect",
        "title": "Cause and Effect Academic Essay",
        "description": "B2 seviyesinde karmaşık bir çevresel veya sosyal meselenin kök nedenlerini ve ortaya çıkardığı çok yönlü sonuçları analiz eden 350 kelimelik akademik kompozisyon.",
        "level": "B2",
        "structure": [
            {
                "section": "Introduction (Giriş Paragrafı)",
                "elements": [
                    "Problem bağlamı, tarihsel arka plan ve Neden-Sonuç odaklı Thesis Statement."
                ]
            },
            {
                "section": "Body Paragraph 1: Root Causes (Kök Nedenler)",
                "elements": [
                    "Sorunu doğuran 2 temel etkenin derinlemesine analizi."
                ]
            },
            {
                "section": "Body Paragraph 2: Systemic Effects (Sistemik Sonuçlar)",
                "elements": [
                    "Bireysel, ekonomik ve ekolojik sonuçların irdelenmesi."
                ]
            },
            {
                "section": "Conclusion (Sonuç ve Çözüm Önerisi)",
                "elements": [
                    "Neden-sonuç zincirinin sentezi ve stratejik politika önerisi."
                ]
            }
        ],
        "key_transitions": [
            "One primary driver of ... is ...",
            "Consequently, ...",
            "This phenomenon stems from ...",
            "As an inevitable outcome, ...",
            "To mitigate these ramifications, ..."
        ],
        "sample_topic": "Analyze the primary causes of brain drain (beyin göçü) among young professionals and evaluate its long-term impact on developing economies.",
        "band_score_tip": "Neden ile sonucu birbirine karıştırmayın; 'stem from', 'result in', 'precipitate' gibi zengin fiil yapıları kullanın.",
        "model_band_score": 92,
        "model_essay": "The emigration of highly educated human capital, colloquially termed 'brain drain,' represents one of the most pressing structural dilemmas facing developing nations today. This accelerating outflow of talented engineers, physicians, and academics is primarily driven by disparities in research infrastructure and limited socioeconomic mobility, ultimately precipitating severe domestic labor shortages and stagnating long-term technological innovation.\n\nTo begin with, two fundamental catalysts fuel the migration of skilled professionals toward Western economies. Chief among these is the stark disparity in scientific funding and workplace meritocracy. In many developing regions, young researchers encounter antiquated laboratory facilities, bureaucratic inertia, and opaque hiring practices that stymie creative intellectual pursuits. When global institutions in North America or Western Europe offer state-of-the-art computational equipment alongside competitive research stipends, talented scholars naturally seek environments where their potential can be fully realized. Furthermore, persistent macroeconomic volatility and currency devaluation erode purchasing power, rendering international employment irresistible from a personal financial perspective.\n\nThe societal repercussions of this persistent exodus are profoundly debilitating. First, the departure of medical professionals and software architects severely undermines public infrastructure. Developing nations expend considerable national tax revenues subsidizing university tuition only to see destination countries reap the economic fruits of that training without incurring education costs. Consequently, domestic hospitals suffer from critical specialist deficits, and local industrial firms struggle to modernize legacy manufacturing pipelines. Over decades, this dynamic widens the technological gulf separating developed and emerging economies.\n\nIn conclusion, brain drain is an understandable reaction to domestic institutional bottlenecks and economic instability. To reverse this destabilizing trend, developing governments must cultivate transparent academic meritocracies, incentivize private-sector research development, and offer returnee grants so that national talent can flourish at home.",
        "annotated_strengths": [
            "Zengin akademik kelime dağarcığı (colloquially termed, debilitating, stark disparity, stymie).",
            "Nedenler ve sonuçlar arasındaki bağ mantıksal olarak kusursuz kurgulanmış.",
            "Sonuç paragrafında sadece özet yapılmamış, ileriye dönük politika önerisi eklenmiş."
        ],
        "common_pitfalls": [
            "Sadece duygusal şikayetlerde bulunup analitik nedensellik kuramamak.",
            "Tek bir nedene takılıp çok boyutlu analizi kaçırmak."
        ]
    },
    {
        "id": "c1-discursive-analysis",
        "title": "Academic Discursive & Nuanced Synthesis",
        "description": "C1 seviyesinde Boğaziçi BUEPT ve Bilkent COPE sınavlarına yönelik, karşıt argümanları çürütüp dengeli senteze ulaştıran 400 kelimelik üst düzey tartışma kompozisyonu.",
        "level": "C1",
        "structure": [
            {
                "section": "Sophisticated Introduction (Akademik Giriş)",
                "elements": [
                    "Felsefi/toplumsal paradoks, karşıt kampların özeti ve incelikli (nuanced) Thesis."
                ]
            },
            {
                "section": "Argument 1 & Refutation (Savunulan Argüman ve Karşı Görüşün Çürütülmesi)",
                "elements": [
                    "İlk tezin kanıtları ve olası itirazların çürütülmesi (Concession & Refutation)."
                ]
            },
            {
                "section": "Argument 2 & Synthesis (Derinlemesine Sentez)",
                "elements": [
                    "İkinci boyutun analizi ve iki kutup arasındaki orta yolun ortaya konması."
                ]
            },
            {
                "section": "Visionary Conclusion (Vizyoner Sonuç)",
                "elements": [
                    "Geniş perspektifli çıkarım ve kavramsal sentez."
                ]
            }
        ],
        "key_transitions": [
            "Proponents contend that ...",
            "Notwithstanding these claims, ...",
            "This dichotomy obscures a deeper reality, namely that ...",
            "Upon closer scrutiny, ...",
            "A balanced paradigm demands that ..."
        ],
        "sample_topic": "Should artificial intelligence systems be granted autonomous copyright over algorithmic creations? Critically evaluate both legal and philosophical perspectives.",
        "band_score_tip": "Basit 'I think' yerine 'Scholars contend', 'It is tenable to argue that' gibi nesnel akademik söylem kullanın.",
        "model_band_score": 95,
        "model_essay": "The rapid ascendancy of generative artificial intelligence has destabilized conventional epistemological boundaries separating synthetic computation from human creative agency. As neural networks autonomously generate award-winning literature, photorealistic digital artwork, and patentable pharmacological molecules, legal theorists find themselves deeply divided over whether algorithmic architectures should be accorded intellectual property protections. While technological determinists argue that recognizing algorithmic copyright incentivizes technological innovation, a more rigorous philosophical inquiry reveals that divorcing authorship from conscious intentionality undermines the foundational premise of intellectual property law.\n\nAdvocates for autonomous synthetic copyright predominantly anchor their reasoning in utilitarian economic models. They assert that developing advanced machine learning models demands astronomical investments in computational hardware, energy, and proprietary data curations. Granting corporate entities copyright ownership over the unassisted outputs of these neural models allegedly safeguards venture capital inflows and accelerates automation across the arts and sciences. Without legal exclusivity, corporate sponsors might restrict access to foundational generative algorithms, thereby constraining technological proliferation.\n\nHowever, this utilitarian defense conflates computational generation with conscious intentionality. Human artistic expression is inextricably bound to subjective lived experience, existential suffering, and moral accountability—dimensions fundamentally inaccessible to stochastic token predictors. An algorithm does not possess aesthetic intent; it merely executes probabilistic tensor calculations over human-engineered cultural corpora. Bestowing legal personhood or copyright rights upon mathematical functions would not reward original genius, but rather facilitate corporate monopolization over public cultural heritage through mass automated content generation.\n\nIn conclusion, the temptation to anthropomorphize generative algorithms must be resisted by jurists and legislators alike. Artificial intelligence should be codified as a sophisticated instrument of human ingenuity rather than an autonomous creative subject. A balanced regulatory framework should attribute intellectual ownership to human prompts and system designers who exercise authentic editorial curation, thereby preserving the sacred link between consciousness and artistic creation.",
        "annotated_strengths": [
            "Olağanüstü kelime dağarcığı ve dil zarafeti (epistemological boundaries, stochastic token predictors, anthropomorphize).",
            "Hukuki ve felsefi argümanlar çok katmanlı olarak inşa edilmiş.",
            "Ezbere şablonlardan tamamen uzak, özgün ve kusursuz akademik yapı."
        ],
        "common_pitfalls": [
            "Konuyu sadece 'AI iyi midir kötü müdür' seviyesine indirgemek.",
            "Kavramların (telif, özne, bilinç) tanımını yapmadan varsayımlarda bulunmak."
        ]
    },
    {
        "id": "c2-epistemic-critique",
        "title": "Epistemological Critique & Scholarly Evaluation",
        "description": "C2 Ustalık seviyesinde doktora ve üst düzey yeterlik standartlarında, bilim felsefesi ve metodolojik temelleri sorgulayan akademik inceleme makalesi.",
        "level": "C2",
        "structure": [
            {
                "section": "Philosophical Exordium (Felsefi Giriş)",
                "elements": [
                    "Epistemik krizin tespiti, ontolojik varsayımlar ve kapsamlı tez bildirisi."
                ]
            },
            {
                "section": "Critical Deconstruction of Orthodoxies (Ortodoks Görüşün Yapısökümü)",
                "elements": [
                    "Yaygın pozitivist/indirgemeci yaklaşımın zayıf yönlerinin felsefi analizi."
                ]
            },
            {
                "section": "Dialectical Counter-Reconstruction (Diyalektik Karşı İnşa)",
                "elements": [
                    "Fenomenolojik veya bütüncül alternatif çerçevenin sunulması."
                ]
            },
            {
                "section": "Epistemic Synthesis & Paradigm Horizon (Epistemik Sentez)",
                "elements": [
                    "Gelecekteki araştırma paradigmalarına yön veren kapsamlı vargı."
                ]
            }
        ],
        "key_transitions": [
            "At the heart of this epistemic impasse lies ...",
            "This reductionist postulate collapses when ...",
            "Far from being mutually exclusive, ...",
            "Consequently, an integrative epistemology must ...",
            "In the final analysis, ..."
        ],
        "sample_topic": "Critique the limitations of quantitative reductionism in contemporary behavioral economics and argue for an interdisciplinary hermeneutic synthesis.",
        "band_score_tip": "C2 seviyesinde dil sadece gramer değil, düşüncenin incelikli mimarisidir. Karmaşık bağlaçlar ve devrik cümleler ölçülü ve organik kullanılmalıdır.",
        "model_band_score": 98,
        "model_essay": "For the greater part of the twentieth century, neoclassical economics operated under the dogmatic presupposition that human decision-making could be exhausted through mathematical formalisms and axiomatic utility maximization. This mechanistic orthodoxy, grounded in the Cartesian ideal of quantitative reductionism, conceptualized individuals as hyper-rational, self-interested automatons. While such abstractions facilitated parsimonious econometric modeling, they simultaneously instituted a profound epistemological blindness regarding the qualitative, socially embedded nature of human choice.\n\nThe empirical anomalies unmasked by behavioral psychology have decisively shattered this narrow paradigm. Human agents do not compute stochastic probabilities in epistemic isolation; rather, decisions are fundamentally mediated by sociocultural narratives, unconscious heuristics, and affective intersubjectivity. When econometricians attempt to force volatile existential commitments into linear mathematical functions, the resulting models exhibit acute diagnostic fragility. The recurring failure of institutional finance to anticipate catastrophic systemic shocks is an indictment not merely of statistical sampling, but of an ontological refusal to accommodate the irrational nuances of collective psychology.\n\nTo transcend this reductionist impasse, contemporary scholarship must inaugurate an authentic hermeneutic turn. Economics cannot remain hermetically sealed within algorithmic abstractions while disdaining the qualitative insights of sociology, evolutionary anthropology, and cognitive neuroscience. An integrative paradigm must treat human agents not as passive calculating instruments, but as meaning-making entities whose market transactions reflect cultural values and ethical constraints.\n\nIn the final analysis, true scientific rigor does not reside in the dogmatic quantification of reality, but in the humility to align analytical methodologies with the multifaceted complexity of the phenomena under investigation. Only by synthesizing quantitative empirical metrics with rich hermeneutic qualitative inquiry can the human sciences formulate a truly comprehensive framework for social and economic flourishing.",
        "annotated_strengths": [
            "Felsefi derinlik, zengin akademik retorik ve kusursuz terminoloji kullanımı.",
            "İktisat ve felsefe metinlerindeki yüksek standartlı dilsel ahenk.",
            "C2 seviyesini eksiksiz temsil eden kusursuz syntaktik kontrol."
        ],
        "common_pitfalls": [
            "Kelime hazneliğini göstermek uğruna anlamsız jargon yığını oluşturmak.",
            "Tezin mantıksal omurgasını kaybetmek."
        ]
    }
]

added_count = 0
for g in NEW_GUIDES:
    if g["id"] not in existing_ids:
        existing_guides.append(g)
        added_count += 1

with open(TARGET_FILE, "w", encoding="utf-8") as f:
    json.dump(existing_guides, f, ensure_ascii=False, indent=2)

print(f"Added {added_count} new writing guides. Total writing guides: {len(existing_guides)}")
from collections import Counter
print("Writing guides by level:", dict(Counter(g["level"] for g in existing_guides)))
