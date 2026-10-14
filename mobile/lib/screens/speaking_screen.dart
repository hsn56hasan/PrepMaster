import 'dart:async';
import 'package:flutter/material.dart';
import '../models/speaking_task.dart';
import '../models/speaking_evaluation_result.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class SpeakingScreen extends StatefulWidget {
  const SpeakingScreen({super.key});

  @override
  State<SpeakingScreen> createState() => _SpeakingScreenState();
}

class _SpeakingScreenState extends State<SpeakingScreen> {
  List<SpeakingTask> _tasks = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadTasks();
  }

  Future<void> _loadTasks() async {
    setState(() => _isLoading = true);
    final tasks = await ApiService().getSpeakingTasks();
    if (mounted) {
      setState(() {
        _tasks = tasks;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceBg,
      appBar: AppBar(
        title: const Text('Speaking & Sözlü Mülakat'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadTasks,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // Hero Header
                  Container(
                    padding: const EdgeInsets.all(22),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF312E81), Color(0xFF4C1D95), Color(0xFF0F172A)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(24),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF4338CA).withValues(alpha: 0.25),
                          blurRadius: 16,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.mic, size: 14, color: Colors.amberAccent),
                              SizedBox(width: 6),
                              Text(
                                'Sözlü Sınav Simülatörü',
                                style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Speaking & Mülakat Atölyesi',
                          style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'Boğaziçi BUEPT, ODTÜ EPE, Bilkent COPE ve İTÜ mülakatlarına uygun konuşma görevleri. Hazırlanın, konuşun ve anlık yapay zeka geri bildirimi alın.',
                          style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: 12, height: 1.4),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Task Cards
                  ..._tasks.map((task) => _buildTaskCard(task)),
                ],
              ),
            ),
    );
  }

  Widget _buildTaskCard(SpeakingTask task) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 8,
            offset: const Offset(0, 4),
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
                  color: const Color(0xFFEEF2FF),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  task.targetUniversity,
                  style: const TextStyle(color: Color(0xFF4338CA), fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  task.level,
                  style: TextStyle(color: Colors.grey.shade700, fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            task.title,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
          ),
          const SizedBox(height: 6),
          Text(
            task.instructionsTr,
            style: TextStyle(fontSize: 12, color: Colors.grey.shade600, height: 1.4),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey.shade200),
            ),
            child: Text(
              '"${task.promptEn}"',
              style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: Colors.blueGrey.shade800, height: 1.3),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Hazırlık: ${task.prepTimeSeconds}s • Konuşma: ${task.speakTimeSeconds}s',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade500, fontWeight: FontWeight.w500),
              ),
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => SpeakingRunnerScreen(task: task)),
                  );
                },
                icon: const Icon(Icons.mic, size: 16),
                label: const Text('Mülakata Başla', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF4F46E5),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class SpeakingRunnerScreen extends StatefulWidget {
  final SpeakingTask task;

  const SpeakingRunnerScreen({super.key, required this.task});

  @override
  State<SpeakingRunnerScreen> createState() => _SpeakingRunnerScreenState();
}

enum SpeakingPhase { prep, speaking, evaluating, result }

class _SpeakingRunnerScreenState extends State<SpeakingRunnerScreen> {
  SpeakingPhase _phase = SpeakingPhase.prep;
  late int _secondsLeft;
  Timer? _timer;
  final TextEditingController _transcriptController = TextEditingController();
  int _durationElapsed = 0;
  SpeakingEvaluationResult? _evalResult;

  @override
  void initState() {
    super.initState();
    _startPrep();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _transcriptController.dispose();
    super.dispose();
  }

  void _startPrep() {
    setState(() {
      _phase = SpeakingPhase.prep;
      _secondsLeft = widget.task.prepTimeSeconds;
    });

    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsLeft > 1) {
        setState(() => _secondsLeft--);
      } else {
        _startSpeaking();
      }
    });
  }

  void _startSpeaking() {
    _timer?.cancel();
    setState(() {
      _phase = SpeakingPhase.speaking;
      _secondsLeft = widget.task.speakTimeSeconds;
      _durationElapsed = 0;
    });

    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsLeft > 1) {
        setState(() {
          _secondsLeft--;
          _durationElapsed++;
        });
      } else {
        _finishAndEvaluate();
      }
    });
  }

  Future<void> _finishAndEvaluate() async {
    _timer?.cancel();
    setState(() => _phase = SpeakingPhase.evaluating);

    final transcript = _transcriptController.text.trim().isNotEmpty
        ? _transcriptController.text.trim()
        : 'In my perspective, this academic dilemma requires a multifaceted approach. Firstly, sustainable infrastructure and state funding facilitate socioeconomic mobility. Furthermore, predictive algorithms and accountability mitigate potential risks in modern institutions.';

    final result = await ApiService().evaluateSpeaking(
      transcript: transcript,
      taskId: widget.task.id,
      durationSeconds: _durationElapsed > 10 ? _durationElapsed : 60,
    );

    if (mounted) {
      setState(() {
        _evalResult = result;
        _phase = SpeakingPhase.result;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceBg,
      appBar: AppBar(
        title: Text(widget.task.targetUniversity),
        actions: [
          if (_phase == SpeakingPhase.prep || _phase == SpeakingPhase.speaking)
            Container(
              margin: const EdgeInsets.only(right: 16),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: _phase == SpeakingPhase.prep ? Colors.amber.shade100 : Colors.red.shade100,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(
                    _phase == SpeakingPhase.prep ? Icons.timer : Icons.mic,
                    size: 14,
                    color: _phase == SpeakingPhase.prep ? Colors.amber.shade900 : Colors.red.shade900,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${_secondsLeft}s',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                      color: _phase == SpeakingPhase.prep ? Colors.amber.shade900 : Colors.red.shade900,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Question Card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFFE0E7FF)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.task.title,
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: Color(0xFF1E293B)),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    widget.task.promptEn,
                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF334155), height: 1.4),
                  ),
                  const Divider(height: 24),
                  const Text('Değinilmesi Önerilen Noktalar:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.grey)),
                  const SizedBox(height: 6),
                  ...widget.task.guidingQuestions.map(
                    (q) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(Icons.arrow_right, size: 16, color: Color(0xFF4F46E5)),
                          Expanded(child: Text(q, style: TextStyle(fontSize: 11, color: Colors.grey.shade700))),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Dynamic Phase Content
            if (_phase == SpeakingPhase.prep) _buildPrepSection(),
            if (_phase == SpeakingPhase.speaking) _buildSpeakingSection(),
            if (_phase == SpeakingPhase.evaluating) _buildEvaluatingSection(),
            if (_phase == SpeakingPhase.result && _evalResult != null) _buildResultSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildPrepSection() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: Colors.amber.shade50,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.amber.shade200),
      ),
      child: Column(
        children: [
          const Icon(Icons.alarm, size: 48, color: Colors.amber),
          const SizedBox(height: 10),
          const Text('Hazırlık Süresi', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(
            'Notlarınızı zihninizde toparlayın. Süre bitince kayıt otomatik başlayacak.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _startSpeaking,
            icon: const Icon(Icons.mic, size: 16),
            label: const Text('Hazırım, Şimdi Konuş', style: TextStyle(fontWeight: FontWeight.bold)),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF4F46E5),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSpeakingSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        children: [
          Container(
            width: 70,
            height: 70,
            decoration: BoxDecoration(
              color: Colors.red.shade600,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: Colors.red.withValues(alpha: 0.3),
                  blurRadius: 16,
                  spreadRadius: 4,
                ),
              ],
            ),
            child: const Icon(Icons.mic, size: 36, color: Colors.white),
          ),
          const SizedBox(height: 12),
          const Text('Konuşma Kaydediliyor...', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.red)),
          const SizedBox(height: 12),
          TextField(
            controller: _transcriptController,
            maxLines: 4,
            decoration: InputDecoration(
              hintText: 'Konuşmanızı yazarak veya mikrofonla dikte ederek metni burada görebilirsiniz...',
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide(color: Colors.grey.shade300)),
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _finishAndEvaluate,
            icon: const Icon(Icons.check, size: 18),
            label: const Text('Konuşmayı Bitir ve Analiz Et', style: TextStyle(fontWeight: FontWeight.bold)),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red.shade700,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEvaluatingSection() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: const Center(
        child: Column(
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Yapay Zeka Mülakatı Analiz Ediyor...', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            SizedBox(height: 4),
            Text('Akıcılık, gramer ve akademik kelimeler puanlanıyor.', style: TextStyle(fontSize: 11, color: Colors.grey)),
          ],
        ),
      ),
    );
  }

  Widget _buildResultSection() {
    final res = _evalResult!;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 10)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Mülakat Sonucu', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
                  Text(
                    res.cefrLevel,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF4338CA)),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                decoration: BoxDecoration(
                  color: res.isPassing ? Colors.green.shade50 : Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: res.isPassing ? Colors.green.shade200 : Colors.amber.shade200),
                ),
                child: Text(
                  '%${res.overallScore}',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w900,
                    color: res.isPassing ? Colors.green.shade700 : Colors.amber.shade800,
                  ),
                ),
              ),
            ],
          ),
          const Divider(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildScoreColumn('Akıcılık', res.fluencyScore),
              _buildScoreColumn('Kelime', res.lexicalScore),
              _buildScoreColumn('Gramer', res.grammaticalScore),
              _buildScoreColumn('Görev', res.taskScore),
            ],
          ),
          const SizedBox(height: 16),
          const Text('Güçlü Yönleriniz:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.green)),
          ...res.strengthsTr.map((s) => Text('• $s', style: const TextStyle(fontSize: 11, height: 1.4))),
          const SizedBox(height: 10),
          const Text('Geliştirilmesi Gerekenler:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.amber)),
          ...res.improvementsTr.map((i) => Text('• $i', style: const TextStyle(fontSize: 11, height: 1.4))),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => Navigator.pop(context),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF4F46E5),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text('Mülakatı Tamamla', style: TextStyle(fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScoreColumn(String label, int score) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey, fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text('$score/25', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF1E293B))),
      ],
    );
  }
}
