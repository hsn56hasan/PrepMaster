import 'dart:math';

/// Konu Yolu alıştırma türleri.
enum ExerciseType { choice, listen, match, order, quiz, type, dialogue }

/// Örnek konuşmanın bir satırı (A/B).
class DialogueLine {
  final String who;
  final String en;
  final String tr;
  const DialogueLine(this.who, this.en, this.tr);
}

/// Tek bir alıştırma. Seçenekli türlerde [answer] doğru seçeneğin metnidir.
class Exercise {
  final int key;
  final ExerciseType type;
  final String prompt;
  final String? display;
  final String? speak;
  final List<String> options;
  final String answer;
  final bool speakAnswer;
  final bool long;
  final List<MapEntry<String, String>> pairs; // eşleştirme: en -> tr
  final List<String> tokens; // cümle kurma
  final String? explain;
  final String? full; // boşluk doldurmanın tam cümlesi
  final List<DialogueLine> context; // konuşmayı tamamla: önceki satırlar
  final String? translation; // doğru cevabın Türkçesi

  const Exercise({
    required this.key,
    required this.type,
    required this.prompt,
    this.display,
    this.speak,
    this.options = const [],
    this.answer = '',
    this.speakAnswer = false,
    this.long = false,
    this.pairs = const [],
    this.tokens = const [],
    this.explain,
    this.full,
    this.context = const [],
    this.translation,
  });

  /// Yanlış yapılıp dersin sonuna geri gelen kopya: seçenekler/kelimeler yeniden karışır.
  Exercise reshuffled(Random rnd) => Exercise(
        key: key,
        type: type,
        prompt: prompt,
        display: display,
        speak: speak,
        options: _shuffle(options, rnd),
        answer: answer,
        speakAnswer: speakAnswer,
        long: long,
        pairs: pairs,
        tokens: _shuffle(tokens, rnd),
        explain: explain,
        full: full,
        context: context,
        translation: translation,
      );

  /// Ekranda gösterilecek doğru cevap.
  String get answerText {
    if (type == ExerciseType.quiz) return full ?? answer;
    if (type == ExerciseType.dialogue && translation != null) return '$answer ($translation)';
    if (type == ExerciseType.match) return pairs.map((p) => '${p.key} = ${p.value}').join(' · ');
    return answer;
  }
}

List<T> _shuffle<T>(List<T> list, Random rnd) => List<T>.of(list)..shuffle(rnd);

class _Item {
  final String en;
  final String tr;
  const _Item(this.en, this.tr);
}

/// Sunucudan gelen ders paketinden (bir ya da birkaç konu) alıştırma listesi üretir.
/// Sıra kolaydan zora: önce tanıma, sonra eşleştirme/dinleme, en sonda cümle kurma ve yazma.
class LessonEngine {
  static List<Exercise> build(Map<String, dynamic> bundle, {Random? random, bool tts = true}) {
    final rnd = random ?? Random();
    final topics = ((bundle['topics'] as List?) ?? const []).cast<Map<String, dynamic>>();
    final level = (bundle['level'] as String?) ?? '';
    final vocab = <_Item>[];
    final phrases = <_Item>[];
    final quiz = <Map<String, dynamic>>[];
    final dialogues = <List<DialogueLine>>[];
    for (final t in topics) {
      for (final v in (t['vocab'] as List? ?? const [])) {
        vocab.add(_Item('${v['en']}', '${v['tr']}'));
      }
      for (final p in (t['phrases'] as List? ?? const [])) {
        phrases.add(_Item('${p['en']}', '${p['tr']}'));
      }
      for (final q in (t['quiz'] as List? ?? const [])) {
        quiz.add(Map<String, dynamic>.from(q as Map));
      }
      final sp = t['speaking'];
      final dl = sp is Map ? sp['dialogue'] : null;
      if (dl is List && dl.length >= 2) {
        dialogues.add([for (final l in dl) DialogueLine('${l['who']}', '${l['en']}', '${l['tr']}')]);
      }
    }
    if (vocab.length < 8 || phrases.length < 3 || quiz.length < 4) return const [];

    final v = _shuffle(vocab, rnd);
    final ph = _shuffle(phrases, rnd);
    final qz = _shuffle(quiz, rnd);
    var key = 0;

    Exercise choice(_Item item, {required bool enToTr}) {
      final others = _shuffle(vocab.where((x) => x.en != item.en).toList(), rnd).take(3);
      return Exercise(
        key: key++,
        type: ExerciseType.choice,
        prompt: enToTr ? 'Bu kelimenin anlamı ne?' : 'Bunun İngilizcesi hangisi?',
        display: enToTr ? item.en : item.tr,
        speak: enToTr ? item.en : null,
        speakAnswer: !enToTr,
        options: _shuffle([enToTr ? item.tr : item.en, ...others.map((o) => enToTr ? o.tr : o.en)], rnd),
        answer: enToTr ? item.tr : item.en,
      );
    }

    Exercise listen(_Item item) {
      if (!tts) return choice(item, enToTr: true);
      final others = _shuffle(vocab.where((x) => x.en != item.en).toList(), rnd).take(3);
      return Exercise(
        key: key++,
        type: ExerciseType.listen,
        prompt: 'Duyduğun kelimeyi seç',
        speak: item.en,
        options: _shuffle([item.en, ...others.map((o) => o.en)], rnd),
        answer: item.en,
      );
    }

    Exercise match(List<_Item> items) => Exercise(
          key: key++,
          type: ExerciseType.match,
          prompt: 'Eşleri bul',
          pairs: [for (final i in items) MapEntry(i.en, i.tr)],
        );

    Exercise order(_Item phrase) {
      final words = phrase.en.trim().split(RegExp(r'\s+'));
      final extra = <String>[];
      if (!level.startsWith('A')) {
        final lower = words.map((w) => w.toLowerCase().replaceAll(RegExp(r'[.,!?]'), '')).toSet();
        extra.addAll(_shuffle(
          vocab.where((x) => !x.en.contains(' ') && !lower.contains(x.en.toLowerCase())).map((x) => x.en).toList(),
          rnd,
        ).take(2));
      }
      return Exercise(
        key: key++,
        type: ExerciseType.order,
        prompt: 'Cümleyi İngilizce kur',
        display: phrase.tr,
        speak: phrase.en,
        tokens: _shuffle([...words, ...extra], rnd),
        answer: words.join(' '),
      );
    }

    Exercise quizEx(Map<String, dynamic> q) {
      final opts = (q['options'] as List).map((o) => '$o').toList();
      final ans = opts[(q['answer'] as num).toInt()];
      final text = '${q['q']}';
      return Exercise(
        key: key++,
        type: ExerciseType.quiz,
        prompt: 'Boşluğu doldur',
        display: text,
        options: _shuffle(opts, rnd),
        answer: ans,
        explain: q['explain_tr'] as String?,
        full: text.replaceFirst('___', ans),
        long: true,
      );
    }

    Exercise phraseChoice(_Item phrase) {
      final others = _shuffle(phrases.where((x) => x.en != phrase.en).toList(), rnd).take(3);
      return Exercise(
        key: key++,
        type: ExerciseType.choice,
        prompt: 'Bu cümle ne anlama geliyor?',
        display: phrase.en,
        speak: phrase.en,
        long: true,
        options: _shuffle([phrase.tr, ...others.map((o) => o.tr)], rnd),
        answer: phrase.tr,
      );
    }

    final replies = [for (final d in dialogues) for (final l in d) if (l.who == 'B') l.en];
    final replyPool = replies.length >= 4 ? replies : [...replies, ...phrases.map((p) => p.en)];

    Exercise? dialogueEx(List<DialogueLine>? d) {
      if (d == null) return null;
      final bIdx = [for (var i = 1; i < d.length; i++) if (d[i].who == 'B') i];
      if (bIdx.isEmpty) return null;
      final i = bIdx[rnd.nextInt(bIdx.length)];
      final answer = d[i].en;
      final pool = _shuffle(replyPool.where((r) => r != answer).toSet().toList(), rnd).take(3).toList();
      if (pool.length < 2) return null;
      return Exercise(
        key: key++,
        type: ExerciseType.dialogue,
        prompt: 'Konuşmayı tamamla',
        context: d.sublist(i - 3 < 0 ? 0 : i - 3, i),
        options: _shuffle([answer, ...pool], rnd),
        answer: answer,
        speak: answer,
        translation: d[i].tr,
        long: true,
      );
    }

    Exercise typeEx(_Item item) => Exercise(
          key: key++,
          type: ExerciseType.type,
          prompt: 'İngilizcesini yaz',
          display: item.tr,
          speak: item.en,
          answer: item.en,
        );

    if (topics.length == 1 || vocab.length < 11 || quiz.length < 5) {
      return <Exercise?>[
        choice(v[0], enToTr: true), choice(v[1], enToTr: true), choice(v[2], enToTr: false),
        match(v.sublist(3, 8)),
        listen(v[4]),
        order(ph[0]), quizEx(qz[0]), quizEx(qz[1]),
        phraseChoice(ph[1]), dialogueEx(dialogues.isEmpty ? null : dialogues.first), typeEx(v[5]), order(ph[2]),
        quizEx(qz[2]), quizEx(qz[3]),
      ].whereType<Exercise>().toList();
    }
    final dl = _shuffle(dialogues, rnd);
    return <Exercise?>[
      choice(v[0], enToTr: true), choice(v[1], enToTr: false), choice(v[2], enToTr: true),
      match(v.sublist(3, 8)),
      listen(v[8]),
      order(ph[0]), quizEx(qz[0]), dialogueEx(dl.isEmpty ? null : dl[0]), quizEx(qz[1]), phraseChoice(ph[1]),
      typeEx(v[9]), quizEx(qz[2]), dialogueEx(dl.length > 1 ? dl[1] : null), order(ph[2]), quizEx(qz[3]),
      typeEx(v[10]), quizEx(qz[4]),
    ].whereType<Exercise>().toList();
  }

  /// Karşılaştırma için sadeleştirme: küçük harf, noktalama yok, tek boşluk.
  static String normalize(String s) => s
      .toLowerCase()
      .replaceAll('’', "'")
      .replaceAll(RegExp(r'[.,!?;:"]'), '')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();

  static String _stripArticle(String s) => s.replaceFirst(RegExp(r'^(to|a|an|the) '), '');

  /// Yazma alıştırması: baştaki to/a/an/the yok sayılır; 5+ harfli cevapta tek harf hatası kabul edilir.
  static ({bool ok, bool typo}) checkTyped(String input, String answer) {
    final a = _stripArticle(normalize(input));
    final b = _stripArticle(normalize(answer));
    if (a.isEmpty) return (ok: false, typo: false);
    if (a == b) return (ok: true, typo: false);
    if (b.length >= 5 && _distance(a, b) <= 1) return (ok: true, typo: true);
    return (ok: false, typo: false);
  }

  static int _distance(String a, String b) {
    if ((a.length - b.length).abs() > 1) return 2;
    final prev = List<int>.generate(b.length + 1, (i) => i);
    for (var i = 1; i <= a.length; i++) {
      var diag = prev[0];
      prev[0] = i;
      for (var j = 1; j <= b.length; j++) {
        final tmp = prev[j];
        prev[j] = [prev[j] + 1, prev[j - 1] + 1, diag + (a[i - 1] == b[j - 1] ? 0 : 1)].reduce(min);
        diag = tmp;
      }
    }
    return prev[b.length];
  }

  /// Sunucuyla aynı yıldız eşikleri (%90 üç, %70 iki, %50 bir).
  static int starsFor(int pct) => pct >= 90 ? 3 : pct >= 70 ? 2 : pct >= 50 ? 1 : 0;
}
