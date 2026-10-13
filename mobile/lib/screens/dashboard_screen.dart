import 'package:flutter/material.dart';
import '../models/university.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'exam_runner_screen.dart';
import 'university_picker_dialog.dart';
import 'listening_screen.dart';
import 'writing_screen.dart';

class DashboardScreen extends StatefulWidget {
  final University currentUniversity;
  final String currentLevel;
  final Function(University) onUniversityChange;
  final Function(String) onLevelChange;
  final Function(int) onTabSwitch;

  const DashboardScreen({
    super.key,
    required this.currentUniversity,
    required this.currentLevel,
    required this.onUniversityChange,
    required this.onLevelChange,
    required this.onTabSwitch,
  });

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<University> _universities = [];
  Map<String, dynamic>? _stats;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final unis = await ApiService().getUniversities();
    final stats = await ApiService().getStats();
    if (mounted) {
      setState(() {
        _universities = unis;
        _stats = stats;
      });
    }
  }

  void _openUniPicker() {
    if (_universities.isEmpty) return;
    showDialog(
      context: context,
      builder: (_) => UniversityPickerDialog(
        universities: _universities,
        selectedUniversity: widget.currentUniversity,
        onSelect: (uni) {
          widget.onUniversityChange(uni);
        },
      ),
    );
  }

  void _startFullExam() async {
    final questions = await ApiService().getQuestions(
      universityId: widget.currentUniversity.id,
      level: widget.currentLevel,
    );
    if (!mounted) return;
    if (questions.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Soru yüklenemedi.')),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ExamRunnerScreen(
          questions: questions,
          university: widget.currentUniversity,
          level: widget.currentLevel,
        ),
      ),
    ).then((_) => _loadData());
  }

  @override
  Widget build(BuildContext context) {
    final uni = widget.currentUniversity;
    final streak = _stats?['profile']?['streak_days'] ?? 1;
    final totalExams = _stats?['total_exams_taken'] ?? 0;
    final avgScore = _stats?['average_exam_score'] ?? 0;
    final masteredVocab = _stats?['mastered_vocab'] ?? 0;
    final totalVocab = _stats?['total_vocab'] ?? 0;
    final mistakeCount = _stats?['unresolved_mistakes'] ?? 0;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [AppTheme.brandBlue, AppTheme.brandNavy]),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.school, size: 18, color: Colors.white),
            ),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Text('PrepMaster', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900)),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                      decoration: BoxDecoration(
                        color: AppTheme.brandLightBlue,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Text('HAZIRLIK', style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: AppTheme.brandBlue)),
                    ),
                  ],
                ),
                InkWell(
                  onTap: _openUniPicker,
                  child: Row(
                    children: [
                      Text(uni.shortName, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted)),
                      const Text(' (Değiştir)', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue)),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_balance_outlined, color: AppTheme.textMain),
            onPressed: _openUniPicker,
            tooltip: 'Üniversite Değiştir',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Level Selector Bar
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Çalışma Kuru (CEFR):', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTheme.textMuted)),
                  Row(
                    children: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'].map((lvl) {
                      final isSel = widget.currentLevel == lvl;
                      return Padding(
                        padding: const EdgeInsets.only(left: 4),
                        child: InkWell(
                          onTap: () => widget.onLevelChange(lvl),
                          borderRadius: BorderRadius.circular(10),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                            decoration: BoxDecoration(
                              color: isSel ? AppTheme.brandBlue : Colors.white,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: isSel ? AppTheme.brandBlue : AppTheme.borderSubtle),
                            ),
                            child: Text(
                              lvl,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w800,
                                color: isSel ? Colors.white : AppTheme.textMain,
                              ),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Hero Card
              Container(
                padding: const EdgeInsets.all(22),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1E3A8A), Color(0xFF1E1B4B)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.brandNavy.withValues(alpha: 0.3),
                      blurRadius: 16,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white24,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            '${uni.shortName} Hazırlık',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.green.withValues(alpha: 0.3),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.4)),
                          ),
                          child: Text(
                            '%${uni.passingScore} Baraj Puanı',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.greenAccent),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    Text(
                      uni.examName,
                      style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Colors.white),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      uni.description,
                      style: const TextStyle(fontSize: 12, color: Colors.white70, height: 1.4),
                    ),
                    const SizedBox(height: 18),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: _startFullExam,
                            icon: const Icon(Icons.play_arrow_rounded, size: 18),
                            label: const Text('Tam Deneme Başlat'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.white,
                              foregroundColor: AppTheme.brandNavy,
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        OutlinedButton(
                          onPressed: () => widget.onTabSwitch(3), // flashcards tab
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.white,
                            side: const BorderSide(color: Colors.white38),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                          ),
                          child: const Text('Kelimeler', style: TextStyle(fontWeight: FontWeight.w700)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Stat Cards
              SizedBox(
                height: 100,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  children: [
                    _statCard(
                      icon: Icons.local_fire_department,
                      iconColor: AppTheme.accentAmber,
                      title: 'Seri',
                      value: '$streak Gün',
                      subtitle: 'Her gün pratik',
                    ),
                    const SizedBox(width: 10),
                    _statCard(
                      icon: Icons.assignment_turned_in,
                      iconColor: AppTheme.brandBlue,
                      title: 'Denemeler',
                      value: '$totalExams',
                      subtitle: 'Tamamlanan',
                    ),
                    const SizedBox(width: 10),
                    _statCard(
                      icon: Icons.trending_up,
                      iconColor: AppTheme.accentEmerald,
                      title: 'Ortalama',
                      value: '%$avgScore',
                      subtitle: 'Başarı notu',
                    ),
                    const SizedBox(width: 10),
                    _statCard(
                      icon: Icons.menu_book,
                      iconColor: Colors.indigo,
                      title: 'Kelimeler',
                      value: '$masteredVocab/$totalVocab',
                      subtitle: 'Öğrenilen',
                    ),
                    const SizedBox(width: 10),
                    InkWell(
                      onTap: () => widget.onTabSwitch(2), // Mistakes tab
                      borderRadius: BorderRadius.circular(20),
                      child: _statCard(
                        icon: Icons.shield_outlined,
                        iconColor: AppTheme.accentRose,
                        title: 'Hata Defterim',
                        value: '$mistakeCount',
                        subtitle: 'Yanlışları Çöz →',
                        borderColor: Colors.red.shade200,
                        isHighlighted: true,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Exam Sections Distribution
              const Text(
                'Sınav Formatı & Soru Dağılımı',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textMain),
              ),
              const SizedBox(height: 10),

              ...uni.sections.map((sec) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(color: AppTheme.borderSubtle),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(sec.name, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.textMain)),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: AppTheme.brandLightBlue,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                'Ağırlık: %${sec.weightPercent}',
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(sec.description, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.4)),
                      ],
                    ),
                  ),
                );
              }),
              const SizedBox(height: 18),
              const Text(
                'Akademik Atölyeler & Pratik',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
              ),
              const SizedBox(height: 10),

              Row(
                children: [
                  Expanded(
                    child: InkWell(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const ListeningScreen()),
                        );
                      },
                      borderRadius: BorderRadius.circular(18),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: AppTheme.borderSubtle),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.02),
                              blurRadius: 8,
                              offset: const Offset(0, 3),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.blue.shade50,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Icon(Icons.headphones, size: 20, color: AppTheme.brandBlue),
                            ),
                            const SizedBox(height: 10),
                            const Text(
                              'Sesli Dinleme',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                            ),
                            const SizedBox(height: 2),
                            const Text(
                              'Note-Taking Simülatörü',
                              style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: InkWell(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const WritingScreen()),
                        );
                      },
                      borderRadius: BorderRadius.circular(18),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: AppTheme.borderSubtle),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.02),
                              blurRadius: 8,
                              offset: const Offset(0, 3),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.indigo.shade50,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Icon(Icons.auto_awesome, size: 20, color: Colors.indigo),
                            ),
                            const SizedBox(height: 10),
                            const Text(
                              'AI Essay Puanlama',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                            ),
                            const SizedBox(height: 2),
                            const Text(
                              'Writing Rehberi & Not',
                              style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _statCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String value,
    required String subtitle,
    Color? borderColor,
    bool isHighlighted = false,
  }) {
    return Container(
      width: 125,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isHighlighted ? Colors.red.shade50.withValues(alpha: 0.4) : Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: borderColor ?? AppTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted)),
              Icon(icon, size: 16, color: iconColor),
            ],
          ),
          Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.textMain)),
          Text(subtitle, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: iconColor)),
        ],
      ),
    );
  }
}
