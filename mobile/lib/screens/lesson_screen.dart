import 'dart:math';

import 'package:flutter/material.dart';

import '../models/lesson_path.dart';
import '../services/api_service.dart';
import '../services/lesson_engine.dart';
import '../services/speech_service.dart';
import '../theme/app_theme.dart';
import '../widgets/panel_widgets.dart';
import '../widgets/press3d.dart';
import 'path_screen.dart' show pathIcon;

typedef BundleLoader = Future<PathResponse> Function(String kind, String? id);
typedef ResultSender = Future<PathResponse> Function({required String nodeId, required int correct, required int total});

enum _Phase { loading, error, intro, exercise, feedback, outOfHearts, saving, end }

/// Tek ders / ünite tekrarı / karışık tekrar: tanıtım, 13–15 alıştırma, 5 kalp, sonuç.
/// Bitince Navigator ile {'next': sıradaki konu id'si} döner (yoksa null).
class LessonScreen extends StatefulWidget {
  final String kind; // topic | unit | review
  final String? id;
  final BundleLoader? loader; // testler için
  final ResultSender? sender; // testler için
  final Random? random;

  const LessonScreen({super.key, required this.kind, this.id, this.loader, this.sender, this.random});

  @override
  State<LessonScreen> createState() => _LessonScreenState();
}

const int kLessonHearts = 5;

class _LessonScreenState extends State<LessonScreen> {
  late final Random _rnd = widget.random ?? Random();
  _Phase _phase = _Phase.loading;
  String? _error;
  Map<String, dynamic>? _bundle;

  final List<Exercise> _queue = [];
  int _total = 0;
  int _done = 0;
  int _hearts = kLessonHearts;
  final Set<int> _firstWrong = {};
  Exercise? _ex;

  // alıştırma içi durum
  String? _selection;
  final List<int> _picked = [];
  final TextEditingController _typed = TextEditingController();
  List<String> _left = [], _right = [];
  final Set<String> _matched = {};
  String? _pickSide, _pickWord, _shake;
  int _misses = 0;

  // geri bildirim
  bool _ok = false;
  bool _typo = false;

  // sonuç
  Map<String, dynamic>? _result;
  String? _saveError;

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  @override
  void dispose() {
    _typed.dispose();
    SpeechService.instance.stop();
    super.dispose();
  }

  String get _nodeId {
    if (widget.kind == 'review') return 'review-${((_bundle?['level'] as String?) ?? 'all').toLowerCase()}';
    return '${_bundle?['id'] ?? widget.id}';
  }

  Future<void> _fetch() async {
    setState(() {
      _phase = _Phase.loading;
      _error = null;
    });
    final loader = widget.loader ?? ApiService().getPathBundle;
    final res = await loader(widget.kind, widget.id);
    if (!mounted) return;
    if (!res.ok) {
      setState(() {
        _phase = _Phase.error;
        _error = res.error;
      });
      return;
    }
    _bundle = res.data;
    _restart();
  }

  void _restart() {
    final list = LessonEngine.build(_bundle!, random: _rnd);
    setState(() {
      _queue
        ..clear()
        ..addAll(list);
      _total = list.length;
      _done = 0;
      _hearts = kLessonHearts;
      _firstWrong.clear();
      _result = null;
      _saveError = null;
      _phase = list.isEmpty ? _Phase.error : _Phase.intro;
      if (list.isEmpty) _error = 'Bu ders için alıştırma üretilemedi.';
    });
  }

  void _speak(String? text, {bool slow = false}) {
    if (text == null || text.isEmpty) return;
    SpeechService.instance.speak(text, slow: slow);
  }

  void _next() {
    if (_queue.isEmpty) {
      _finish();
      return;
    }
    final ex = _queue.removeAt(0);
    setState(() {
      _ex = ex;
      _phase = _Phase.exercise;
      _selection = null;
      _picked.clear();
      _typed.clear();
      _matched.clear();
      _pickSide = null;
      _pickWord = null;
      _shake = null;
      _misses = 0;
      if (ex.type == ExerciseType.match) {
        _left = [for (final p in ex.pairs) p.key]..shuffle(_rnd);
        _right = [for (final p in ex.pairs) p.value]..shuffle(_rnd);
      }
    });
    if (ex.type == ExerciseType.listen) {
      Future.delayed(const Duration(milliseconds: 250), () {
        if (mounted && _ex == ex) _speak(ex.speak);
      });
    }
  }

  bool get _canCheck {
    final ex = _ex;
    if (ex == null || _phase != _Phase.exercise) return false;
    switch (ex.type) {
      case ExerciseType.choice:
      case ExerciseType.listen:
      case ExerciseType.quiz:
        return _selection != null;
      case ExerciseType.order:
        return _picked.isNotEmpty;
      case ExerciseType.type:
        return _typed.text.trim().isNotEmpty;
      case ExerciseType.match:
        return false;
    }
  }

  void _check() {
    final ex = _ex;
    if (ex == null || !_canCheck) return;
    var ok = false, typo = false;
    switch (ex.type) {
      case ExerciseType.choice:
      case ExerciseType.listen:
      case ExerciseType.quiz:
        ok = _selection == ex.answer;
        break;
      case ExerciseType.order:
        final built = _picked.map((i) => ex.tokens[i]).join(' ');
        ok = LessonEngine.normalize(built) == LessonEngine.normalize(ex.answer);
        break;
      case ExerciseType.type:
        final r = LessonEngine.checkTyped(_typed.text, ex.answer);
        ok = r.ok;
        typo = r.typo;
        break;
      case ExerciseType.match:
        break;
    }
    _feedback(ok, typo: typo);
  }

  void _feedback(bool ok, {bool typo = false}) {
    final ex = _ex!;
    FocusScope.of(context).unfocus();
    setState(() {
      _ok = ok;
      _typo = typo;
      _phase = _Phase.feedback;
      if (ok) {
        _done += 1;
      } else {
        _firstWrong.add(ex.key);
        _hearts -= 1;
        _queue.add(ex.reshuffled(_rnd)); // yanlış alıştırma dersin sonunda yeniden gelir
      }
    });
    if (ok) {
      if (ex.speakAnswer) {
        _speak(ex.answer);
      } else if (ex.type != ExerciseType.listen && ex.type != ExerciseType.match) {
        _speak(ex.speak);
      }
    }
  }

  void _afterFeedback() {
    if (_hearts <= 0) {
      setState(() => _phase = _Phase.outOfHearts);
      return;
    }
    _next();
  }

  void _tapMatch(String side, String word) {
    if (_phase != _Phase.exercise) return;
    if (side == 'en') _speak(word);
    if (_pickSide == null || _pickSide == side) {
      setState(() {
        _pickSide = side;
        _pickWord = word;
        _shake = null;
      });
      return;
    }
    final en = side == 'en' ? word : _pickWord!;
    final tr = side == 'tr' ? word : _pickWord!;
    final pair = _ex!.pairs.firstWhere((p) => p.key == en);
    if (pair.value == tr) {
      setState(() {
        _matched.add(en);
        _pickSide = null;
        _pickWord = null;
        _shake = null;
      });
      if (_matched.length == _ex!.pairs.length) {
        // Eşleştirmede yanlış dokunuş kalp götürmez; birden fazla hata ilk deneme doğrusunu bozar
        if (_misses > 1) _firstWrong.add(_ex!.key);
        setState(() {
          _done += 1;
          _ok = true;
          _typo = false;
          _phase = _Phase.feedback;
        });
      }
    } else {
      setState(() {
        _misses += 1;
        _shake = word;
        _pickSide = null;
        _pickWord = null;
      });
    }
  }

  Future<void> _finish() async {
    setState(() => _phase = _Phase.saving);
    final correct = _total - _firstWrong.length;
    final sender = widget.sender ?? ApiService().postPathResult;
    final res = await sender(nodeId: _nodeId, correct: correct, total: _total);
    if (!mounted) return;
    setState(() {
      _phase = _Phase.end;
      _result = res.data;
      _saveError = res.ok ? null : res.error;
    });
    final pct = _total == 0 ? 0 : (correct * 100 / _total).round();
    if (LessonEngine.starsFor(pct) > 0) _speak(['Well done!', 'Great job!', 'Excellent!'][_rnd.nextInt(3)]);
  }

  Future<void> _close() async {
    final inProgress = (_phase == _Phase.exercise || _phase == _Phase.feedback) && _done > 0;
    if (inProgress) {
      final leave = await showDialog<bool>(
        context: context,
        builder: (c) => AlertDialog(
          title: const Text('Dersten çıkılsın mı?'),
          content: const Text('Çıkarsan bu dersteki ilerlemen kaydedilmez.'),
          actions: [
            TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Devam et')),
            TextButton(onPressed: () => Navigator.pop(c, true), child: const Text('Çık')),
          ],
        ),
      );
      if (leave != true || !mounted) return;
    }
    if (mounted) Navigator.of(context).pop(_phase == _Phase.end ? {'next': null} : null);
  }

  // ------------------------------------------------------------------ çizim

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) _close();
      },
      child: Scaffold(
        backgroundColor: dark ? AppTheme.darkSurfaceBg : const Color(0xFFF6FBF8),
        body: SafeArea(
          child: Column(children: [
            _topBar(),
            Expanded(child: _body()),
            _bottom(),
          ]),
        ),
      ),
    );
  }

  Widget _topBar() {
    final showProgress = _phase == _Phase.exercise || _phase == _Phase.feedback;
    return Padding(
      padding: const EdgeInsets.fromLTRB(6, 6, 14, 4),
      child: Row(children: [
        IconButton(
          key: const Key('lesson_close'),
          tooltip: 'Kapat',
          onPressed: _close,
          icon: Icon(Icons.close_rounded, color: PanelColors.muted(context)),
        ),
        if (showProgress) ...[
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(99),
              child: TweenAnimationBuilder<double>(
                tween: Tween(end: _total == 0 ? 0 : _done / _total),
                duration: const Duration(milliseconds: 350),
                builder: (_, v, _) => LinearProgressIndicator(
                  value: v,
                  minHeight: 14,
                  color: AppTheme.brandBlue,
                  backgroundColor: PanelColors.track(context),
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Semantics(
            label: '$_hearts kalp',
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.favorite_rounded, color: AppTheme.accentRose, size: 22),
              const SizedBox(width: 3),
              Text('$_hearts',
                  key: const Key('lesson_hearts'),
                  style: const TextStyle(color: AppTheme.accentRose, fontWeight: FontWeight.w900, fontSize: 16)),
            ]),
          ),
        ] else
          const Spacer(),
      ]),
    );
  }

  TextStyle get _h1 => TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: PanelColors.text(context), height: 1.2);

  Widget _body() {
    switch (_phase) {
      case _Phase.loading:
      case _Phase.saving:
        return Center(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 12),
            Text(_phase == _Phase.saving ? 'Sonuç kaydediliyor…' : 'Ders hazırlanıyor…',
                style: TextStyle(color: PanelColors.muted(context))),
          ]),
        );
      case _Phase.error:
        return Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.lock_clock_rounded, size: 44, color: PanelColors.muted(context)),
              const SizedBox(height: 10),
              Text(_error ?? 'Ders açılamadı.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: PanelColors.text(context), fontWeight: FontWeight.w600)),
            ]),
          ),
        );
      case _Phase.intro:
        return _intro();
      case _Phase.outOfHearts:
        return _scroll([
          const SizedBox(height: 40),
          const Icon(Icons.heart_broken_rounded, size: 72, color: AppTheme.accentRose),
          const SizedBox(height: 14),
          Text('Kalplerin bitti', textAlign: TextAlign.center, style: _h1),
          const SizedBox(height: 8),
          Text('Sorun değil, bekleme süresi yok. Kelimelere bir kez daha göz atıp dersi baştan dene.',
              textAlign: TextAlign.center, style: TextStyle(color: PanelColors.muted(context), height: 1.4)),
        ]);
      case _Phase.end:
        return _end();
      case _Phase.exercise:
      case _Phase.feedback:
        return _exercise();
    }
  }

  Widget _scroll(List<Widget> children) => SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(18, 10, 18, 24),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: children),
      );

  Widget _intro() {
    final b = _bundle!;
    final topics = ((b['topics'] as List?) ?? const []).cast<Map<String, dynamic>>();
    if (widget.kind == 'topic' && topics.isNotEmpty) {
      final t = topics.first;
      final vocab = ((t['vocab'] as List?) ?? const []).cast<Map>();
      final tip = (t['tip_example'] as Map?) ?? const {};
      return _scroll([
        Text('${b['level']} · ${b['unit_title'] ?? ''}'.toUpperCase(),
            style: const TextStyle(color: Color(0xFF047857), fontSize: 11, fontWeight: FontWeight.w900, letterSpacing: 0.6)),
        const SizedBox(height: 4),
        Text('${t['title_tr']}', style: _h1),
        Text('${t['title_en']}', style: TextStyle(color: PanelColors.muted(context))),
        const SizedBox(height: 10),
        Text('${t['intro_tr']}', style: TextStyle(color: PanelColors.text(context), height: 1.4)),
        const SizedBox(height: 18),
        Text('BU DERSİN KELİMELERİ',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w900, letterSpacing: 0.6, color: PanelColors.muted(context))),
        const SizedBox(height: 8),
        LayoutBuilder(builder: (context, c) {
          final w = (c.maxWidth - 8) / 2;
          return Wrap(spacing: 8, runSpacing: 8, children: [
            for (final v in vocab)
              SizedBox(
                width: w,
                child: _VocabTile(en: '${v['en']}', tr: '${v['tr']}', onTap: () => _speak('${v['en']}')),
              ),
          ]);
        }),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Theme.of(context).brightness == Brightness.dark ? const Color(0x1F059669) : const Color(0xFFECFDF5),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFA7F3D0)),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Row(children: [
              Icon(Icons.lightbulb_rounded, size: 18, color: Color(0xFF047857)),
              SizedBox(width: 6),
              Text('İpucu', style: TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF047857))),
            ]),
            const SizedBox(height: 6),
            Text('${t['tip_tr']}', style: TextStyle(color: PanelColors.text(context), height: 1.4)),
            const SizedBox(height: 8),
            InkWell(
              onTap: () => _speak('${tip['en']}'),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('${tip['en']}', style: TextStyle(fontWeight: FontWeight.w800, color: PanelColors.text(context))),
                Text('${tip['tr']}', style: TextStyle(fontSize: 12, color: PanelColors.muted(context))),
              ]),
            ),
          ]),
        ),
      ]);
    }
    return _scroll([
      Text('${b['level'] ?? ''} · ${widget.kind == 'unit' ? 'Ünite tekrarı' : 'Karışık tekrar'}'.toUpperCase(),
          style: const TextStyle(color: Color(0xFF047857), fontSize: 11, fontWeight: FontWeight.w900, letterSpacing: 0.6)),
      const SizedBox(height: 4),
      Text('${b['title_tr']}', style: _h1),
      const SizedBox(height: 10),
      Text('$_total alıştırma, bu konulardan karışık geliyor:', style: TextStyle(color: PanelColors.text(context))),
      const SizedBox(height: 10),
      for (final t in topics)
        Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(children: [
            Icon(pathIcon(t['icon'] as String?), size: 20, color: AppTheme.brandBlue),
            const SizedBox(width: 8),
            Expanded(child: Text('${t['title_tr']}', style: TextStyle(color: PanelColors.text(context)))),
          ]),
        ),
    ]);
  }

  Widget _exercise() {
    final ex = _ex!;
    final locked = _phase != _Phase.exercise;
    final children = <Widget>[
      Text(ex.prompt, style: _h1),
      const SizedBox(height: 16),
    ];
    switch (ex.type) {
      case ExerciseType.choice:
      case ExerciseType.quiz:
        children.add(_displayCard(ex));
        children.add(const SizedBox(height: 16));
        children.addAll(_options(ex, locked));
        break;
      case ExerciseType.listen:
        children.add(Row(mainAxisAlignment: MainAxisAlignment.center, crossAxisAlignment: CrossAxisAlignment.end, children: [
          Press3D(
            key: const Key('lesson_listen'),
            semanticLabel: 'Dinle',
            onTap: () => _speak(ex.speak),
            color: AppTheme.brandBlue,
            baseColor: const Color(0xFF047857),
            borderRadius: BorderRadius.circular(24),
            width: 88,
            height: 88,
            depth: 6,
            padding: EdgeInsets.zero,
            child: const Center(child: Icon(Icons.volume_up_rounded, size: 40, color: Colors.white)),
          ),
          const SizedBox(width: 12),
          Press3D(
            semanticLabel: 'Yavaş dinle',
            onTap: () => _speak(ex.speak, slow: true),
            color: AppTheme.brandSage,
            baseColor: const Color(0xFF4A775F),
            borderRadius: BorderRadius.circular(18),
            width: 58,
            height: 58,
            depth: 5,
            padding: EdgeInsets.zero,
            child: const Center(child: Icon(Icons.slow_motion_video_rounded, size: 26, color: Colors.white)),
          ),
        ]));
        children.add(const SizedBox(height: 20));
        children.addAll(_options(ex, locked));
        break;
      case ExerciseType.match:
        children.add(Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Expanded(child: Column(children: [for (final w in _left) _matchTile('en', w)])),
          const SizedBox(width: 10),
          Expanded(child: Column(children: [for (final w in _right) _matchTile('tr', w)])),
        ]));
        break;
      case ExerciseType.order:
        children.add(_displayCard(ex));
        children.add(const SizedBox(height: 10));
        children.add(Container(
          key: const Key('lesson_answer_line'),
          constraints: const BoxConstraints(minHeight: 58),
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            border: Border.symmetric(horizontal: BorderSide(color: PanelColors.border(context), width: 2)),
          ),
          child: Align(
            alignment: Alignment.centerLeft,
            child: _picked.isEmpty
                ? Text('Kelimelere sırayla dokun', style: TextStyle(fontSize: 12, color: PanelColors.muted(context)))
                : Wrap(spacing: 8, runSpacing: 8, children: [
                    for (final i in _picked)
                      _token(ex.tokens[i], onTap: locked ? null : () => setState(() => _picked.remove(i))),
                  ]),
          ),
        ));
        children.add(const SizedBox(height: 18));
        children.add(Wrap(alignment: WrapAlignment.center, spacing: 8, runSpacing: 8, children: [
          for (var i = 0; i < ex.tokens.length; i++)
            _token(ex.tokens[i],
                key: Key('lesson_token_$i'),
                used: _picked.contains(i),
                onTap: locked || _picked.contains(i) ? null : () => setState(() => _picked.add(i))),
        ]));
        break;
      case ExerciseType.type:
        children.add(_displayCard(ex));
        children.add(const SizedBox(height: 16));
        children.add(TextField(
          key: const Key('lesson_type_input'),
          controller: _typed,
          enabled: !locked,
          autofocus: true,
          autocorrect: false,
          enableSuggestions: false,
          textInputAction: TextInputAction.done,
          onChanged: (_) => setState(() {}),
          onSubmitted: (_) => _check(),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: PanelColors.text(context)),
          decoration: InputDecoration(
            hintText: 'İngilizcesini yaz…',
            filled: true,
            fillColor: PanelColors.card(context),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide(color: PanelColors.border(context), width: 2),
            ),
            disabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide(color: PanelColors.border(context), width: 2),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: const BorderSide(color: Color(0xFF34D399), width: 2),
            ),
          ),
        ));
        break;
    }
    return _scroll(children);
  }

  Widget _displayCard(Exercise ex) {
    final text = ex.display ?? '';
    Widget content;
    if (ex.type == ExerciseType.quiz) {
      final parts = text.split('___');
      content = Text.rich(TextSpan(children: [
        TextSpan(text: parts.first),
        const TextSpan(
          text: ' ______ ',
          style: TextStyle(color: AppTheme.brandBlue, fontWeight: FontWeight.w900),
        ),
        if (parts.length > 1) TextSpan(text: parts.sublist(1).join('___')),
      ]));
    } else {
      content = Text(text);
    }
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: PanelColors.card(context),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: PanelColors.border(context), width: 2),
      ),
      child: Row(crossAxisAlignment: CrossAxisAlignment.center, children: [
        if (ex.speak != null && ex.type != ExerciseType.type && ex.type != ExerciseType.order) ...[
          InkWell(
            borderRadius: BorderRadius.circular(10),
            onTap: () => _speak(ex.speak),
            child: Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(color: AppTheme.brandLightBlue, borderRadius: BorderRadius.circular(10)),
              child: const Icon(Icons.volume_up_rounded, size: 20, color: AppTheme.brandBlue),
            ),
          ),
          const SizedBox(width: 12),
        ],
        Expanded(
          child: DefaultTextStyle.merge(
            style: TextStyle(
              fontSize: ex.long ? 17 : 21,
              fontWeight: ex.long ? FontWeight.w700 : FontWeight.w900,
              color: PanelColors.text(context),
              height: 1.4,
            ),
            child: content,
          ),
        ),
      ]),
    );
  }

  List<Widget> _options(Exercise ex, bool locked) {
    return [
      for (var i = 0; i < ex.options.length; i++)
        Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: _OptionTile(
            key: Key('lesson_option_$i'),
            index: i + 1,
            text: ex.options[i],
            state: locked
                ? (ex.options[i] == ex.answer
                    ? _OptState.right
                    : (ex.options[i] == _selection ? _OptState.wrong : _OptState.idle))
                : (ex.options[i] == _selection ? _OptState.selected : _OptState.idle),
            onTap: locked
                ? null
                : () {
                    setState(() => _selection = ex.options[i]);
                    if (ex.type == ExerciseType.listen) _speak(ex.options[i]);
                  },
          ),
        ),
    ];
  }

  Widget _matchTile(String side, String word) {
    final en = side == 'en' ? word : _ex!.pairs.firstWhere((p) => p.value == word).key;
    final done = _matched.contains(en);
    final picked = _pickSide == side && _pickWord == word;
    final state = done
        ? _OptState.done
        : picked
            ? _OptState.selected
            : (_shake == word ? _OptState.wrong : _OptState.idle);
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: _OptionTile(
        key: Key('lesson_match_${side}_$word'),
        text: word,
        center: true,
        state: state,
        onTap: done || _phase != _Phase.exercise ? null : () => _tapMatch(side, word),
      ),
    );
  }

  Widget _token(String w, {Key? key, bool used = false, VoidCallback? onTap}) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final bg = used ? PanelColors.track(context) : PanelColors.card(context);
    return Press3D(
      key: key,
      onTap: onTap,
      color: bg,
      baseColor: used ? bg : PanelColors.border(context),
      borderColor: used ? bg : PanelColors.border(context),
      depth: used ? 0 : 3,
      borderRadius: BorderRadius.circular(12),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      child: Text(w,
          style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: used ? Colors.transparent : (dark ? AppTheme.darkTextMain : AppTheme.textMain))),
    );
  }

  Widget _end() {
    final correct = _total - _firstWrong.length;
    final pct = _total == 0 ? 0 : (correct * 100 / _total).round();
    final stars = (_result?['stars'] as num?)?.toInt() ?? LessonEngine.starsFor(pct);
    final xp = (_result?['xp_gained'] as num?)?.toInt() ?? 0;
    final title = stars == 0 ? 'Az kaldı!' : (pct == 100 ? 'Kusursuz!' : 'Ders tamamlandı!');
    final sub = stars == 0
        ? 'Geçmek için ilk denemede en az %50 doğru gerekiyor.'
        : (_result?['first_completion'] == true && widget.kind == 'topic' ? 'Sıradaki ders açıldı.' : 'Bilgini tazeledin.');
    Widget tile(String label, String value, Color color) => Expanded(
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 6),
            decoration: BoxDecoration(
              color: PanelColors.card(context),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: PanelColors.border(context)),
            ),
            child: Column(children: [
              Text(label, style: TextStyle(fontSize: 11, color: PanelColors.muted(context), fontWeight: FontWeight.w700)),
              const SizedBox(height: 4),
              FittedBox(
                child: Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: color)),
              ),
            ]),
          ),
        );
    return _scroll([
      const SizedBox(height: 18),
      Row(mainAxisAlignment: MainAxisAlignment.center, crossAxisAlignment: CrossAxisAlignment.end, children: [
        for (var s = 1; s <= 3; s++)
          TweenAnimationBuilder<double>(
            key: Key('lesson_star_$s'),
            tween: Tween(begin: 0.3, end: 1),
            duration: Duration(milliseconds: 380 + s * 160),
            curve: Curves.elasticOut,
            builder: (_, v, child) => Transform.scale(scale: v, child: child),
            child: Icon(Icons.star_rounded,
                size: s == 2 ? 84 : 64, color: s <= stars ? AppTheme.accentAmber : PanelColors.border(context)),
          ),
      ]),
      const SizedBox(height: 10),
      Text(title, textAlign: TextAlign.center, style: _h1.copyWith(fontSize: 26)),
      const SizedBox(height: 4),
      Text(sub, textAlign: TextAlign.center, style: TextStyle(color: PanelColors.muted(context))),
      const SizedBox(height: 22),
      Row(children: [
        tile('Doğruluk', '%$pct', PanelColors.text(context)),
        const SizedBox(width: 8),
        tile('XP', '+$xp', AppTheme.accentAmber),
        const SizedBox(width: 8),
        tile('Kalp', '$_hearts', AppTheme.accentRose),
      ]),
      if (_saveError != null) ...[
        const SizedBox(height: 14),
        Text(_saveError!, textAlign: TextAlign.center, style: const TextStyle(color: AppTheme.accentRose, fontWeight: FontWeight.w700)),
      ],
    ]);
  }

  // ------------------------------------------------------------------ alt panel

  Widget _primary(String label, VoidCallback? onTap, {Key? key, Color? color, Color? base}) {
    final enabled = onTap != null;
    return Press3D(
      key: key,
      onTap: onTap,
      color: enabled ? (color ?? AppTheme.brandBlue) : PanelColors.track(context),
      baseColor: enabled ? (base ?? const Color(0xFF047857)) : PanelColors.border(context),
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
      child: Center(
        child: Text(label,
            style: TextStyle(
                color: enabled ? Colors.white : PanelColors.muted(context),
                fontWeight: FontWeight.w900,
                fontSize: 15,
                letterSpacing: 0.3)),
      ),
    );
  }

  Widget _secondary(String label, VoidCallback onTap, {Key? key}) => Press3D(
        key: key,
        onTap: onTap,
        color: PanelColors.card(context),
        baseColor: PanelColors.border(context),
        borderColor: PanelColors.border(context),
        depth: 3,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 13),
        child: Center(
          child: Text(label, style: TextStyle(color: PanelColors.text(context), fontWeight: FontWeight.w800)),
        ),
      );

  Widget _bottom() {
    final dark = Theme.of(context).brightness == Brightness.dark;
    Color bg = PanelColors.card(context);
    Color border = PanelColors.border(context);
    Widget child;
    switch (_phase) {
      case _Phase.loading:
      case _Phase.saving:
        return const SizedBox(height: 8);
      case _Phase.error:
        child = Row(children: [
          Expanded(child: _secondary('Yola dön', () => Navigator.of(context).pop())),
          if (_bundle == null) ...[
            const SizedBox(width: 10),
            Expanded(child: _primary('Tekrar dene', _fetch)),
          ],
        ]);
        break;
      case _Phase.intro:
        child = _primary('Derse başla', _next, key: const Key('lesson_start'));
        break;
      case _Phase.exercise:
        child = Row(children: [
          _secondary('Atla', () => _feedback(false), key: const Key('lesson_skip')),
          const SizedBox(width: 10),
          if (_ex?.type != ExerciseType.match)
            Expanded(child: _primary('Kontrol et', _canCheck ? _check : null, key: const Key('lesson_check')))
          else
            const Spacer(),
        ]);
        break;
      case _Phase.feedback:
        final ex = _ex!;
        final ok = _ok;
        bg = ok
            ? (dark ? const Color(0xFF064E3B) : const Color(0xFFD1FAE5))
            : (dark ? const Color(0xFF4C0519) : const Color(0xFFFFE4E6));
        border = ok ? const Color(0xFFA7F3D0) : const Color(0xFFFECDD3);
        final fg = ok
            ? (dark ? const Color(0xFFA7F3D0) : const Color(0xFF065F46))
            : (dark ? const Color(0xFFFECDD3) : const Color(0xFF9F1239));
        final title = ok
            ? (_typo
                ? 'Doğru, küçük bir yazım hatası var'
                : (ex.type == ExerciseType.match && _misses > 0
                    ? 'Tamamlandı'
                    : const ['Harika!', 'Aynen böyle!', 'Çok iyi!', 'Doğru!'][ex.key % 4]))
            : 'Doğru cevap:';
        child = Column(crossAxisAlignment: CrossAxisAlignment.stretch, mainAxisSize: MainAxisSize.min, children: [
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(color: dark ? Colors.white12 : Colors.white, shape: BoxShape.circle),
              child: Icon(ok ? Icons.check_rounded : Icons.close_rounded,
                  color: ok ? AppTheme.brandBlue : AppTheme.accentRose),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(title, key: const Key('lesson_feedback_title'),
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: fg)),
                if (!ok || _typo)
                  Text(ex.answerText, style: TextStyle(fontWeight: FontWeight.w700, color: fg)),
                if (ex.type == ExerciseType.quiz && (ex.explain ?? '').isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(ex.explain!, style: TextStyle(fontSize: 12, color: fg)),
                  ),
              ]),
            ),
          ]),
          const SizedBox(height: 12),
          _primary(_hearts <= 0 ? 'Bitir' : 'Devam', _afterFeedback,
              key: const Key('lesson_continue'),
              color: ok ? (dark ? const Color(0xFF34D399) : AppTheme.brandBlue) : AppTheme.accentRose,
              base: ok ? (dark ? AppTheme.brandBlue : const Color(0xFF047857)) : const Color(0xFFBE123C)),
        ]);
        break;
      case _Phase.outOfHearts:
        child = Row(children: [
          Expanded(child: _secondary('Yola dön', () => Navigator.of(context).pop())),
          const SizedBox(width: 10),
          Expanded(child: _primary('Tekrar dene', _restart, key: const Key('lesson_retry'))),
        ]);
        break;
      case _Phase.end:
        final next = _result?['next_topic'] as String?;
        child = Row(children: [
          Expanded(child: _secondary('Yola dön', () => Navigator.of(context).pop({'next': null}), key: const Key('lesson_back'))),
          const SizedBox(width: 10),
          Expanded(
            child: next != null
                ? _primary('Sonraki ders', () => Navigator.of(context).pop({'next': next}), key: const Key('lesson_next'))
                : _primary('Tekrar çöz', _restart, key: const Key('lesson_retry')),
          ),
        ]);
        break;
    }
    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
      decoration: BoxDecoration(color: bg, border: Border(top: BorderSide(color: border, width: 2))),
      child: child,
    );
  }
}

enum _OptState { idle, selected, right, wrong, done }

class _OptionTile extends StatelessWidget {
  final int? index;
  final String text;
  final _OptState state;
  final VoidCallback? onTap;
  final bool center;

  const _OptionTile({super.key, this.index, required this.text, required this.state, this.onTap, this.center = false});

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    Color bg = PanelColors.card(context), border = PanelColors.border(context), fg = PanelColors.text(context);
    switch (state) {
      case _OptState.selected:
        bg = dark ? const Color(0x2E059669) : const Color(0xFFECFDF5);
        border = const Color(0xFF34D399);
        fg = dark ? const Color(0xFFA7F3D0) : const Color(0xFF065F46);
        break;
      case _OptState.right:
        bg = dark ? const Color(0x3810B981) : const Color(0xFFD1FAE5);
        border = const Color(0xFF10B981);
        fg = dark ? const Color(0xFFA7F3D0) : const Color(0xFF065F46);
        break;
      case _OptState.wrong:
        bg = dark ? const Color(0x2EF43F5E) : const Color(0xFFFFE4E6);
        border = const Color(0xFFFB7185);
        fg = dark ? const Color(0xFFFECDD3) : const Color(0xFF9F1239);
        break;
      case _OptState.done:
        fg = PanelColors.muted(context).withValues(alpha: 0.5);
        border = PanelColors.border(context).withValues(alpha: 0.5);
        bg = PanelColors.track(context).withValues(alpha: 0.4);
        break;
      case _OptState.idle:
        break;
    }
    return Press3D(
      onTap: onTap,
      color: bg,
      baseColor: state == _OptState.done ? bg : border,
      borderColor: border,
      depth: state == _OptState.done ? 0 : 4,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
      child: Row(children: [
        if (index != null) ...[
          Container(
            width: 26,
            height: 26,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: border, width: 2),
            ),
            child: Text('$index', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: PanelColors.muted(context))),
          ),
          const SizedBox(width: 12),
        ],
        Expanded(
          child: Text(text,
              textAlign: center ? TextAlign.center : TextAlign.start,
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: fg)),
        ),
      ]),
    );
  }
}

class _VocabTile extends StatelessWidget {
  final String en;
  final String tr;
  final VoidCallback onTap;
  const _VocabTile({required this.en, required this.tr, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Press3D(
      onTap: onTap,
      color: PanelColors.card(context),
      baseColor: PanelColors.border(context),
      borderColor: PanelColors.border(context),
      depth: 3,
      borderRadius: BorderRadius.circular(14),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 9),
      child: Row(children: [
        Expanded(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(en,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(fontWeight: FontWeight.w800, color: PanelColors.text(context))),
            Text(tr,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(fontSize: 12, color: PanelColors.muted(context))),
          ]),
        ),
        const Icon(Icons.volume_up_rounded, size: 18, color: AppTheme.brandBlue),
      ]),
    );
  }
}
