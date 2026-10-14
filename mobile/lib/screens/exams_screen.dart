import 'package:flutter/material.dart';
import '../models/university.dart';
import '../models/question.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'exam_runner_screen.dart';
import 'listening_screen.dart';

class ExamsScreen extends StatelessWidget {
  final University currentUniversity;
  final String currentLevel;

  const ExamsScreen({
    super.key,
    required this.currentUniversity,
    required this.currentLevel,
  });

  void _launchMockExam(BuildContext context) async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Resmi muafiyet deneme sınavı hazırlanıyor...'), duration: Duration(seconds: 1)),
    );
    final mockData = await ApiService().getMockExam(currentUniversity.id);
    final List<Question> questions = (mockData['parsed_questions'] as List<dynamic>?)?.cast<Question>() ?? [];
    if (!context.mounted) return;
    if (questions.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Soru havuzu yüklenemedi.')),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ExamRunnerScreen(
          questions: questions,
          university: currentUniversity,
          level: currentLevel,
        ),
      ),
    );
  }

  void _launchExam(BuildContext context, {String? category, String? level}) async {
    final questions = await ApiService().getQuestions(
      universityId: currentUniversity.id,
      level: level ?? currentLevel,
      category: category,
    );

    if (questions.isEmpty) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Bu filtreye uygun soru bulunamadı.')),
        );
      }
      return;
    }

    if (context.mounted) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ExamRunnerScreen(
            questions: questions,
            university: currentUniversity,
            level: level ?? currentLevel,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Okul Denemeleri & Modüller'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Header info
          Text(
            '${currentUniversity.name} Formatı',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.textMain),
          ),
          const SizedBox(height: 4),
          const Text(
            'Üniversitenizin gerçek sınav süresi ve soru tiplerine göre hazırlanmış testlerle pratik yapın.',
            style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 20),

          // 1. Full Simulation
          _examCard(
            context: context,
            badge: 'TAM DENEME',
            badgeBg: AppTheme.brandBlue,
            levelText: 'Tüm Kurlar',
            title: 'Resmi Muafiyet / Kur Geçme Denemesi',
            desc: 'Restatement, Cloze Test, Reading ve Grammar bölümlerini içeren kapsamlı deneme sınavı.',
            isPrimary: true,
            onTap: () => _launchMockExam(context),
          ),
          const SizedBox(height: 14),

          // 2. Restatement
          _examCard(
            context: context,
            badge: 'ÖZEL MODÜL',
            badgeBg: Colors.indigo,
            levelText: 'B2 - C2',
            title: 'Restatement (En Yakın Anlam) Atölyesi',
            desc: 'İTÜ ve Boğaziçi sınavlarının en kritik bölümü olan cümle paraphrase soruları.',
            onTap: () => _launchExam(context, category: 'Restatement'),
          ),
          const SizedBox(height: 14),

          // 3. Reading
          _examCard(
            context: context,
            badge: 'AKADEMİK OKUMA',
            badgeBg: AppTheme.accentAmber,
            levelText: 'B1 - C2',
            title: 'Akademik Reading & Çıkarım Testi',
            desc: 'Makaleler üzerinden ana fikir, detay, yazar tutumu ve kelime anlamı soruları.',
            onTap: () => _launchExam(context, category: 'Reading'),
          ),
          const SizedBox(height: 14),

          // 4. Grammar & Cloze
          _examCard(
            context: context,
            badge: 'USE OF ENGLISH',
            badgeBg: AppTheme.accentEmerald,
            levelText: 'A1 - C1',
            title: 'Grammar & Cloze Test Serisi',
            desc: 'Zamanlar, bağlaçlar, devrik yapılar ve metin içi boşluk doldurma.',
            onTap: () => _launchExam(context, category: 'Grammar'),
          ),
          const SizedBox(height: 14),

          // 5. Listening & Note-Taking
          _examCard(
            context: context,
            badge: '🎧 SESLİ DİNLEME',
            badgeBg: Colors.purple,
            levelText: 'B2 - C1',
            title: 'Listening & Note-Taking Sınavları',
            desc: 'Boğaziçi BUEPT, İTÜ ve ODTÜ EPE sesli akademik ders dinleme ve not alma simülatörü.',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ListeningScreen()),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _examCard({
    required BuildContext context,
    required String badge,
    required Color badgeBg,
    required String levelText,
    required String title,
    required String desc,
    bool isPrimary = false,
    required VoidCallback onTap,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isPrimary ? AppTheme.brandLightBlue.withValues(alpha: 0.6) : Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(
          color: isPrimary ? AppTheme.brandBlue : AppTheme.borderSubtle,
          width: isPrimary ? 2 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: badgeBg,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  badge,
                  style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white),
                ),
              ),
              Text(
                levelText,
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            title,
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppTheme.textMain),
          ),
          const SizedBox(height: 4),
          Text(
            desc,
            style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.4),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: onTap,
              style: ElevatedButton.styleFrom(
                backgroundColor: isPrimary ? AppTheme.brandBlue : Colors.grey.shade100,
                foregroundColor: isPrimary ? Colors.white : AppTheme.textMain,
              ),
              child: const Text('Sınavı Başlat'),
            ),
          ),
        ],
      ),
    );
  }
}
