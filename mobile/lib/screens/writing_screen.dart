import 'package:flutter/material.dart';
import '../models/writing_guide.dart';
import '../models/essay_evaluation_result.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class WritingScreen extends StatefulWidget {
  final String currentLevel;
  const WritingScreen({super.key, this.currentLevel = 'B2'});

  @override
  State<WritingScreen> createState() => _WritingScreenState();
}

class _WritingScreenState extends State<WritingScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<WritingGuide> _guides = [];
  bool _isLoading = true;
  late String _selectedLevel;

  // AI Evaluation State
  final TextEditingController _essayController = TextEditingController();
  int _wordCount = 0;
  bool _isEvaluating = false;
  EssayEvaluationResult? _evalResult;

  final List<Map<String, String>> _prompts = [
    {
      'id': 'boun_p1',
      'uni': 'Boğaziçi BUEPT',
      'title': 'AI in Medicine: Benefits vs Ethical Dilemmas',
      'desc': 'Some argue that autonomous AI diagnostics undermine human clinical care, while others claim their efficiency saves lives. Discuss both views and state your opinion.'
    },
    {
      'id': 'itu_p1',
      'uni': 'İTÜ Proficiency',
      'title': 'Transition to Renewable Energy: Causes and Impacts',
      'desc': 'Explain the fundamental causes driving the global shift from fossil fuels to renewable sources and analyze its potential impact on modern urban engineering.'
    },
    {
      'id': 'metu_p1',
      'uni': 'ODTÜ EPE',
      'title': 'Urban Architecture and Climate Adaptation',
      'desc': 'To what extent can bioclimatic urban architecture and green roofs mitigate the severe effects of urban heat islands in developing megacities?'
    },
    {
      'id': 'custom',
      'uni': 'Serbest Konu',
      'title': 'Kendi Belirlediğiniz Bir Konuda Essay Yazın',
      'desc': 'Sınavınızda çıkabilecek herhangi bir kompozisyon konusunu yazarak yapay zekaya puanlatın.'
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
          const SnackBar(content: Text('Değerlendirme sırasında bir hata oluştu.')),
        );
      }
    }
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
            Tab(icon: Icon(Icons.auto_awesome, size: 18), text: 'AI Essay Puanlama'),
            Tab(icon: Icon(Icons.menu_book, size: 18), text: 'Rehber & Şablonlar'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildAIEvaluatorTab(),
          _buildGuidesTab(),
        ],
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
              colors: [Color(0xFF312E81), Color(0xFF1E1B4B)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(22),
            boxShadow: [
              BoxShadow(
                color: Colors.indigo.withValues(alpha: 0.3),
                blurRadius: 14,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.indigoAccent.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.psychology, size: 14, color: Colors.white),
                    SizedBox(width: 4),
                    Text(
                      'Yapay Zeka Destekli',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Akıllı Essay Değerlendirici',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Colors.white),
              ),
              const SizedBox(height: 6),
              const Text(
                'Kompozisyonunuzu hazırlık muafiyet kriterlerine (Task, Cohesion, Lexical, Grammar) göre anında puanlatın.',
                style: TextStyle(fontSize: 12, color: Colors.white70, height: 1.3),
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
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: _selectedPrompt['id'],
                isExpanded: true,
                decoration: InputDecoration(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  fillColor: Colors.grey.shade50,
                  filled: true,
                ),
                items: _prompts.map((p) {
                  return DropdownMenuItem<String>(
                    value: p['id'],
                    child: Text(
                      '[${p['uni']}] ${p['title']}',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                }).toList(),
                onChanged: (val) {
                  setState(() {
                    _selectedPrompt = _prompts.firstWhere((p) => p['id'] == val);
                  });
                },
              ),
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue.shade100),
                ),
                child: Text(
                  _selectedPrompt['desc']!,
                  style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: AppTheme.brandNavy, height: 1.3),
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
                  const Text(
                    '2. Kompozisyonunuzu Yazın:',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: _wordCount >= 250 ? Colors.green.shade50 : Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: _wordCount >= 250 ? AppTheme.accentEmerald : AppTheme.borderSubtle,
                      ),
                    ),
                    child: Text(
                      '$_wordCount / 250 kelime',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: _wordCount >= 250 ? AppTheme.accentEmerald : AppTheme.textMuted,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _essayController,
                onChanged: _onEssayChanged,
                maxLines: 10,
                style: const TextStyle(fontSize: 13, height: 1.5, fontFamily: 'serif'),
                decoration: InputDecoration(
                  hintText: 'Write your essay here with clear paragraphs (Introduction, Body 1, Body 2, Conclusion)...',
                  hintStyle: TextStyle(fontSize: 12, color: Colors.grey.shade400),
                  filled: true,
                  fillColor: Colors.grey.shade50,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isEvaluating ? null : _evaluateEssay,
                  icon: _isEvaluating
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.psychology, size: 18),
                  label: Text(_isEvaluating ? 'Analiz Ediliyor...' : 'Yapay Zeka ile Analiz Et'),
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
        border: Border.all(color: r.isPassing ? AppTheme.accentEmerald : AppTheme.accentRose, width: 1.5),
        boxShadow: [
          BoxShadow(
            color: (r.isPassing ? AppTheme.accentEmerald : AppTheme.accentRose).withValues(alpha: 0.1),
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
                      r.isPassing ? '✓ Muafiyet Barajını Geçti' : '⚠️ Barajın Altında Kaldı',
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Puan: ${r.overallScore} / 100',
                      style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Colors.white),
                    ),
                    Text(
                      'Tahmini CEFR: ${r.estimatedCefr}',
                      style: const TextStyle(fontSize: 11, color: Colors.white70),
                    ),
                  ],
                ),
                Text(
                  '${r.wordCount} Kelime',
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Colors.white70),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // 4 Criteria Breakdown
          const Text(
            'Kriter Puan Dağılımı',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
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
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue),
            ),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: r.detectedTransitions.map((t) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: Colors.blue.shade200),
                  ),
                  child: Text(t, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: AppTheme.brandBlue)),
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
                    Text('Güçlü Yönleriniz:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.accentEmerald)),
                  ],
                ),
                const SizedBox(height: 4),
                ...r.strengthsTr.map((s) => Text('• $s', style: const TextStyle(fontSize: 11, color: AppTheme.brandNavy))),
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
                    Icon(Icons.lightbulb_outline, size: 14, color: Colors.amber.shade900),
                    const SizedBox(width: 4),
                    Text('Geliştirme Tavsiyeleri:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.amber.shade900)),
                  ],
                ),
                const SizedBox(height: 4),
                ...r.improvementsTr.map((imp) => Text('• $imp', style: const TextStyle(fontSize: 11, color: AppTheme.brandNavy))),
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
            Text(title, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w700, color: AppTheme.textMuted), maxLines: 1),
            const SizedBox(height: 2),
            Text(score, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: AppTheme.brandNavy)),
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
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: ['A2', 'B1', 'B2', 'C1', 'C2', 'all'].map((lvl) {
              final isSel = _selectedLevel == lvl;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(
                    lvl == 'all' ? 'Tüm Kurlar' : '$lvl ${lvl == widget.currentLevel ? "★" : ""}',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isSel ? Colors.white : AppTheme.textMain,
                    ),
                  ),
                  selected: isSel,
                  selectedColor: AppTheme.brandBlue,
                  backgroundColor: Colors.white,
                  onSelected: (val) {
                    if (val) {
                      setState(() => _selectedLevel = lvl);
                      _loadGuides(level: lvl);
                    }
                  },
                ),
              );
            }).toList(),
          ),
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
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMuted),
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
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: AppTheme.brandNavy),
                      ),
                    ),
                    if (g.modelBandScore != null)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.green.shade50,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: AppTheme.accentEmerald.withValues(alpha: 0.5)),
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
                  style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.4),
                ),
                const SizedBox(height: 14),

                const Text(
                  'İDEAL PARAGRAF İSKELETİ',
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: AppTheme.brandBlue, letterSpacing: 1),
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
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                        ),
                        const SizedBox(height: 6),
                        ...st.elements.map((el) => Padding(
                              padding: const EdgeInsets.only(bottom: 2),
                              child: Text('• $el', style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                            )),
                      ],
                    ),
                  );
                }),

                // Key Transitions
                if (g.keyTransitions.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  const Text(
                    'ÖNERİLEN GEÇİŞ BAĞLAÇLARI',
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: AppTheme.brandBlue, letterSpacing: 1),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: g.keyTransitions.map((tr) => Container(
                      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.blue.shade200),
                      ),
                      child: Text(
                        tr,
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.brandBlue),
                      ),
                    )).toList(),
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
                            Icon(Icons.assignment_outlined, size: 14, color: Color(0xFFB45309)),
                            SizedBox(width: 4),
                            Text(
                              'Örnek Sınav Konusu:',
                              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFB45309)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '"${g.sampleTopic}"',
                          style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: AppTheme.brandNavy, height: 1.3),
                        ),
                        if (g.bandScoreTip != null && g.bandScoreTip!.isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Text(
                            '💡 İpucu: ${g.bandScoreTip}',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF92400E)),
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
                    data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                    child: Container(
                      decoration: BoxDecoration(
                        color: AppTheme.surfaceBg,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppTheme.borderSubtle),
                      ),
                      child: ExpansionTile(
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        collapsedShape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        tilePadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 2),
                        leading: const Icon(Icons.menu_book, color: AppTheme.brandBlue, size: 20),
                        title: Text(
                          'Band ${g.modelBandScore ?? 90}+ Model Essay & Hata Analizi',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
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
                                    border: Border.all(color: AppTheme.borderSubtle),
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
                                      color: Colors.green.shade50.withValues(alpha: 0.6),
                                      borderRadius: BorderRadius.circular(12),
                                      border: Border.all(color: Colors.green.shade200),
                                    ),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Row(
                                          children: [
                                            Icon(Icons.check_circle_outline, size: 14, color: AppTheme.accentEmerald),
                                            SizedBox(width: 4),
                                            Text(
                                              'Neden Yüksek Puan Aldı? (Güçlü Yönler):',
                                              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.accentEmerald),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 6),
                                        ...g.annotatedStrengths.map((str) => Padding(
                                              padding: const EdgeInsets.only(bottom: 2),
                                              child: Text('• $str', style: const TextStyle(fontSize: 11, color: AppTheme.brandNavy)),
                                            )),
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
                                      color: Colors.red.shade50.withValues(alpha: 0.6),
                                      borderRadius: BorderRadius.circular(12),
                                      border: Border.all(color: Colors.red.shade200),
                                    ),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          children: [
                                            Icon(Icons.warning_amber_rounded, size: 14, color: Colors.red.shade800),
                                            const SizedBox(width: 4),
                                            Text(
                                              'Sık Yapılan Hatalar (Puan Kırdıran Noktalar):',
                                              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.red.shade800),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 6),
                                        ...g.commonPitfalls.map((pit) => Padding(
                                              padding: const EdgeInsets.only(bottom: 2),
                                              child: Text('• $pit', style: const TextStyle(fontSize: 11, color: AppTheme.brandNavy)),
                                            )),
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
