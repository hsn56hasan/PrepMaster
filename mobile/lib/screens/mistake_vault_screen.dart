import 'package:flutter/material.dart';
import '../models/mistake_item.dart';
import '../models/university.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'exam_runner_screen.dart';

class MistakeVaultScreen extends StatefulWidget {
  final University currentUniversity;
  final String currentLevel;

  const MistakeVaultScreen({
    super.key,
    required this.currentUniversity,
    required this.currentLevel,
  });

  @override
  State<MistakeVaultScreen> createState() => _MistakeVaultScreenState();
}

class _MistakeVaultScreenState extends State<MistakeVaultScreen> {
  List<MistakeItem> _mistakes = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadMistakes();
  }

  Future<void> _loadMistakes() async {
    setState(() => _isLoading = true);
    final list = await ApiService().getMistakes();
    if (mounted) {
      setState(() {
        _mistakes = list;
        _isLoading = false;
      });
    }
  }

  Future<void> _resolveMistake(String questionId) async {
    await ApiService().resolveMistake(questionId);
    _loadMistakes();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Soru çözüldü olarak işaretlendi ve arşivlendi.')),
      );
    }
  }

  void _startMistakeExam() {
    if (_mistakes.isEmpty) return;
    final questions = _mistakes.map((m) => m.questionDetails).toList();
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ExamRunnerScreen(
          questions: questions,
          university: widget.currentUniversity,
          level: widget.currentLevel,
          isMistakeExam: true,
        ),
      ),
    ).then((_) => _loadMistakes());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Hata Defterim'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadMistakes,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadMistakes,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Hero Card
                    Container(
                      padding: const EdgeInsets.all(22),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF881337), Color(0xFF0F172A)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.red.shade900.withValues(alpha: 0.3),
                            blurRadius: 16,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.white24,
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: const Row(
                                  children: [
                                    Icon(Icons.shield_outlined, size: 14, color: Colors.white),
                                    SizedBox(width: 4),
                                    Text('Kişisel Hata Havuzu', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white)),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.redAccent.withValues(alpha: 0.3),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: Colors.redAccent.shade100, width: 1),
                                ),
                                child: Text(
                                  '${_mistakes.length} Yanlış Soru',
                                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          const Text(
                            'Smart Mistake Vault',
                            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: Colors.white),
                          ),
                          const SizedBox(height: 4),
                          const Text(
                            'Yanlış yaptığınız tüm sorular burada birikir. Eksiklerinizi tekrar çözerek sınav barajını garantileyin.',
                            style: TextStyle(fontSize: 12, color: Colors.white70, height: 1.4),
                          ),
                          const SizedBox(height: 18),
                          if (_mistakes.isNotEmpty)
                            ElevatedButton.icon(
                              onPressed: _startMistakeExam,
                              icon: const Icon(Icons.play_arrow_rounded, size: 18),
                              label: const Text('Yanlışlarımı Sınav Olarak Tekrar Çöz'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppTheme.accentRose,
                                foregroundColor: Colors.white,
                              ),
                            ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    if (_mistakes.isEmpty)
                      Container(
                        padding: const EdgeInsets.all(32),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(24),
                          border: Border.all(color: AppTheme.borderSubtle),
                        ),
                        child: Column(
                          children: const [
                            Icon(Icons.check_circle_outline_rounded, size: 48, color: AppTheme.accentEmerald),
                            SizedBox(height: 12),
                            Text(
                              'Harika! Hata Defteriniz Boş',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Henüz çözülmemiş yanlış sorunuz bulunmuyor. Yeni bir deneme sınavı çözerek kendinizi test edebilirsiniz!',
                              textAlign: TextAlign.center,
                              style: TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.4),
                            ),
                          ],
                        ),
                      )
                    else
                      ..._mistakes.map((m) {
                        final q = m.questionDetails;
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 16),
                          child: Container(
                            padding: const EdgeInsets.all(18),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(22),
                              border: Border.all(color: Colors.red.shade100, width: 1.5),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Row(
                                      children: [
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                          decoration: BoxDecoration(
                                            color: Colors.red.shade50,
                                            borderRadius: BorderRadius.circular(8),
                                          ),
                                          child: Text(
                                            '${q.category} • ${q.level}',
                                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.accentRose),
                                          ),
                                        ),
                                        const SizedBox(width: 6),
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                          decoration: BoxDecoration(
                                            color: Colors.amber.shade50,
                                            borderRadius: BorderRadius.circular(8),
                                            border: Border.all(color: Colors.amber.shade200),
                                          ),
                                          child: Text(
                                            '${m.wrongCount} kez yanlış',
                                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: AppTheme.accentAmber),
                                          ),
                                        ),
                                      ],
                                    ),
                                    Text(
                                      q.universityId.toUpperCase(),
                                      style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: AppTheme.textMuted),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 12),

                                if (q.passage != null && q.passage!.isNotEmpty) ...[
                                  Container(
                                    padding: const EdgeInsets.all(12),
                                    decoration: BoxDecoration(
                                      color: Colors.grey.shade50,
                                      borderRadius: BorderRadius.circular(12),
                                      border: Border.all(color: Colors.grey.shade200),
                                    ),
                                    child: Text(
                                      q.passage!,
                                      style: const TextStyle(fontSize: 12, height: 1.5, color: Color(0xFF475569)),
                                    ),
                                  ),
                                  const SizedBox(height: 12),
                                ],

                                Text(
                                  q.question,
                                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.textMain),
                                ),
                                const SizedBox(height: 12),

                                // Options comparison
                                ...q.options.map((opt) {
                                  final isCorrect = opt.key == q.correctAnswer;
                                  final isWrong = opt.key == m.lastWrongAnswer;

                                  Color borderCol = AppTheme.borderSubtle;
                                  Color bgCol = Colors.grey.shade50;
                                  if (isCorrect) {
                                    borderCol = AppTheme.accentEmerald;
                                    bgCol = Colors.green.shade50.withValues(alpha: 0.5);
                                  } else if (isWrong) {
                                    borderCol = AppTheme.accentRose;
                                    bgCol = Colors.red.shade50.withValues(alpha: 0.5);
                                  }

                                  return Padding(
                                    padding: const EdgeInsets.only(bottom: 6),
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                      decoration: BoxDecoration(
                                        color: bgCol,
                                        borderRadius: BorderRadius.circular(12),
                                        border: Border.all(color: borderCol, width: (isCorrect || isWrong) ? 1.5 : 1),
                                      ),
                                      child: Row(
                                        children: [
                                          Text('${opt.key}) ', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 12)),
                                          Expanded(child: Text(opt.text, style: const TextStyle(fontSize: 12))),
                                          if (isCorrect)
                                            const Text('✓ Doğru', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.accentEmerald)),
                                          if (isWrong)
                                            const Text('✗ Yanıtın', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.accentRose)),
                                        ],
                                      ),
                                    ),
                                  );
                                }),
                                const SizedBox(height: 12),

                                // Explanation
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: AppTheme.brandLightBlue,
                                    borderRadius: BorderRadius.circular(14),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        'Neden Yanıldınız? (Çözüm Analizi)',
                                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        q.explanationTr,
                                        style: const TextStyle(fontSize: 12, height: 1.4, color: AppTheme.brandNavy),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(height: 12),

                                Align(
                                  alignment: Alignment.centerRight,
                                  child: ElevatedButton.icon(
                                    onPressed: () => _resolveMistake(q.id),
                                    icon: const Icon(Icons.check, size: 16),
                                    label: const Text('Çözdüm (Arşivle)'),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppTheme.accentEmerald,
                                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                      textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      }),
                  ],
                ),
              ),
            ),
    );
  }
}
