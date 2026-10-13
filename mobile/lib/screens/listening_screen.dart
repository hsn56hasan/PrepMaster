import 'dart:async';
import 'package:flutter/material.dart';
import '../models/listening_track.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class ListeningScreen extends StatefulWidget {
  const ListeningScreen({super.key});

  @override
  State<ListeningScreen> createState() => _ListeningScreenState();
}

class _ListeningScreenState extends State<ListeningScreen> {
  List<ListeningTrack> _tracks = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadTracks();
  }

  Future<void> _loadTracks() async {
    setState(() => _isLoading = true);
    final tracks = await ApiService().getListeningTracks();
    if (mounted) {
      setState(() {
        _tracks = tracks;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceBg,
      appBar: AppBar(
        title: const Text('Dinleme (Listening) & Not Alma'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadTracks,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // Hero Header
                  Container(
                    padding: const EdgeInsets.all(22),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF1E3A8A), Color(0xFF0F172A)],
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
                                color: Colors.blue.withValues(alpha: 0.3),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.4)),
                              ),
                              child: const Row(
                                children: [
                                  Icon(Icons.headphones, size: 14, color: Colors.white),
                                  SizedBox(width: 4),
                                  Text(
                                    'Sesli Akademik Simülasyon',
                                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Listening & Note-Taking Sınavları',
                          style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Colors.white),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Boğaziçi BUEPT, İTÜ ve ODTÜ EPE sınav formatlarına uygun sesli dersleri dinleyin; notlarınızı alarak soruları yanıtlayın.',
                          style: TextStyle(fontSize: 12, color: Colors.white70, height: 1.4),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),
                  const Text(
                    'Mevcut Dinleme Sınavları',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                  ),
                  const SizedBox(height: 12),

                  ..._tracks.map((track) {
                    final isNoteTaking = track.type == 'note_taking';
                    return Container(
                      margin: const EdgeInsets.only(bottom: 14),
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppTheme.borderSubtle),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.03),
                            blurRadius: 10,
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
                                  color: isNoteTaking ? Colors.amber.shade50 : Colors.blue.shade50,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(
                                    color: isNoteTaking ? Colors.amber.shade300 : Colors.blue.shade200,
                                  ),
                                ),
                                child: Text(
                                  isNoteTaking ? '📝 Note-Taking' : '🎧 While-Listening',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w800,
                                    color: isNoteTaking ? Colors.amber.shade900 : AppTheme.brandBlue,
                                  ),
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: Colors.grey.shade100,
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  track.level,
                                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.textMuted),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Text(
                            track.title,
                            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            track.subtitle,
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTheme.brandBlue),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            track.instructionsTr,
                            style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.3),
                          ),
                          const SizedBox(height: 14),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                '${track.questions.length} Soru • ${track.targetUniversity}',
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.textMuted),
                              ),
                              ElevatedButton.icon(
                                onPressed: () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => ListeningRunnerScreen(track: track),
                                    ),
                                  );
                                },
                                icon: const Icon(Icons.play_arrow, size: 16),
                                label: const Text('Başlat'),
                                style: ElevatedButton.styleFrom(
                                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                  textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  }),
                ],
              ),
            ),
    );
  }
}

class ListeningRunnerScreen extends StatefulWidget {
  final ListeningTrack track;
  const ListeningRunnerScreen({super.key, required this.track});

  @override
  State<ListeningRunnerScreen> createState() => _ListeningRunnerScreenState();
}

class _ListeningRunnerScreenState extends State<ListeningRunnerScreen> {
  final TextEditingController _notesController = TextEditingController();
  final Map<String, String> _answers = {};
  bool _questionsRevealed = false;
  bool _isPlaying = false;
  double _playbackProgress = 0.0;
  double _playbackRate = 1.0;
  Timer? _audioTimer;
  bool _isSubmitted = false;
  int _score = 0;

  @override
  void initState() {
    super.initState();
    _questionsRevealed = widget.track.type != 'note_taking';
  }

  @override
  void dispose() {
    _audioTimer?.cancel();
    _notesController.dispose();
    super.dispose();
  }

  void _toggleAudio() {
    if (_isPlaying) {
      _pauseAudio();
    } else {
      _startAudio();
    }
  }

  void _startAudio() {
    setState(() => _isPlaying = true);
    _audioTimer?.cancel();
    _audioTimer = Timer.periodic(const Duration(milliseconds: 500), (timer) {
      if (!mounted) return;
      setState(() {
        final step = 0.5 * _playbackRate / widget.track.lectureDurationSeconds;
        _playbackProgress += step;
        if (_playbackProgress >= 1.0) {
          _playbackProgress = 1.0;
          _isPlaying = false;
          _audioTimer?.cancel();
        }
      });
    });
  }

  void _pauseAudio() {
    _audioTimer?.cancel();
    setState(() => _isPlaying = false);
  }

  void _revealQuestions() {
    _pauseAudio();
    setState(() {
      _questionsRevealed = true;
    });
  }

  Future<void> _submitExam() async {
    int correctCount = 0;
    for (var q in widget.track.questions) {
      final chosen = _answers[q.id];
      final isCorrect = chosen == q.correctAnswer;
      if (isCorrect) {
        correctCount++;
      } else if (chosen != null) {
        // Record mistake to Mistake Vault
        ApiService().recordMistake(
          questionId: q.id,
          universityId: widget.track.universityId,
          level: widget.track.level,
          category: 'Listening',
          wrongAnswer: chosen,
        );
      }
    }

    setState(() {
      _isSubmitted = true;
      _score = ((correctCount / widget.track.questions.length) * 100).round();
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Dinleme Sınavı Tamamlandı! Skor: $_score% ($correctCount / ${widget.track.questions.length})'),
        backgroundColor: _score >= 65 ? AppTheme.accentEmerald : AppTheme.accentRose,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final t = widget.track;
    final isNoteTaking = t.type == 'note_taking';

    return Scaffold(
      backgroundColor: AppTheme.surfaceBg,
      appBar: AppBar(
        title: Text(t.title),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Audio Player Card
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0F172A), Color(0xFF1E1B4B)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(22),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.2),
                  blurRadius: 12,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    InkWell(
                      onTap: _toggleAudio,
                      borderRadius: BorderRadius.circular(16),
                      child: Container(
                        width: 52,
                        height: 52,
                        decoration: BoxDecoration(
                          color: _isPlaying ? AppTheme.accentAmber : AppTheme.brandBlue,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Icon(
                          _isPlaying ? Icons.pause : Icons.play_arrow,
                          color: Colors.white,
                          size: 28,
                        ),
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Akademik Dinleme Kaydı',
                            style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.blueAccent),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            t.subtitle,
                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Colors.white),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 2),
                          Text(
                            _isPlaying ? '▶ Dinleniyor... Notlarınızı alın' : (_playbackProgress >= 1.0 ? '✓ Dinleme Bitti' : 'Oynatmak için dokunun'),
                            style: TextStyle(fontSize: 11, color: _isPlaying ? Colors.amberAccent : Colors.white60),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // Progress Bar
                LinearProgressIndicator(
                  value: _playbackProgress,
                  backgroundColor: Colors.white12,
                  valueColor: AlwaysStoppedAnimation<Color>(_isPlaying ? AppTheme.accentAmber : AppTheme.brandBlue),
                  minHeight: 6,
                  borderRadius: BorderRadius.circular(3),
                ),
                const SizedBox(height: 10),

                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Süre: ~${(t.lectureDurationSeconds * (1 - _playbackProgress)).round()} sn kaldı',
                      style: const TextStyle(fontSize: 11, color: Colors.white60),
                    ),
                    Row(
                      children: [
                        const Text('Hız: ', style: TextStyle(fontSize: 11, color: Colors.white60)),
                        _speedChip(0.85),
                        const SizedBox(width: 4),
                        _speedChip(1.0),
                        const SizedBox(width: 4),
                        _speedChip(1.15),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Note Taking Sheet
          if (isNoteTaking) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.amber.shade50.withValues(alpha: 0.5),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.amber.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.edit_note, size: 18, color: Colors.amber.shade900),
                          const SizedBox(width: 6),
                          Text(
                            'Dijital Not Defteriniz',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Colors.amber.shade900),
                          ),
                        ],
                      ),
                      const Text(
                        '💡 Kısaltmalar kullanın',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _notesController,
                    maxLines: 5,
                    style: const TextStyle(fontSize: 12, height: 1.4),
                    decoration: InputDecoration(
                      hintText: 'Örn:\n- Confirmation bias: Peter Wason 1960\n- Framing effect: Kahneman & Tversky (%90 survival vs %10 mortality)...',
                      hintStyle: TextStyle(fontSize: 11, color: Colors.grey.shade400),
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.amber.shade200),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

            if (!_questionsRevealed)
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.amber.shade300, width: 1.5),
                ),
                child: Column(
                  children: [
                    const Icon(Icons.lock, size: 32, color: Colors.amber),
                    const SizedBox(height: 8),
                    const Text(
                      'Sorular Şu Anda Gizli',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Boğaziçi ve ODTÜ sınavlarında dinleme bitene kadar sorular verilmez. Notlarınızı aldıktan sonra soruları açın.',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                    ),
                    const SizedBox(height: 14),
                    ElevatedButton.icon(
                      onPressed: _revealQuestions,
                      icon: const Icon(Icons.lock_open, size: 16),
                      label: const Text('Dinlemeyi Bitir ve Soruları Aç'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.amber.shade800,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                      ),
                    ),
                  ],
                ),
              ),
          ],

          // Questions List
          if (_questionsRevealed) ...[
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Sorular (${t.questions.length})',
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                ),
                if (_isSubmitted)
                  Text(
                    'Skor: $_score%',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w900,
                      color: _score >= 65 ? AppTheme.accentEmerald : AppTheme.accentRose,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),

            ...t.questions.asMap().entries.map((entry) {
              final idx = entry.key;
              final q = entry.value;
              final chosen = _answers[q.id];

              return Container(
                margin: const EdgeInsets.only(bottom: 14),
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
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          width: 22,
                          height: 22,
                          decoration: BoxDecoration(
                            color: AppTheme.brandBlue,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Center(
                            child: Text(
                              '${idx + 1}',
                              style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w800),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            q.question,
                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.brandNavy),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    ...q.options.map((opt) {
                      final isSelected = chosen == opt.key;
                      Color bg = Colors.grey.shade50;
                      Color border = AppTheme.borderSubtle;
                      Color textCol = AppTheme.brandNavy;

                      if (_isSubmitted) {
                        if (opt.key == q.correctAnswer) {
                          bg = Colors.green.shade50;
                          border = AppTheme.accentEmerald;
                          textCol = Colors.green.shade900;
                        } else if (isSelected && opt.key != q.correctAnswer) {
                          bg = Colors.red.shade50;
                          border = AppTheme.accentRose;
                          textCol = Colors.red.shade900;
                        }
                      } else if (isSelected) {
                        bg = AppTheme.brandLightBlue;
                        border = AppTheme.brandBlue;
                        textCol = AppTheme.brandBlue;
                      }

                      return Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: InkWell(
                          onTap: _isSubmitted
                              ? null
                              : () {
                                  setState(() {
                                    _answers[q.id] = opt.key;
                                  });
                                },
                          borderRadius: BorderRadius.circular(10),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: BoxDecoration(
                              color: bg,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: border, width: isSelected ? 1.5 : 1),
                            ),
                            child: Row(
                              children: [
                                Text('${opt.key}) ', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 12)),
                                Expanded(child: Text(opt.text, style: TextStyle(fontSize: 12, color: textCol))),
                              ],
                            ),
                          ),
                        ),
                      );
                    }),

                    if (_isSubmitted) ...[
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppTheme.brandLightBlue,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '✓ Doğru Cevap: ${q.correctAnswer}',
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.accentEmerald),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              q.explanationTr,
                              style: const TextStyle(fontSize: 11, color: AppTheme.brandNavy, height: 1.3),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              );
            }),

            if (!_isSubmitted)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: ElevatedButton.icon(
                  onPressed: _submitExam,
                  icon: const Icon(Icons.check_circle, size: 18),
                  label: const Text('Cevapları Gönder & Puanla'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.accentEmerald,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
          ],
        ],
      ),
    );
  }

  Widget _speedChip(double rate) {
    final isSel = _playbackRate == rate;
    return InkWell(
      onTap: () {
        setState(() => _playbackRate = rate);
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(
          color: isSel ? AppTheme.brandBlue : Colors.white12,
          borderRadius: BorderRadius.circular(6),
        ),
        child: Text(
          '${rate}x',
          style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: isSel ? Colors.white : Colors.white70),
        ),
      ),
    );
  }
}
