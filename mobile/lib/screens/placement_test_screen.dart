import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/question.dart';
import '../services/placement_test.dart';
import '../theme/app_theme.dart';

/// Seviye tespit sınavı: A1'den C2'ye uyarlamalı, internet gerektirmez.
/// Sonunda önerilen kur gösterilir ve istenirse çalışma kuru olarak ayarlanır.
class PlacementTestScreen extends StatefulWidget {
  final String currentLevel;
  final void Function(String level) onApplyLevel;

  /// Testler için: verilirse uygulama içi havuz yerine bu sorular kullanılır.
  final Map<String, List<Question>>? pool;

  const PlacementTestScreen({
    super.key,
    required this.currentLevel,
    required this.onApplyLevel,
    this.pool,
  });

  static const prefLevel = 'placement_level';
  static const prefMastered = 'placement_mastered';
  static const prefDate = 'placement_date';

  @override
  State<PlacementTestScreen> createState() => _PlacementTestScreenState();
}

enum _Stage { intro, question, result }

class _PlacementTestScreenState extends State<PlacementTestScreen> {
  _Stage _stage = _Stage.intro;
  PlacementEngine? _engine;
  bool _loading = false;
  bool _applied = false;

  Future<void> _start() async {
    setState(() => _loading = true);
    Map<String, List<Question>> pool;
    try {
      pool = widget.pool ?? await PlacementEngine.loadPool();
    } catch (_) {
      pool = const {};
    }
    if (!mounted) return;
    final engine = PlacementEngine(pool);
    setState(() {
      _loading = false;
      _engine = engine;
      _applied = false;
      _stage = engine.isFinished ? _Stage.result : _Stage.question;
    });
    if (engine.isFinished) await _saveResult(engine);
  }

  Future<void> _answer(String key) async {
    final engine = _engine!;
    engine.answer(key);
    if (engine.isFinished) {
      await _saveResult(engine);
      if (!mounted) return;
      setState(() => _stage = _Stage.result);
    } else {
      setState(() {});
    }
  }

  Future<void> _saveResult(PlacementEngine engine) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      PlacementTestScreen.prefLevel,
      engine.recommendedLevel,
    );
    await prefs.setString(
      PlacementTestScreen.prefMastered,
      engine.masteredLevel ?? 'none',
    );
    await prefs.setString(
      PlacementTestScreen.prefDate,
      DateTime.now().toIso8601String(),
    );
  }

  Future<bool> _confirmExit() async {
    if (_stage != _Stage.question) return true;
    final leave = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Sınavdan çıkılsın mı?'),
        content: const Text('Cevapların kaydedilmeyecek.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Devam et'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Çık'),
          ),
        ],
      ),
    );
    return leave ?? false;
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: _stage != _Stage.question,
      onPopInvokedWithResult: (didPop, _) async {
        if (didPop) return;
        final navigator = Navigator.of(context);
        if (await _confirmExit()) navigator.pop();
      },
      child: Scaffold(
        appBar: AppBar(title: const Text('Seviye Tespit Sınavı')),
        body: SafeArea(
          child: switch (_stage) {
            _Stage.intro => _buildIntro(),
            _Stage.question => _buildQuestion(),
            _Stage.result => _buildResult(),
          },
        ),
      ),
    );
  }

  Widget _buildIntro() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Icon(
            Icons.insights_rounded,
            size: 56,
            color: AppTheme.brandBlue,
          ),
          const SizedBox(height: 12),
          const Text(
            'Seviyeni 5 dakikada öğren',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 8),
          const Text(
            'Sınav A1\'den başlar ve sen doğru cevapladıkça zorlaşır. Her kurda en '
            'fazla ${PlacementEngine.perLevel} soru sorulur; ${PlacementEngine.passMark} '
            'doğru yapınca bir üst kura geçersin. Zorlandığın kurda sınav biter.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              height: 1.4,
              color: AppTheme.textMuted,
            ),
          ),
          const SizedBox(height: 16),
          _infoRow(Icons.format_list_numbered_rounded, 'En fazla 24 soru'),
          _infoRow(Icons.timer_outlined, 'Süre sınırı yok, acele etme'),
          _infoRow(Icons.wifi_off_rounded, 'İnternet gerekmez'),
          _infoRow(
            Icons.school_outlined,
            'Sonunda önerilen çalışma kurunu görürsün',
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            key: const Key('placement_begin'),
            onPressed: _loading ? null : _start,
            icon: _loading
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.play_arrow_rounded),
            label: const Text('Sınava başla'),
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
        ],
      ),
    );
  }

  Widget _infoRow(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppTheme.brandBlue),
          const SizedBox(width: 10),
          Expanded(child: Text(text, style: const TextStyle(fontSize: 14))),
        ],
      ),
    );
  }

  Widget _buildQuestion() {
    final engine = _engine!;
    final q = engine.current!;
    final r = engine.results[engine.currentLevel]!;
    final progress = engine.maxQuestions == 0
        ? 0.0
        : engine.answeredCount / engine.maxQuestions;
    return SingleChildScrollView(
      key: ValueKey(q.id),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: AppTheme.brandBlue,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Kur ${engine.currentLevel}',
                  key: const Key('placement_level_badge'),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w800,
                    fontSize: 12,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Bu kurda soru ${r.answered + 1} • Toplam ${engine.answeredCount + 1}',
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppTheme.textMuted,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(value: progress, minHeight: 6),
          ),
          const SizedBox(height: 18),
          Text(
            q.question,
            key: const Key('placement_question'),
            style: const TextStyle(
              fontSize: 16,
              height: 1.45,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 18),
          for (final o in q.options)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: OutlinedButton(
                key: Key('placement_opt_${o.key}'),
                onPressed: () => _answer(o.key),
                style: OutlinedButton.styleFrom(
                  alignment: Alignment.centerLeft,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 12,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${o.key})',
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(o.text, style: const TextStyle(height: 1.35)),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildResult() {
    final engine = _engine!;
    final mastered = engine.masteredLevel;
    final rec = engine.recommendedLevel;
    final noQuestions = engine.maxQuestions == 0;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1E3A8A), Color(0xFF1E1B4B)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(18),
            ),
            child: Column(
              children: [
                const Text(
                  'Önerilen çalışma kurun',
                  style: TextStyle(color: Colors.white70, fontSize: 13),
                ),
                const SizedBox(height: 6),
                Text(
                  rec,
                  key: const Key('placement_recommended'),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 44,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  noQuestions
                      ? 'Soru havuzu yüklenemedi; kurunu elle seçebilirsin.'
                      : mastered == null
                      ? 'A1 sorularında zorlandın; temelden başlamak en iyisi.'
                      : mastered == 'C2'
                      ? 'Tüm kurları geçtin! C2 ile pratiğe devam et.'
                      : '$mastered kurunu geçtin, $rec kurunda zorlandın.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    height: 1.35,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${engine.answeredCount} sorudan ${engine.correctCount} doğru',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          const Text(
            'Kur kur sonuçların',
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 8),
          for (final l in placementLevels) _levelRow(engine.results[l]!),
          const SizedBox(height: 20),
          if (rec != widget.currentLevel && !_applied)
            FilledButton.icon(
              key: const Key('placement_apply'),
              onPressed: () {
                widget.onApplyLevel(rec);
                setState(() => _applied = true);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Çalışma kurun $rec olarak ayarlandı.'),
                  ),
                );
              },
              icon: const Icon(Icons.check_rounded),
              label: Text('Çalışma kurumu $rec yap'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            )
          else
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.accentEmerald.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                'Çalışma kurun zaten $rec.',
                key: const Key('placement_level_set'),
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: AppTheme.accentEmerald,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  key: const Key('placement_retry'),
                  onPressed: _start,
                  child: const Text('Tekrar çöz'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton(
                  key: const Key('placement_close'),
                  onPressed: () => Navigator.of(context).maybePop(),
                  child: const Text('Kapat'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _levelRow(PlacementLevelResult r) {
    final (IconData icon, Color color, String label) = switch (r.passed) {
      true => (Icons.check_circle_rounded, AppTheme.accentEmerald, 'Geçti'),
      false => (Icons.cancel_rounded, AppTheme.accentRose, 'Zorlandın'),
      null => (
        Icons.remove_circle_outline_rounded,
        AppTheme.textMuted,
        'Sorulmadı',
      ),
    };
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          SizedBox(
            width: 34,
            child: Text(
              r.level,
              style: const TextStyle(fontWeight: FontWeight.w800),
            ),
          ),
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(label, style: TextStyle(color: color)),
          ),
          if (r.answered > 0)
            Text(
              '${r.correct}/${r.answered}',
              style: const TextStyle(color: AppTheme.textMuted, fontSize: 13),
            ),
        ],
      ),
    );
  }
}
