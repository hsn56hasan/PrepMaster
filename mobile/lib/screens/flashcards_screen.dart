import 'dart:math';

import 'package:flutter/material.dart';

import '../models/vocabulary.dart';
import '../services/api_service.dart';
import '../services/speech_service.dart';
import '../theme/app_theme.dart';
import '../widgets/level_selector.dart';

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
    SpeechService.instance.stop();
    setState(() {
      _currentIndex = (_currentIndex + 1) % _vocabList.length;
      _isFlipped = false;
      _flipController.reset();
    });
  }

  void _prevCard() {
    if (_vocabList.isEmpty) return;
    SpeechService.instance.stop();
    setState(() {
      _currentIndex =
          (_currentIndex - 1 + _vocabList.length) % _vocabList.length;
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
    SpeechService.instance.stop();
    _flipController.dispose();
    super.dispose();
  }

  /// Sesli okuma; telefonda İngilizce ses yoksa nasıl kurulacağını söyler.
  Future<void> _say(String text, {bool slow = false}) async {
    final ok = await SpeechService.instance.speak(text, slow: slow);
    if (!ok && mounted) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(
            key: Key('tts_unavailable'),
            content: Text(
              'Sesli okuma için telefonda İngilizce ses gerekli: Ayarlar > Genel yönetim > '
              'Metin okuma çıkışı bölümünden İngilizce ses verisini indirin.',
            ),
            duration: Duration(seconds: 6),
          ),
        );
    }
  }

  /// Hoparlör düğmesi: okurken simgesi dalgaya döner.
  Widget _speakButton({
    required Key key,
    required String text,
    required String label,
    required IconData icon,
    bool slow = false,
    bool onDark = false,
  }) {
    return ValueListenableBuilder<String?>(
      valueListenable: SpeechService.instance.speaking,
      builder: (context, current, _) {
        final active = current == text.trim();
        final fg = onDark ? Colors.white : AppTheme.brandBlue;
        return TextButton.icon(
          key: key,
          onPressed: () => _say(text, slow: slow),
          icon: Icon(
            active ? Icons.graphic_eq_rounded : icon,
            size: 18,
            color: fg,
          ),
          label: Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w800,
              color: fg,
            ),
          ),
          style: TextButton.styleFrom(
            backgroundColor: onDark
                ? Colors.white.withValues(alpha: 0.15)
                : AppTheme.brandLightBlue,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            minimumSize: const Size(0, 36),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(18),
            ),
          ),
        );
      },
    );
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
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: AppTheme.brandLightBlue,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _vocabList.isEmpty
                      ? '0 / 0'
                      : '${_currentIndex + 1} / ${_vocabList.length}',
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
                LevelSelector(
                  selected: _selectedLevel,
                  onSelected: (lvl) {
                    SpeechService.instance.stop();
                    setState(() => _selectedLevel = lvl);
                    _loadVocab();
                  },
                ),

                Expanded(
                  child: _vocabList.isEmpty
                      ? const Center(
                          child: Text(
                            'Bu seviyede kelime bulunamadı.',
                            style: TextStyle(color: AppTheme.textMuted),
                          ),
                        )
                      : Center(
                          child: Padding(
                            padding: const EdgeInsets.all(20),
                            child: ConstrainedBox(
                              constraints: const BoxConstraints(maxHeight: 420),
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
                                            transform: Matrix4.identity()
                                              ..rotateY(pi),
                                            alignment: Alignment.center,
                                            child: _buildBackCard(
                                              _vocabList[_currentIndex],
                                            ),
                                          )
                                        : _buildFrontCard(
                                            _vocabList[_currentIndex],
                                          ),
                                  );
                                },
                              ),
                            ),
                          ),
                        ),
                ),

                // Controls row
                if (_vocabList.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(
                      bottom: 24,
                      left: 20,
                      right: 20,
                    ),
                    child: Row(
                      children: [
                        IconButton.filledTonal(
                          onPressed: _prevCard,
                          icon: const Icon(Icons.chevron_left_rounded),
                          tooltip: 'Önceki',
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => _markStatus('learning'),
                            icon: const Icon(Icons.schedule, size: 16),
                            label: const FittedBox(
                              fit: BoxFit.scaleDown,
                              child: Text('Tekrar Et', maxLines: 1),
                            ),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: AppTheme.accentAmber,
                              side: const BorderSide(
                                color: AppTheme.accentAmber,
                              ),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 12,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => _markStatus('mastered'),
                            icon: const Icon(Icons.check, size: 16),
                            label: const FittedBox(
                              fit: BoxFit.scaleDown,
                              child: Text('Öğrendim', maxLines: 1),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppTheme.accentEmerald,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 12,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        IconButton.filledTonal(
                          onPressed: _nextCard,
                          icon: const Icon(Icons.chevron_right_rounded),
                          tooltip: 'Sonraki',
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
        height: double.infinity,
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
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: AppTheme.brandLightBlue,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${word.level} Seviyesi',
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: AppTheme.brandBlue,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Flexible(
                  child: Text(
                    word.partOfSpeech.toUpperCase(),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.textMuted,
                    ),
                  ),
                ),
              ],
            ),
            Expanded(
              child: Center(
                child: SingleChildScrollView(
                  child: Column(
                    children: [
                      FittedBox(
                        fit: BoxFit.scaleDown,
                        child: Text(
                          word.word,
                          style: const TextStyle(
                            fontSize: 34,
                            fontWeight: FontWeight.w900,
                            color: AppTheme.textMain,
                          ),
                        ),
                      ),
                      if (word.pronunciation.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          word.pronunciation,
                          style: const TextStyle(
                            fontSize: 14,
                            fontFamily: 'monospace',
                            color: AppTheme.textMuted,
                          ),
                        ),
                      ],
                      const SizedBox(height: 12),
                      Wrap(
                        alignment: WrapAlignment.center,
                        spacing: 8,
                        runSpacing: 6,
                        children: [
                          _speakButton(
                            key: const Key('tts_word'),
                            text: word.word,
                            label: 'Dinle',
                            icon: Icons.volume_up_rounded,
                          ),
                          _speakButton(
                            key: const Key('tts_word_slow'),
                            text: word.word,
                            label: 'Yavaş',
                            icon: Icons.slow_motion_video_rounded,
                            slow: true,
                          ),
                        ],
                      ),
                      const SizedBox(height: 14),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 14,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.grey.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.grey.shade200),
                        ),
                        child: Text(
                          '"${word.collocation.isNotEmpty ? word.collocation : 'Akademik Bağlam'}"',
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 12,
                            fontStyle: FontStyle.italic,
                            color: Color(0xFF475569),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Row(
              children: [
                const Icon(
                  Icons.flip_rounded,
                  size: 14,
                  color: AppTheme.textMuted,
                ),
                const SizedBox(width: 4),
                const Expanded(
                  child: Text(
                    'Çevirmek için dokun',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                  ),
                ),
                Text(
                  word.status == 'mastered' ? '✓ Öğrenildi' : '○ Öğreniliyor',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: word.status == 'mastered'
                        ? AppTheme.accentEmerald
                        : AppTheme.textMuted,
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
        height: double.infinity,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF064E3B), Color(0xFF065F46)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(28),
          boxShadow: [
            BoxShadow(
              color: AppTheme.sageSwatch.withValues(alpha: 0.3),
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
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white24,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'Türkçe Anlam',
                    maxLines: 1,
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Flexible(
                  child: Text(
                    word.word,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontWeight: FontWeight.w700,
                      fontSize: 13,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      word.meaningTr,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w900,
                        color: Color(0xFFFDE047),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      word.definitionEn,
                      style: const TextStyle(
                        fontSize: 13,
                        color: Colors.white,
                        height: 1.4,
                      ),
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
                          Row(
                            children: [
                              const Expanded(
                                child: Text(
                                  'Örnek Cümle:',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w800,
                                    color: Colors.amberAccent,
                                  ),
                                ),
                              ),
                              _speakButton(
                                key: const Key('tts_sentence'),
                                text: word.exampleSentence,
                                label: 'Dinle',
                                icon: Icons.volume_up_rounded,
                                onDark: true,
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '"${word.exampleSentence}"',
                            style: const TextStyle(
                              fontSize: 12,
                              fontStyle: FontStyle.italic,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (word.synonyms.isNotEmpty) ...[
                      const SizedBox(height: 10),
                      Text(
                        'Eş Anlamlılar: ${word.synonyms.join(", ")}',
                        style: const TextStyle(
                          fontSize: 11,
                          color: Colors.white70,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
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
