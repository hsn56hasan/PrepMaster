import 'package:flutter/material.dart';
import '../models/exam_result.dart';
import '../models/university.dart';
import '../theme/app_theme.dart';

class ExamResultScreen extends StatelessWidget {
  final ExamResult result;
  final University university;

  const ExamResultScreen({
    super.key,
    required this.result,
    required this.university,
  });

  @override
  Widget build(BuildContext context) {
    final isPassed = result.score >= university.passingScore;
    final timeAnalytics = result.timeAnalytics;
    final avgTime = timeAnalytics['avg_time_per_question'] ?? 0;
    final timeTraps = timeAnalytics['time_traps_count'] ?? 0;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Sınav Sonuç Raporu'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Score Banner
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: isPassed
                      ? [const Color(0xFF065F46), const Color(0xFF047857)]
                      : [const Color(0xFF881337), const Color(0xFFBE123C)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(24),
                boxShadow: [
                  BoxShadow(
                    color: (isPassed ? AppTheme.accentEmerald : AppTheme.accentRose).withValues(alpha: 0.3),
                    blurRadius: 16,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: const BoxDecoration(
                      color: Colors.white24,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      isPassed ? Icons.emoji_events_rounded : Icons.info_outline_rounded,
                      color: Colors.white,
                      size: 32,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    isPassed ? 'Tebrikler, Barajı Geçtiniz!' : 'Sınav Tamamlandı',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: Colors.white),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${university.name} • Hedef Baraj: %${university.passingScore}',
                    style: const TextStyle(fontSize: 12, color: Colors.white70),
                  ),
                  const SizedBox(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _metricBadge('%${result.score.toInt()}', 'Başarı Oranı', Colors.white),
                      _metricBadge('${result.correctCount}', 'Doğru', Colors.greenAccent),
                      _metricBadge('${result.wrongCount}', 'Yanlış/Boş', Colors.amberAccent),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Time Management Panel
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: const [
                          Icon(Icons.speed, size: 20, color: AppTheme.accentAmber),
                          SizedBox(width: 8),
                          Text(
                            'Zaman Yönetimi Analizi',
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                          ),
                        ],
                      ),
                      Text(
                        'Toplam: ${result.durationSeconds ~/ 60} dk ${result.durationSeconds % 60} sn',
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.amber.shade50,
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: Colors.amber.shade200),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Ort. Soru Süresi', style: TextStyle(fontSize: 10, color: AppTheme.textMuted)),
                              const SizedBox(height: 2),
                              Text(
                                '${avgTime}s / soru',
                                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.accentAmber),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: (timeTraps > 0 ? Colors.red.shade50 : Colors.green.shade50),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(
                              color: (timeTraps > 0 ? Colors.red.shade200 : Colors.green.shade200),
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Zaman Tuzağı (>90s)', style: TextStyle(fontSize: 10, color: AppTheme.textMuted)),
                              const SizedBox(height: 2),
                              Text(
                                '$timeTraps Soru',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w800,
                                  color: (timeTraps > 0 ? AppTheme.accentRose : AppTheme.accentEmerald),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Detailed Explanations
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Detaylı Çözüm Açıklamaları',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                ),
                if (result.wrongCount > 0)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Text(
                      '${result.wrongCount} Hata Kaydedildi',
                      style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: AppTheme.accentRose),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),

            ...result.details.asMap().entries.map((entry) {
              final index = entry.key;
              final d = entry.value;
              final isTimeTrap = d.timeSpent >= 90;

              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(
                      color: d.isCorrect ? Colors.green.shade200 : Colors.red.shade200,
                      width: 1.2,
                    ),
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
                                  color: d.isCorrect ? Colors.green.shade50 : Colors.red.shade50,
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  'Soru ${index + 1} (${d.category})',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w800,
                                    color: d.isCorrect ? AppTheme.accentEmerald : AppTheme.accentRose,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: isTimeTrap ? Colors.amber.shade100 : Colors.grey.shade100,
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  '⏱️ ${d.timeSpent}s',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w700,
                                    color: isTimeTrap ? AppTheme.accentAmber : AppTheme.textMuted,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          Text(
                            'Yanıt: ${d.chosenAnswer} | Doğru: ${d.correctAnswer}',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(
                        d.questionText,
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                      ),
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppTheme.brandLightBlue,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.lightbulb_outline, size: 16, color: AppTheme.brandBlue),
                                const SizedBox(width: 4),
                                Text(
                                  'Neden ${d.correctAnswer}? (Çözüm Analizi)',
                                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              d.explanationTr,
                              style: const TextStyle(fontSize: 12, height: 1.4, color: AppTheme.brandNavy),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),
            const SizedBox(height: 16),

            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Tamamla ve Dashboard\'a Dön'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _metricBadge(String value, String label, Color color) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: color)),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.white70)),
      ],
    );
  }
}
