import 'dart:async';
import 'package:flutter/material.dart';
import '../models/question.dart';
import '../models/university.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'exam_result_screen.dart';

class ExamRunnerScreen extends StatefulWidget {
  final List<Question> questions;
  final University university;
  final String level;
  final bool isMistakeExam;

  const ExamRunnerScreen({
    super.key,
    required this.questions,
    required this.university,
    required this.level,
    this.isMistakeExam = false,
  });

  @override
  State<ExamRunnerScreen> createState() => _ExamRunnerScreenState();
}

class _ExamRunnerScreenState extends State<ExamRunnerScreen> {
  int _currentIndex = 0;
  final Map<String, String> _userAnswers = {};
  final Map<String, int> _questionTimes = {};
  final Set<String> _flaggedQuestionIds = {};

  late int _secondsRemaining;
  late int _totalSeconds;
  Timer? _timer;
  int _lastQuestionEnterTime = 0;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    // 90 seconds per question or minimum 3 minutes
    _totalSeconds = (widget.questions.length * 90).clamp(180, 10800);
    _secondsRemaining = _totalSeconds;
    _lastQuestionEnterTime = DateTime.now().millisecondsSinceEpoch;

    _startTimer();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsRemaining > 0) {
        setState(() {
          _secondsRemaining--;
        });
      } else {
        _timer?.cancel();
        _finishExam(autoSubmit: true);
      }
    });
  }

  void _trackTimeLeave() {
    final currentQ = widget.questions[_currentIndex];
    final now = DateTime.now().millisecondsSinceEpoch;
    final elapsed = ((now - _lastQuestionEnterTime) / 1000).round().clamp(1, 1000);
    _questionTimes[currentQ.id] = (_questionTimes[currentQ.id] ?? 0) + elapsed;
  }

  void _trackTimeEnter() {
    _lastQuestionEnterTime = DateTime.now().millisecondsSinceEpoch;
  }

  void _selectOption(String key) {
    setState(() {
      _userAnswers[widget.questions[_currentIndex].id] = key;
    });
  }

  void _toggleFlag() {
    final qId = widget.questions[_currentIndex].id;
    setState(() {
      if (_flaggedQuestionIds.contains(qId)) {
        _flaggedQuestionIds.remove(qId);
      } else {
        _flaggedQuestionIds.add(qId);
      }
    });
  }

  void _nextQuestion() {
    if (_currentIndex < widget.questions.length - 1) {
      _trackTimeLeave();
      setState(() {
        _currentIndex++;
      });
      _trackTimeEnter();
    }
  }

  void _prevQuestion() {
    if (_currentIndex > 0) {
      _trackTimeLeave();
      setState(() {
        _currentIndex--;
      });
      _trackTimeEnter();
    }
  }

  void _jumpToQuestion(int index) {
    _trackTimeLeave();
    setState(() {
      _currentIndex = index;
    });
    _trackTimeEnter();
    Navigator.pop(context); // close palette modal
  }

  Future<void> _finishExam({bool autoSubmit = false}) async {
    if (!autoSubmit) {
      final confirm = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Sınavı Tamamla', style: TextStyle(fontWeight: FontWeight.w800)),
          content: Text(
            'Toplam ${widget.questions.length} sorudan ${_userAnswers.length} tanesini yanıtladınız. Sınavı bitirip sonuçları görmek istiyor musunuz?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Devam Et'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(ctx, true),
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.accentEmerald),
              child: const Text('Sınavı Bitir'),
            ),
          ],
        ),
      );
      if (confirm != true) return;
    }

    _timer?.cancel();
    _trackTimeLeave();

    setState(() => _isSubmitting = true);

    final durationSpent = _totalSeconds - _secondsRemaining;

    try {
      final result = await ApiService().submitExam(
        universityId: widget.university.id,
        level: widget.level,
        durationSeconds: durationSpent,
        answers: _userAnswers,
        questionTimes: _questionTimes,
        isMistakePractice: widget.isMistakeExam,
      );

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => ExamResultScreen(
            result: result,
            university: widget.university,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isSubmitting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Hata oluştu: $e')),
      );
    }
  }

  void _showPalette() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Soru Navigasyonu',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                  ),
                  Text(
                    '${_userAnswers.length}/${widget.questions.length} Yanıtlandı',
                    style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Flexible(
                child: GridView.builder(
                  shrinkWrap: true,
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 5,
                    mainAxisSpacing: 10,
                    crossAxisSpacing: 10,
                  ),
                  itemCount: widget.questions.length,
                  itemBuilder: (context, i) {
                    final q = widget.questions[i];
                    final isAns = _userAnswers.containsKey(q.id);
                    final isFlag = _flaggedQuestionIds.contains(q.id);
                    final isCur = i == _currentIndex;

                    Color bg = Colors.white;
                    Color textCol = AppTheme.textMain;
                    Border? border = Border.all(color: AppTheme.borderSubtle);

                    if (isAns) {
                      bg = AppTheme.brandBlue;
                      textCol = Colors.white;
                      border = null;
                    }
                    if (isFlag) {
                      border = Border.all(color: AppTheme.accentAmber, width: 2);
                    }
                    if (isCur) {
                      border = Border.all(color: AppTheme.brandNavy, width: 2.5);
                    }

                    return InkWell(
                      onTap: () => _jumpToQuestion(i),
                      borderRadius: BorderRadius.circular(12),
                      child: Container(
                        decoration: BoxDecoration(
                          color: bg,
                          borderRadius: BorderRadius.circular(12),
                          border: border,
                        ),
                        child: Center(
                          child: Text(
                            '${i + 1}',
                            style: TextStyle(
                              color: textCol,
                              fontWeight: FontWeight.w800,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _legendItem(AppTheme.brandBlue, 'Yanıtlandı'),
                  _legendItem(AppTheme.accentAmber, 'İşaretli'),
                  _legendItem(Colors.grey.shade300, 'Boş'),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _legendItem(Color color, String label) {
    return Row(
      children: [
        Container(width: 10, height: 10, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
      ],
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.questions.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Sınav')),
        body: const Center(child: Text('Bu sınava ait soru bulunamadı.')),
      );
    }

    final q = widget.questions[_currentIndex];
    final selectedOption = _userAnswers[q.id];
    final isFlagged = _flaggedQuestionIds.contains(q.id);

    final mins = _secondsRemaining ~/ 60;
    final secs = _secondsRemaining % 60;
    final timeStr = '${mins.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
    final isUrgent = _secondsRemaining < 180;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        final exit = await showDialog<bool>(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Sınavdan Çıkılsın mı?'),
            content: const Text('Sınavdan çıkarsanız ilerlemeniz kaydedilmeyecektir.'),
            actions: [
              TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('İptal')),
              TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Çık')),
            ],
          ),
        );
        if (exit == true && context.mounted) {
          Navigator.pop(context);
        }
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: AppTheme.brandNavy,
          foregroundColor: Colors.white,
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.isMistakeExam ? 'Hata Defteri Sınavı' : widget.university.examName,
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Colors.white),
              ),
              Text(
                'Soru ${_currentIndex + 1} / ${widget.questions.length}',
                style: const TextStyle(fontSize: 11, color: Colors.white70),
              ),
            ],
          ),
          actions: [
            // Timer Badge
            Container(
              margin: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: isUrgent ? AppTheme.accentRose.withValues(alpha: 0.3) : Colors.black26,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isUrgent ? AppTheme.accentRose : Colors.white24,
                  width: 1.5,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.timer,
                    size: 15,
                    color: isUrgent ? AppTheme.accentRose : AppTheme.accentAmber,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    timeStr,
                    style: TextStyle(
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.w800,
                      fontSize: 13,
                      color: isUrgent ? Colors.redAccent : Colors.amber.shade200,
                    ),
                  ),
                ],
              ),
            ),
            IconButton(
              icon: const Icon(Icons.grid_view_rounded, color: Colors.white),
              onPressed: _showPalette,
            ),
          ],
        ),
        body: _isSubmitting
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('Sonuçlar hesaplanıyor ve karne hazırlanıyor...', style: TextStyle(fontWeight: FontWeight.w700)),
                  ],
                ),
              )
            : SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Question Meta bar
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: AppTheme.brandLightBlue,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                q.category,
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue),
                              ),
                            ),
                            const SizedBox(width: 6),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.grey.shade100,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                q.level,
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.textMuted),
                              ),
                            ),
                          ],
                        ),
                        InkWell(
                          onTap: _toggleFlag,
                          borderRadius: BorderRadius.circular(8),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                            decoration: BoxDecoration(
                              color: isFlagged ? AppTheme.accentAmber.withValues(alpha: 0.15) : Colors.white,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: isFlagged ? AppTheme.accentAmber : AppTheme.borderSubtle,
                              ),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  isFlagged ? Icons.bookmark : Icons.bookmark_border,
                                  size: 16,
                                  color: isFlagged ? AppTheme.accentAmber : AppTheme.textMuted,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  isFlagged ? 'İşaretli' : 'İşaretle',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                    color: isFlagged ? AppTheme.accentAmber : AppTheme.textMuted,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Reading passage if present
                    if (q.passage != null && q.passage!.isNotEmpty) ...[
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: AppTheme.borderSubtle),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'READING PASSAGE',
                              style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 1.2, color: AppTheme.textMuted),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              q.passage!,
                              style: const TextStyle(fontSize: 13, height: 1.6, color: Color(0xFF334155)),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Question text
                    Container(
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppTheme.borderSubtle),
                      ),
                      child: Text(
                        q.question,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          height: 1.5,
                          color: AppTheme.textMain,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Options list
                    ...q.options.map((opt) {
                      final isSelected = selectedOption == opt.key;
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: InkWell(
                          onTap: () => _selectOption(opt.key),
                          borderRadius: BorderRadius.circular(16),
                          child: Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: isSelected ? AppTheme.brandLightBlue : Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: isSelected ? AppTheme.brandBlue : AppTheme.borderSubtle,
                                width: isSelected ? 2 : 1,
                              ),
                            ),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  width: 28,
                                  height: 28,
                                  decoration: BoxDecoration(
                                    color: isSelected ? AppTheme.brandBlue : Colors.grey.shade100,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Center(
                                    child: Text(
                                      opt.key,
                                      style: TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.w800,
                                        color: isSelected ? Colors.white : AppTheme.textMain,
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Padding(
                                    padding: const EdgeInsets.only(top: 3),
                                    child: Text(
                                      opt.text,
                                      style: TextStyle(
                                        fontSize: 13.5,
                                        height: 1.4,
                                        fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                                        color: isSelected ? AppTheme.brandNavy : AppTheme.textMain,
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    }),
                  ],
                ),
              ),
        bottomNavigationBar: Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          decoration: const BoxDecoration(
            color: Colors.white,
            border: Border(top: BorderSide(color: AppTheme.borderSubtle)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              OutlinedButton.icon(
                onPressed: _currentIndex > 0 ? _prevQuestion : null,
                icon: const Icon(Icons.chevron_left, size: 18),
                label: const Text('Önceki'),
                style: OutlinedButton.styleFrom(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
              ),
              ElevatedButton.icon(
                onPressed: () => _finishExam(),
                icon: const Icon(Icons.check_circle_outline, size: 18),
                label: const Text('Tamamla'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.accentEmerald,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
              ),
              OutlinedButton.icon(
                onPressed: _currentIndex < widget.questions.length - 1 ? _nextQuestion : null,
                icon: const Icon(Icons.chevron_right, size: 18),
                label: const Text('Sonraki'),
                style: OutlinedButton.styleFrom(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
