import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../models/writing_guide.dart';
import '../models/essay_evaluation_result.dart';
import '../services/api_service.dart';
import '../services/essay_import_service.dart';
import '../theme/app_theme.dart';
import '../widgets/level_selector.dart';

class WritingScreen extends StatefulWidget {
  final String currentLevel;
  const WritingScreen({super.key, this.currentLevel = 'B2'});

  @override
  State<WritingScreen> createState() => _WritingScreenState();
}

class _WritingScreenState extends State<WritingScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<WritingGuide> _guides = [];
  bool _isLoading = true;
  late String _selectedLevel;

  // AI Evaluation State
  final TextEditingController _essayController = TextEditingController();
  int _wordCount = 0;
  bool _isEvaluating = false;
  EssayEvaluationResult? _evalResult;

  // Dosyadan yükleme (yalnızca fotoğraf veya PDF)
  bool _importing = false;
  String? _importNote;
  bool _importNoteIsError = false;

  final List<Map<String, String>> _prompts = [
    {
      'id': 'boun_p1',
      'uni': 'Boğaziçi BUEPT',
      'title': 'AI in Medicine: Benefits vs Ethical Dilemmas',
      'desc': 'Some argue that autonomous AI diagnostics undermine human clinical care, while others claim their efficiency saves lives. Discuss both views and state your opinion.',
    },
    {
      'id': 'itu_p1',
      'uni': 'İTÜ Proficiency',
      'title': 'Transition to Renewable Energy: Causes and Impacts',
      'desc': 'Explain the fundamental causes driving the global shift from fossil fuels to renewable sources and analyze its potential impact on modern urban engineering.',
    },
    {
      'id': 'metu_p1',
      'uni': 'ODTÜ EPE',
      'title': 'Urban Architecture and Climate Adaptation',
      'desc': 'To what extent can bioclimatic urban architecture and green roofs mitigate the severe effects of urban heat islands in developing megacities?',
    },
    {
      'id': 'custom',
      'uni': 'Serbest Konu',
      'title': 'Kendi Belirlediğiniz Bir Konuda Essay Yazın',
      'desc': 'Sınavınızda çıkabilecek herhangi bir kompozisyon konusunu yazarak yapay zekaya puanlatın.',
    },
  ];

  late Map<String, String> _selectedPrompt;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _selectedPrompt = _prompts.first;
    _selectedLevel = widget.currentLevel;
    _loadGuides();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _essayController.dispose();
    super.dispose();
  }

  Future<void> _loadGuides({String? level}) async {
    setState(() => _isLoading = true);
    final targetLvl = level ?? _selectedLevel;
    final list = await ApiService().getWritingGuides(level: targetLvl);
    if (mounted) {
      setState(() {
        _guides = list;
        _isLoading = false;
      });
    }
  }

  void _onEssayChanged(String val) {
    final words = RegExp(r"\b[A-Za-z0-9'-]+\b").allMatches(val.trim());
    setState(() {
      _wordCount = words.length;
    });
  }

  void _setImportNote(String? note, {bool error = false}) {
    if (!mounted) return;
    setState(() {
      _importNote = note;
      _importNoteIsError = error;
    });
  }

  Future<void> _chooseEssaySource() async {
    final choice = await showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.fromLTRB(20, 0, 20, 8),
              child: Text(
                'Yalnızca fotoğraf (JPG, PNG, WEBP) veya PDF, en fazla 10 MB.',
                style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
              ),
            ),
            ListTile(
              key: const Key('essay_src_camera'),
              leading: const Icon(Icons.photo_camera_outlined),
              title: const Text('Fotoğraf çek'),
              onTap: () => Navigator.pop(ctx, 'camera'),
            ),
            ListTile(
              key: const Key('essay_src_gallery'),
              leading: const Icon(Icons.photo_library_outlined),
              title: const Text('Galeriden fotoğraf seç'),
              onTap: () => Navigator.pop(ctx, 'gallery'),
            ),
            ListTile(
              key: const Key('essay_src_pdf'),
              leading: const Icon(Icons.picture_as_pdf_outlined),
              title: const Text('PDF seç'),
              onTap: () => Navigator.pop(ctx, 'pdf'),
            ),
          ],
        ),
      ),
    );
    if (choice == null) return;
    await _importEssay(choice);
  }

  Future<void> _importEssay(String source) async {
    setState(() => _importing = true);
    _setImportNote(null);
    try {
      Uint8List bytes;
      String name;
      String? path;
      if (source == 'pdf') {
        final f = await FilePicker.pickFile(
          type: FileType.custom,
          allowedExtensions: EssayImportService.allowedExtensions,
        );
        if (f == null) return;
        bytes = await f.readAsBytes();
        name = f.name;
        path = f.path;
      } else {
        final x = await ImagePicker().pickImage(
          source: source == 'camera' ? ImageSource.camera : ImageSource.gallery,
          maxWidth: 2400,
          imageQuality: 90,
        );
        if (x == null) return;
        bytes = await x.readAsBytes();
        name = x.name;
        path = x.path;
      }
      if (bytes.length > EssayImportService.maxBytes) {
        _setImportNote('Dosya en fazla 10 MB olabilir.', error: true);
        return;
      }
      final kind = EssayImportService.detectKind(
        bytes.sublist(0, bytes.length < 12 ? bytes.length : 12),
      );
      if (kind == null) {
        _setImportNote(EssayImportService.onlyPhotoOrPdf, error: true);
        return;
      }
      _setImportNote(kind == EssayFileKind.pdf ? '$name okunuyor...' : '$name: yazı okunuyor...');
      String text;
      if (kind == EssayFileKind.pdf) {
        text = await EssayImportService.extractPdf(bytes, name);
      } else {
        if (path == null) throw EssayImportException('Fotoğraf açılamadı.');
        text = await EssayImportService.recognizeImage(path);
      }
      _essayController.text = text;
      _onEssayChanged(text);
      final words = EssayImportService.countWords(text);
      _setImportNote(
        kind == EssayFileKind.pdf
            ? '$name: $words kelime okundu. Metni kontrol edip analiz et.'
            : '$name: $words kelime okundu. El yazısında tanıma hataları olabilir; metni kontrol edip düzelttikten sonra analiz et.',
      );
    } on EssayImportException catch (e) {
      _setImportNote(e.message, error: true);
    } catch (_) {
      _setImportNote('Dosya okunamadı. Başka bir dosya deneyin ya da metni kutuya yazın.', error: true);
    } finally {
      if (mounted) setState(() => _importing = false);
    }
  }

  Future<void> _evaluateEssay() async {
    final text = _essayController.text.trim();
    if (text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Lütfen önce bir essay metni girin.')),
      );
      return;
    }

    setState(() => _isEvaluating = true);

    try {
      final result = await ApiService().evaluateEssay(
        essay: text,
        prompt: _selectedPrompt['desc'],
        universityId: 'itu',
        level: 'B2',
      );

      if (mounted) {
        setState(() {
          _evalResult = result;
          _isEvaluating = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() => _isEvaluating = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Değerlendirme sırasında bir hata oluştu.'),
          ),
        );
      }
    }
  }

  Widget _buildImportBox() {
    return Container(
      key: const Key('essay_import_box'),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.upload_file, size: 20, color: AppTheme.brandBlue),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  "Kağıda yazdın mı? Fotoğrafını veya PDF'ini yükle",
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                ),
              ),
              const SizedBox(width: 8),
              OutlinedButton(
                key: const Key('essay_upload_button'),
                onPressed: _importing ? null : _chooseEssaySource,
                child: _importing
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('Yükle'),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const Text(
            'Yalnızca fotoğraf (JPG, PNG, WEBP) veya PDF. Fotoğraf telefonunda okunur, sunucuya gönderilmez.',
            style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
          ),
          if (_importNote != null) ...[
            const SizedBox(height: 8),
            Text(
              _importNote!,
              key: const Key('essay_import_note'),
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: _importNoteIsError ? Colors.red.shade700 : AppTheme.accentEmerald,
              ),
            ),
          ],
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceBg,
      appBar: AppBar(
        title: const Text('Writing & Essay Platformu'),
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          indicatorColor: AppTheme.accentEmerald,
          indicatorWeight: 3,
          tabs: const [
            Tab(
              icon: Icon(Icons.auto_awesome, size: 18),
              text: 'AI Essay Puanlama',
            ),
            Tab(
              icon: Icon(Icons.menu_book, size: 18),
              text: 'Rehber & Şablonlar',
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [_buildAIEvaluatorTab(), _buildGuidesTab()],
      ),
    );
  }

  // --- TAB 1: AI ESSAY EVALUATOR ---
  Widget _buildAIEvaluatorTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Hero Intro
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF065F46), Color(0xFF022C22)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(22),
            boxShadow: [
              BoxShadow(
                color: AppTheme.sageSwatch.withValues(alpha: 0.3),
                blurRadius: 14,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: AppTheme.sageSwatch.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.psychology, size: 14, color: Colors.white),
                    SizedBox(width: 4),
                    Text(
                      'Yapay Zeka Destekli',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Akıllı Essay Değerlendirici',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w900,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'Kompozisyonunuzu hazırlık muafiyet kriterlerine (Task, Cohesion, Lexical, Grammar) göre anında puanlatın.',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.white70,
                  height: 1.3,
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Prompt Selector
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.borderSubtle),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '1. Hedef Sınav Konusu Seçin:',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  color: AppTheme.brandNavy,
                ),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: _selectedPrompt['id'],
                isExpanded: true,
                decoration: InputDecoration(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 10,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  fillColor: Colors.grey.shade50,
                  filled: true,
                ),
                items: _prompts.map((p) {
                  return DropdownMenuItem<String>(
                    value: p['id'],
                    child: Text(
                      '[${p['uni']}] ${p['title']}',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                }).toList(),
                onChanged: (val) {
                  setState(() {
                    _selectedPrompt = _prompts.firstWhere(
                      (p) => p['id'] == val,
                    );
                  });
                },
              ),
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.brandSwatch.shade50.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppTheme.brandSwatch.shade100),
                ),
                child: Text(
                  _selectedPrompt['desc']!,
                  style: const TextStyle(
                    fontSize: 11,
                    fontStyle: FontStyle.italic,
                    color: AppTheme.brandNavy,
                    height: 1.3,
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Essay Input Field
        Container(
          padding: const EdgeInsets.all(16),
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
                  const Expanded(
                    child: Text(
                      '2. Kompozisyonunuzu Yazın:',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.brandNavy,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: _wordCount >= 250
                          ? Colors.green.shade50
                          : Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: _wordCount >= 250
                            ? AppTheme.accentEmerald
                            : AppTheme.borderSubtle,
                      ),
                    ),
                    child: Text(
                      '$_wordCount / 250 kelime',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: _wordCount >= 250
                            ? AppTheme.accentEmerald
                            : AppTheme.textMuted,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              _buildImportBox(),
              const SizedBox(height: 10),
              TextField(
                controller: _essayController,
                onChanged: _onEssayChanged,
                maxLines: 10,
                style: const TextStyle(
                  fontSize: 13,
                  height: 1.5,
                  fontFamily: 'serif',
                ),
                decoration: InputDecoration(
                  hintText: 'Write your essay here with clear paragraphs (Introduction, Body 1, Body 2, Conclusion)...',
                  hintStyle: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade400,
                  ),
                  filled: true,
                  fillColor: Colors.grey.shade50,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isEvaluating ? null : _evaluateEssay,
                  icon: _isEvaluating
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.psychology, size: 18),
                  label: Text(
                    _isEvaluating
                        ? 'Analiz Ediliyor...'
                        : 'Yapay Zeka ile Analiz Et',
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.brandBlue,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
            ],
          ),
        ),

        // Evaluation Results
        if (_evalResult != null) ...[
          const SizedBox(height: 16),
          _buildEvaluationResultCard(_evalResult!),
        ],

        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildEvaluationResultCard(EssayEvaluationResult r) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(
          color: r.isPassing ? AppTheme.accentEmerald : AppTheme.accentRose,
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: (r.isPassing ? AppTheme.accentEmerald : AppTheme.accentRose)
                .withValues(alpha: 0.1),
            blurRadius: 14,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Banner
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: r.isPassing
                    ? [const Color(0xFF065F46), const Color(0xFF047857)]
                    : [const Color(0xFF881337), const Color(0xFFBE123C)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      r.isPassing
                          ? '✓ Muafiyet Barajını Geçti'
                          : '⚠️ Barajın Altında Kaldı',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Puan: ${r.overallScore} / 100',
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      'Tahmini CEFR: ${r.estimatedCefr}',
                      style: const TextStyle(
                        fontSize: 11,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
                Text(
                  '${r.wordCount} Kelime',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // 4 Criteria Breakdown
          const Text(
            'Kriter Puan Dağılımı',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w800,
              color: AppTheme.brandNavy,
            ),
          ),
          const SizedBox(height: 8),

          Row(
            children: [
              _criteriaBox('Task Response', '${r.taskAchievementScore}/25'),
              const SizedBox(width: 8),
              _criteriaBox('Cohesion', '${r.coherenceCohesionScore}/25'),
              const SizedBox(width: 8),
              _criteriaBox('Vocabulary', '${r.lexicalResourceScore}/25'),
              const SizedBox(width: 8),
              _criteriaBox('Grammar', '${r.grammaticalRangeScore}/25'),
            ],
          ),

          const SizedBox(height: 16),

          // Detected transitions
          if (r.detectedTransitions.isNotEmpty) ...[
            const Text(
              'Tespit Edilen Geçiş Bağlaçları:',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                color: AppTheme.brandBlue,
              ),
            ),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: r.detectedTransitions.map((t) {
                return Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 3,
                  ),
                  decoration: BoxDecoration(
                    color: AppTheme.brandSwatch.shade50,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: AppTheme.brandSwatch.shade200),
                  ),
                  child: Text(
                    t,
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.brandBlue,
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 12),
          ],

          // Strengths
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.green.shade50.withValues(alpha: 0.6),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.green.shade200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.check, size: 14, color: AppTheme.accentEmerald),
                    SizedBox(width: 4),
                    Text(
                      'Güçlü Yönleriniz:',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.accentEmerald,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                ...r.strengthsTr.map(
                  (s) => Text(
                    '• $s',
                    style: const TextStyle(
                      fontSize: 11,
                      color: AppTheme.brandNavy,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 10),

          // Improvements
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.amber.shade50.withValues(alpha: 0.6),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.amber.shade200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.lightbulb_outline,
                      size: 14,
                      color: Colors.amber.shade900,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Geliştirme Tavsiyeleri:',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: Colors.amber.shade900,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                ...r.improvementsTr.map(
                  (imp) => Text(
                    '• $imp',
                    style: const TextStyle(
                      fontSize: 11,
                      color: AppTheme.brandNavy,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _criteriaBox(String title, String score) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: Colors.grey.shade50,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: AppTheme.borderSubtle),
        ),
        child: Column(
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 9,
                fontWeight: FontWeight.w700,
                color: AppTheme.textMuted,
              ),
              maxLines: 1,
            ),
            const SizedBox(height: 2),
            Text(
              score,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w900,
                color: AppTheme.brandNavy,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // --- TAB 2: GUIDES LIST ---
  Widget _buildGuidesTab() {
    if (_isLoading) return const Center(child: CircularProgressIndicator());

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Level Filter Chips
        LevelSelector(
          selected: _selectedLevel,
          highlight: widget.currentLevel,
          padding: EdgeInsets.zero,
          onSelected: (lvl) {
            setState(() => _selectedLevel = lvl);
            _loadGuides(level: lvl);
          },
        ),
        const SizedBox(height: 16),

        if (_guides.isEmpty)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.borderSubtle),
            ),
            child: Center(
              child: Column(
                children: [
                  const Text(
                    'Bu seviyede yazma rehberi bulunamadı.',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textMuted,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextButton(
                    onPressed: () {
                      setState(() => _selectedLevel = 'all');
                      _loadGuides(level: 'all');
                    },
                    child: const Text('Tüm Yazma Rehberlerini Göster'),
                  ),
                ],
              ),
            ),
          ),

        ..._guides.map((g) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          g.title,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w900,
                            color: AppTheme.brandNavy,
                          ),
                        ),
                      ),
                      if (g.modelBandScore != null)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.green.shade50,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(
                              color: AppTheme.accentEmerald.withValues(
                                alpha: 0.5,
                              ),
                            ),
                          ),
                          child: Text(
                            'Band ${g.modelBandScore} / 100',
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w900,
                              color: AppTheme.accentEmerald,
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    g.description,
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppTheme.textMuted,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 14),

                  const Text(
                    'İDEAL PARAGRAF İSKELETİ',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: AppTheme.brandBlue,
                      letterSpacing: 1,
                    ),
                  ),
                  const SizedBox(height: 8),

                  ...g.structure.map((st) {
                    return Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppTheme.surfaceBg,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AppTheme.borderSubtle),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            st.section,
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w800,
                              color: AppTheme.brandNavy,
                            ),
                          ),
                          const SizedBox(height: 6),
                          ...st.elements.map(
                            (el) => Padding(
                              padding: const EdgeInsets.only(bottom: 2),
                              child: Text(
                                '• $el',
                                style: const TextStyle(
                                  fontSize: 11,
                                  color: AppTheme.textMuted,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),

                  // Key Transitions
                  if (g.keyTransitions.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    const Text(
                      'ÖNERİLEN GEÇİŞ BAĞLAÇLARI',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.brandBlue,
                        letterSpacing: 1,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: g.keyTransitions
                          .map(
                            (tr) => Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 9,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: AppTheme.brandSwatch.shade50,
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: AppTheme.brandSwatch.shade200),
                              ),
                              child: Text(
                                tr,
                                style: const TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w700,
                                  color: AppTheme.brandBlue,
                                ),
                              ),
                            ),
                          )
                          .toList(),
                    ),
                  ],

                  // Sample Topic Card
                  if (g.sampleTopic.isNotEmpty) ...[
                    const SizedBox(height: 14),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.amber.shade50.withValues(alpha: 0.6),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: Colors.amber.shade200),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(
                                Icons.assignment_outlined,
                                size: 14,
                                color: Color(0xFFB45309),
                              ),
                              SizedBox(width: 4),
                              Text(
                                'Örnek Sınav Konusu:',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFFB45309),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '"${g.sampleTopic}"',
                            style: const TextStyle(
                              fontSize: 11,
                              fontStyle: FontStyle.italic,
                              color: AppTheme.brandNavy,
                              height: 1.3,
                            ),
                          ),
                          if (g.bandScoreTip != null &&
                              g.bandScoreTip!.isNotEmpty) ...[
                            const SizedBox(height: 6),
                            Text(
                              '💡 İpucu: ${g.bandScoreTip}',
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF92400E),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],

                  // Model Essay Exemplar Card & Expansion
                  if (g.modelEssay != null && g.modelEssay!.isNotEmpty) ...[
                    const SizedBox(height: 14),
                    Theme(
                      data: Theme.of(context)
                          .copyWith(dividerColor: Colors.transparent),
                      child: Container(
                        decoration: BoxDecoration(
                          color: AppTheme.surfaceBg,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: AppTheme.borderSubtle),
                        ),
                        child: ExpansionTile(
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                          collapsedShape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                          tilePadding: const EdgeInsets.symmetric(
                            horizontal: 14,
                            vertical: 2,
                          ),
                          leading: const Icon(
                            Icons.menu_book,
                            color: AppTheme.brandBlue,
                            size: 20,
                          ),
                          title: Text(
                            'Band ${g.modelBandScore ?? 90}+ Model Essay & Hata Analizi',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w800,
                              color: AppTheme.brandNavy,
                            ),
                          ),
                          children: [
                            Padding(
                              padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Divider(height: 1),
                                  const SizedBox(height: 12),
                                  Container(
                                    width: double.infinity,
                                    padding: const EdgeInsets.all(14),
                                    decoration: BoxDecoration(
                                      color: Colors.white,
                                      borderRadius: BorderRadius.circular(12),
                                      border: Border.all(
                                        color: AppTheme.borderSubtle,
                                      ),
                                    ),
                                    child: Text(
                                      g.modelEssay!,
                                      style: const TextStyle(
                                        fontSize: 12,
                                        height: 1.6,
                                        fontFamily: 'serif',
                                        color: Color(0xFF1E293B),
                                      ),
                                    ),
                                  ),
                                  if (g.annotatedStrengths.isNotEmpty) ...[
                                    const SizedBox(height: 12),
                                    Container(
                                      width: double.infinity,
                                      padding: const EdgeInsets.all(12),
                                      decoration: BoxDecoration(
                                        color: Colors.green.shade50.withValues(
                                          alpha: 0.6,
                                        ),
                                        borderRadius: BorderRadius.circular(12),
                                        border: Border.all(
                                          color: Colors.green.shade200,
                                        ),
                                      ),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          const Row(
                                            children: [
                                              Icon(
                                                Icons.check_circle_outline,
                                                size: 14,
                                                color: AppTheme.accentEmerald,
                                              ),
                                              SizedBox(width: 4),
                                              Text(
                                                'Neden Yüksek Puan Aldı? (Güçlü Yönler):',
                                                style: TextStyle(
                                                  fontSize: 11,
                                                  fontWeight: FontWeight.w800,
                                                  color: AppTheme.accentEmerald,
                                                ),
                                              ),
                                            ],
                                          ),
                                          const SizedBox(height: 6),
                                          ...g.annotatedStrengths.map(
                                            (str) => Padding(
                                              padding: const EdgeInsets.only(
                                                bottom: 2,
                                              ),
                                              child: Text(
                                                '• $str',
                                                style: const TextStyle(
                                                  fontSize: 11,
                                                  color: AppTheme.brandNavy,
                                                ),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                  if (g.commonPitfalls.isNotEmpty) ...[
                                    const SizedBox(height: 10),
                                    Container(
                                      width: double.infinity,
                                      padding: const EdgeInsets.all(12),
                                      decoration: BoxDecoration(
                                        color: Colors.red.shade50.withValues(
                                          alpha: 0.6,
                                        ),
                                        borderRadius: BorderRadius.circular(12),
                                        border: Border.all(
                                          color: Colors.red.shade200,
                                        ),
                                      ),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Row(
                                            children: [
                                              Icon(
                                                Icons.warning_amber_rounded,
                                                size: 14,
                                                color: Colors.red.shade800,
                                              ),
                                              const SizedBox(width: 4),
                                              Text(
                                                'Sık Yapılan Hatalar (Puan Kırdıran Noktalar):',
                                                style: TextStyle(
                                                  fontSize: 11,
                                                  fontWeight: FontWeight.w800,
                                                  color: Colors.red.shade800,
                                                ),
                                              ),
                                            ],
                                          ),
                                          const SizedBox(height: 6),
                                          ...g.commonPitfalls.map(
                                            (pit) => Padding(
                                              padding: const EdgeInsets.only(
                                                bottom: 2,
                                              ),
                                              child: Text(
                                                '• $pit',
                                                style: const TextStyle(
                                                  fontSize: 11,
                                                  color: AppTheme.brandNavy,
                                                ),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          );
        }),
      ],
    );
  }
}
