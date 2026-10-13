import 'dart:math';
import 'package:flutter/material.dart';
import '../models/vocabulary.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class FlashcardsScreen extends StatefulWidget {
  final String currentLevel;

  const FlashcardsScreen({super.key, required this.currentLevel});

  @override
  State<FlashcardsScreen> createState() => _FlashcardsScreenState();
}

class _FlashcardsScreenState extends State<FlashcardsScreen>
    with SingleTickerProviderStateMixin {
  late String _selectedLevel;
  List<VocabularyItem> _vocabList = [];
  int _currentIndex = 0;
  bool _isLoading = true;

  late AnimationController _flipController;
  late Animation<double> _flipAnimation;
  bool _isFlipped = false;

  @override
  void initState() {
    super.initState();
    _selectedLevel = widget.currentLevel;

    _flipController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    _flipAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _flipController, curve: Curves.easeInOut),
    );

    _loadVocab();
  }

  Future<void> _loadVocab() async {
    setState(() => _isLoading = true);
    final list = await ApiService().getVocabulary(level: _selectedLevel);
    if (mounted) {
      setState(() {
        _vocabList = list;
        _currentIndex = 0;
        _isFlipped = false;
        _flipController.reset();
        _isLoading = false;
      });
    }
  }

  void _flipCard() {
    if (_isFlipped) {
      _flipController.reverse();
    } else {
      _flipController.forward();
    }
    setState(() {
      _isFlipped = !_isFlipped;
    });
  }

  void _nextCard() {
    if (_vocabList.isEmpty) return;
    setState(() {
      _currentIndex = (_currentIndex + 1) % _vocabList.length;
      _isFlipped = false;
      _flipController.reset();
    });
  }

  void _prevCard() {
    if (_vocabList.isEmpty) return;
    setState(() {
      _currentIndex = (_currentIndex - 1 + _vocabList.length) % _vocabList.length;
      _isFlipped = false;
      _flipController.reset();
    });
  }

  Future<void> _markStatus(String status) async {
    if (_vocabList.isEmpty) return;
    final item = _vocabList[_currentIndex];
    setState(() {
      item.status = status;
    });
    await ApiService().updateVocabStatus(item.id, status);
    _nextCard();
  }

  @override
  void dispose() {
    _flipController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Akademik Kelime Kartları'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.brandLightBlue,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _vocabList.isEmpty ? '0 / 0' : '${_currentIndex + 1} / ${_vocabList.length}',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.brandBlue,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Level selector bar
                Container(
                  height: 48,
                  margin: const EdgeInsets.symmetric(vertical: 8),
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    children: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'all'].map((lvl) {
                      final isSel = _selectedLevel == lvl;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text(lvl.toUpperCase()),
                          selected: isSel,
                          onSelected: (_) {
                            setState(() => _selectedLevel = lvl);
                            _loadVocab();
                          },
                          selectedColor: AppTheme.brandBlue,
                          labelStyle: TextStyle(
                            color: isSel ? Colors.white : AppTheme.textMain,
                            fontWeight: FontWeight.w800,
                            fontSize: 12,
                          ),
                          backgroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                      );
                    }).toList(),
                  ),
                ),

                Expanded(
                  child: _vocabList.isEmpty
                      ? const Center(
                          child: Text('Bu seviyede kelime bulunamadı.', style: TextStyle(color: AppTheme.textMuted)),
                        )
                      : Center(
                          child: Padding(
                            padding: const EdgeInsets.all(20),
                            child: AnimatedBuilder(
                              animation: _flipAnimation,
                              builder: (context, child) {
                                final angle = _flipAnimation.value * pi;
                                final isUnder = (angle > pi / 2);

                                return Transform(
                                  transform: Matrix4.identity()
                                    ..setEntry(3, 2, 0.001)
                                    ..rotateY(angle),
                                  alignment: Alignment.center,
                                  child: isUnder
                                      ? Transform(
                                          transform: Matrix4.identity()..rotateY(pi),
                                          alignment: Alignment.center,
                                          child: _buildBackCard(_vocabList[_currentIndex]),
                                        )
                                      : _buildFrontCard(_vocabList[_currentIndex]),
                                );
                              },
                            ),
                          ),
                        ),
                ),

                // Controls row
                if (_vocabList.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 24, left: 20, right: 20),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        IconButton.filledTonal(
                          onPressed: _prevCard,
                          icon: const Icon(Icons.chevron_left_rounded),
                        ),
                        const SizedBox(width: 12),
                        OutlinedButton.icon(
                          onPressed: () => _markStatus('learning'),
                          icon: const Icon(Icons.schedule, size: 16),
                          label: const Text('Tekrar Et'),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: AppTheme.accentAmber,
                            side: const BorderSide(color: AppTheme.accentAmber),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                        ),
                        const SizedBox(width: 10),
                        ElevatedButton.icon(
                          onPressed: () => _markStatus('mastered'),
                          icon: const Icon(Icons.check, size: 16),
                          label: const Text('Öğrendim'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.accentEmerald,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                        ),
                        const SizedBox(width: 12),
                        IconButton.filledTonal(
                          onPressed: _nextCard,
                          icon: const Icon(Icons.chevron_right_rounded),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
    );
  }

  Widget _buildFrontCard(VocabularyItem word) {
    return InkWell(
      onTap: _flipCard,
      borderRadius: BorderRadius.circular(28),
      child: Container(
        width: double.infinity,
        height: 380,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: AppTheme.borderSubtle),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.brandLightBlue,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${word.level} Seviyesi',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue),
                  ),
                ),
                Text(
                  word.partOfSpeech.toUpperCase(),
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                ),
              ],
            ),
            Column(
              children: [
                Text(
                  word.word,
                  style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w900, color: AppTheme.textMain),
                ),
                if (word.pronunciation.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    word.pronunciation,
                    style: const TextStyle(fontSize: 14, fontFamily: 'monospace', color: AppTheme.textMuted),
                  ),
                ],
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey.shade200),
                  ),
                  child: Text(
                    '"${word.collocation.isNotEmpty ? word.collocation : 'Akademik Bağlam'}"',
                    style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: Color(0xFF475569)),
                  ),
                ),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: const [
                    Icon(Icons.flip_rounded, size: 14, color: AppTheme.textMuted),
                    SizedBox(width: 4),
                    Text('Çevirmek için dokun', style: TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                  ],
                ),
                Text(
                  word.status == 'mastered' ? '✓ Öğrenildi' : '○ Öğreniliyor',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: word.status == 'mastered' ? AppTheme.accentEmerald : AppTheme.textMuted,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBackCard(VocabularyItem word) {
    return InkWell(
      onTap: _flipCard,
      borderRadius: BorderRadius.circular(28),
      child: Container(
        width: double.infinity,
        height: 380,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF1E3A8A), Color(0xFF312E81)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(28),
          boxShadow: [
            BoxShadow(
              color: Colors.indigo.withValues(alpha: 0.3),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white24,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text('Türkçe Anlam & Detay', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white)),
                ),
                Text(word.word, style: const TextStyle(color: Colors.white70, fontWeight: FontWeight.w700, fontSize: 13)),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  word.meaningTr,
                  style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Color(0xFFFDE047)),
                ),
                const SizedBox(height: 8),
                Text(
                  word.definitionEn,
                  style: const TextStyle(fontSize: 13, color: Colors.white, height: 1.4),
                ),
                const SizedBox(height: 14),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Örnek Cümle:', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.amberAccent)),
                      const SizedBox(height: 4),
                      Text(
                        '"${word.exampleSentence}"',
                        style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: Colors.white),
                      ),
                    ],
                  ),
                ),
                if (word.synonyms.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Text(
                    'Eş Anlamlılar: ${word.synonyms.join(", ")}',
                    style: const TextStyle(fontSize: 11, color: Colors.white70),
                  ),
                ],
              ],
            ),
            const Center(
              child: Text(
                'Tekrar çevirmek için dokun',
                style: TextStyle(fontSize: 11, color: Colors.white60),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
