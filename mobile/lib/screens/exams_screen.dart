import 'package:flutter/material.dart';

import '../models/university.dart';
import '../models/question.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/panel_widgets.dart';
import 'exam_runner_screen.dart';
import 'listening_screen.dart';
import 'university_paywall_sheet.dart';
import 'student_document_scan_sheet.dart';

/// Okul denemeleri: web ile aynı sade satır listesi, kilit uyarısı, kur ilerlemesi,
/// sınav formatı ve ipuçları.
class ExamsScreen extends StatefulWidget {
  final University currentUniversity;
  final String currentLevel;

  const ExamsScreen({
    super.key,
    required this.currentUniversity,
    required this.currentLevel,
  });

  @override
  State<ExamsScreen> createState() => _ExamsScreenState();
}

class _ExamsScreenState extends State<ExamsScreen> {
  Map<String, dynamic>? _overview;

  University get _uni => widget.currentUniversity;
  String get _level => widget.currentLevel;

  @override
  void initState() {
    super.initState();
    _loadOverview();
  }

  @override
  void didUpdateWidget(covariant ExamsScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.currentLevel != widget.currentLevel ||
        oldWidget.currentUniversity.id != widget.currentUniversity.id) {
      _loadOverview();
    }
  }

  Future<void> _loadOverview() async {
    final overview = await ApiService().getDashboardOverview(level: _level);
    if (mounted) setState(() => _overview = overview);
  }

  /// Erişim yoksa ödeme penceresini açar; varsa true döner.
  Future<bool> _ensureAccess(VoidCallback retry) async {
    final hasAccess = await ApiService().checkUniversityAccess(
      universityId: _uni.id,
    );
    if (!mounted) return false;
    if (!hasAccess) {
      UniversityPaywallSheet.show(
        context,
        universityId: _uni.id,
        universityName: _uni.name,
        onUnlockSuccess: () {
          _loadOverview();
          if (mounted) retry();
        },
      );
      return false;
    }
    return true;
  }

  Future<void> _launchMockExam() async {
    if (!await _ensureAccess(_launchMockExam)) return;
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Resmi muafiyet deneme sınavı hazırlanıyor...'),
        duration: Duration(seconds: 1),
      ),
    );
    final mockData = await ApiService().getMockExam(_uni.id, level: _level);
    final List<Question> questions =
        (mockData['parsed_questions'] as List<dynamic>?)?.cast<Question>() ??
        [];
    _openRunner(questions, _level);
  }

  /// [strict]: yalnız okulun soruları (kur bitirme). Değilse okul (≤30) + genel (≤40'a kadar).
  Future<void> _launchExam({String? category, bool strict = false}) async {
    if (!await _ensureAccess(
      () => _launchExam(category: category, strict: strict),
    )) {
      return;
    }
    final fetched = await ApiService().getQuestions(
      universityId: _uni.id,
      level: _level,
      category: category,
    );
    var schoolQs = fetched.where((q) => q.universityId == _uni.id).toList();
    List<Question> questions;
    if (strict) {
      questions = schoolQs;
    } else {
      if (schoolQs.length > 30) {
        schoolQs.shuffle();
        schoolQs = schoolQs.take(30).toList();
      }
      final otherQs = fetched.where((q) => q.universityId != _uni.id).toList()
        ..shuffle();
      questions = [...schoolQs, ...otherQs.take(40 - schoolQs.length)];
    }
    _openRunner(questions, _level);
  }

  Future<void> _openRunner(List<Question> questions, String level) async {
    if (!mounted) return;
    if (questions.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Bu filtreye uygun soru bulunamadı.')),
      );
      return;
    }
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ExamRunnerScreen(
          questions: questions,
          university: _uni,
          level: level,
        ),
      ),
    );
    _loadOverview();
  }

  String _duration(int questions) {
    final minutes = (questions * 90 / 60).round();
    return minutes >= 60
        ? '~${minutes ~/ 60} sa ${minutes % 60} dk'
        : '~$minutes dk';
  }

  Widget _examRow({
    required String keyName,
    required IconData icon,
    required Color color,
    required String title,
    required String meta,
    required VoidCallback onStart,
    String? badge,
    Map<String, dynamic>? progress,
    bool primary = false,
    bool locked = false,
    bool last = false,
  }) {
    final total = (progress?['total'] as num?)?.toInt() ?? 0;
    final correct = (progress?['correct'] as num?)?.toInt() ?? 0;
    return DecoratedBox(
      decoration: BoxDecoration(
        border: last
            ? null
            : Border(bottom: BorderSide(color: PanelColors.border(context))),
      ),
      child: InkWell(
        key: Key('exam_row_$keyName'),
        onTap: onStart,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, size: 20, color: Colors.white),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        Text(
                          title,
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w800,
                            color: PanelColors.text(context),
                          ),
                        ),
                        if (badge != null)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: AppTheme.brandLightBlue,
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              badge,
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w700,
                                color: AppTheme.brandBlue,
                              ),
                            ),
                          ),
                        if (locked)
                          Icon(
                            Icons.lock_outline,
                            size: 14,
                            color: PanelColors.muted(context),
                          ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      meta,
                      style: TextStyle(
                        fontSize: 12,
                        color: PanelColors.muted(context),
                      ),
                    ),
                    if (total > 0) ...[
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Expanded(
                            child: ProgressLine(
                              value: correct / total,
                              color: color,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            '$correct/$total doğru',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: PanelColors.muted(context),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 8),
              primary
                  ? IconButton.filled(
                      key: Key('exam_start_$keyName'),
                      onPressed: onStart,
                      tooltip: 'Başlat',
                      style: IconButton.styleFrom(
                        backgroundColor: AppTheme.brandBlue,
                      ),
                      icon: const Icon(Icons.play_arrow_rounded),
                    )
                  : IconButton.outlined(
                      key: Key('exam_start_$keyName'),
                      onPressed: onStart,
                      tooltip: 'Başlat',
                      icon: const Icon(Icons.play_arrow_rounded),
                    ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final locked = _overview != null && _overview!['pool'] != 'school';
    Map<String, dynamic>? levelProgress;
    if (_overview != null && !locked) {
      for (final l in (_overview!['levels'] as List<dynamic>? ?? [])) {
        if (l['level'] == _level) levelProgress = l as Map<String, dynamic>;
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Okul Denemeleri'),
        actions: [
          IconButton(
            icon: const Icon(Icons.document_scanner_outlined),
            tooltip: 'Öğrenci Belgesi Doğrula',
            onPressed: () => StudentDocumentScanSheet.show(context),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadOverview,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            PanelCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: [
                      _chip(
                        '${_uni.shortName} · $_level',
                        AppTheme.brandLightBlue,
                        AppTheme.brandBlue,
                      ),
                      _chip(
                        'Baraj %${_uni.passingScore}',
                        const Color(0xFFECFDF5),
                        AppTheme.accentEmerald,
                      ),
                      _chip(
                        '${_uni.durationMinutes} dk',
                        const Color(0xFFF1F5F9),
                        AppTheme.textMuted,
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '${_uni.examName} denemeleri',
                    style: TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w800,
                      color: PanelColors.text(context),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Okulunun sınav formatına göre hazırlanmış denemeler. Kur değiştirmek için Özet sekmesini kullan.',
                    style: TextStyle(
                      fontSize: 12,
                      color: PanelColors.muted(context),
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 10),
            if (locked) ...[
              AlertRow(
                key: const Key('exams_locked'),
                tone: AlertTone.info,
                icon: Icons.lock_outline,
                text:
                    '${_uni.shortName} denemeleri kilitli. Kilidi açınca 204 özgün soru ve tüm denemeler açılır.',
                actionLabel: 'Kilidi aç',
                onTap: () => UniversityPaywallSheet.show(
                  context,
                  universityId: _uni.id,
                  universityName: _uni.name,
                  onUnlockSuccess: _loadOverview,
                ),
              ),
              const SizedBox(height: 10),
            ],
            PanelCard(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              child: Column(
                children: [
                  _examRow(
                    keyName: 'mock',
                    icon: Icons.school_outlined,
                    color: AppTheme.brandBlue,
                    title: '$_level muafiyet denemesi',
                    meta:
                        '30 soru · dinleme · yazma ve konuşma · ${_uni.durationMinutes} dk',
                    badge: 'Önerilen',
                    primary: true,
                    locked: locked,
                    onStart: _launchMockExam,
                  ),
                  _examRow(
                    keyName: 'level',
                    icon: Icons.flag_outlined,
                    color: const Color(0xFF0F6E56),
                    title: '$_level kur bitirme sınavı',
                    meta: '34 soru · ${_duration(34)}',
                    progress: levelProgress,
                    locked: locked,
                    onStart: () => _launchExam(strict: true),
                  ),
                  _examRow(
                    keyName: 'reading',
                    icon: Icons.menu_book_outlined,
                    color: categoryColor('Reading'),
                    title: 'Reading sınavı',
                    meta: 'Okuma parçaları ve çıkarım soruları',
                    locked: locked,
                    onStart: () => _launchExam(category: 'Reading'),
                  ),
                  _examRow(
                    keyName: 'restatement',
                    icon: Icons.repeat,
                    color: categoryColor('Restatement'),
                    title: 'Restatement sınavı',
                    meta: 'Yakın anlamlı cümle soruları',
                    locked: locked,
                    onStart: () => _launchExam(category: 'Restatement'),
                  ),
                  _examRow(
                    keyName: 'grammar',
                    icon: Icons.spellcheck,
                    color: categoryColor('Cloze Test'),
                    title: 'Grammar sınavı',
                    meta: 'Dilbilgisi ve yapı soruları',
                    locked: locked,
                    onStart: () => _launchExam(category: 'Grammar'),
                  ),
                  _examRow(
                    keyName: 'listening',
                    icon: Icons.headphones_outlined,
                    color: categoryColor('Grammar'),
                    title: 'Listening ve not alma',
                    meta: 'Sesli akademik ders ve sorular',
                    last: true,
                    onStart: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ListeningScreen(currentLevel: _level),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            if (_uni.sections.isNotEmpty) ...[
              const SizedBox(height: 12),
              PanelCard(
                key: const Key('exam_format'),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _cardTitle('Sınav formatı'),
                    for (var i = 0; i < _uni.sections.length; i++)
                      ProgressRow(
                        leading: NumberDot(
                          number: i + 1,
                          color: AppTheme.brandBlue,
                        ),
                        title: _uni.sections[i].name,
                        trailingText:
                            '${_uni.sections[i].questionsCount} soru · %${_uni.sections[i].weightPercent}',
                        progress: _uni.sections[i].weightPercent / 100,
                        color: AppTheme.brandBlue,
                        showDivider: i < _uni.sections.length - 1,
                      ),
                  ],
                ),
              ),
            ],
            if (_uni.tips.isNotEmpty) ...[
              const SizedBox(height: 12),
              PanelCard(
                key: const Key('exam_tips'),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _cardTitle('Sınav ipuçları'),
                    for (final tip in _uni.tips)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(
                              Icons.lightbulb_outline,
                              size: 16,
                              color: AppTheme.accentAmber,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                tip,
                                style: TextStyle(
                                  fontSize: 12,
                                  height: 1.4,
                                  color: PanelColors.muted(context),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _cardTitle(String text) => Padding(
    padding: const EdgeInsets.only(bottom: 4),
    child: Text(
      text,
      style: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w800,
        color: PanelColors.text(context),
      ),
    ),
  );

  Widget _chip(String text, Color bg, Color fg) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(
      color: bg,
      borderRadius: BorderRadius.circular(6),
    ),
    child: Text(
      text,
      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: fg),
    ),
  );
}
